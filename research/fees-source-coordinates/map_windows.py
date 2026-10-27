import collections
import hashlib
import gzip
import importlib.util
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
s = importlib.util.spec_from_file_location('dispatch_elf_helpers', HERE / 'elf_helpers.py')
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)


def dynamic_symbols(image):
    section = next(x for x in m.elf_layout(image)['sections'] if x['name'] == '.dynsym')
    strings = m.section_data(image, '.dynstr')
    rows = []
    for offset in range(section['offset'], section['offset'] + section['size'], 24):
        name, info, _, index, address, size = struct.unpack_from('<IBBHQQ', image, offset)
        rows.append(dict(name=strings[name:].split(b'\0')[0].decode(), info=info,
                         index=index, address=address, bytes=size))
    return rows


def windows(image):
    section = next(x for x in m.elf_layout(image)['sections'] if x['name'] == '.text')
    start, end = section['address'], section['address'] + section['size']
    rows = m.instructions(image, start, section['size'])
    by_address = {start + r['offset']: r for r in rows}
    relocations = dict(m.relocations(image))
    dyn = dynamic_symbols(image)
    starts = {start, struct.unpack_from('<Q', image, 24)[0]}
    starts.update(r['address'] for r in dyn if r['info'] & 15 == 2 and r['index']
                  and start <= r['address'] < end)
    for address, row in by_address.items():
        if ('call_target' in row and relocations.get(address, 0) & 0xffffffff != 10
                and start <= row['call_target'] < end):
            starts.add(row['call_target'])
    for address, info in relocations.items():
        if info & 0xffffffff != 8:
            continue
        if address in by_address:
            value = by_address[address].get('lddw_value', 0)
        else:
            try:
                value = int.from_bytes(m.at_address(image, address, 8), 'little') >> 32
            except StopIteration:
                continue
        if start <= value < end:
            starts.add(value)
    starts = sorted(starts)
    assert all(address in by_address for address in starts)
    symbols = {r['address']: r for r in m.functions(image)}
    result = []
    for address, stop in zip(starts, starts[1:] + [end]):
        body = m.instructions(image, address, stop - address)
        normalized, annotations = bytearray(), []
        for row in body:
            raw = bytearray.fromhex(row['raw'])
            absolute = address + row['offset']
            info = relocations.get(absolute, 0)
            if info & 0xffffffff == 10:
                assert row['opcode'] == 0x85
                raw[4:8] = bytes(4)
                annotations.append([row['offset'], 'import', dyn[info >> 32]['name']])
            elif 'call_target' in row:
                raw[4:8] = bytes(4)
            elif info & 0xffffffff == 8:
                assert row['opcode'] == 0x18
                raw[4:8] = raw[12:16] = bytes(4)
                annotations.append([row['offset'], 'opaque_relocated_pointer'])
            normalized.extend(raw)
        raw = m.at_address(image, address, stop - address)
        signature = hashlib.sha256(bytes(normalized) + json.dumps(annotations).encode()).hexdigest()
        result.append(dict(address=address, bytes=stop - address, instructions=len(body),
            raw_sha256=hashlib.sha256(raw).hexdigest(), signature=signature,
            name=symbols.get(address, {}).get('name'),
            symbol_bytes=symbols.get(address, {}).get('bytes'), cfg=m.cfg(body),
            annotations=annotations))
    return result


def compare(original, candidate):
    a, b = collections.defaultdict(list), collections.defaultdict(list)
    for r in original:
        a[r['signature']].append(r)
    for r in candidate:
        b[r['signature']].append(r)
    pairs, ambiguous = [], []
    for key in sorted(a.keys() & b.keys()):
        if len(a[key]) == len(b[key]) == 1:
            pairs.append(dict(original=a[key][0], candidate=b[key][0]))
        else:
            ambiguous.append(dict(original=a[key], candidate=b[key]))
    unmatched_original = [r for r in original if r['signature'] not in b]
    unmatched_candidate = [r for r in candidate if r['signature'] not in a]
    return dict(unique_pairs=pairs, ambiguous=ambiguous,
                unmatched_original=unmatched_original, unmatched_candidate=unmatched_candidate)


def dispatch_order(image, address, size, idl):
    names = {int.from_bytes(bytes(i['discriminator']), 'little'): i['name']
             for i in idl['instructions']}
    result = [dict(offset=r['offset'], name=names[r['lddw_value']],
                   discriminator=r['lddw_value'])
              for r in m.instructions(image, address, size) if r.get('lddw_value') in names]
    assert len(result) == 31 and len({r['name'] for r in result}) == 31
    return result


def nearest_same_extent(original_image, candidate_image, comparison):
    """Diagnostic candidates only; never used to accept a match or break a tie."""
    def normalized(image, window, rel, dyn):
        result = []
        for row in m.instructions(image, window['address'], window['bytes']):
            raw = bytearray.fromhex(row['raw'])
            info = rel.get(window['address'] + row['offset'], 0)
            annotation = None
            if info & 0xffffffff == 10:
                raw[4:8] = bytes(4)
                annotation = ['import', dyn[info >> 32]['name']]
            elif 'call_target' in row:
                raw[4:8] = bytes(4)
            elif info & 0xffffffff == 8:
                raw[4:8] = raw[12:16] = bytes(4)
                annotation = ['opaque_relocated_pointer']
            result.append((row, bytes(raw), annotation))
        return result
    original_relocations, candidate_relocations = dict(m.relocations(original_image)), dict(m.relocations(candidate_image))
    original_dynamic, candidate_dynamic = dynamic_symbols(original_image), dynamic_symbols(candidate_image)
    by_extent = collections.defaultdict(list)
    for window in comparison['unmatched_original']:
        by_extent[window['bytes']].append((window, normalized(
            original_image, window, original_relocations, original_dynamic)))
    result = []
    for window in comparison['unmatched_candidate']:
        rows = normalized(candidate_image, window, candidate_relocations, candidate_dynamic)
        alternatives = []
        for original_window, original_rows in by_extent[window['bytes']]:
            if [r[0]['offset'] for r in rows] != [r[0]['offset'] for r in original_rows]:
                continue
            differences = []
            for (a, left, left_annotation), (b, right, right_annotation) in zip(original_rows, rows):
                if left != right or left_annotation != right_annotation:
                    differences.append(dict(offset=a['offset'], original_raw=a['raw'], candidate_raw=b['raw'],
                        original_annotation=left_annotation, candidate_annotation=right_annotation,
                        immediate_only=(left[:4] == right[:4] and left[8:12] == right[8:12]
                                        and left_annotation == right_annotation)))
            alternatives.append(dict(original_address=original_window['address'], differences=differences))
        if alternatives:
            minimum = min(len(r['differences']) for r in alternatives)
            result.append(dict(candidate_address=window['address'], candidate_name=window['name'],
                bytes=window['bytes'], minimum_differing_instructions=minimum,
                alternatives=[r for r in alternatives if len(r['differences']) == minimum]))
    return result


def analyze():
    experiment = json.loads((HERE / 'experiment.json').read_text())
    original = (ROOT / 'evidence/original/pump_fees/deployed.so').read_bytes()
    assert m.digest(original) == '4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
    original_windows = windows(original)
    assert len(original_windows) == 585
    result = dict(original_sha256=m.digest(original), original_window_count=585, variants={})
    retained = {}
    for label, variant in experiment['variants'].items():
        images = {}
        for kind, descriptor in variant['files'].items():
            raw = gzip.decompress((HERE / descriptor['path']).read_bytes())
            assert len(raw) == descriptor['bytes'] and m.digest(raw) == descriptor['sha256']
            images[kind] = raw
        image = images['symbols']
        assert m.section_data(image, '.text') == m.section_data(images['candidate'], '.text')
        inferred = windows(image)
        assert {r['address']: r['bytes'] for r in inferred} == {
            r['address']: r['bytes'] for r in m.functions(image)}
        comparison = compare(original_windows, inferred)
        comparison.update(candidate_sha256=m.digest(images['candidate']), candidate_windows=len(inferred),
            inferred_boundaries_equal_symbol_table=True,
            unique_pair_bytes=sum(p['original']['bytes'] for p in comparison['unique_pairs']),
            unique_raw_pairs=sum(p['original']['raw_sha256'] == p['candidate']['raw_sha256']
                                 for p in comparison['unique_pairs']),
            equals_original_capture=images['candidate'] == original,
            equals_original_elf_extent=images['candidate'] == original[:m.elf_layout(original)['elf_extent']])
        retained[label] = image
        result['variants'][label] = comparison
    left, right = retained['control'], retained['coordinates']
    assert m.functions(left) == m.functions(right)
    changed = []
    for symbol in m.functions(left):
        before = m.instructions(left, symbol['address'], symbol['bytes'])
        after = m.instructions(right, symbol['address'], symbol['bytes'])
        assert [r['offset'] for r in before] == [r['offset'] for r in after]
        differences = []
        for a, b in zip(before, after):
            if a['raw'] != b['raw']:
                x, y = bytes.fromhex(a['raw']), bytes.fromhex(b['raw'])
                assert a['opcode'] == b['opcode'] == 0x62
                assert x[:4] == y[:4] and x[8:] == y[8:]
                differences.append(dict(offset=a['offset'], before=a['raw'], after=b['raw'],
                                        before_immediate=a['immediate'], after_immediate=b['immediate']))
        if differences:
            changed.append(dict(symbol=symbol, differences=differences))
    assert len(changed) == 16 and sum(len(r['differences']) for r in changed) == 21
    result['control_to_coordinates_code_differences'] = changed
    control = {p['original']['address'] for p in result['variants']['control']['unique_pairs']}
    proposal = {p['original']['address'] for p in result['variants']['coordinates']['unique_pairs']}
    result['delta'] = dict(added_original_windows=sorted(proposal - control),
                          lost_original_windows=sorted(control - proposal))
    assert len(proposal - control) == 8 and not control - proposal
    return result


if __name__ == '__main__':
    print(json.dumps(analyze(), indent=2))

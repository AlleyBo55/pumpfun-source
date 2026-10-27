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

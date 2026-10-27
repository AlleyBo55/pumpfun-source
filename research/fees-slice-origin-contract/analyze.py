"""Bind complete sharing wrapper/drop windows to their exact source changes."""
import gzip
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('sharing_ownership_windows', HERE / 'window_map.py')
wm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wm)


def source(e, label, name):
    override = e['variants'][label]['source_overrides'].get(name)
    return (HERE / override if override else ROOT / name).read_bytes().decode('utf-8')


def analyze():
    e = json.loads((HERE / 'experiment.json').read_text())
    original = (ROOT / 'evidence/original/pump_fees/deployed.so').read_bytes()
    assert wm.m.digest(original) == '4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
    original_windows = wm.windows(original)
    originals = {r['address']: r for r in original_windows}
    result = dict(original_sha256=wm.m.digest(original), variants={})
    retained, candidates = {}, {}
    for label, variant in e['variants'].items():
        images = {}
        for kind, descriptor in variant['files'].items():
            image = gzip.decompress((HERE / descriptor['path']).read_bytes())
            assert len(image) == descriptor['bytes'] and wm.m.digest(image) == descriptor['sha256']
            images[kind] = image
        candidate = images['symbols']
        assert wm.m.section_data(candidate, '.text') == wm.m.section_data(images['candidate'], '.text')
        windows = wm.windows(candidate)
        by_address = {r['address']: r for r in windows}
        symbols = wm.m.functions(candidate)
        assert set(by_address) == {r['address'] for r in symbols}
        assert all(by_address[r['address']]['bytes'] == r['bytes'] for r in symbols)
        comparison = wm.compare(original_windows, windows)
        comparison.update(candidate_windows=len(windows), candidate_sha256=wm.m.digest(images['candidate']),
            unique_raw_pairs=sum(r['original']['raw_sha256'] == r['candidate']['raw_sha256'] for r in comparison['unique_pairs']),
            equals_original_capture=images['candidate'] == original,
            equals_original_elf_extent=images['candidate'] == original[:wm.m.elf_layout(original)['elf_extent']])
        result['variants'][label] = comparison
        retained[label], candidates[label] = images, by_address
    before = {r['original']['address'] for r in result['variants']['control']['unique_pairs']}
    after = {r['original']['address'] for r in result['variants']['origins']['unique_pairs']}
    result['delta'] = dict(added_original_windows=sorted(after - before), lost_original_windows=sorted(before - after))
    assert after - before == {r[0] for r in e['targets']} and not before - after
    name = 'programs/pump-fees/src/state.rs'
    before_source = source(e, 'control', name)
    lines = before_source.splitlines(keepends=True)
    for number in (393, 446):
        i = number - 1
        assert lines[i].strip() == 'merged[offset..end].clone_from_slice(incoming);'
        assert all(line == '\n' for line in lines[i + 5:i + 12])
        block = lines[i:i + 5]
        block[0] = '    ' + block[0]
        lines[i:i + 12] = ['\n'] * 5 + block + ['\n'] * 2
    assert source(e, 'origins', name) == ''.join(lines)
    assert set(e['variants']['control']['input_sha256']) == set(e['variants']['origins']['input_sha256'])
    for item in e['variants']['control']['input_sha256']:
        if item != name:
            assert source(e, 'control', item) == source(e, 'origins', item)
    contracts = {'original': contract(original, original_windows, {r['address']: r['address'] for r in original_windows})}
    expected_delta = []
    for label in ('control', 'origins'):
        pairs = {r['original']['address']: r['candidate']['address'] for r in result['variants'][label]['unique_pairs']}
        image = retained[label]['symbols']
        contracts[label] = contract(image, list(candidates[label].values()), pairs,
            columns=(15, 29) if label == 'control' else (19, 33),
            lines=(393, 446) if label == 'control' else (398, 451))
        assert contracts[label]['pieces'] == contracts['original']['pieces']
        assert contracts[label]['panic_callee_signature'] == contracts['original']['panic_callee_signature']
        assert contracts[label]['formatter_signature'] == contracts['original']['formatter_signature']
        for actual, wanted in zip(contracts[label]['locations'], contracts['original']['locations']):
            assert actual['file'] == wanted['file']
            assert actual['line'] == wanted['line'] - (5 if label == 'control' else 0)
            assert actual['column'] == wanted['column'] - (4 if label == 'control' else 0)
            if label == 'origins':
                for relative, field, delta in [(16, 'line', 5), (20, 'column', 4)]:
                    offset = file_offset(retained[label]['candidate'], actual['record_address'] + relative)
                    import struct
                    old = struct.pack('<I', actual[field] - delta)
                    new = struct.pack('<I', actual[field])
                    expected_delta.extend([offset + i, x, y] for i, (x, y) in enumerate(zip(old, new)) if x != y)
    a, b = [retained[label]['candidate'] for label in ('control', 'origins')]
    assert len(a) == len(b)
    changes = [[i, x, y] for i, (x, y) in enumerate(zip(a, b)) if x != y]
    assert changes == sorted(expected_delta) and len(changes) == 8
    assert wm.m.section_data(a, '.text') == wm.m.section_data(b, '.text')
    for row in contracts['origins']['locations']:
        assert row['file'] == 'programs/pump-fees/src/state.rs'
    result['slice_contracts'] = contracts
    result['artifact_delta'] = dict(bytes=changes, entire_text_raw_equal=True,
        statement_tokens_unchanged=True, only_whitespace_changed=True,
        new_instruction_body_coverage=0)
    return result


def file_offset(image, address):
    rows = [s for s in wm.m.elf_layout(image)['sections']
            if s['address'] <= address < s['address'] + s['size'] and s['name'] in ('.rodata', '.data.rel.ro')]
    assert len(rows) == 1
    return rows[0]['offset'] + address - rows[0]['address']


def relocated_string(image, address):
    import struct
    packed, length = struct.unpack('<QQ', wm.m.at_address(image, address, 16))
    assert dict(wm.m.relocations(image))[address] & 0xffffffff == 8
    assert packed & 0xffffffff == 0
    return wm.m.at_address(image, packed >> 32, length).decode()


def contract(image, windows, pairs, columns=(19, 33), lines=(398, 451)):
    import struct
    by_address = {r['address']: r for r in windows}
    reference_image = (ROOT / 'evidence/original/pump_fees/deployed.so').read_bytes()
    assert wm.m.digest(reference_image) == '4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
    reference = {r['address']: r for r in wm.windows(reference_image)}
    rows = {r['offset']: r for r in wm.m.instructions(image, pairs[784168], 200)}
    assert by_address[pairs[784168]]['bytes'] == 200
    assert rows[152]['immediate'] == 3 and rows[160]['immediate'] == 2
    pieces = [relocated_string(image, rows[16]['lddw_value'] + n * 16) for n in range(3)]
    assert pieces == ['source slice length (', ') does not match destination slice length (', ')']
    panic = rows[192]['call_target']
    formatter = rows[88]['lddw_value']
    assert by_address[panic]['signature'] == by_address[pairs[771136]]['signature']
    assert rows[104]['source'] == rows[112]['source'] == 1
    locations, edges = [], []
    for original, line in zip((261816, 265976), lines):
        instructions = {r['offset']: r for r in wm.m.instructions(image, pairs[original], 4160)}
        assert by_address[pairs[original]]['bytes'] == 4160
        assert instructions[2096]['call_target'] == pairs[784168]
        range_target = instructions[1264]['call_target']
        assert by_address[range_target]['bytes'] == 8
        assert by_address[range_target]['raw_sha256'] == reference[783752]['raw_sha256']
        range_call = wm.m.instructions(image, range_target, 8)[0]
        assert range_call['call_target'] == range_target + 8
        assert by_address[range_call['call_target']]['signature'] == reference[783760]['signature']
        for offset in (1248, 2080):
            record = instructions[offset]['lddw_value']
            _, _, actual_line, column = struct.unpack('<QQII', wm.m.at_address(image, record, 24))
            file = relocated_string(image, record)
            assert file == 'programs/pump-fees/src/state.rs' and actual_line == line
            assert column == columns[0 if offset == 1248 else 1]
            locations.append(dict(original_caller=original, caller=pairs[original], pointer_offset=offset,
                record_address=record, file=file, line=actual_line, column=column))
        edges.append(dict(original_caller=original, caller=pairs[original], call_offset=2096,
            actual_target=pairs[784168], complete_helper_signature=by_address[pairs[784168]]['signature'],
            range_call_offset=1264, range_target=range_target, range_stub_raw_equal=True,
            range_stub_next_target=range_call['call_target'],
            range_stub_next_signature=by_address[range_call['call_target']]['signature']))
    return dict(helper=pairs[784168], pieces=pieces, piece_count=3, numeric_arguments=2,
        argument_order=['source_length', 'destination_length'],
        panic_callee=panic, panic_callee_signature=by_address[panic]['signature'],
        formatter=formatter, formatter_signature=by_address[formatter]['signature'],
        encoded_caller_edges=edges, locations=locations,
        identity='core::slice::copy_from_slice::len_mismatch_fail',
        all_transitive_data_identity_claimed=False)

"""Bind the authority-update body and exact diagnostic source origin to original and rebuilt bytes."""
import collections
import gzip
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('account_origin_windows', HERE / 'window_map.py')
wm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wm)


def source(e, label, name):
    override = e['variants'][label]['source_overrides'].get(name)
    return (HERE / override if override else ROOT / name).read_bytes().decode('utf-8')


def helper_line(text, name):
    rows = [row for row in text.splitlines() if 'pub fn ' + name + '(' in row]
    assert len(rows) == 1
    return rows[0]


def analyze():
    e = json.loads((HERE / 'experiment.json').read_text())
    TARGETS = e['targets']
    original = (ROOT / 'evidence/original/pump_fees/deployed.so').read_bytes()
    assert wm.m.digest(original) == '4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
    original_windows = wm.windows(original)
    original_by_address = {row['address']: row for row in original_windows}
    result = dict(original_sha256=wm.m.digest(original), original_windows=len(original_windows), variants={})
    retained = {}
    for label, variant in e['variants'].items():
        images = {}
        for kind, descriptor in variant['files'].items():
            raw = gzip.decompress((HERE / descriptor['path']).read_bytes())
            assert len(raw) == descriptor['bytes'] and wm.m.digest(raw) == descriptor['sha256']
            images[kind] = raw
        candidate = images['symbols']
        assert wm.m.section_data(candidate, '.text') == wm.m.section_data(images['candidate'], '.text')
        windows = wm.windows(candidate)
        by_address = {row['address']: row for row in windows}
        symbols = wm.m.functions(candidate)
        assert set(by_address) == {row['address'] for row in symbols}
        assert all(by_address[row['address']]['bytes'] == row['bytes'] for row in symbols)
        comparison = wm.compare(original_windows, windows)
        comparison.update(candidate_windows=len(windows), candidate_sha256=wm.m.digest(images['candidate']),
            inferred_boundaries_equal_all_symbol_extents=True,
            unique_raw_pairs=sum(row['original']['raw_sha256'] == row['candidate']['raw_sha256']
                                 for row in comparison['unique_pairs']),
            equals_original_capture=images['candidate'] == original,
            equals_original_elf_extent=images['candidate'] == original[:wm.m.elf_layout(original)['elf_extent']])
        result['variants'][label] = comparison
        retained[label] = images
    before = {row['original']['address'] for row in result['variants']['control']['unique_pairs']}
    after = {row['original']['address'] for row in result['variants']['origins']['unique_pairs']}
    result['delta'] = dict(added_original_windows=sorted(after - before), lost_original_windows=sorted(before - after))
    assert after - before == {row[0] for row in TARGETS} and not before - after
    address, size, offset, line, name, _, new_file = e['targets'][0]
    path = 'programs/pump-fees/src/instructions/' + new_file
    control = source(e, 'control', 'programs/pump-fees/src/lib.rs')
    start = control.index('    pub fn set_authority(')
    body = control.index('{', start)
    end = control.index('\n    }', body)
    contents = control[body + 1:end]
    included = source(e, 'origins', path)
    assert included == '\n' * 45 + '{\n' + contents.removeprefix('\n') + '\n}\n'
    assert included.splitlines()[line - 1].strip().startswith('require!(new_authority != Pubkey::default()')
    expected = control[:body + 1] + ' include!("instructions/admin/update_fee_program_global.rs") ' + '\n' * contents.count('\n') + control[end:]
    proposed = source(e, 'origins', 'programs/pump-fees/src/lib.rs')
    assert proposed == expected and len(proposed.splitlines()) == len(control.splitlines())
    negative_expected = control[:body + 1] + ' include!("instructions/admin/update_fee_program_global.rs") ' + control[end:]
    assert source(e, 'negative', 'programs/pump-fees/src/lib.rs') == negative_expected
    assert source(e, 'negative', path) == included
    negative = {row['original']['address'] for row in result['variants']['negative']['unique_pairs']}
    assert negative - before == {103408} and before - negative == {659640, 660160}
    assert len(result['variants']['negative']['unmatched_original']) == 86
    result['negative_delta'] = dict(added_original_windows=sorted(negative - before), lost_original_windows=sorted(before - negative))
    assert set(e['variants']['origins']['input_sha256']) - set(e['variants']['control']['input_sha256']) == {path}
    for item in e['variants']['control']['input_sha256']:
        if item != 'programs/pump-fees/src/lib.rs':
            assert source(e, 'control', item) == source(e, 'origins', item)
            assert source(e, 'control', item) == source(e, 'negative', item)
    pair = next(row for row in result['variants']['origins']['unique_pairs'] if row['original']['address'] == address)
    assert pair['original']['bytes'] == pair['candidate']['bytes'] == size == 3320
    assert 'set_authority' in pair['candidate']['name']
    values = []
    for image, start in [(original, address), (retained['origins']['symbols'], pair['candidate']['address'])]:
        rows = {r['offset']: r for r in wm.m.instructions(image, start, size)}
        assert rows[offset]['opcode'] == 0x62 and rows[offset]['immediate'] == line == 47
        assert rows[offset + 8]['opcode'] == 0x7a and rows[offset + 8]['immediate'] == len(path) == 70
        pointer = rows[offset - 40]['lddw_value']
        assert dict(wm.m.relocations(image))[start + offset - 40] & 0xffffffff == 8
        assert wm.m.at_address(image, pointer, len(path)) == path.encode()
        values.append(dict(address=start, pointer=pointer, line_instruction=rows[offset], length_instruction=rows[offset + 8]))
    result['origin_bindings'] = [dict(source=path, guard_line=line, bytes=size,
        original=values[0], candidate=values[1], body_tokens_preserved=True,
        all_other_public_source_preserved=True, lib_line_count_preserved=True)]
    return result

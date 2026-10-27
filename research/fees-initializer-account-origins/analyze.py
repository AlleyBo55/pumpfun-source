"""Bind five account-parser source locations to original and rebuilt bytes."""
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


def declaration(text, name):
    position = text.index('pub struct ' + name + "<'info>")
    start = text.rfind('#[derive(Accounts)]', 0, position)
    event = '#[event_cpi]\n'
    if text[max(0, start - len(event)):start] == event:
        start -= len(event)
    return text[start:text.index('\n}', position) + 2]


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
    paired = {row['original']['address']: row['candidate']
              for row in result['variants']['origins']['unique_pairs']}
    candidate = retained['origins']['symbols']
    records = []
    for address, size, offset, line, name, old_file, new_file in TARGETS:
        assert original_by_address[address]['bytes'] == size
        path = 'programs/pump-fees/src/instructions/' + new_file
        proposed = source(e, 'origins', path)
        previous = source(e, 'control', 'programs/pump-fees/src/' + old_file)
        assert declaration(previous, name) == declaration(proposed, name)
        assert proposed.splitlines()[line - 1] == '#[derive(Accounts)]'
        values = []
        for image, start in [(original, address), (candidate, paired[address]['address'])]:
            rows = {row['offset']: row for row in wm.m.instructions(image, start, size)}
            assert rows[offset]['opcode'] == 0x62 and rows[offset]['immediate'] == line
            assert rows[offset + 8]['opcode'] == 0x7a and rows[offset + 8]['immediate'] == len(path)
            pointer = rows[offset - 40]['lddw_value']
            assert dict(wm.m.relocations(image))[start + offset - 40] & 0xffffffff == 8
            assert wm.m.at_address(image, pointer, len(path)) == path.encode()
            values.append(dict(address=start, pointer=pointer, line_instruction=rows[offset],
                               length_instruction=rows[offset + 8]))
        records.append(dict(type=name, source=path, derive_line=line, bytes=size,
                            declaration_unchanged=True, original=values[0], candidate=values[1]))
    result['origin_bindings'] = records
    changed_sources = {}
    for _, _, _, _, name, old_file, new_file in TARGETS:
        old_path = 'programs/pump-fees/src/' + old_file
        previous = changed_sources.get(old_path, source(e, 'control', old_path))
        block = declaration(previous, name)
        replacement = 'pub use crate::instructions::' + new_file[:-3].replace('/', '::') + '::*;'
        replacement += '\n' * block.count('\n')
        changed_sources[old_path] = previous.replace(block, replacement, 1)
    for name, expected in changed_sources.items():
        assert source(e, 'origins', name) == expected
    for name in ('programs/pump-fees/src/lib.rs', 'programs/pump-fees/src/types.rs',
                 'programs/pump-fees/src/state.rs', 'programs/pump-fees/src/sharing_update.rs'):
        assert source(e, 'control', name) == source(e, 'origins', name)
    return result


if __name__ == '__main__':
    print(json.dumps(analyze(), indent=2))

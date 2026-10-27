"""Bind Shareholder Copy specialization and a negative control to original and rebuilt bytes."""
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
    types = 'programs/pump-fees/src/types.rs'
    control = source(e, 'control', types)
    for label, name in [('origins', 'Shareholder'), ('negative', 'FeeTier')]:
        previous = '#[derive(AnchorSerialize, AnchorDeserialize, Clone)]\npub struct ' + name
        assert control.count(previous) == 1
        assert source(e, label, types) == control.replace(previous, previous.replace('Clone)]', 'Clone, Copy)]'))
        assert set(e['variants'][label]['input_sha256']) == set(e['variants']['control']['input_sha256'])
        for name in e['variants']['control']['input_sha256']:
            if name != types:
                assert source(e, label, name) == source(e, 'control', name)
    negative = {row['original']['address'] for row in result['variants']['negative']['unique_pairs']}
    assert negative == before
    result['negative_delta'] = dict(added_original_windows=[], lost_original_windows=[])
    pair = next(row for row in result['variants']['origins']['unique_pairs'] if row['original']['address'] == 58520)
    assert pair['original']['bytes'] == pair['candidate']['bytes'] == 336
    assert 'Vec' in pair['candidate']['name'] and 'clone' in pair['candidate']['name']
    original_by_address = {row['address']: row for row in original_windows}
    candidate_by_address = {row['address']: row for row in wm.windows(retained['origins']['symbols'])}
    a = wm.m.instructions(original, 58520, 336)
    b = wm.m.instructions(retained['origins']['symbols'], pair['candidate']['address'], 336)
    edges = []
    for x, y in zip(a, b):
        assert x['offset'] == y['offset']
        if 'call_target' not in x:
            continue
        left, right = original_by_address[x['call_target']], candidate_by_address[y['call_target']]
        edges.append(dict(offset=x['offset'], original_target=x['call_target'], candidate_target=y['call_target'],
            candidate_name=right['name'], equal_complete_callee_signature=left['signature'] == right['signature'],
            equal_raw_callee_bytes=left['raw_sha256'] == right['raw_sha256']))
    assert [row['offset'] for row in edges] == [280, 328]
    assert all(row['equal_complete_callee_signature'] and row['equal_raw_callee_bytes'] for row in edges)
    result['clone_call_bindings'] = edges
    return result

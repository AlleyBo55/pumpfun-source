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
    name = 'programs/pump-fees/src/lib.rs'
    previous = source(e, 'control', name)
    needle = 'require!(current.len().max(offset + incoming.len()) <= 50, FeeError::TooManyFeeTiers);'
    replacement = needle + ' current.reserve((offset + incoming.len()).saturating_sub(current.len()));'
    assert previous.count(needle) == 1
    assert source(e, 'origins', name) == previous.replace(needle, replacement)
    assert set(e['variants']['control']['input_sha256']) == set(e['variants']['origins']['input_sha256'])
    for item in e['variants']['control']['input_sha256']:
        if item != name:
            assert source(e, 'control', item) == source(e, 'origins', item)
    pairs = {r['original']['address']: r['candidate'] for r in result['variants']['origins']['unique_pairs']}
    target = pairs[54864]
    assert target['bytes'] == originals[54864]['bytes'] == 368
    assert target['raw_sha256'] != originals[54864]['raw_sha256']
    image = retained['origins']['symbols']
    bindings = []
    for label, raw, address in [('original', original, 54864), ('origins', image, target['address'])]:
        rows = {r['offset']: r for r in wm.m.instructions(raw, address, 368)}
        assert rows[128]['lddw_value'] == 230584300921369396
        assert (rows[192]['opcode'], rows[192]['destination'], rows[192]['immediate']) == (0x27, 3, 40)
        assert (rows[216]['opcode'], rows[216]['destination'], rows[216]['immediate']) == (0x27, 1, 40)
        callees = {}
        for offset, expected in [(288, 53968), (328, 765304)]:
            actual = rows[offset]['call_target']
            assert actual == (expected if label == 'original' else pairs[expected]['address'])
            callees[str(offset)] = dict(original=expected, actual=actual,
                normalized_signature=originals[expected]['signature'],
                raw_equal=originals[expected]['raw_sha256'] == pairs[expected]['raw_sha256'])
        bindings.append(dict(label=label, address=address, bytes=368, element_bytes=40, callees=callees))
    callers = []
    for address in (261816, 265976):
        body = originals[address]
        instructions = {r['offset']: r for r in wm.m.instructions(original, address, body['bytes'])}
        assert instructions[3736]['call_target'] == 54864
        callers.append(dict(original_caller=address, bytes=body['bytes'], call_offset=3736))
    actual_callers = []
    for body in candidates['origins'].values():
        offsets = [r['offset'] for r in wm.m.instructions(image, body['address'], body['bytes'])
            if r.get('call_target') == target['address']]
        if offsets:
            assert '12upsert_tiers17h' in body['name']
            actual_callers.append(dict(address=body['address'], bytes=body['bytes'], offsets=offsets, name=body['name']))
    assert len(actual_callers) == 1 and actual_callers[0]['offsets'] == [984]
    result['reserve_bindings'] = dict(helper=bindings, original_callers=callers, candidate_callers=actual_callers,
        only_reachable_reserve_statement_added=True, full_original_upsert_callers_recovered=False)
    return result

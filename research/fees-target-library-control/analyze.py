"""Re-derive the rejected library trial and its precise byte-level limits."""
import gzip
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('library_control_windows', HERE / 'window_map.py')
wm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wm)


def analyze():
    e = json.loads((HERE / 'experiment.json').read_text())
    original = (ROOT / 'evidence/original/pump_fees/deployed.so').read_bytes()
    assert wm.m.digest(original) == '4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
    original_windows = wm.windows(original)
    originals = {r['address']: r for r in original_windows}
    result = dict(original_sha256=wm.m.digest(original), variants={}, type_id_evidence={}, bounds_check={})
    result['bounds_check']['original'] = next(r for r in wm.m.instructions(original, 784168, 200) if r['offset'] == 152)
    for label, variant in e['variants'].items():
        images = {}
        for kind, record in variant['files'].items():
            image = gzip.decompress((HERE / record['path']).read_bytes())
            assert len(image) == record['bytes'] and wm.m.digest(image) == record['sha256']
            images[kind] = image
        image = images['symbols']
        assert wm.m.section_data(image, '.text') == wm.m.section_data(images['candidate'], '.text')
        windows = wm.windows(image)
        by_address = {r['address']: r for r in windows}
        symbols = wm.m.functions(image)
        assert set(by_address) == {r['address'] for r in symbols}
        assert all(by_address[r['address']]['bytes'] == r['bytes'] for r in symbols)
        comparison = wm.compare(original_windows, windows)
        comparison.update(candidate_windows=len(windows), candidate_sha256=wm.m.digest(images['candidate']),
            unique_raw_pairs=sum(r['original']['raw_sha256'] == r['candidate']['raw_sha256'] for r in comparison['unique_pairs']),
            equals_original_capture=images['candidate'] == original,
            equals_original_elf_extent=images['candidate'] == original[:wm.m.elf_layout(original)['elf_extent']])
        result['variants'][label] = comparison
        evidence = []
        for address in e['type_id_windows']:
            row = originals[address]
            assert row['bytes'] == 56
            evidence.append(dict(original_address=address, original_raw_sha256=row['raw_sha256'],
                raw_equal_candidates=[r['address'] for r in windows if r['raw_sha256'] == row['raw_sha256']],
                structural_candidates=[r['address'] for r in windows if r['signature'] == row['signature']]))
        result['type_id_evidence'][label] = evidence
        bound = next(r for r in symbols if 'panic_bounds_check' in r['name'])
        assert bound['bytes'] == 200
        result['bounds_check'][label] = next(r for r in wm.m.instructions(image, bound['address'], 200) if r['offset'] == 152)
    before = {r['original']['address'] for r in result['variants']['control']['unique_pairs']}
    after = {r['original']['address'] for r in result['variants']['origins']['unique_pairs']}
    result['delta'] = dict(added_original_windows=sorted(after - before), lost_original_windows=sorted(before - after))
    assert result['delta'] == dict(added_original_windows=[], lost_original_windows=[767336])
    old = {r['address'] for r in result['variants']['control']['unmatched_original']}
    new = {r['address'] for r in result['variants']['origins']['unmatched_original']}
    assert new - old == set(e['type_id_windows']) and not old - new
    assert all(row['raw_equal_candidates'] for row in result['type_id_evidence']['control'])
    assert all(not row['structural_candidates'] and not row['raw_equal_candidates'] for row in result['type_id_evidence']['origins'])
    assert result['bounds_check']['original']['immediate'] == 3
    assert result['bounds_check']['control']['immediate'] == result['bounds_check']['origins']['immediate'] == 2
    return result

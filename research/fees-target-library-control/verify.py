"""Verify retained bytes, controlled inputs, bounded execution and raw audit."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def main():
    manifest = json.loads((HERE / 'manifest.json').read_text())
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name != 'manifest.json' and '__pycache__' not in p.parts}
    assert actual == set(manifest)
    for name, expected in manifest.items():
        path = HERE / name
        assert path.resolve().is_relative_to(HERE) and not path.is_symlink() and sha(path.read_bytes()) == expected
    e = json.loads((HERE / 'experiment.json').read_text())
    assert len(e['harness_sha256']) == 187
    for name, expected in e['harness_sha256'].items():
        assert sha((ROOT / name).read_bytes()) == expected
    inputs = e['variants']['control']['input_sha256']
    assert inputs == e['variants']['origins']['input_sha256'] and len(inputs) == 33
    for label, variant in e['variants'].items():
        for name, expected in inputs.items():
            override = variant['source_overrides'].get(name)
            path = HERE / override if override else ROOT / name
            assert sha(path.read_bytes()) == expected
        launch = json.loads((HERE / f'builds/{label}-launch.json').read_text())
        build = json.loads((HERE / f'builds/{label}-result.json').read_text())
        assert launch['input_sha256'] == build['input_sha256'] == inputs
        assert build['exit_code'] == build['strip_exit_code'] == 0 and build['source_unchanged']
        assert launch['rustc_sha256'] == e['tool_sha256']['rustc-v144']
        assert e['strip_replay'][label]['exit_code'] == 0
        assert e['strip_replay'][label]['sha256'] == variant['files']['candidate']['sha256']
        flags = json.loads(gzip.decompress((HERE / f'receipts/{label}-exhaustive.json.gz').read_bytes()))
        assert flags['candidate_sha256'] == variant['files']['candidate']['sha256']
        assert flags['original_sha256'] == '4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
        assert flags['case_count'] == len(flags['cases']) == 1542
        assert not flags['failures'] and not flags['compute_differences']
        assert all(r['original'] == r['candidate'] for r in flags['cases'])
        assert {(r['cap'], r['pool'], r['flag_hex']) for r in flags['cases']} == {
            (cap, pool, flag) for cap in (0, 1000, 2**128 - 1) for pool in (0, 1)
            for flag in [''] + [bytes([b]).hex() for b in range(256)]}
    archive = e['archive']
    assert archive['asset_id'] == 234589699 and archive['bytes'] == 410949923
    assert archive['sha256'] == '37eaae7397161361a8daa9635851cb26ff752875de66bc3fa22f316db9c23cb5'
    assert len(archive['members']) == 25
    assert archive == json.loads((HERE / 'archive-check.json').read_text())
    trial_launch = json.loads((HERE / 'builds/origins-launch.json').read_text())
    assert trial_launch['sysroot_manifest_sha256'] == sha((HERE / 'archive-check.json').read_bytes())
    control_receipt = json.loads(gzip.decompress((HERE / 'receipts/control-full.json.gz').read_bytes()))
    assert control_receipt['candidate_sha256'] == e['variants']['control']['files']['candidate']['sha256']
    assert control_receipt['case_count'] == 17331 and len(control_receipt['suites']) == 18 and not control_receipt['mismatches']
    spec = importlib.util.spec_from_file_location('target_library_analysis', HERE / 'analyze.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.analyze()
    assert result == json.loads(gzip.decompress((HERE / 'analysis.json.gz').read_bytes()))
    for label, unique, unmatched, raw in [('control', 353, 85, 57), ('origins', 352, 89, 55)]:
        row = result['variants'][label]
        assert len(row['unique_pairs']) == unique and len(row['unmatched_original']) == unmatched
        assert row['unique_raw_pairs'] == raw and row['candidate_windows'] == 580
        assert not row['equals_original_capture'] and not row['equals_original_elf_extent']
    sys.path.insert(0, str(ROOT / 'scripts'))
    import compare
    saved = json.loads((HERE / 'core-raw-identity.json').read_text())
    assert saved['head'] == e['selected_at_revision'] and saved['padding_requested'] is False
    assert set(e['raw_bindings']) == {'pump', 'pump_amm', 'pump_fees', 'mayhem'}
    for name, binding in e['raw_bindings'].items():
        original = (ROOT / binding['original']).read_bytes()
        candidate = (ROOT / binding['candidate']).read_bytes()
        assert sha(candidate) == binding['candidate_sha256']
        assert compare.compare(original, candidate) == saved['selected'][name]
        assert not saved['selected'][name]['full_byte_equality']
    original = (ROOT / 'evidence/original/pump_fees/deployed.so').read_bytes()
    record = e['variants']['control']['files']['candidate']
    assert compare.compare(original, gzip.decompress((HERE / record['path']).read_bytes())) == saved['research_fees_pr123']
    print('PASS: rejected Darwin target-library trial; four lost Type-ID windows; unchanged bounds-check mismatch; 3,084 exact focused comparisons; raw identity 0/4')


if __name__ == '__main__':
    main()

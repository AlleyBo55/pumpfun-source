#!/usr/bin/env python3
"""Verify ordinary source integrity; optionally compare LOCAL compiler outputs.

Default verification/materialization reads no program ELF and runs no compiler,
VM or network operation. Runtime receipts are neither included nor consumed.
"""
import argparse
import difflib
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / '.git').exists())
PARENT = 'repro/donation-relay/security-metadata-source-recovery'
PARSER = 'repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py'
WINDOWS = 'repro/donation-relay/swap-receipt-coordinate-recovery/original-windows.json'
ORIGINAL = 'evidence/dependencies/donation_relay/deployed.so'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def safe_name(name):
    path = PurePosixPath(name)
    assert name and not path.is_absolute() and '..' not in path.parts
    assert str(path) == name
    return path


def safe_file(root, name):
    safe_name(name)
    path = root
    for part in PurePosixPath(name).parts:
        path = path / part
        assert not path.is_symlink()
    assert path.resolve().is_relative_to(root.resolve())
    return path


def check_manifest():
    expected = read(HERE / 'manifest.json')
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob('*')
              if p.is_file() and p.name != 'manifest.json' and '__pycache__' not in p.parts}
    assert actual == set(expected)
    for name, digest in expected.items():
        assert sha(safe_file(HERE, name).read_bytes()) == digest, name


def check_parents():
    # Only source-loader and public parser/inventory files: no program artifacts.
    for group in read(HERE / 'parent-inputs.json').values():
        for name, digest in group.items():
            assert sha(safe_file(ROOT, name).read_bytes()) == digest, name


def validate_sources(baseline, recovered):
    expected = read(HERE / 'source-inputs.json')
    assert len(baseline) == len(recovered) == 56
    assert set(baseline) == set(recovered)
    for label, source in [('baseline', baseline), ('recovered', recovered)]:
        for name in source:
            safe_name(name)
        assert {name: sha(data) for name, data in source.items()} == expected[label]
    changed = [name for name in baseline if baseline[name] != recovered[name]]
    assert changed == ['src/shared_donation.rs']
    before = baseline[changed[0]].decode().splitlines(keepends=True)
    after = recovered[changed[0]].decode().splitlines(keepends=True)
    patch = ''.join(difflib.unified_diff(before, after,
                    fromfile='a/src/shared_donation.rs', tofile='b/src/shared_donation.rs'))
    assert patch.encode() == (HERE / 'source.patch').read_bytes()
    return changed


def sources():
    check_parents()
    parent = module('worker_public_source_parent', ROOT / PARENT / 'verify.py')
    baseline, _ = parent.sources()  # Public source map, not its ELF/runtime verifier.
    recovered = dict(baseline)
    recovered['src/shared_donation.rs'] = (HERE / 'source/shared_donation.rs').read_bytes()
    validate_sources(baseline, recovered)
    return baseline, recovered


def materialize(destination, source):
    assert not destination.exists() and not destination.is_symlink()
    destination.mkdir(parents=True)
    for name, data in source.items():
        target = safe_file(destination, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    assert {str(p.relative_to(destination)): sha(p.read_bytes())
            for p in destination.rglob('*') if p.is_file()} == {
                name: sha(data) for name, data in source.items()}


def check_analysis(baseline, recovered):
    expected = read(HERE / 'expected.json')
    summary = recovered['comparison-summary.json']
    assert summary['original_sha256'] == expected['original_sha256']
    assert summary['candidate_sha256'] == expected['candidate_sha256']
    assert summary['unstripped_sha256'] == expected['symbols_sha256']
    assert summary['original_inferred_windows'] == expected['original_windows'] == 492
    assert summary['original_normalized_match_windows'] == expected['normalized_windows'] == 483
    assert summary['original_raw_match_windows'] == expected['raw_windows'] == 130
    assert not summary['whole_file_equal']
    before = {r['ordinal'] for r in baseline['match-ledger.json'] if r['normalized_candidate_indices']}
    after = {r['ordinal'] for r in recovered['match-ledger.json'] if r['normalized_candidate_indices']}
    assert len(before) == 482 and after - before == {112} and not before - after
    original = recovered['original-function-ledger.json'][112]
    selected = [f for f in recovered['candidate-function-ledger.json']
                if any('13donate_shared' in name for name in f['names'])]
    assert len(selected) == 1
    candidate = selected[0]
    assert original['bytes'] == candidate['bytes'] == expected['worker_bytes'] == 10248
    assert original['normalized_sha256'] == candidate['normalized_sha256'] == expected['worker_normalized_sha256']
    witness = next(w for w in recovered['match-witnesses.json']
                   if w['original_ordinal'] == 112 and w['candidate_index'] == candidate['index'])
    assert not witness['raw_body']
    assert len(witness['direct_calls']) == 51
    assert all(call['normalized_body_pair'] for call in witness['direct_calls'])
    return {'normalized_windows': 483, 'raw_windows': 130, 'gained': [112],
            'lost': [], 'worker_bytes': 10248, 'whole_file_equal': False,
            'common_position_different_bytes': summary['common_position_different_bytes'],
            'original_only_tail': summary['original_only_tail'],
            'scope': 'Complete local instruction windows; not semantic/data closure or runtime verification.'}


def compare(candidate_path, symbols_path):
    check_parents()
    expected = read(HERE / 'expected.json')
    original = (ROOT / ORIGINAL).read_bytes()
    candidate, symbols = candidate_path.read_bytes(), symbols_path.read_bytes()
    assert sha(original) == expected['original_sha256']
    assert sha(candidate) == expected['candidate_sha256']
    assert sha(symbols) == expected['symbols_sha256']
    analyzer = module('worker_pinned_public_elf_parser', ROOT / PARSER)
    metadata = read(ROOT / PARENT / 'metadata.json')
    baseline = {}
    for kind, descriptor in metadata['baseline_artifacts'].items():
        raw = gzip.decompress(safe_file(ROOT, descriptor['path']).read_bytes())
        assert len(raw) == descriptor['bytes'] and sha(raw) == descriptor['sha256']
        baseline[kind] = raw
    results = {}
    with tempfile.TemporaryDirectory(prefix='worker-local-comparison-') as temp:
        directory = Path(temp)
        (directory / 'original.so').write_bytes(original)
        (directory / 'original-windows.json').write_bytes((ROOT / WINDOWS).read_bytes())
        for label, c, s in [('baseline', baseline['candidate'], baseline['symbols']),
                            ('recovered', candidate, symbols)]:
            (directory / 'candidate.so').write_bytes(c)
            (directory / 'unstripped.so').write_bytes(s)
            results[label] = analyzer.analyze(directory)
    return check_analysis(results['baseline'], results['recovered'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--materialize', type=Path)
    parser.add_argument('--candidate', type=Path, help='Optional local stripped compiler output')
    parser.add_argument('--symbols', type=Path, help='Optional local unstripped compiler output')
    args = parser.parse_args()
    assert (args.candidate is None) == (args.symbols is None), 'Supply both local ELF paths'
    check_manifest()
    _, recovered = sources()
    if args.materialize:
        materialize(args.materialize, recovered)
    result = {'source_verified': True, 'source_file_count': 56,
              'changed_files': ['src/shared_donation.rs'],
              'compiler_executed': False, 'runtime_verified': False,
              'elf_comparison': 'not requested'}
    if args.candidate:
        result['elf_comparison'] = compare(args.candidate, args.symbols)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()

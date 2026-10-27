#!/usr/bin/env python3
"""Recheck bounded negative source trials and the four-slot Jupiter residual."""
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import json
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def manifest(path):
    records = read(path / 'manifest.json')
    actual = {str(p.relative_to(path)) for p in path.rglob('*')
              if p.is_file() and p.name != 'manifest.json' and '__pycache__' not in p.parts}
    assert actual == set(records), (path, actual ^ set(records))
    for name, digest in records.items():
        p = path / name
        assert not p.is_symlink() and p.resolve().is_relative_to(path) and sha(p.read_bytes()) == digest, name


def sources():
    for name, digest in read(HERE / 'parents.json').items():
        assert sha((ROOT / name).read_bytes()) == digest, name
    parent_path = ROOT / 'repro/donation-relay/source-location-recovery'
    manifest(parent_path)
    parent = module('cpi_trial_parent', parent_path / 'verify.py')
    parser, _, proposals = parent.load()
    base, _ = parent.source(proposals, 'combined')
    assert len(base) == 56
    return parser, base


def normalized(elf, function):
    result = bytearray(elf.at(function['start'], function['bytes']))
    for call in function['direct_calls']:
        result[call['offset'] + 4:call['offset'] + 8] = bytes(4)
    for ref in function['data_references']:
        result[ref['offset'] + 4:ref['offset'] + 8] = bytes(4)
        result[ref['offset'] + 12:ref['offset'] + 16] = bytes(4)
    assert sha(result) == function['normalized_sha256']
    return result


def trial_source(label, record):
    path = HERE / record.get('source_path', f'trials/{label}/settlement_handlers.rs')
    raw = path.read_bytes()
    return gzip.decompress(raw) if path.suffix == '.gz' else raw


def derive():
    parser, base = sources()
    metadata = read(HERE / 'metadata.json')
    assert len(metadata['variants']) == 53
    assert [len(metadata['groups'][g]) for g in ('burn-field-order', 'burn-ownership', 'jupiter-vector', 'jupiter-layout', 'jupiter-borrowed-arguments')] == [16, 16, 4, 14, 3]
    original = (ROOT / 'evidence/dependencies/donation_relay/deployed.so').read_bytes()
    original_elf = parser.Elf(original)
    windows_path = ROOT / 'repro/donation-relay/swap-receipt-coordinate-recovery/original-windows.json'
    windows = read(windows_path)
    assert sha(original) == '367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563'
    report, cache = {}, {}
    best_analysis = None
    for label, record in metadata['variants'].items():
        directory = HERE / 'trials' / label
        launch, build = read(directory / 'launch.json'), read(directory / 'result.json')
        source = dict(base)
        source['src/settlement_handlers.rs'] = trial_source(label, record)
        assert launch['inputs'] == {n: sha(b) for n, b in source.items()}
        assert build['source_unchanged'] and build['exit_code'] == 0
        log = (directory / 'build.log').read_bytes()
        assert sha(log) == build['log_sha256']
        assert b'Compiling donation-relay-source-proposal' in log
        assert b'--crate-name donation_relay_source_proposal' in log and b'--sysroot' in log
        images = {}
        for kind, artifact in record['artifacts'].items():
            raw = gzip.decompress((HERE / artifact['path']).read_bytes())
            assert sha(raw) == artifact['sha256'] and len(raw) == artifact['bytes']
            assert sha(raw) == build[kind + '_sha256']
            images[kind] = raw
        assert len(images['candidate']) == build['candidate_bytes']
        key = (sha(images['candidate']), sha(images['symbols']))
        if key not in cache:
            with tempfile.TemporaryDirectory() as temporary:
                d = Path(temporary)
                for name, raw in [('original.so', original), ('candidate.so', images['candidate']),
                                  ('unstripped.so', images['symbols']), ('original-windows.json', windows_path.read_bytes())]:
                    (d / name).write_bytes(raw)
                cache[key] = parser.analyze(d)
        analysis = cache[key]
        ordinal = record['target_ordinal']
        assert ordinal in (90, 109)
        term = '14invoke_jupiter17h' if ordinal == 90 else '14burn_and_close17h'
        candidates = [f for f in analysis['candidate-function-ledger.json'] if any(term in name for name in f['names'])]
        assert len(candidates) == 1
        candidate = candidates[0]
        target = analysis['original-function-ledger.json'][ordinal]
        assert target['bytes'] == (2496 if ordinal == 90 else 2856)
        assert candidate['bytes'] == record['observed']['bytes']
        assert candidate['normalized_sha256'] == record['observed']['normalized_sha256']
        assert not record['observed']['matched']
        assert not analysis['match-ledger.json'][ordinal]['normalized_candidate_indices']
        summary = analysis['comparison-summary.json']
        assert not summary['whole_file_equal']
        report[label] = dict(target_ordinal=ordinal, target_bytes=target['bytes'],
                             candidate_function_bytes=candidate['bytes'],
                             candidate_function_normalized_sha256=candidate['normalized_sha256'],
                             candidate_sha256=summary['candidate_sha256'],
                             normalized_windows=summary['original_normalized_match_windows'],
                             raw_windows=summary['original_raw_match_windows'],
                             target_matched=False)
        if label == metadata['preferred_partial_trial']:
            assert summary['original_normalized_match_windows'] == 480 and summary['original_raw_match_windows'] == 130
            control = read(ROOT / 'repro/donation-relay/source-location-recovery/builds/combined/match-ledger.json')
            assert [bool(r['normalized_candidate_indices']) for r in control] == [bool(r['normalized_candidate_indices']) for r in analysis['match-ledger.json']]
            u = normalized(original_elf, target)
            v = normalized(parser.Elf(images['symbols']), candidate)
            assert len(u) == len(v) == 2496
            differences = [dict(offset=i, original=u[i:i+8].hex(), candidate=v[i:i+8].hex())
                           for i in range(0, len(u), 8) if u[i:i+8] != v[i:i+8]]
            assert [d['offset'] for d in differences] == [80, 96, 1680, 1688]
            best_analysis = dict(summary=summary, differing_normalized_instruction_slots=differences,
                                 equal_normalized_instruction_slots=308,
                                 interpretation='Four stack-memory instruction slots remain unequal. This is not a complete normalized window match.')
    assert best_analysis
    confirmation = read(HERE / 'confirmation/result.json')
    launch = read(HERE / 'confirmation/launch.json')
    best_launch = read(HERE / 'trials/jupiter-iter-cloned/launch.json')
    assert launch['inputs'] == best_launch['inputs']
    assert confirmation['source_unchanged'] and confirmation['exit_code'] == 0
    assert confirmation['candidate_sha256'] == best_analysis['summary']['candidate_sha256']
    assert confirmation['symbols_sha256'] == best_analysis['summary']['unstripped_sha256']
    log = (HERE / 'confirmation/build.log').read_bytes()
    assert sha(log) == confirmation['log_sha256']
    assert b'Compiling donation-relay-source-proposal' in log and b'--crate-name donation_relay_source_proposal' in log
    controller = (HERE / 'controllers/build_jupiter_confirmation.py').read_text()
    assert 'original.so' not in controller and 'deployed.so' not in controller
    runtime = read(HERE / 'fresh-runtime.json.gz')
    assert runtime['candidate_sha256'] == best_analysis['summary']['candidate_sha256']
    assert runtime['runner_sha256'] == sha((HERE / 'replay_saved.py').read_bytes())
    frozen = {}
    for name, digest in runtime['input_reports'].items():
        file = ROOT / name
        assert sha(file.read_bytes()) == digest
        for i, row in enumerate(read(file)['cases']):
            frozen[str(file.relative_to(ROOT / 'repro/donation-relay/distribution-worker-source-recovery/settlement')) + ':' + str(i)] = row
    helper = module('cpi_trial_runtime_checker', ROOT / 'repro/donation-relay/swap-receipt-coordinate-recovery/verify.py')
    helper.EXPECTED['recovered'] = runtime['candidate_sha256']
    harness = module('cpi_trial_runtime', ROOT / 'repro/donation-relay/local-validation-proposal/harness_proposal.py')
    assert runtime['harness_sha256'] == sha(Path(harness.__file__).read_bytes())
    assert runtime['token2022_sha256'] == sha((ROOT / 'evidence/dependencies/spl_token_2022/deployed.so').read_bytes())
    runtime_summary = helper.check_runtime(runtime, frozen, harness)
    return dict(variants=report, preferred_partial_trial=best_analysis, confirmation=confirmation, runtime=runtime_summary,
                scope='Source-build experiments, not selected artifacts. No recovered window is claimed; runtime evidence applies only to the named Jupiter trial and existing bounded fixtures.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--materialize', type=Path)
    ap.add_argument('--variant', default='jupiter-iter-cloned')
    args = ap.parse_args()
    if not args.write:
        manifest(HERE)
    if args.materialize:
        assert not args.materialize.exists()
        _, source = sources()
        variants = read(HERE / 'metadata.json')['variants']
        assert args.variant in variants
        source['src/settlement_handlers.rs'] = trial_source(args.variant, variants[args.variant])
        for name, raw in source.items():
            p = args.materialize / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
        print('Materialized', len(source), 'source inputs for', args.variant)
        return
    report = derive()
    if args.write:
        (HERE / 'report.json').write_bytes(encoded(report))
        records = {str(p.relative_to(HERE)): sha(p.read_bytes()) for p in sorted(HERE.rglob('*'))
                   if p.is_file() and p.name != 'manifest.json' and '__pycache__' not in p.parts}
        (HERE / 'manifest.json').write_bytes(encoded(records))
    else:
        assert read(HERE / 'report.json') == report
    print('PASS: 53 compiled source trials; no target window recovered; Jupiter retains 480 windows with exactly four differing instruction slots and 536 bounded replay records')


if __name__ == '__main__':
    main()

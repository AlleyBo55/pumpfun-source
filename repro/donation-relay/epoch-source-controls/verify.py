#!/usr/bin/env python3
"""Verify the epoch-close field-cache and error-result source controls."""
from pathlib import Path
import argparse
import collections
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


def manifest(path):
    values = read(path / 'manifest.json')
    actual = {str(p.relative_to(path)) for p in path.rglob('*') if p.is_file()
              and p.name != 'manifest.json' and '__pycache__' not in p.parts}
    assert actual == set(values)
    for name, digest in values.items():
        file = path / name
        assert not file.is_symlink() and file.resolve().is_relative_to(path) and sha(file.read_bytes()) == digest, name


def parent():
    for name, digest in read(HERE / 'parents.json').items():
        assert sha((ROOT / name).read_bytes()) == digest, name
    p = ROOT / 'repro/donation-relay/burn-mint-ownership-recovery'
    manifest(p)
    spec = importlib.util.spec_from_file_location('donation_control_parent', p / 'verify.py')
    prior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    parser, base = prior.parent()
    base['src/settlement_handlers.rs'] = prior.recovered_source(base)
    assert len(base) == 56
    return parser, base


def compiler_control(parser, base, original, windows, matched_before):
    record = read(HERE / 'metadata.json')['compiler_control']
    folder = HERE / record['directory']
    launch, build = read(folder / 'launch.json'), read(folder / 'result.json')
    tools = read(folder / 'tools.json')
    assert launch['inputs'] == {name: sha(raw) for name, raw in base.items()}
    assert build['exit_code'] == 0 and build['source_unchanged']
    assert tools[launch['compiler']]['sha256'] == launch['compiler_sha256']
    assert launch['compiler_sha256'] == '54569cce5e0a4234638c30c3130ea6fff69e8d664f539e05de909ab36ed66fe2'
    assert '/v1.48/' in launch['command'][0]
    assert tools[launch['command'][0]]['sha256'] == launch['cargo_sha256']
    assert launch['target_rustflags'].endswith('/v1.48/platform-tools/llvm/bin/ld.lld')
    assert 'relay-linux-v148/sdk/rust' in launch['target_rustflags']
    linker = launch['target_rustflags'].rsplit('=', 1)[1]
    assert tools[linker]['sha256'] == launch['linker_sha256']
    drivers = {value['sha256'] for name, value in tools.items() if 'librustc_driver-' in name}
    assert drivers == {'8347d1e316dae00dc1209e504df0b5925b007b3a3b8ac35fc2dd351780d9dc4a',
                       '6653fa3aa863af73b25b4dcce914c2b15d224a5f2f4add412b8b584d93dfda18'}
    assert (folder / 'rustc-version.txt').read_text().startswith('rustc 1.84.1-dev\n')
    log = (folder / 'build.log').read_bytes()
    assert sha(log) == build['build_log_sha256']
    assert b'Compiling donation-relay-source-proposal' in log
    assert (launch['compiler'] + ' --crate-name donation_relay_source_proposal').encode() in log
    images = {}
    for kind, descriptor in record['artifacts'].items():
        raw = gzip.decompress((HERE / descriptor['path']).read_bytes())
        assert sha(raw) == descriptor['sha256'] == build[kind + '_sha256']
        assert len(raw) == descriptor['bytes']
        images[kind] = raw
    with tempfile.TemporaryDirectory() as temp:
        folder2 = Path(temp)
        for name, raw in [('original.so', original), ('candidate.so', images['candidate']),
                          ('unstripped.so', images['symbols']), ('original-windows.json', windows.read_bytes())]:
            (folder2 / name).write_bytes(raw)
        analysis = parser.analyze(folder2)
    matched_after = {row['ordinal'] for row in analysis['match-ledger.json'] if row['normalized_candidate_indices']}
    result = dict(gained=sorted(matched_after - matched_before),
                  lost=sorted(matched_before - matched_after),
                  summary=analysis['comparison-summary.json'])
    assert result == read(folder / 'frontier-change.json')
    assert result['gained'] == [] and len(result['lost']) == 256
    assert result['summary']['original_normalized_match_windows'] == 226
    assert result['summary']['original_raw_match_windows'] == 108
    assert not result['summary']['whole_file_equal']
    return result


def derive():
    parser, base = parent()
    metadata = read(HERE / 'metadata.json')
    assert len(metadata['variants']) == 14
    groups = collections.Counter(r['group'] for r in metadata['variants'].values())
    assert groups == {'field-cache': 6, 'error-type': 3, 'result-shape': 5}
    original = (ROOT / 'evidence/dependencies/donation_relay/deployed.so').read_bytes()
    assert sha(original) == '367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563'
    windows = ROOT / 'repro/donation-relay/swap-receipt-coordinate-recovery/original-windows.json'
    baseline = read(ROOT / 'repro/donation-relay/burn-mint-ownership-recovery/builds/recovered/match-ledger.json')
    matched_before = {r['ordinal'] for r in baseline if r['normalized_candidate_indices']}
    native_compiler = read(ROOT / 'repro/donation-relay/burn-mint-ownership-recovery/builds/recovered/launch.json')['rustc_sha256']
    symbols = {96: 'settlement_handlers11close_epoch'}
    cache, result = {}, {}
    comparisons = 0
    for label, record in metadata['variants'].items():
        d = HERE / 'builds' / label
        source = dict(base)
        assert set(record['source_overrides']) == {'src/settlement_handlers.rs'}
        for name, path in record['source_overrides'].items():
            p = HERE / path
            raw = p.read_bytes()
            source[name] = gzip.decompress(raw) if p.suffix == '.gz' else raw
        assert source['src/settlement_handlers.rs'].split(b'macro_rules! just_error', 1)[1] == base['src/settlement_handlers.rs'].split(b'macro_rules! just_error', 1)[1]
        launch, build = read(d / 'launch.json'), read(d / 'result.json')
        assert launch['inputs'] == {name: sha(raw) for name, raw in source.items()}
        assert build['exit_code'] == 0 and build['source_unchanged']
        assert launch['rustc_sha256'] == native_compiler
        log = (d / 'build.log').read_bytes()
        assert sha(log) == build.get('log_sha256', build.get('build_log_sha256'))
        assert b'Compiling donation-relay-source-proposal' in log and b'--crate-name donation_relay_source_proposal' in log
        images = {}
        for kind, descriptor in record['artifacts'].items():
            raw = gzip.decompress((HERE / descriptor['path']).read_bytes())
            assert sha(raw) == descriptor['sha256'] == build[kind + '_sha256']
            assert len(raw) == descriptor['bytes']
            images[kind] = raw
        key = (sha(images['candidate']), sha(images['symbols']))
        if key not in cache:
            with tempfile.TemporaryDirectory() as temp:
                p = Path(temp)
                for name, raw in [('original.so', original), ('candidate.so', images['candidate']),
                                  ('unstripped.so', images['symbols']), ('original-windows.json', windows.read_bytes())]:
                    (p / name).write_bytes(raw)
                cache[key] = parser.analyze(p)
        analysis = cache[key]
        summary, ledger = analysis['comparison-summary.json'], analysis['match-ledger.json']
        matched_after = {r['ordinal'] for r in ledger if r['normalized_candidate_indices']}
        targets = {}
        for ordinal, expected in record['targets'].items():
            i = int(ordinal)
            assert i in symbols
            rows = [r for r in analysis['candidate-function-ledger.json'] if any(symbols[i] in name for name in r['names'])]
            assert len(rows) == 1
            row = rows[0]
            assert row['bytes'] == expected['bytes'] and row['normalized_sha256'] == expected['normalized_sha256']
            assert expected['matched'] is False and not ledger[i]['normalized_candidate_indices']
            targets[ordinal] = dict(original_bytes=ledger[i]['bytes'], candidate_bytes=row['bytes'],
                                    normalized_sha256=row['normalized_sha256'], matched=False)
            comparisons += 1
        assert not summary['whole_file_equal']
        result[label] = dict(summary=summary, targets=targets,
                             gained_windows=sorted(matched_after - matched_before),
                             lost_windows=sorted(matched_before - matched_after))
    assert comparisons == 14
    assert not any(r['gained_windows'] or r['lost_windows'] for r in result.values())
    compiler = compiler_control(parser, base, original, windows, matched_before)
    return dict(variants=result, groups=dict(groups), targeted_comparisons=comparisons,
                compiler_control=compiler,
                scope='Fourteen epoch-close source controls retain the frontier. The compiler substitution loses 256 matches with no gain. No candidate is promoted.')



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--materialize', type=Path)
    ap.add_argument('--variant')
    args = ap.parse_args()
    if not args.write:
        manifest(HERE)
    if args.materialize:
        assert args.variant and not args.materialize.exists()
        _, source = parent()
        record = read(HERE / 'metadata.json')['variants'][args.variant]
        for name, filename in record['source_overrides'].items():
            p = HERE / filename
            raw = p.read_bytes()
            source[name] = gzip.decompress(raw) if p.suffix == '.gz' else raw
        for name, raw in source.items():
            p = args.materialize / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
        print('Materialized', len(source), 'source inputs')
        return
    report = derive()
    if args.write:
        (HERE / 'report.json').write_bytes(encoded(report))
        records = {str(p.relative_to(HERE)): sha(p.read_bytes()) for p in sorted(HERE.rglob('*'))
                   if p.is_file() and p.name != 'manifest.json' and '__pycache__' not in p.parts}
        (HERE / 'manifest.json').write_bytes(encoded(records))
    else:
        assert report == read(HERE / 'report.json')
    print('PASS: 14 unchanged-frontier source controls; compiler substitution loses 256 matches without a gain; no promotion')


if __name__ == '__main__':
    main()

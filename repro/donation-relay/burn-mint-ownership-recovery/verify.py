#!/usr/bin/env python3
"""Verify mint ownership recovery without relaxing the instruction matcher."""
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
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def manifest(path):
    values = read(path / 'manifest.json')
    files = {str(p.relative_to(path)) for p in path.rglob('*') if p.is_file()
             and p.name != 'manifest.json' and '__pycache__' not in p.parts}
    assert files == set(values)
    for name, digest in values.items():
        p = path / name
        assert not p.is_symlink() and p.resolve().is_relative_to(path) and sha(p.read_bytes()) == digest, name


def parent():
    for name, digest in read(HERE / 'parents.json').items():
        assert sha((ROOT / name).read_bytes()) == digest, name
    p = ROOT / 'repro/donation-relay/jupiter-option-source-recovery'
    manifest(p)
    jupiter = module('burn_jupiter_parent', p / 'verify.py')
    _, parser, base = jupiter.parent()
    base['src/settlement_handlers.rs'] = jupiter.core_sources(base)['option-match']
    assert len(base) == 56
    return parser, base


def source_bytes(record):
    p = HERE / record['source_path']
    raw = p.read_bytes()
    return gzip.decompress(raw) if p.suffix == '.gz' else raw


def recovered_source(base):
    text = base['src/settlement_handlers.rs'].decode()
    start = text.index("pub fn burn_and_close<'info>")
    stop = text.index('\nmacro_rules! distribution_error', start)
    body = text[start:stop]
    replacements = {
        'let (mint,authority,destination,program)=(ctx.mint,ctx.authority,ctx.destination,ctx.program);':
        'let BurnCloseContext {token,mint,authority,destination,program}=ctx;',
        'mint:mint.clone()': 'mint:mint',
        'from:ctx.token.clone()': 'from:token.clone()',
        'account:ctx.token': 'account:token',
    }
    for old, new in replacements.items():
        assert body.count(old) == 1
        body = body.replace(old, new)
    return (text[:start] + body + text[stop:]).encode()


def derive(write=False):
    parser, base = parent()
    recovered = recovered_source(base)
    metadata = read(HERE / 'metadata.json')
    assert len(metadata['variants']) == 46
    original = (ROOT / 'evidence/dependencies/donation_relay/deployed.so').read_bytes()
    assert sha(original) == '367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563'
    windows = ROOT / 'repro/donation-relay/swap-receipt-coordinate-recovery/original-windows.json'
    previous = read(ROOT / 'repro/donation-relay/jupiter-option-source-recovery/builds/option-match/match-ledger.json')
    before = {r['ordinal'] for r in previous if r['normalized_candidate_indices']}
    location_check = module('burn_location_check', ROOT / 'repro/donation-relay/source-location-recovery/verify.py')
    _, locations, _ = location_check.load()
    old_location = read(ROOT / 'repro/donation-relay/source-location-recovery/location-values.json')
    location_keys = {(r['original_ordinal'], r['reference_offset']) for r in old_location['variants']['combined']['location_pairs']}
    jupiter_report = read(ROOT / 'repro/donation-relay/jupiter-option-source-recovery/report.json')
    location_keys.update(tuple(pair) for pair in jupiter_report['variants']['option-match']['location_cohort']['new_pairs'])
    assert len(location_keys) == 348
    result, runtime, cache = {}, {}, {}
    for label, record in metadata['variants'].items():
        d = HERE / 'builds' / label
        source = dict(base)
        source['src/settlement_handlers.rs'] = source_bytes(record)
        if label in ('recovered', 'linux-recovered'):
            assert source['src/settlement_handlers.rs'] == recovered
        launch, build = read(d / 'launch.json'), read(d / 'result.json')
        assert launch['inputs'] == {n: sha(raw) for n, raw in source.items()}
        assert build['exit_code'] == 0 and build['source_unchanged']
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
        after = {r['ordinal'] for r in ledger if r['normalized_candidate_indices']}
        target_index = record['target_ordinal']
        matched = bool(ledger[target_index]['normalized_candidate_indices'])
        assert matched == record['observed']['matched']
        term = '14burn_and_close17h' if target_index == 109 else '11close_epoch17h'
        functions = [f for f in analysis['candidate-function-ledger.json'] if any(term in n for n in f['names'])]
        assert len(functions) == 1
        function = functions[0]
        if 'bytes' in record['observed']:
            assert function['bytes'] == record['observed']['bytes']
            assert function['normalized_sha256'] == record['observed']['normalized_sha256']
        assert not summary['whole_file_equal']
        result[label] = dict(summary=summary, target_ordinal=target_index, target_matched=matched,
                             target_candidate_bytes=function['bytes'], target_normalized_sha256=function['normalized_sha256'],
                             added_original_windows=sorted(after - before), lost_original_windows=sorted(before - after))
        if label in ('recovered', 'linux-recovered'):
            assert after - before == {109} and not before - after
            assert summary['original_normalized_match_windows'] == 482
            assert summary['original_raw_match_windows'] == 130
            assert summary['candidate_bytes'] == 818096
            for name in ['comparison-summary.json', 'match-ledger.json']:
                if write:
                    (d / name).write_bytes(encoded(analysis[name]))
                else:
                    assert read(d / name) == analysis[name]
            candidates = [f for f in analysis['candidate-function-ledger.json']
                          if any('14burn_and_close17h' in n for n in f['names'])]
            assert len(candidates) == 1
            candidate = candidates[0]
            target = analysis['original-function-ledger.json'][109]
            assert target['bytes'] == candidate['bytes'] == 2856
            assert target['normalized_sha256'] == candidate['normalized_sha256']
            oi = {f['start']: f['ordinal'] for f in analysis['original-function-ledger.json']}
            ci = {f['start']: f['index'] for f in analysis['candidate-function-ledger.json']}
            assert len(target['direct_calls']) == len(candidate['direct_calls']) == 24
            edges = []
            for a, b in zip(target['direct_calls'], candidate['direct_calls']):
                assert a['offset'] == b['offset']
                i, j = oi[a['target']], ci[b['target']]
                assert j in ledger[i]['normalized_candidate_indices']
                edges.append(dict(offset=a['offset'], original_ordinal=i, candidate_index=j))
            result[label]['direct_callee_matches'] = edges
            pairs = location_check.pairs(parser, locations, original, images['symbols'], analysis)
            assert {(r['original_ordinal'], r['reference_offset']) for r in pairs} == location_keys
            assert len(pairs) == 348 and all(r['equal'] for r in pairs)
            result[label]['equal_location_pairs'] = 348
        if record.get('fresh_runtime'):
            receipt = read(d / 'fresh-runtime.json.gz')
            assert receipt['candidate_sha256'] == summary['candidate_sha256']
            assert receipt['runner_sha256'] == sha((HERE / 'replay_saved.py').read_bytes())
            frozen = {}
            for name, digest in receipt['input_reports'].items():
                file = ROOT / name
                assert sha(file.read_bytes()) == digest
                for i, row in enumerate(read(file)['cases']):
                    frozen[str(file.relative_to(ROOT / 'repro/donation-relay/distribution-worker-source-recovery/settlement')) + ':' + str(i)] = row
            helper = module('burn_receipt_' + label.replace('-', '_'), ROOT / 'repro/donation-relay/swap-receipt-coordinate-recovery/verify.py')
            helper.EXPECTED['recovered'] = receipt['candidate_sha256']
            hp = ROOT / 'repro/donation-relay/local-validation-proposal/harness_proposal.py'
            assert receipt['harness_sha256'] == sha(hp.read_bytes())
            assert receipt['token2022_sha256'] == sha((ROOT / 'evidence/dependencies/spl_token_2022/deployed.so').read_bytes())
            runtime[label] = helper.check_runtime(receipt, frozen, module('burn_runtime_' + label.replace('-', '_'), hp))
    assert set(runtime) == {'recovered', 'linux-recovered'}
    return dict(variants=result, runtime=runtime, recovered_original_ordinal=109,
                remaining_ordinals=[92, 93, 94, 95, 96, 97, 98, 99, 100, 112],
                scope='Complete normalized burn/close body and matched direct callees; not whole-file, data or exhaustive semantic identity.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--materialize', type=Path)
    ap.add_argument('--variant', default='recovered')
    args = ap.parse_args()
    if not args.write:
        manifest(HERE)
    if args.materialize:
        assert not args.materialize.exists()
        _, source = parent()
        records = read(HERE / 'metadata.json')['variants']
        assert args.variant in records
        source['src/settlement_handlers.rs'] = source_bytes(records[args.variant])
        for name, raw in source.items():
            p = args.materialize / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
        print('Materialized', len(source), 'exact source inputs')
        return
    report = derive(args.write)
    if args.write:
        (HERE / 'report.json').write_bytes(encoded(report))
        values = {str(p.relative_to(HERE)): sha(p.read_bytes()) for p in sorted(HERE.rglob('*'))
                  if p.is_file() and p.name != 'manifest.json' and '__pycache__' not in p.parts}
        (HERE / 'manifest.json').write_bytes(encoded(values))
    else:
        assert report == read(HERE / 'report.json')
    print('PASS: complete 2,856-byte burn/close window on both compiler recipes; 482/492 matches, 10 unmatched, 348 equal location pairs and two fresh 536-record replays')


if __name__ == '__main__':
    main()

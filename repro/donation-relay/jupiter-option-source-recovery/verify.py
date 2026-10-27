#!/usr/bin/env python3
"""Verify the complete Jupiter optional-seed body and independent build controls."""
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import json
import struct
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
    p = ROOT / 'repro/donation-relay/residual-cpi-source-trials'
    manifest(p)
    prior = module('jupiter_recovery_parent', p / 'verify.py')
    parser, base = prior.sources()
    return prior, parser, base


def core_sources(base):
    near = base['src/settlement_handlers.rs'].decode().replace(
        'let infos=remaining.to_vec();', 'let infos=remaining.iter().cloned().collect::<Vec<_>>();')
    optional = near.replace('invoke_jupiter(program.key(),authority,remaining,data,seeds)?',
                            'invoke_jupiter(program.key(),authority,remaining,data,Some(seeds))?')
    optional = optional.replace(
        "pub fn invoke_jupiter<'info>(program:Pubkey,authority:Pubkey,remaining:&[AccountInfo<'info>],data:Vec<u8>,seeds:&[&[&[u8]]])",
        "pub fn invoke_jupiter<'info>(program:Pubkey,authority:Pubkey,remaining:&[AccountInfo<'info>],data:Vec<u8>,seeds:Option<&[&[&[u8]]]>)")
    old = 'if seeds.is_empty() {anchor_lang::solana_program::program::invoke(&ix,&infos)?;} else {anchor_lang::solana_program::program::invoke_signed(&ix,&infos,seeds)?;}Ok(())'
    let = 'if let Some(seeds)=seeds {anchor_lang::solana_program::program::invoke_signed(&ix,&infos,seeds)?;} else {anchor_lang::solana_program::program::invoke(&ix,&infos)?;}Ok(())'
    match = 'match seeds {Some(seeds)=>anchor_lang::solana_program::program::invoke_signed(&ix,&infos,seeds)?,None=>anchor_lang::solana_program::program::invoke(&ix,&infos)?};Ok(())'
    assert near.count(old) == optional.count(old) == 1
    return {'linux-iterator-control': near.encode(), 'option-if-some': optional.replace(old, let).encode(),
            'option-match': optional.replace(old, match).encode(), 'linux-option-match': optional.replace(old, match).encode()}


def derive(write=False):
    prior, parser, base = parent()
    location_verifier = module('jupiter_locations', ROOT / 'repro/donation-relay/source-location-recovery/verify.py')
    _, locations, _ = location_verifier.load()
    old_locations = read(ROOT / 'repro/donation-relay/source-location-recovery/location-values.json')
    old_location_keys = {(r['original_ordinal'], r['reference_offset']) for r in old_locations['variants']['combined']['location_pairs']}
    assert len(old_location_keys) == 346
    expected_sources = core_sources(base)
    metadata = read(HERE / 'metadata.json')
    assert len(metadata['variants']) == 23
    original = (ROOT / 'evidence/dependencies/donation_relay/deployed.so').read_bytes()
    windows_path = ROOT / 'repro/donation-relay/swap-receipt-coordinate-recovery/original-windows.json'
    control = read(ROOT / 'repro/donation-relay/source-location-recovery/builds/combined/match-ledger.json')
    before = {r['ordinal'] for r in control if r['normalized_candidate_indices']}
    reports, runtime, cache, core_images = {}, {}, {}, {}
    for label, record in metadata['variants'].items():
        d = HERE / 'builds' / label
        source = dict(base)
        source['src/settlement_handlers.rs'] = (d / 'settlement_handlers.rs').read_bytes()
        if label in expected_sources:
            assert source['src/settlement_handlers.rs'] == expected_sources[label], label
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
        if label in expected_sources:
            core_images[label] = images['candidate']
        key = (sha(images['candidate']), sha(images['symbols']))
        if key not in cache:
            with tempfile.TemporaryDirectory() as temporary:
                p = Path(temporary)
                for name, raw in [('original.so', original), ('candidate.so', images['candidate']),
                                  ('unstripped.so', images['symbols']), ('original-windows.json', windows_path.read_bytes())]:
                    (p / name).write_bytes(raw)
                cache[key] = parser.analyze(p)
        result = cache[key]
        summary, ledger = result['comparison-summary.json'], result['match-ledger.json']
        after = {r['ordinal'] for r in ledger if r['normalized_candidate_indices']}
        expected_gain = {90} if record['group'] == 'recovered' else set()
        assert after - before == expected_gain and not before - after, label
        assert summary['original_normalized_match_windows'] == (481 if expected_gain else 480)
        assert not summary['whole_file_equal']
        target = result['original-function-ledger.json'][90]
        candidates = [f for f in result['candidate-function-ledger.json']
                      if any('14invoke_jupiter17h' in name for name in f['names'])]
        assert len(candidates) == 1
        candidate = candidates[0]
        reports[label] = dict(summary=summary, added_original_windows=sorted(expected_gain),
                              lost_original_windows=[], jupiter_candidate_bytes=candidate['bytes'],
                              jupiter_normalized_match=candidate['normalized_sha256'] == target['normalized_sha256'])
        if label in expected_sources:
            for name in ['comparison-summary.json', 'match-ledger.json']:
                if write:
                    (d / name).write_bytes(encoded(result[name]))
                else:
                    assert read(d / name) == result[name]
        if expected_gain:
            assert candidate['bytes'] == target['bytes'] == 2496
            assert candidate['normalized_sha256'] == target['normalized_sha256']
            assert summary['original_raw_match_windows'] == 130
            oelf, celf = parser.Elf(original), parser.Elf(images['symbols'])
            # The original and candidate branch on the incoming optional pointer,
            # not on the slice length. Check the actual loads/stores and branch.
            expected = {80: (0x7b, 0x1a, -240, 0), 88: (0x79, 0x51, -4080, 0),
                        96: (0x7b, 0x1a, -224, 0), 1400: (0x79, 0xa1, -224, 0),
                        1408: (0x55, 0x01, 33, 0)}
            for elf, f in [(oelf, target), (celf, candidate)]:
                assert all(struct.unpack('<BBhi', elf.at(f['start'] + off, 8)) == insn
                           for off, insn in expected.items())
            oi = {f['start']: f['ordinal'] for f in result['original-function-ledger.json']}
            ci = {f['start']: f['index'] for f in result['candidate-function-ledger.json']}
            edges = []
            assert len(target['direct_calls']) == len(candidate['direct_calls'])
            for a, b in zip(target['direct_calls'], candidate['direct_calls']):
                assert a['offset'] == b['offset']
                i, j = oi[a['target']], ci[b['target']]
                assert j in ledger[i]['normalized_candidate_indices']
                edges.append(dict(offset=a['offset'], original_ordinal=i, candidate_index=j))
            reports[label]['complete_direct_callee_matches'] = edges
            pairs = location_verifier.pairs(parser, locations, original, images['symbols'], result)
            keys = {(p['original_ordinal'], p['reference_offset']) for p in pairs}
            assert len(pairs) == len(keys) == 348 and old_location_keys <= keys
            assert all(p['equal'] for p in pairs)
            reports[label]['location_cohort'] = dict(equal_pairs=348, retained_parent_pairs=346,
                                                     new_pairs=[list(k) for k in sorted(keys - old_location_keys)])
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
            helper = module('jupiter_option_receipt_' + label.replace('-', '_'), ROOT / 'repro/donation-relay/swap-receipt-coordinate-recovery/verify.py')
            helper.EXPECTED['recovered'] = receipt['candidate_sha256']
            harness_path = ROOT / 'repro/donation-relay/local-validation-proposal/harness_proposal.py'
            assert receipt['harness_sha256'] == sha(harness_path.read_bytes())
            assert receipt['token2022_sha256'] == sha((ROOT / 'evidence/dependencies/spl_token_2022/deployed.so').read_bytes())
            runtime[label] = helper.check_runtime(receipt, frozen, module('jupiter_option_harness_' + label.replace('-', '_'), harness_path))
    assert set(runtime) == {'option-match', 'linux-option-match', 'linux-iterator-control'}
    assert reports['option-match']['summary']['candidate_bytes'] == reports['linux-option-match']['summary']['candidate_bytes'] == 818176
    partial = gzip.decompress((ROOT / 'repro/donation-relay/residual-cpi-source-trials/artifacts/007b200e784270f1b9dbe8cc1c15a1553e04b9bbf46344d96ce5d2c082fc0113.so.gz').read_bytes())
    differences = {}
    for label, control_image in [('option-match', partial), ('linux-option-match', core_images['linux-iterator-control'])]:
        recovered = core_images[label]
        assert len(control_image) == len(recovered)
        values = [dict(offset=i, before=a, after=b) for i, (a, b) in enumerate(zip(control_image, recovered)) if a != b]
        assert len(values) == 10
        differences[label] = values
    return dict(variants=reports, runtime=runtime, recovered_original_ordinal=90,
                whole_stripped_file_changes_from_iterator_controls=differences,
                remaining_ordinals=[92, 93, 94, 95, 96, 97, 98, 99, 100, 109, 112],
                scope='Complete normalized Jupiter window and matched direct callees, not complete raw bytes, all data, historical source or exhaustive semantics.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--materialize', type=Path)
    ap.add_argument('--variant', default='option-match')
    args = ap.parse_args()
    if not args.write:
        manifest(HERE)
    if args.materialize:
        assert not args.materialize.exists()
        _, _, base = parent()
        assert args.variant in read(HERE / 'metadata.json')['variants']
        base['src/settlement_handlers.rs'] = (HERE / 'builds' / args.variant / 'settlement_handlers.rs').read_bytes()
        for name, raw in base.items():
            p = args.materialize / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
        print('Materialized', len(base), 'exact source inputs')
        return
    report = derive(args.write)
    if args.write:
        (HERE / 'report.json').write_bytes(encoded(report))
        values = {str(p.relative_to(HERE)): sha(p.read_bytes()) for p in sorted(HERE.rglob('*'))
                  if p.is_file() and p.name != 'manifest.json' and '__pycache__' not in p.parts}
        (HERE / 'manifest.json').write_bytes(encoded(values))
    else:
        assert report == read(HERE / 'report.json')
    print('PASS: complete Jupiter window 90 on both build recipes; 481/492 normalized windows, 11 unmatched; fresh bounded replay on both recovered binaries')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Recompute source-only security metadata recovery; never compile or run ELF."""
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import json
import re
import struct
import tempfile
import tomllib

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'evidence/dependencies/donation_relay/deployed.so').is_file())
PARSER = 'repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py'
WINDOWS = 'repro/donation-relay/swap-receipt-coordinate-recovery/original-windows.json'
ORIGINAL = 'evidence/dependencies/donation_relay/deployed.so'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def manifest():
    expected = read(HERE / 'manifest.json')
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob('*')
              if p.is_file() and p.name != 'manifest.json' and '__pycache__' not in p.parts}
    assert actual == set(expected)
    for name, digest in expected.items():
        p = HERE / name
        assert p.resolve().is_relative_to(HERE) and not p.is_symlink()
        assert sha(p.read_bytes()) == digest, name


def safe_source_name(name):
    path = Path(name)
    assert name and not path.is_absolute() and '..' not in path.parts
    assert str(path) == name
    return path


def sources():
    snapshot = read(HERE / 'source-snapshot.json.gz')
    source = {name: value.encode() for name, value in snapshot.items()}
    for name in source:
        safe_source_name(name)
    assert len(source) == 57
    receipt = read(HERE / 'source-inputs.json')
    assert {n: sha(b) for n, b in source.items()} == receipt['files']
    assert source['src/embedded_security.rs'] == (HERE / 'source/embedded_security.rs').read_bytes()
    before = dict(source)
    before.pop('src/embedded_security.rs')
    suffix = b'\nmod embedded_security;\n'
    assert before['src/lib.rs'].endswith(suffix)
    before['src/lib.rs'] = before['src/lib.rs'][:-len(suffix)]
    declaration = b'solana-security-txt = "=1.1.3"\n'
    assert before['Cargo.toml'].count(declaration) == 1
    before['Cargo.toml'] = before['Cargo.toml'].replace(declaration, b'')
    lock = before['Cargo.lock'].decode()
    start = lock.index('name = "donation-relay-source-proposal"')
    end = lock.index('\n[[package]]', start)
    root = lock[start:end]
    assert root.count(' "solana-security-txt",\n') == 1
    lock = lock[:start] + root.replace(' "solana-security-txt",\n', '') + lock[end:]
    before['Cargo.lock'] = lock.encode()
    hashes = {n: sha(b) for n, b in before.items()}
    assert len(before) == 56 and hashes == read(HERE / 'base-inputs.json')['files']
    upstream = read(ROOT / 'repro/donation-relay/burn-mint-ownership-recovery/builds/linux-recovered/launch.json')
    assert hashes == upstream['inputs']
    changed = {n for n, b in source.items() if before.get(n) != b}
    assert changed == {'Cargo.toml', 'Cargo.lock', 'src/lib.rs', 'src/embedded_security.rs'}
    assert tomllib.loads(source['Cargo.toml'].decode())['dependencies']['solana-security-txt'] == '=1.1.3'
    lock = tomllib.loads(source['Cargo.lock'].decode())
    package = next(p for p in lock['package'] if p['name'] == 'solana-security-txt')
    assert package['version'] == '1.1.3'
    assert package['checksum'] == read(HERE / 'metadata.json')['macro_registry_checksum']
    provenance = read(HERE / 'provenance/security-txt-package.json')
    assert provenance['sha256'] == package['checksum']
    assert provenance['source_files']['src/lib.rs'] == sha((HERE / 'provenance/solana-security-txt-lib.rs').read_bytes())
    return before, source


def semantic_payload(source):
    text = source['src/embedded_security.rs'].decode()
    fields = [(name, json.loads(value)) for name, value in
              re.findall(r'^\s+(\w+): ("[^"\n]*"),?$', text, re.M)]
    assert [n for n, _ in fields] == ['name', 'project_url', 'contacts', 'policy',
                                     'preferred_languages', 'source_code', 'auditors', 'acknowledgements']
    return ('=======BEGIN SECURITY.TXT V1=======\0' +
            ''.join(name + '\0' + value + '\0' for name, value in fields) +
            '=======END SECURITY.TXT V1=======\0').encode()


def dynamic_symbols(elf):
    section = elf.by_name['.dynsym']
    strings = elf.section_bytes(elf.by_name['.dynstr'])
    result = []
    for offset in range(section['offset'], section['offset'] + section['size'], 24):
        n, info, other, index, value, size = struct.unpack_from('<IBBHQQ', elf.b, offset)
        result.append(dict(name=elf.string(strings, n), info=info, other=other,
                           section=index, address=value, bytes=size))
    return result


def security_object(elf, expected):
    symbols = [s for s in dynamic_symbols(elf) if s['name'] == 'SECURITY_TXT']
    assert len(symbols) == 1, 'expected one exported SECURITY_TXT object'
    symbol = symbols[0]
    assert symbol['info'] == 17 and symbol['other'] == 0 and symbol['bytes'] == 16
    assert symbol['section'] == elf.by_name['.data.rel.ro']['index']
    address = symbol['address']
    relocation = elf.relocations.get(address)
    assert relocation and relocation['type'] == 8 and relocation['symbol'] == ''
    raw = elf.at(address, 16)
    low, pointer, size = struct.unpack('<IIQ', raw)
    assert low == 0 and size == len(expected) == 510
    section = elf.containing(pointer)
    assert section and section['name'] == '.rodata'
    payload = elf.at(pointer, size)
    assert payload == expected
    return dict(symbol=symbol, object_hex=raw.hex(), relocation=relocation,
                payload_address=pointer, payload_bytes=size, payload_sha256=sha(payload))


def elf_extent(elf):
    h = struct.unpack_from('<16sHHIQQQIHHHHHH', elf.b)
    extent = max(h[8], h[5] + h[9] * h[10], h[6] + h[11] * h[12])
    for section in elf.sections:
        if section['type'] != 8:
            extent = max(extent, section['offset'] + section['size'])
    for i in range(h[10]):
        _, _, offset, _, _, size, _, _ = struct.unpack_from('<IIQQQQQQ', elf.b, h[5] + i * h[9])
        extent = max(extent, offset + size)
    assert extent <= len(elf.b)
    return dict(full_file_bytes=len(elf.b), elf_extent_bytes=extent,
                trailing_bytes=len(elf.b) - extent, trailing_all_zero=not any(elf.b[extent:]),
                elf_extent_sha256=sha(elf.b[:extent]), full_file_sha256=sha(elf.b))


def analyze(parser, original, image, symbols):
    with tempfile.TemporaryDirectory() as temporary:
        p = Path(temporary)
        for name, data in [('original.so', original), ('candidate.so', image),
                           ('unstripped.so', symbols), ('original-windows.json', (ROOT / WINDOWS).read_bytes())]:
            (p / name).write_bytes(data)
        return parser.analyze(p)


def runtime(candidate_sha):
    receipt = read(HERE / 'fresh-runtime.json.gz')
    assert receipt['runner_sha256'] == sha((HERE / 'replay_saved.py').read_bytes())
    assert receipt['candidate_sha256'] == candidate_sha
    harness_path = ROOT / 'repro/donation-relay/local-validation-proposal/harness_proposal.py'
    assert receipt['harness_sha256'] == sha(harness_path.read_bytes())
    assert receipt['token2022_sha256'] == sha((ROOT / 'evidence/dependencies/spl_token_2022/deployed.so').read_bytes())
    frozen = {}
    for name, digest in receipt['input_reports'].items():
        path = ROOT / safe_source_name(name)
        assert sha(path.read_bytes()) == digest
        for i, row in enumerate(read(path)['cases']):
            relative = path.relative_to(ROOT / 'repro/donation-relay/distribution-worker-source-recovery/settlement')
            frozen[str(relative) + ':' + str(i)] = row
    helper = module('security_runtime_check', ROOT / 'repro/donation-relay/swap-receipt-coordinate-recovery/verify.py')
    helper.EXPECTED['recovered'] = candidate_sha
    return helper.check_runtime(receipt, frozen, module('security_runtime_harness', harness_path))


def derive():
    for name, digest in read(HERE / 'inputs.json').items():
        assert sha((ROOT / name).read_bytes()) == digest, name
    before, source = sources()
    payload = semantic_payload(source)
    assert payload.replace(b'\0', b'\n') == (ROOT / 'localnet/relay/embedded-security.txt').read_bytes()
    metadata = read(HERE / 'metadata.json')
    parser = module('security_metadata_elf', ROOT / PARSER)
    original = (ROOT / ORIGINAL).read_bytes()
    assert sha(original) == metadata['original_sha256']
    variants = {}
    for label in ['baseline', 'recovered']:
        if label == 'baseline':
            images = {k: gzip.decompress((ROOT / v['path']).read_bytes())
                      for k, v in metadata['baseline_artifacts'].items()}
        else:
            images = {k: gzip.decompress((HERE / ('artifacts/' + n + '.so.gz')).read_bytes())
                      for k, n in [('candidate', 'candidate'), ('symbols', 'symbols')]}
        result = read(HERE / 'builds' / label / 'result.json')
        launch = read(HERE / 'builds' / label / 'launch.json')
        assert result['returncode'] == result['strip_returncode'] == 0
        assert result['source_unchanged'] and result['registry_sources_unchanged'] and not result['backend_error_lines']
        assert launch['source_hashes'] == {n: sha(b) for n, b in (before if label == 'baseline' else source).items()}
        log = (HERE / 'builds' / label / 'build.log').read_bytes()
        assert sha(log) == result['build_log_sha256']
        roots = [line for line in log.decode().splitlines() if 'Running `' in line and '--crate-name donation_relay_source_proposal ' in line]
        assert len(roots) == 1
        assert '--locked' in launch['command'] and '--offline' in launch['command']
        if label == 'recovered':
            assert result['seed_target_unchanged'] and result['actual_root_rustc_invocations'] == 1
            assert sha((HERE / 'builds/recovered/driver.py').read_bytes()) == launch['driver_sha256']
            assert read(HERE / 'builds/recovered/clean-root.json')['remaining_root_artifacts'] == []
        for kind, raw in images.items():
            assert sha(raw) == result[kind + '_sha256']
            if label == 'recovered':
                assert sha(raw) == metadata[kind + '_sha256']
        analysis = analyze(parser, original, images['candidate'], images['symbols'])
        for name in ['comparison-summary.json', 'match-ledger.json', 'section-comparison.json']:
            assert analysis[name] == read(HERE / 'analysis' / label / name)
        summary = analysis['comparison-summary.json']
        assert summary['original_normalized_match_windows'] == 482 and summary['original_raw_match_windows'] == 130
        assert not summary['whole_file_equal']
        variants[label] = dict(images=images, analysis=analysis)
    old, new = (variants[label]['analysis'] for label in ['baseline', 'recovered'])
    oldset = {r['ordinal'] for r in old['match-ledger.json'] if r['normalized_candidate_indices']}
    newset = {r['ordinal'] for r in new['match-ledger.json'] if r['normalized_candidate_indices']}
    assert newset == oldset
    original_elf = parser.Elf(original)
    baseline_elf = parser.Elf(variants['baseline']['images']['candidate'])
    recovered_elf = parser.Elf(variants['recovered']['images']['candidate'])
    assert not [s for s in dynamic_symbols(baseline_elf) if s['name'] == 'SECURITY_TXT']
    objects = {label: security_object(elf, payload) for label, elf in [('original', original_elf), ('recovered', recovered_elf)]}
    assert original_elf.section_bytes(original_elf.by_name['.dynstr']) == recovered_elf.section_bytes(recovered_elf.by_name['.dynstr'])
    location_check = module('security_location_check', ROOT / 'repro/donation-relay/source-location-recovery/verify.py')
    locations = module('security_location_reader', ROOT / 'research/relay-location-data-audit/audit.py')
    cohorts = {}
    for label, variant in variants.items():
        pairs = location_check.pairs(parser, locations, original, variant['images']['symbols'], variant['analysis'])
        assert len(pairs) == 348 and all(p['equal'] for p in pairs)
        cohorts[label] = sorted((p['original_ordinal'], p['reference_offset']) for p in pairs)
    assert cohorts['baseline'] == cohorts['recovered']
    extents = {label: elf_extent(elf) for label, elf in [('original', original_elf), ('baseline', baseline_elf), ('recovered', recovered_elf)]}
    assert extents['original']['elf_extent_bytes'] == 818280
    assert extents['original']['trailing_bytes'] == 12168 and extents['original']['trailing_all_zero']
    assert extents['baseline']['trailing_bytes'] == extents['recovered']['trailing_bytes'] == 0
    return dict(summaries={k: v['analysis']['comparison-summary.json'] for k, v in variants.items()},
                added_normalized_windows=sorted(newset - oldset), lost_normalized_windows=sorted(oldset - newset),
                equal_source_location_pairs=348, dynamic_string_table_equal=True, security_objects=objects,
                extents=extents, runtime=runtime(metadata['candidate_sha256']),
                scope='Reconstructed semantic metadata and unchanged bounded instruction/location/replay checks; not whole-file identity or historical source recovery.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--materialize', type=Path)
    args = ap.parse_args()
    if not args.write:
        manifest()
    if args.materialize:
        assert not args.materialize.exists(), 'destination must not exist'
        _, source = sources()
        args.materialize.mkdir(parents=True)
        for name, raw in source.items():
            path = args.materialize / safe_source_name(name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        print('Materialized 57 exact ordinary source files; no ELF included')
        return
    report = derive()
    if args.write:
        (HERE / 'report.json').write_bytes(encoded(report))
        entries = {str(p.relative_to(HERE)): sha(p.read_bytes()) for p in sorted(HERE.rglob('*'))
                   if p.is_file() and p.name != 'manifest.json' and '__pycache__' not in p.parts}
        (HERE / 'manifest.json').write_bytes(encoded(entries))
    else:
        assert report == read(HERE / 'report.json')
    print('PASS: exact 510-byte SECURITY_TXT payload and .dynstr; 482/492 normalized, 130 raw, 348 locations, 536 replay records; NOT whole-file identity')


if __name__ == '__main__':
    main()

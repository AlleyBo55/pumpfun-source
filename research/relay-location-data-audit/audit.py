#!/usr/bin/env python3
"""Hash-bound static pointer/string/location audit. Never compiles or executes ELF."""
import collections
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
PARSER = 'repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py'
WINDOWS = 'repro/donation-relay/swap-receipt-coordinate-recovery/original-windows.json'
ORIGINAL = 'evidence/dependencies/donation_relay/deployed.so'
LATEST = 'repro/donation-relay/mint-fee-pair-recovery/'
INPUTS = {
    PARSER: '095fc2d63be0fe4233bdf4e5946cac8d03d9b1747fd39147eea9a98c12dda175',
    WINDOWS: 'c002df05d4489259f1cfd2b2391220cae38f6ffb0055f35f659e68a4935fd7bd',
    ORIGINAL: '367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563',
    LATEST + 'candidate.so.gz': '8d95f6327e6c69b0fa9f50f5b24210c5065687238f52a225490e6012996f1d7c',
    LATEST + 'symbols.so.gz': '6f2b8498fbf7771849830df18d2165fecd112f96e70a8cff41aaccf116632112',
    LATEST + 'launch.json': '7d8ac1016fa2ac9787bd5b5cba7f583d6c346165a68c4243a0a541c62fdeaee1',
}
STRIPPED_SHA = 'da61931f49713668c567791c4b36a49c3a75a1004ed331020054bcb13521f2c6'
SYMBOLS_SHA = 'dbf90f7721368f6bf3c56846b5dc1f07ab05837ac67356d0ef95ced4dc4f620c'


def H(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def read_location(elf, address):
    """Recognize a 24-byte location-shaped object, not an arbitrary 64-byte tail.

    SBF R_BPF_64_RELATIVE non-text pointers in these pinned files hold their
    virtual-address addend in the high 32 bits. Require that actual relocation,
    a zero low word, and exact allocated source-string extent before decoding.
    Rust type identity remains an inference; callers/source provide attribution.
    """
    relocation = elf.relocations.get(address)
    section = elf.containing(address)
    if not relocation or relocation['type'] != 8 or not section or section['name'] != '.data.rel.ro':
        return None
    try:
        raw = elf.at(address, 24)
        low, pointer, length, line, column = struct.unpack('<IIQII', raw)
        if low != 0 or not (1 <= length <= 300 and 1 <= line <= 100000 and 1 <= column <= 300):
            return None
        string_section = elf.containing(pointer)
        if not string_section or string_section['name'] != '.rodata':
            return None
        text = elf.at(pointer, length)
    except (ValueError, struct.error):
        return None
    if not text.endswith(b'.rs') or not all(32 <= x < 127 for x in text):
        return None
    return {'object_address': address, 'object_bytes': 24, 'object_hex': raw.hex(),
            'object_sha256': H(raw), 'pointer_relocation': relocation,
            'string_address': pointer, 'string_bytes': length, 'string_hex': text.hex(),
            'string_sha256': H(text), 'path': text.decode('ascii'), 'line': line,
            'column': column, 'type_identity': 'inferred Rust panic Location'}


def key(value):
    return value['path'], value['line'], value['column']


def derive():
    for name, digest in INPUTS.items():
        path = ROOT / name
        assert not path.is_symlink() and H(path.read_bytes()) == digest, name
    parser = module('location_pinned_elf', ROOT / PARSER)
    proposals = module('location_source_proposals', P / 'proposals.py')
    source = proposals.inputs()
    launch = json.loads((ROOT / (LATEST + 'launch.json')).read_text())
    for name, data in source.items():
        assert H(data) == launch['inputs'][name], name
    stripped = gzip.decompress((ROOT / (LATEST + 'candidate.so.gz')).read_bytes())
    symbols = gzip.decompress((ROOT / (LATEST + 'symbols.so.gz')).read_bytes())
    assert H(stripped) == STRIPPED_SHA and H(symbols) == SYMBOLS_SHA
    original_bytes = (ROOT / ORIGINAL).read_bytes()
    o, c, s = parser.Elf(original_bytes), parser.Elf(symbols), parser.Elf(stripped)
    for section in c.sections:
        if section['flags'] & 2 and section['type'] != 8:
            other = s.by_name[section['name']]
            assert section['address'] == other['address']
            assert c.section_bytes(section) == s.section_bytes(other)
    windows = json.loads((ROOT / WINDOWS).read_text())
    of = []
    for w in windows:
        f = o.function(w['start'], w['bytes'], [])
        assert f['raw_sha256'] == w['sha256']
        f['ordinal'] = w['ordinal']; of.append(f)
    syms = collections.defaultdict(list)
    for symbol in c.symbols:
        if symbol['type'] == 2 and symbol['size']:
            syms[(symbol['start'], symbol['size'])].append(symbol['name'])
    cf = [c.function(a, z, sorted(names)) for (a, z), names in sorted(syms.items())]
    normalized = collections.defaultdict(list)
    for i, f in enumerate(cf):
        normalized[f['bytes'], f['normalized_sha256']].append(i)
    omap = {f['start']: f['ordinal'] for f in of}
    cmap = {f['start']: i for i, f in enumerate(cf)}
    groups = {}
    unique = matched = location_pairs = equal_pairs = data_pairs = 0
    for a in of:
        indices = normalized.get((a['bytes'], a['normalized_sha256']), [])
        matched += bool(indices)
        if len(indices) != 1:
            continue
        unique += 1; j = indices[0]; b = cf[j]
        assert len(a['data_references']) == len(b['data_references'])
        for ar, br in zip(a['data_references'], b['data_references']):
            assert ar['offset'] == br['offset']
            data_pairs += 1
            x, y = read_location(o, ar['target']), read_location(c, br['target'])
            if not x or not y:
                continue
            location_pairs += 1
            if key(x) == key(y):
                equal_pairs += 1; continue
            group_key = key(x) + key(y)
            if group_key not in groups:
                groups[group_key] = {'original': x, 'candidate': y, 'uses': []}
            # A nearby direct call is retained as a call-site witness, not a
            # whole-function dataflow or reachability proof.
            calls = []
            for ac, bc in zip(a['direct_calls'], b['direct_calls']):
                if ar['offset'] < ac['offset'] <= ar['offset'] + 64:
                    oi, ci = omap.get(ac['target']), cmap.get(bc['target'])
                    calls.append({'instruction_offset': ac['offset'], 'original_target_ordinal': oi,
                                  'candidate_target_index': ci,
                                  'candidate_target_symbols': [] if ci is None else cf[ci]['names'],
                                  'target_normalized_body_equal': oi is not None and ci is not None
                                      and of[oi]['normalized_sha256'] == cf[ci]['normalized_sha256']
                                      and of[oi]['bytes'] == cf[ci]['bytes']})
            groups[group_key]['uses'].append({
                'original_ordinal': a['ordinal'], 'original_start': a['start'],
                'candidate_index': j, 'candidate_start': b['start'], 'candidate_symbols': b['names'],
                'body_bytes': a['bytes'], 'normalized_body_sha256': a['normalized_sha256'],
                'original_body_sha256': a['raw_sha256'], 'candidate_body_sha256': b['raw_sha256'],
                'reference_instruction_offset': ar['offset'],
                'original_location_address': x['object_address'],
                'candidate_location_address': y['object_address'],
                'original_location_hex': x['object_hex'],
                'candidate_location_hex': y['object_hex'],
                'original_reference_instruction_hex': o.at(a['start'] + ar['offset'], 16).hex(),
                'candidate_reference_instruction_hex': c.at(b['start'] + br['offset'], 16).hex(),
                'nearby_direct_calls': calls})
    result_groups = [groups[k] for k in sorted(groups)]
    uses = sum(len(g['uses']) for g in result_groups)
    assert (len(of), len(cf), matched, unique, len(groups), uses) == (492, 492, 480, 336, 6, 43)
    return {'inputs': INPUTS, 'candidate_decompressed_sha256': STRIPPED_SHA,
            'symbols_decompressed_sha256': SYMBOLS_SHA,
            'source_input_sha256': {name: H(data) for name, data in source.items()},
            'original_bytes': len(original_bytes), 'candidate_bytes': len(stripped),
            'whole_file_equal': original_bytes == stripped,
            'original_windows': len(of), 'candidate_windows': len(cf),
            'normalized_matched_windows': matched, 'uniquely_matched_windows_scanned': unique,
            'paired_data_references_scanned': data_pairs, 'recognized_location_pairs': location_pairs,
            'equal_location_pairs': equal_pairs, 'different_location_uses': uses,
            'distinct_different_location_pairs': len(groups), 'groups': result_groups,
            'source_proposals': proposals.verify_proposals(),
            'scope': 'Only uniquely normalized-matched complete functions and independently bounded 24-byte location-shaped records; not all data, indirect calls, reachability, or program semantics.',
            'compiled': False, 'target_executed': False, 'new_raw_or_normalized_gains_claimed': 0}


def check_manifest():
    manifest = json.loads((P / 'manifest.json').read_text())
    actual = {str(f.relative_to(P)) for f in P.rglob('*') if f.is_file()
              and f.name != 'manifest.json' and '__pycache__' not in f.parts}
    assert actual == set(manifest)
    for name, digest in manifest.items():
        f = P / name
        assert f.resolve().is_relative_to(P) and not f.is_symlink()
        assert H(f.read_bytes()) == digest, name


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--write', action='store_true', help='Write only this audit JSON/manifest; never a compiled artifact')
    args = p.parse_args()
    report = derive()
    if args.write:
        (P / 'location-audit.json').write_bytes(encoded(report))
        manifest = {str(f.relative_to(P)): H(f.read_bytes()) for f in sorted(P.rglob('*'))
                    if f.is_file() and f.name != 'manifest.json' and '__pycache__' not in f.parts}
        (P / 'manifest.json').write_bytes(encoded(manifest))
    else:
        check_manifest()
        assert (P / 'location-audit.json').read_bytes() == encoded(report)
    print(json.dumps({k: report[k] for k in ['normalized_matched_windows', 'uniquely_matched_windows_scanned',
        'recognized_location_pairs', 'equal_location_pairs', 'different_location_uses',
        'distinct_different_location_pairs', 'compiled', 'target_executed', 'whole_file_equal']}))


if __name__ == '__main__':
    main()

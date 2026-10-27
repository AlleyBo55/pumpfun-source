#!/usr/bin/env python3
"""Verify package inventory only by default. Explicit paths opt into byte checks.
No instruction decoder or native VM package is imported. Historical claims and
receipts remain immutable under history/ and rea-evidence/.
"""
from pathlib import Path
import argparse, hashlib, json, struct

P = Path(__file__).resolve().parent
H = lambda b: hashlib.sha256(b).hexdigest()
ORIG_SHA = '4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
CAND_SHA = '6c44d9f2ffe9b18c79a6344b256d8acd7a34c10e77b894c51f46512a447b8ce6'

def resolve_call(buf, call_off):
    """Resolve an on-disk src=1 local CALL in eight-byte instruction units.

    Anza sbpf elf.rs fixes PC-relative calls as target_pc=i+1+imm;
    ebpf.rs specifies INSN_SIZE=8. This does not resolve syscall hashes,
    relocated runtime encodings or prove original-to-candidate attribution.
    """
    if call_off < 0 or call_off % 8 or call_off + 8 > len(buf):
        raise ValueError('CALL must be a complete aligned instruction')
    insn = buf[call_off:call_off + 8]
    if insn[:4] != bytes([0x85, 0x10, 0, 0]):
        raise ValueError('Only on-disk src=1 local CALL is supported')
    return call_off + 8 + 8 * struct.unpack('<i', insn[4:])[0]

def verify_inventory():
    actual = {str(p.relative_to(P)): H(p.read_bytes()) for p in P.rglob('*')
              if p.is_file() and p != P / 'manifest-sha256.json'
              and '__pycache__' not in p.parts}
    if actual != json.loads((P / 'manifest-sha256.json').read_text()):
        raise ValueError('Package inventory mismatch')
    return len(actual)

def check_rea_bytes(original, candidate):
    """Check existing saved read_bytes receipts against explicit binary inputs.

    This does not rerun REA, search originals, infer layouts or attribute calls.
    """
    data = {'deployed.so': original, 'cand-fees-current.so': candidate}
    count = 0
    for path in sorted((P / 'rea-evidence').glob('ev_*.json')):
        rec = json.loads(path.read_text())
        if rec['operation'] != 'read_bytes':
            continue
        subject = rec['subject']
        if subject['name'] not in data:
            raise ValueError('Unknown saved read subject: ' + subject['name'])
        body = data[subject['name']]
        if H(body) != subject.get('sha256'):
            raise ValueError('Saved subject digest mismatch: ' + path.name)
        start = int(rec['parameters']['address'], 16)
        length = rec['parameters']['length']
        if start < 0 or length < 0 or start + length > len(body):
            raise ValueError('Saved byte range outside explicit input')
        if rec['bytes_hex'] != body[start:start + length].hex():
            raise ValueError('Saved byte range mismatch: ' + path.name)
        count += 1
    return count

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--original', type=Path, help='Explicit captured original for saved-byte checks')
    ap.add_argument('--candidate', type=Path, help='Explicit unrelocated current-source candidate')
    args = ap.parse_args(argv)
    if bool(args.original) != bool(args.candidate):
        ap.error('--original and --candidate must be supplied together')
    for path in [args.original, args.candidate]:
        if path is not None and not path.is_file():
            ap.error('Missing explicit input: ' + str(path))
    members = verify_inventory()
    if args.original is None:
        print(json.dumps({'state': 'PASS_PACKAGE_INVENTORY_ONLY', 'manifest_entries': members,
                          'original_bytes_read': False, 'shape_or_call_attribution_proven': False}))
        return 0
    original = args.original.read_bytes()
    candidate = args.candidate.read_bytes()
    if H(original) != ORIG_SHA or H(candidate) != CAND_SHA:
        raise ValueError('Explicit binary digest mismatch')
    count = check_rea_bytes(original, candidate)
    # Derived only on explicit invocation; no numeric target is asserted from
    # the flawed historical byte-displacement calculation.
    targets = {'original': resolve_call(original, 71240),
               'candidate_A': resolve_call(candidate, 0x144e0),
               'candidate_B': resolve_call(candidate, 0x145a8),
               'candidate_C': resolve_call(candidate, 0x14660)}
    print(json.dumps({'state': 'SAVED_BYTES_CHECKED_LOCAL_CALL_FORMULA_APPLIED',
                      'saved_byte_receipts_checked': count, 'file_offset_targets': targets,
                      'original_to_candidate_attribution_proven': False}, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

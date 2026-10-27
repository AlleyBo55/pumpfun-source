#!/usr/bin/env python3
"""Verify retained disassembly and actual assembly round-trip bytes offline."""
import gzip
import hashlib
import json
from pathlib import Path
import struct
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from sbpf_disassembly_inventory import sections


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify():
    manifest = json.loads((P / 'manifest.json').read_text())
    for name, digest in manifest.items():
        assert sha((P / name).read_bytes()) == digest, name
    inventory = json.loads((P / 'inventory/manifest.json').read_text())
    report = json.loads((P / 'roundtrip-report.json').read_text())
    assert inventory['generator_sha256'] == sha((ROOT / 'scripts/sbpf_disassembly_inventory.py').read_bytes())
    assert report['generator_sha256'] == sha((ROOT / 'scripts/sbpf_disassembly_roundtrip.py').read_bytes())
    assert report['inventory_manifest_sha256'] == sha((P / 'inventory/manifest.json').read_bytes())
    assert not report['counts_toward_source_reconstruction_acceptance']
    rebuilt = {row['name']: row for row in report['programs']}
    total = 0
    for entry in inventory['programs']:
        name = entry['name']
        compressed = (P / 'inventory' / (name + '.json.gz')).read_bytes()
        assert sha(compressed) == entry['inventory_sha256']
        decoded = json.loads(gzip.decompress(compressed))
        original = (ROOT / entry['input']).read_bytes()
        assert sha(original) == entry['input_sha256'] == decoded['input_sha256']
        text = sections(original)['.text']
        start, size = text[4:6]
        expected = original[start:start+size]
        assert sha(expected) == entry['text_sha256']
        at = start
        for row in decoded['instructions']:
            assert row['file_offset'] == at
            raw = bytes.fromhex(row['raw'])
            assert raw == original[at:at+len(raw)]
            op, regs, off, imm = struct.unpack_from('<BBhi', raw)
            assert (op, regs & 15, regs >> 4, off, imm) == (
                row['opcode'], row['dst'], row['src'], row['displacement'], row['immediate'])
            assert len(raw) == (16 if op == 0x18 else 8)
            if row.get('loader_relocation', {}).get('type') == 10:
                assert 'relative_call_target_file_offset' not in row
            at += len(raw)
        assert at == start + size
        assembly = gzip.decompress((P / 'inventory' / (name + '.s.gz')).read_bytes())
        assert sha(assembly) == entry['assembly_sha256']
        assert assembly.decode().splitlines() == [row['assembly'] for row in decoded['instructions']]
        assert not (P / 'inventory' / (name + '.stderr')).read_bytes()
        symbolic = gzip.decompress((P / 'assembly' / (name + '.s.gz')).read_bytes())
        assert sha(symbolic) == rebuilt[name]['assembly_sha256']
        candidate = (P / 'roundtrip-elfs' / (name + '.so')).read_bytes()
        assert sha(candidate) == rebuilt[name]['reassembled_elf_sha256']
        assembled = sections(candidate)['.text']
        actual = candidate[assembled[4]:assembled[4]+assembled[5]]
        assert actual == expected
        assert actual and candidate != original
        assert rebuilt[name]['full_text_equality'] and not rebuilt[name]['full_elf_equality']
        assert not rebuilt[name]['independent_source_reconstruction']
        total += len(decoded['instructions'])
    assert len(rebuilt) == len(inventory['programs']) == 9
    print(json.dumps(dict(verified=True, programs=9, instructions=total,
                          exact_reference_assembly_text_roundtrips=9,
                          independent_source_reconstruction=False, full_original_elf_identity=False)))


if __name__ == '__main__':
    verify()

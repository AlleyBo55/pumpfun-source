#!/usr/bin/env python3
"""Verify canonical LLVM SBF listings against every executable input byte.

LLVM's SBF addresses are decimal eight-byte instruction slots. LDDW occupies
two slots on one listing row. This checks coverage and raw bytes, not the
correctness of LLVM's mnemonic/operand interpretation or function boundaries.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

# Reuse the repository ELF parser without changing the digest-pinned scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from analyze import elf_layout

SECTION = re.compile(r'^Disassembly of section (.+):$')
LABEL = re.compile(r'^[0-9a-fA-F]+ <.*>:$')
ROW = re.compile(r'^\s*(\d+):\t([0-9a-fA-F ]+)\t(.+)$')


def verify_listing(binary, listing):
    layout = elf_layout(binary)
    if layout['machine'] not in (247, 263):
        raise ValueError('Expected an eBPF or SBF ELF machine')
    sections = [s for s in layout['sections'] if s['flags'] & 4 and s['type'] != 8]
    if not sections or len({s['name'] for s in sections}) != len(sections):
        raise ValueError('Expected uniquely named executable file sections')
    expected = {s['name']: s for s in sections}
    verified = {}
    current = None
    for line_number, line in enumerate(listing.splitlines(), 1):
        header = SECTION.fullmatch(line)
        if header:
            current = header[1]
            if current not in expected or current in verified:
                raise ValueError(f'Unexpected or repeated section: {current}')
            verified[current] = {'bytes': 0, 'instruction_rows': 0, 'lddw_rows': 0}
            continue
        if not line.strip() or LABEL.fullmatch(line.strip()):
            continue
        row = ROW.fullmatch(line)
        if current is None:
            if row:
                raise ValueError(f'Instruction outside a section at line {line_number}')
            continue  # LLVM's file-format preamble is not executable data.
        if row is None:
            raise ValueError(f'Unrecognized listing row at line {line_number}')
        encoded = bytes.fromhex(row[2])
        if len(encoded) not in (8, 16) or (len(encoded) == 16) != (encoded[0] == 0x18):
            raise ValueError(f'Invalid instruction width at line {line_number}')
        if '<unknown>' in row[3] or row[3].lstrip().startswith(('.byte', '.word')):
            raise ValueError(f'Undecoded instruction at line {line_number}')
        section, progress = expected[current], verified[current]
        if int(row[1]) * 8 != section['address'] + progress['bytes']:
            raise ValueError(f'Noncontiguous instruction address at line {line_number}')
        if progress['bytes'] + len(encoded) > section['size']:
            raise ValueError(f'Instruction exceeds section at line {line_number}')
        offset = section['offset'] + progress['bytes']
        if encoded != binary[offset:offset + len(encoded)]:
            raise ValueError(f'Instruction bytes differ at line {line_number}')
        progress['bytes'] += len(encoded)
        progress['instruction_rows'] += 1
        progress['lddw_rows'] += len(encoded) == 16
    for name, section in expected.items():
        if name not in verified or verified[name]['bytes'] != section['size']:
            raise ValueError(f'Missing executable bytes in section: {name}')
        verified[name]['instruction_slots'] = verified[name]['bytes'] // 8
    return {
        'complete_executable_byte_coverage': True,
        'executable_bytes_verified': sum(s['bytes'] for s in verified.values()),
        'instruction_rows': sum(s['instruction_rows'] for s in verified.values()),
        'instruction_slots': sum(s['instruction_slots'] for s in verified.values()),
        'sections': verified,
        'semantic_decode_verified': False,
        'function_boundaries_verified': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('binary', type=Path)
    parser.add_argument('listing', type=Path)
    args = parser.parse_args()
    binary, listing = args.binary.read_bytes(), args.listing.read_bytes()
    result = verify_listing(binary, listing.decode('utf-8'))
    result.update(binary_sha256=hashlib.sha256(binary).hexdigest(),
                  listing_sha256=hashlib.sha256(listing).hexdigest())
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

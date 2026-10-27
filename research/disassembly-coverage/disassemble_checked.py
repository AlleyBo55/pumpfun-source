#!/usr/bin/env python3
"""Generate byte-checked analyst disassembly, never a rebuilt executable.

Byte-checked successor to the digest-pinned scripts/disassemble.py, which stays
unchanged because saved checkpoints and the P27 guard bind its hash.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_disassembly import verify_listing


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--objdump', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.objdump = args.objdump.resolve()
    # Freeze originals before LLVM runs; recheck the tool and inputs afterwards.
    programs = json.loads((ROOT / 'repro/programs.json').read_text())
    if not programs:
        raise ValueError('Program list is empty')
    inputs = {name: (ROOT / f'evidence/original/{name}/deployed.so').read_bytes()
              for name in programs}
    tool_hash = sha(args.objdump.read_bytes())
    version = subprocess.check_output([str(args.objdump), '--version'], text=True)
    args.output.mkdir(parents=True, exist_ok=False)
    manifest = {'tool_sha256': tool_hash, 'version': version, 'outputs': {}}
    for name, binary in inputs.items():
        path = ROOT / f'evidence/original/{name}/deployed.so'
        target = args.output / f'{name}.asm'
        with target.open('xb') as out:
            subprocess.run([str(args.objdump), '-d', str(path.relative_to(ROOT))],
                           cwd=ROOT, stdout=out, check=True)
        listing = target.read_bytes()
        coverage = verify_listing(binary, listing.decode('utf-8'))
        manifest['outputs'][name] = {'input_sha256': sha(binary),
                                     'output_sha256': sha(listing),
                                     'listing_validation': coverage}
    if sha(args.objdump.read_bytes()) != tool_hash:
        raise ValueError('Disassembler changed during capture')
    for name, binary in inputs.items():
        path = ROOT / f'evidence/original/{name}/deployed.so'
        if sha(path.read_bytes()) != sha(binary):
            raise ValueError(f'Original changed during disassembly: {name}')
    manifest['inputs_unchanged'] = True
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()

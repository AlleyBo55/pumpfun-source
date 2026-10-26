#!/usr/bin/env python3
"""Run the unchanged ATA proof with hash-checked published external receipts."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[3]
WRAPPER = 'repro/ata/portable-monomorph-proof/verify_ata_monomorph_order.py'
PROOF = 'repro/ata/monomorph-order-proof'
MANIFEST_SHA256 = '5808bb8fae39ea750f33119b31f8856e91a5c0640cc68a8c0292609378e6cb08'
RETIRED_VERSION = 'work/ata-toolchain-audit/official/version.md'
PUBLISHED_VERSION = 'repro/identity-audit/2026-10-25/ata/official/version.md'
VERSION_RECEIPT = {
    'bytes': 247,
    'sha256': '390cb9c02aa9dc28dfbee87f923dc1e0db31d1f41546fe49111d790ef208a2d3',
}


def read_regular(root, name):
    relative = PurePosixPath(name)
    if relative.is_absolute() or '..' in relative.parts or not relative.parts:
        raise ValueError('unsafe receipt path: ' + name)
    path = root
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError('symlink receipt path: ' + name)
    if not path.is_file():
        raise ValueError('missing regular receipt: ' + name)
    return path.read_bytes()


def checked_bytes(root, name, expected):
    data = read_regular(root, name)
    if (len(data) != expected['bytes'] or
            hashlib.sha256(data).hexdigest() != expected['sha256']):
        raise ValueError('receipt hash/length mismatch: ' + name)
    return data


def verify(root):
    root = root.resolve(strict=True)
    proof = root / PROOF
    manifest_bytes = read_regular(root, PROOF + '/manifest.json')
    if hashlib.sha256(manifest_bytes).hexdigest() != MANIFEST_SHA256:
        raise ValueError('published proof manifest hash mismatch')
    manifest = json.loads(manifest_bytes)
    for name, expected in manifest.items():
        checked_bytes(root, PROOF + '/' + name, expected)
    references = json.loads(read_regular(root, PROOF + '/external-inputs.json'))
    if references.get(RETIRED_VERSION) != VERSION_RECEIPT:
        raise ValueError('retired version receipt differs from the published alias binding')

    # Recreate only the proof's five external reference paths in a private,
    # temporary root. The original proof and all its manifests stay unchanged.
    with tempfile.TemporaryDirectory(prefix='ata-proof-receipts-') as directory:
        overlay = Path(directory)
        for original, expected in references.items():
            published = PUBLISHED_VERSION if original == RETIRED_VERSION else original
            data = checked_bytes(root, published, expected)
            destination = overlay / original
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        result = subprocess.run(
            [sys.executable, '-B', str(proof / 'verify.py'),
             '--repository-root', str(overlay)],
            cwd=overlay,
            check=False,
        )
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository-root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        return verify(args.repository_root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, 'ATA proof verification failed: ' + str(error) + '\n')


if __name__ == '__main__':
    sys.exit(main())

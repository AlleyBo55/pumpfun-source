"""Exercise the published proof through a minimal relocated checkout."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from verify_ata_monomorph_order import (
    PROOF, PUBLISHED_VERSION, RETIRED_VERSION, ROOT, WRAPPER, read_regular,
)


class PortableAtaProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_temp = tempfile.TemporaryDirectory(prefix='ata-proof-fixture-')
        cls.base = Path(cls.base_temp.name)
        shutil.copytree(ROOT / PROOF, cls.base / PROOF)
        references = json.loads((ROOT / PROOF / 'external-inputs.json').read_text())
        for name in references:
            published = PUBLISHED_VERSION if name == RETIRED_VERSION else name
            destination = cls.base / published
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / published, destination)

    @classmethod
    def tearDownClass(cls):
        cls.base_temp.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ata-proof-relocated-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'checkout'
        shutil.copytree(self.base, self.root)

    def run_wrapper(self):
        return subprocess.run(
            [sys.executable, '-B', str(ROOT / WRAPPER),
             '--repository-root', str(self.root)],
            cwd=self.temp.name, text=True, capture_output=True, check=False,
        )

    def test_relocated_minimal_checkout_checks_every_external_receipt(self):
        self.assertFalse((self.root / RETIRED_VERSION).exists())
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('external receipts verified', result.stdout)

    def test_corrupt_published_version_is_rejected(self):
        path = self.root / PUBLISHED_VERSION
        data = bytearray(path.read_bytes())
        data[0] ^= 1
        path.write_bytes(data)
        result = self.run_wrapper()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('receipt hash/length mismatch: ' + PUBLISHED_VERSION, result.stderr)

    def test_retired_work_file_cannot_replace_missing_published_receipt(self):
        retired = self.root / RETIRED_VERSION
        retired.parent.mkdir(parents=True)
        (self.root / PUBLISHED_VERSION).rename(retired)
        result = self.run_wrapper()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('missing regular receipt: ' + PUBLISHED_VERSION, result.stderr)

    def test_other_external_receipts_still_require_exact_hashes(self):
        references = json.loads((self.root / PROOF / 'external-inputs.json').read_text())
        name = next(name for name in references if name != RETIRED_VERSION)
        (self.root / name).write_bytes(b'wrong receipt')
        result = self.run_wrapper()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('receipt hash/length mismatch: ' + name, result.stderr)

    def test_symlink_receipt_is_rejected_even_with_correct_bytes(self):
        path = self.root / PUBLISHED_VERSION
        external = Path(self.temp.name) / 'version.md'
        path.rename(external)
        path.symlink_to(external)
        result = self.run_wrapper()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('symlink receipt path: ' + PUBLISHED_VERSION, result.stderr)

    def test_symlink_parent_is_rejected(self):
        parent = (self.root / PUBLISHED_VERSION).parent
        external = Path(self.temp.name) / 'official'
        parent.rename(external)
        parent.symlink_to(external, target_is_directory=True)
        result = self.run_wrapper()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('symlink receipt path: ' + PUBLISHED_VERSION, result.stderr)

    def test_tampered_proof_script_is_rejected_before_execution(self):
        (self.root / PROOF / 'verify.py').write_text("print('untrusted code ran')\n")
        result = self.run_wrapper()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('untrusted code ran', result.stdout)
        self.assertIn('receipt hash/length mismatch: ' + PROOF + '/verify.py', result.stderr)

    def test_script_and_manifest_cannot_be_resealed_together(self):
        data = b"print('untrusted code ran')\n"
        (self.root / PROOF / 'verify.py').write_bytes(data)
        path = self.root / PROOF / 'manifest.json'
        manifest = json.loads(path.read_text())
        manifest['verify.py'] = {
            'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
        }
        path.write_text(json.dumps(manifest))
        result = self.run_wrapper()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('untrusted code ran', result.stdout)
        self.assertIn('published proof manifest hash mismatch', result.stderr)

    def test_receipt_path_cannot_escape_selected_root(self):
        outside = Path(self.temp.name) / 'outside.txt'
        outside.write_text('outside the checkout')
        for name in ('../outside.txt', str(outside)):
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, 'unsafe receipt path'):
                    read_regular(self.root, name)


if __name__ == '__main__':
    unittest.main()

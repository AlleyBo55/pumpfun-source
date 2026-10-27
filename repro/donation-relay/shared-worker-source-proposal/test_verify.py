#!/usr/bin/env python3
"""Source-only controls; no compiler, ELF input or replay receipt is used."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('worker_source_tests', HERE / 'verify.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline, cls.recovered = V.sources()

    def test_integrity(self):
        V.check_manifest()
        self.assertEqual(V.validate_sources(self.baseline, self.recovered), ['src/shared_donation.rs'])

    def test_source_loading_never_reads_program_elf_or_replay(self):
        original = Path.read_bytes
        observed = []
        def guarded(path):
            name = str(path)
            self.assertFalse(name.endswith(('.so', '.so.gz')))
            self.assertNotIn('fresh-runtime', name)
            self.assertNotIn('fresh-replay', name)
            observed.append(name)
            return original(path)
        with patch.object(Path, 'read_bytes', guarded):
            baseline, recovered = V.sources()
        self.assertEqual(len(baseline), 56)
        self.assertEqual(len(recovered), 56)
        self.assertTrue(observed)

    def test_changed_override_rejected(self):
        bad = dict(self.recovered)
        bad['src/shared_donation.rs'] += b'\n// unreviewed\n'
        with self.assertRaises(AssertionError):
            V.validate_sources(self.baseline, bad)

    def test_unrelated_change_rejected(self):
        bad = dict(self.recovered)
        bad['src/lib.rs'] += b'\n'
        with self.assertRaises(AssertionError):
            V.validate_sources(self.baseline, bad)

    def test_extra_input_rejected(self):
        bad = dict(self.recovered)
        bad['extra.rs'] = b'fn extra() {}'
        with self.assertRaises(AssertionError):
            V.validate_sources(self.baseline, bad)

    def test_unsafe_source_names_rejected(self):
        for name in ['', '../escape', '/absolute', 'a/../b', 'a//b']:
            with self.subTest(name=name), self.assertRaises(AssertionError):
                V.safe_name(name)

    def test_source_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'real').write_text('not source')
            (root / 'link').symlink_to(root / 'real')
            with self.assertRaises(AssertionError):
                V.safe_file(root, 'link')

    def test_materialized_source_is_exact(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / 'new'
            V.materialize(destination, self.recovered)
            files = {str(p.relative_to(destination)): p.read_bytes()
                     for p in destination.rglob('*') if p.is_file()}
            self.assertEqual(files, self.recovered)
            with self.assertRaises(AssertionError):
                V.materialize(destination, self.recovered)


if __name__ == '__main__':
    unittest.main()

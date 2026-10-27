"""Synthetic shell admission tests: sentinel replaces compiler; no ELF/native VM."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('build_prefix.sh').resolve()

class BuildPathTests(unittest.TestCase):
    def fixture(self, root):
        source = root / 'repo/programs/pump'
        source.mkdir(parents=True)
        (source / 'Cargo.toml').write_text('[package]\nname="synthetic"\nversion="0.0.0"\n[workspace]\n')
        (source / 'Cargo.lock').write_text('# SYNTHETIC INPUT ONLY\n')
        tools = root / 'tools'
        tools.mkdir()
        sentinel = tools / 'cargo-build-sbf'
        sentinel.write_text('#!/bin/sh\nprintf "%s\\n" "$CARGO_TARGET_DIR" > "$SYNTHETIC_TARGET_RECORD"\nexit 73\n')
        sentinel.chmod(0o755)
        # The helper targets GNU sed. This path-only fixture does not test
        # source rewriting and must also run on hosts with BSD sed.
        sed = tools / 'sed'
        sed.write_text('#!/bin/sh\nexit 0\n')
        sed.chmod(0o755)
        return dict(os.environ, PATH=str(tools) + os.pathsep + os.environ['PATH'],
                    SYNTHETIC_TARGET_RECORD=str(root / 'sentinel.txt'))

    def run_script(self, root, env):
        return subprocess.run(['bash', str(SCRIPT), 'repo', 'out'], cwd=root,
                              env=env, capture_output=True, text=True)

    def test_relative_target_is_absolute_before_workspace_change(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t).resolve()
            env = self.fixture(root)
            env['CARGO_TARGET_DIR'] = 'target'
            result = self.run_script(root, env)
            self.assertEqual(result.returncode, 73, result.stderr)
            self.assertEqual((root / 'sentinel.txt').read_text().strip(), str(root / 'target'))
            self.assertTrue((root / 'target').is_dir())

    def test_default_target_is_under_fresh_absolute_output(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t).resolve()
            env = self.fixture(root)
            env.pop('CARGO_TARGET_DIR', None)
            result = self.run_script(root, env)
            self.assertEqual(result.returncode, 73, result.stderr)
            self.assertEqual((root / 'sentinel.txt').read_text().strip(), str(root / 'out/target'))

    def test_existing_target_preserved_before_compiler(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t).resolve()
            env = self.fixture(root)
            target = root / 'target'
            target.mkdir()
            (target / 'prior').write_text('PRESERVE')
            env['CARGO_TARGET_DIR'] = 'target'
            result = self.run_script(root, env)
            self.assertEqual(result.returncode, 2)
            self.assertIn('Target already exists', result.stderr)
            self.assertEqual((target / 'prior').read_text(), 'PRESERVE')
            self.assertFalse((root / 'sentinel.txt').exists())
            self.assertFalse((root / 'out').exists())

    def test_dangling_target_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t).resolve()
            env = self.fixture(root)
            (root / 'target').symlink_to(root / 'missing')
            env['CARGO_TARGET_DIR'] = 'target'
            result = self.run_script(root, env)
            self.assertEqual(result.returncode, 2)
            self.assertTrue((root / 'target').is_symlink())
            self.assertFalse((root / 'sentinel.txt').exists())

    def test_target_cannot_alias_output(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t).resolve()
            env = self.fixture(root)
            env['CARGO_TARGET_DIR'] = './out'
            result = self.run_script(root, env)
            self.assertEqual(result.returncode, 2)
            self.assertIn('distinct', result.stderr)
            self.assertFalse((root / 'sentinel.txt').exists())

if __name__ == '__main__':
    unittest.main()

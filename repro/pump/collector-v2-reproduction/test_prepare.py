"""Preparation safety checks use only temporary synthetic inputs."""
import hashlib
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import prepare


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='collector-prepare-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def archive(self, members):
        path = self.root / 'fixture.tar'
        with tarfile.open(path, 'w') as stream:
            for name, data, kind in members:
                member = tarfile.TarInfo(name)
                member.mode = 0o644
                if kind == 'symlink':
                    member.type = tarfile.SYMTYPE
                    member.linkname = data
                    stream.addfile(member)
                else:
                    member.size = len(data)
                    stream.addfile(member, io.BytesIO(data))
        return path

    def test_tampered_cached_asset_rejected_without_network(self):
        cache = self.root / 'cache'
        cache.mkdir()
        (cache / 'asset').write_bytes(b'wrong')
        downloads = self.root / 'downloads'
        downloads.mkdir()
        expected = hashlib.sha256(b'right').hexdigest()
        with patch('prepare.urllib.request.urlopen') as network:
            with self.assertRaisesRegex(ValueError, 'altered input'):
                prepare.acquire('asset', ('https://example.invalid/asset', 5, expected), downloads, cache)
        network.assert_not_called()
        self.assertFalse((downloads / 'asset').exists())

    def test_escaping_member_rejected(self):
        archive = self.archive([('../outside', b'bad', 'file')])
        with self.assertRaisesRegex(ValueError, 'unsafe archive path'):
            prepare.safe_extract(archive, self.root / 'extract')
        self.assertFalse((self.root / 'outside').exists())

    def test_escaping_symlink_rejected(self):
        archive = self.archive([('escape', '../../outside', 'symlink')])
        with self.assertRaises(tarfile.FilterError):
            prepare.safe_extract(archive, self.root / 'extract')

    def test_internal_symlink_preserved(self):
        archive = self.archive([('bin/tool', b'compiler', 'file'), ('bin/alias', 'tool', 'symlink')])
        destination = self.root / 'extract'
        prepare.safe_extract(archive, destination)
        self.assertTrue((destination / 'bin/alias').is_symlink())
        self.assertEqual((destination / 'bin/alias').read_bytes(), b'compiler')

    def test_sdk_script_mode_restored_without_changing_bytes(self):
        data = b'#!/bin/sh\nexit 0\n'
        archive = self.archive([('scripts/strip.sh', data, 'file')])
        official = self.root / 'official'
        (official / 'scripts').mkdir(parents=True)
        (official / 'scripts/strip.sh').write_bytes(data)
        (official / 'scripts/strip.sh').chmod(0o755)
        retained = self.root / 'sdk'
        result = prepare.restore_sdk(official, retained, archive,
                                     {'scripts/strip.sh': hashlib.sha256(data).hexdigest()})
        self.assertEqual((retained / 'scripts/strip.sh').stat().st_mode & 0o777, 0o755)
        self.assertEqual((retained / 'scripts/strip.sh').read_bytes(), data)
        self.assertEqual(result['scripts/strip.sh'], {'before': '0o644', 'after': '0o755'})

    def test_private_cargo_rustc_and_rustdoc_proxies(self):
        source = self.root / 'rustup-init'
        source.write_bytes(b'fake rustup is never executed')
        launch = self.root / 'launch'
        prepare.private_proxies(launch, source)
        for name in ('cargo', 'rustc', 'rustdoc'):
            self.assertTrue((launch / name).is_symlink())
            self.assertEqual((launch / name).resolve(), (launch / 'rustup').resolve())
        self.assertEqual((launch / 'rustup').stat().st_mode & 0o777, 0o755)

    def test_existing_cache_link_is_never_repointed(self):
        old = self.root / 'old'
        old.mkdir()
        new = self.root / 'new'
        new.mkdir()
        cache = self.root / 'cache/platform-tools'
        cache.parent.mkdir()
        cache.symlink_to(old, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'points elsewhere'):
            prepare.ensure_cache_link(cache, new)
        self.assertEqual(cache.resolve(), old.resolve())

    def test_equivalent_existing_compiler_is_reused_without_repointing(self):
        old = self.root / 'old'
        old.mkdir()
        (old / 'compiler').write_bytes(b'pinned compiler')
        new = self.root / 'new'
        new.mkdir()
        cache = self.root / 'cache'
        cache.symlink_to(old, target_is_directory=True)
        inventory = {'compiler': {'type': 'regular', 'sha256': hashlib.sha256(b'pinned compiler').hexdigest()}}
        self.assertFalse(prepare.ensure_cache_link(cache, new, inventory))
        self.assertEqual(cache.resolve(), old.resolve())

    def test_changed_existing_compiler_is_rejected(self):
        old = self.root / 'old'
        old.mkdir()
        (old / 'compiler').write_bytes(b'wrong compiler')
        cache = self.root / 'cache'
        cache.symlink_to(old, target_is_directory=True)
        inventory = {'compiler': {'type': 'regular', 'sha256': hashlib.sha256(b'pinned compiler').hexdigest()}}
        with self.assertRaisesRegex(ValueError, 'altered input'):
            prepare.ensure_cache_link(cache, self.root / 'new', inventory)
        self.assertEqual(cache.resolve(), old.resolve())

    def test_extra_existing_compiler_file_is_rejected(self):
        old = self.root / 'old'
        old.mkdir()
        (old / 'compiler').write_bytes(b'pinned compiler')
        (old / 'unexpected').write_bytes(b'extra file')
        cache = self.root / 'cache'
        cache.symlink_to(old, target_is_directory=True)
        inventory = {'compiler': {'type': 'regular', 'sha256': hashlib.sha256(b'pinned compiler').hexdigest()}}
        with self.assertRaisesRegex(ValueError, 'membership mismatch'):
            prepare.ensure_cache_link(cache, self.root / 'new', inventory)
        self.assertEqual(cache.resolve(), old.resolve())

    def compiler_with_link(self, target='lld'):
        compiler = self.root / 'compiler-tree'
        (compiler / 'llvm/bin').mkdir(parents=True)
        (compiler / 'llvm/bin/lld').write_bytes(b'pinned linker')
        (compiler / 'llvm/bin/ld.lld').symlink_to(target)
        inventory = {
            'llvm/bin/lld': {'type': 'regular', 'sha256': hashlib.sha256(b'pinned linker').hexdigest()},
            'llvm/bin/ld.lld': {'type': 'symlink', 'target': 'lld'},
        }
        return compiler, inventory

    def test_pinned_linker_symlink_passes(self):
        compiler, inventory = self.compiler_with_link()
        self.assertEqual(prepare.verify_compiler_tree(compiler, inventory), 1)

    def test_existing_cache_with_redirected_linker_is_rejected(self):
        outside = self.root / 'outside'
        outside.write_bytes(b'pinned linker')
        compiler, inventory = self.compiler_with_link('../../../outside')
        cache = self.root / 'cache'
        cache.symlink_to(compiler, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink target mismatch'):
            prepare.ensure_cache_link(cache, self.root / 'new', inventory)
        self.assertEqual((compiler / 'llvm/bin/ld.lld').readlink(), Path('../../../outside'))
        self.assertEqual(cache.resolve(), compiler.resolve())

    def test_unexpected_compiler_symlink_is_rejected(self):
        compiler, inventory = self.compiler_with_link()
        (compiler / 'extra-link').symlink_to('llvm/bin/lld')
        with self.assertRaisesRegex(ValueError, 'membership mismatch'):
            prepare.verify_compiler_tree(compiler, inventory)

    def test_recorded_inside_tree_dangling_link_passes(self):
        compiler, inventory = self.compiler_with_link()
        link = compiler / 'llvm/lib/python3.13/site-packages/lldb/lldb-argdumper'
        link.parent.mkdir(parents=True)
        target = '../../../../bin/lldb-argdumper'
        link.symlink_to(target)
        inventory[str(link.relative_to(compiler))] = {'type': 'symlink', 'target': target}
        self.assertFalse(link.exists())
        self.assertEqual(prepare.verify_compiler_tree(compiler, inventory), 1)

    def test_exact_target_must_still_resolve_inside_tree(self):
        compiler, inventory = self.compiler_with_link('../../../outside')
        inventory['llvm/bin/ld.lld']['target'] = '../../../outside'
        with self.assertRaisesRegex(ValueError, 'resolves outside tree'):
            prepare.verify_compiler_tree(compiler, inventory)

    def test_symlink_cannot_replace_regular_compiler_file(self):
        compiler, inventory = self.compiler_with_link()
        (compiler / 'llvm/bin/lld').unlink()
        outside = self.root / 'outside'
        outside.write_bytes(b'pinned linker')
        (compiler / 'llvm/bin/lld').symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'membership mismatch'):
            prepare.verify_compiler_tree(compiler, inventory)

    def test_failed_native_preparation_retains_logs(self):
        with patch('prepare.subprocess.run') as run:
            run.return_value.returncode = 7
            with self.assertRaisesRegex(ValueError, 'failed; retained'):
                prepare.run(['never-run'], {}, self.root, self.root, 'fetch')
        self.assertTrue((self.root / 'fetch.stdout').is_file())
        self.assertIn('"returncode": 7', (self.root / 'fetch.json').read_text())


if __name__ == '__main__':
    unittest.main()

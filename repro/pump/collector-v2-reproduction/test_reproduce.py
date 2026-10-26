import json
from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest

import reproduce as r


class ReproductionGates(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='collector-reproduction-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def fixture_outputs(self):
        for role, (relative, _, _) in r.EXPECTED.items():
            source = r.ROOT / r.PACKAGE / 'artifacts' / ('candidate.so' if role == 'executable' else 'unstripped.so')
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, path)
        (self.root / 'build.log').write_text('Finished release profile\n')

    def test_sealed_source_and_helpers(self):
        source, helpers = r.source_inputs()
        self.assertEqual(len(source), 37)
        self.assertEqual(len(helpers), 4)

    def test_altered_source_is_rejected(self):
        source = r.ROOT / r.PACKAGE
        target = self.root / r.PACKAGE
        for name in ('manifest.json', 'build-input-source37.json', 'build-plan/availability.json', 'build-plan/future-plan.json'):
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / name, path)
        shutil.copytree(source / 'build-input-source', target / 'build-input-source')
        (target / 'build-input-source/programs/pump/src/admin_cto.rs').write_text('modified source')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            r.source_inputs(self.root)

    def test_altered_tool_is_rejected(self):
        path = self.root / 'tool'
        path.write_bytes(b'changed executable')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            r.checked(path, r.CLI)

    def test_linker_symlink_is_authenticated(self):
        binary = self.root / 'lld'
        binary.write_bytes(b'pinned linker')
        link = self.root / 'ld.lld'
        link.symlink_to('lld')
        inventory = {'lld': {'type': 'regular', 'sha256': r.sha(binary)},
                     'ld.lld': {'type': 'symlink', 'target': 'lld'}}
        self.assertEqual(r.compiler_tree(self.root, inventory)['symlinks'], 1)
        link.unlink()
        link.symlink_to('/different/linker')
        with self.assertRaisesRegex(ValueError, 'symlink target differs'):
            r.compiler_tree(self.root, inventory)

    def test_extra_compiler_symlink_is_rejected(self):
        (self.root / 'unexpected-link').symlink_to('/outside')
        with self.assertRaisesRegex(ValueError, 'membership differs'):
            r.compiler_tree(self.root, {})

    def test_recorded_dangling_debugger_link_is_allowed_inside_tree(self):
        (self.root / 'lldb-utility').symlink_to('missing-debugger-utility')
        result = r.compiler_tree(self.root, {'lldb-utility': {'type': 'symlink', 'target': 'missing-debugger-utility'}})
        self.assertEqual(result['symlinks'], 1)

    def test_private_host_selection_is_exact(self):
        seed = self.root / 'seed'
        toolchains = seed / 'toolchains'
        toolchains.mkdir(parents=True)
        correct = toolchains / '1.94.0-aarch64-apple-darwin'
        correct.mkdir()
        stable = toolchains / 'stable-aarch64-apple-darwin'
        stable.symlink_to(correct)
        settings = seed / 'settings.toml'
        settings.write_text('version="12"\ndefault_toolchain="stable-aarch64-apple-darwin"\nprofile="minimal"\n')
        r.host_selection(seed)
        settings.write_text(settings.read_text() + '[overrides]\n"/workspace"="nightly"\n')
        with self.assertRaisesRegex(ValueError, 'settings'):
            r.host_selection(seed)
        settings.write_text('version="12"\ndefault_toolchain="stable-aarch64-apple-darwin"\nprofile="minimal"\n')
        stable.unlink()
        stable.symlink_to(toolchains / 'other')
        with self.assertRaisesRegex(ValueError, 'alias differs'):
            r.host_selection(seed)

    def test_ancestor_toolchain_selector_is_rejected(self):
        for name in ('rust-toolchain', 'rust-toolchain.toml'):
            selector = self.root / name
            selector.write_text('unrecorded toolchain')
            with self.assertRaisesRegex(ValueError, 'unrecorded selector'):
                r.reject_selectors((self.root / 'workspace',))
            selector.unlink()

    def test_sdk_archive_requires_restored_executable_modes(self):
        archive = r.ROOT / 'repro/pump_fees/linux-darwin-v144-attribution/inputs/recorded-sdk-sbf-sdk-snapshot.tar.gz'
        with tarfile.open(archive) as stream:
            stream.extractall(self.root, filter='data')
        expected = json.loads((r.ROOT / r.PACKAGE / 'build-plan/availability.json').read_text())['sdk_source_sha256']
        with self.assertRaisesRegex(ValueError, 'not executable'):
            r.sdk_inputs(self.root, expected)
        for name in expected:
            if name.startswith('scripts/') and name.endswith('.sh'):
                (self.root / name).chmod(0o755)
        self.assertEqual(r.sdk_inputs(self.root, expected), 53)
        (self.root / 'scripts/strip.sh').write_text('different strip command')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            r.sdk_inputs(self.root, expected)

    def test_whole_tested_fixtures_pass_comparison_gate(self):
        self.fixture_outputs()
        result = r.outputs(self.root, 0)
        self.assertTrue(all(v['whole_file_equal'] for v in result.values()))

    def test_failed_compile_never_accepts_even_matching_files(self):
        self.fixture_outputs()
        with self.assertRaisesRegex(ValueError, 'build failed'):
            r.outputs(self.root, 1)

    def test_missing_symbols_is_rejected(self):
        self.fixture_outputs()
        (self.root / r.EXPECTED['unstripped'][0]).unlink()
        with self.assertRaisesRegex(ValueError, 'missing file'):
            r.outputs(self.root, 0)

    def test_changed_output_is_rejected(self):
        self.fixture_outputs()
        path = self.root / r.EXPECTED['executable'][0]
        with path.open('r+b') as stream:
            stream.seek(100)
            stream.write(b'bad')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            r.outputs(self.root, 0)

    def test_backend_error_rejects_matching_output(self):
        self.fixture_outputs()
        (self.root / 'build.log').write_text('Error: Function example Stack offset exceeded\n')
        with self.assertRaisesRegex(ValueError, 'backend errors'):
            r.outputs(self.root, 0)


if __name__ == '__main__':
    unittest.main()

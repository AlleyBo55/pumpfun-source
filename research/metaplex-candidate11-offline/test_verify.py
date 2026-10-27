import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

import verify


class RetainedEvidenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.package = Path(temporary.name) / 'isolated'
        self.package.mkdir()
        for name in ('rebuild.py', 'verify.py', 'receipts.json.gz', 'upstream-source.tar.gz',
                     '40337545179.zip', '40337930953.zip', '40338395968.zip'):
            shutil.copyfile(verify.PACKAGE / name, self.package / name)

    def observation(self):
        with zipfile.ZipFile(self.package / '40338395968.zip') as archive:
            members = {name: archive.read(name) for name in archive.namelist()}
        source = verify.rebuild.source_members(self.package / 'upstream-source.tar.gz',
                                              json.loads(members['upstream-source-manifest.json']))
        return members, json.loads(members['observation.json']), source

    def test_minimal_relocated_replay(self):
        result = subprocess.run([sys.executable, '-B', str(self.package / 'verify.py')],
                                cwd=self.package, capture_output=True, check=True)
        findings = json.loads(result.stdout)
        self.assertTrue(findings['raw_candidate11_equal'])
        self.assertEqual(findings['source_files'], 812)
        self.assertEqual(findings['locked_registry_archives'], 537)
        self.assertTrue(findings['sdk_auxiliary_download_failure_retained'])
        self.assertFalse(findings['deployed_identity_claimed'])

    def test_changed_archives_source_receipts_and_observer_rejected(self):
        for name in ('40337545179.zip', '40337930953.zip', '40338395968.zip',
                     'upstream-source.tar.gz', 'rebuild.py', 'receipts.json.gz'):
            path = self.package / name
            original = path.read_bytes()
            if name.endswith('.gz'):
                import gzip
                path.write_bytes(gzip.compress(gzip.decompress(original) + b' ', mtime=0))
            else:
                path.write_bytes(original + b' ')
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'differs|Changed evidence'):
                verify.verify(self.package)
            path.write_bytes(original)

    def test_padded_raw_artifact_cannot_pass(self):
        members, state, source = self.observation()
        members['token_metadata.so'] += b'\0'
        with self.assertRaisesRegex(ValueError, 'Raw candidate11 gate differs'):
            verify.derive(members, state, source)

    def test_network_change_cannot_pass(self):
        members, state, source = self.observation()
        row, = [row for row in state['commands'] if row['label'] == 'start-offline-build-container']
        row['command'][row['command'].index('--network') + 1] = 'bridge'
        with self.assertRaisesRegex(ValueError, 'Build networking differs'):
            verify.derive(members, state, source)

    def test_candidate_match_cannot_be_promoted_to_deployed_identity(self):
        members, state, source = self.observation()
        state['raw']['deployed_identity_claimed'] = True
        members['raw-result.json'] = json.dumps(state['raw']).encode()
        with self.assertRaisesRegex(ValueError, 'Raw identity scope differs'):
            verify.derive(members, state, source)

    def test_sdk_failure_cannot_be_removed_from_summary(self):
        members, state, source = self.observation()
        members['build-candidate11.stderr.log'] = b'Finished release\n'
        with self.assertRaisesRegex(ValueError, 'auxiliary-download failure differs'):
            verify.derive(members, state, source)


if __name__ == '__main__':
    unittest.main()

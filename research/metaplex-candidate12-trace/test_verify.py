"""Reject false raw identity, branch attribution and cross-run comparisons."""
import copy
import gzip
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import analyze
import compare
import verify


class ContrastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = Path(__file__).resolve().parent
        cls.receipt = json.loads(gzip.decompress((cls.package / 'receipt.json.gz').read_bytes()))
        cls.members, cls.state = verify.artifact(cls.package, cls.receipt)
        cls.log = cls.members['build-candidate12-traced.stderr.log']
        cls.raw = cls.members['token_metadata.so']
        cls.parts = analyze.snapshots(cls.log)
        cls.sources = verify.rebuild.source_members(cls.package / 'upstream-source.tar.gz',
            json.loads(cls.members['upstream-source-manifest.json']))
        root = cls.package / 'reference'
        receipt = json.loads(gzip.decompress((root / 'receipt.json.gz').read_bytes()))
        cls.reference, _ = verify.artifact(root, receipt, runs={compare.REFERENCE_RUN:
            (compare.REFERENCE_HEAD, 'success', compare.REFERENCE_ZIP)})

    def test_retained_package(self):
        result = verify.verify(self.package)
        self.assertEqual(result['snapshots'], 8)
        self.assertTrue(result['raw_candidate12_equal'])
        self.assertTrue(result['comparison']['non_diagnostic_compiler_arguments_equal'])

    def test_changed_or_padded_raw_is_rejected(self):
        for raw in (self.raw[:-1] + bytes([self.raw[-1] ^ 1]), self.raw + b'\0'):
            with self.subTest(bytes=len(raw)), self.assertRaisesRegex(ValueError, 'Raw candidate12 gate'):
                analyze.derive(self.log, raw)

    def test_complemented_machine_condition_is_rejected(self):
        text = self.parts[3][1].decode().replace('JUGT_rr %47:gpr, %22:gpr', 'JUGE_rr %47:gpr, %22:gpr')
        with self.assertRaisesRegex(ValueError, 'Expected one unsigned'):
            analyze.machine_guard(text, virtual=True)

    def test_error_edge_cannot_be_relabelled_success(self):
        text = self.parts[5][1].decode().replace('JUGT_rr $r9, $r7, %bb.34', 'JUGT_rr $r9, $r7, %bb.37')
        with self.assertRaisesRegex(ValueError, 'error 86'):
            analyze.machine_guard(text, virtual=False)

    def test_required_success_jump_cannot_be_dropped(self):
        text = self.parts[6][1].decode().replace('  JMP %bb.39\n', '', 1)
        with self.assertRaisesRegex(ValueError, 'success jump'):
            analyze.machine_guard(text, virtual=False)

    def test_total_load_cannot_be_substituted_for_remaining(self):
        text = self.parts[5][1].decode().replace('from %ir.236)', 'from %ir.227)')
        with self.assertRaisesRegex(ValueError, 'Remaining-use load'):
            analyze.machine_guard(text, virtual=False)

    def test_missing_stage_is_rejected(self):
        log = self.log.replace(analyze.STAGES[3][1].encode(), b'changed stage', 1)
        with self.assertRaisesRegex(ValueError, 'compiler stage'):
            analyze.snapshots(log)

    def test_wrong_final_ir_error_target_is_rejected(self):
        log = self.log.replace(b'br i1 %238, label %248, label %243',
                               b'br i1 %238, label %239, label %243')
        with self.assertRaisesRegex(ValueError, 'data/control-flow'):
            analyze.derive(log, self.raw)

    def test_network_enabled_compilation_is_rejected(self):
        state = copy.deepcopy(self.state)
        start = next(row['command'] for row in state['commands'] if row['label'] == 'start-offline-build-container')
        start[start.index('--network')+1] = 'bridge'
        with self.assertRaisesRegex(ValueError, 'Build networking'):
            verify.derive(self.members, state, self.sources)

    def test_padded_deployment_claim_is_rejected(self):
        state = copy.deepcopy(self.state)
        state['raw']['deployed_identity_claimed'] = True
        members = dict(self.members, **{'raw-result.json': json.dumps(state['raw']).encode()})
        with self.assertRaisesRegex(ValueError, 'Raw identity scope'):
            verify.derive(members, state, self.sources)

    def test_changed_reference_raw_output_is_rejected(self):
        reference = dict(self.reference, **{'token_metadata.so': self.raw})
        with self.assertRaisesRegex(ValueError, 'Reference raw'):
            compare.derive(self.members, reference)

    def test_extra_source_change_is_rejected(self):
        manifest = json.loads(self.members['source-manifest.json'])
        manifest['programs/token-metadata/Cargo.lock'] = '0' * 64
        members = dict(self.members, **{'source-manifest.json': json.dumps(manifest).encode()})
        with self.assertRaisesRegex(ValueError, 'changes more than'):
            compare.derive(members, self.reference)

    def test_non_diagnostic_argument_change_is_rejected(self):
        members = dict(self.members)
        members['rustc-4272.argv'] = members['rustc-4272.argv'].replace(b'opt-level=z', b'opt-level=z\0-Cdebuginfo=1')
        with self.assertRaisesRegex(ValueError, 'Non-diagnostic compiler arguments'):
            compare.derive(members, self.reference)

    def test_altered_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw = (self.package / '40352331268.zip').read_bytes()
            (root / '40352331268.zip').write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
            with self.assertRaisesRegex(ValueError, 'Changed evidence: artifact ZIP'):
                verify.artifact(root, self.receipt)

    def test_altered_snapshot_is_rejected_in_relocated_package(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'package'
            shutil.copytree(self.package, root)
            self.assertTrue(verify.verify(root)['raw_candidate12_equal'])
            path = root / 'snapshots/after-block-placement.txt'
            path.write_bytes(path.read_bytes().replace(b'JUGT_rr $r9, $r7', b'JUGE_rr $r9, $r7'))
            with self.assertRaisesRegex(ValueError, 'Saved snapshot differs'):
                verify.verify(root)


if __name__ == '__main__':
    unittest.main()

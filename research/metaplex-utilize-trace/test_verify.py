"""Reject broken attribution, scope and retained-evidence bindings offline."""
import copy
import gzip
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import analyze
import verify


class TraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = Path(__file__).resolve().parent
        cls.receipt = json.loads(gzip.decompress((cls.package / 'receipt.json.gz').read_bytes()))
        cls.members, cls.state = verify.artifact(cls.package, cls.receipt)
        cls.log = cls.members['build-candidate11-traced.stderr.log']
        cls.raw = cls.members['token_metadata.so']
        cls.parts = analyze.snapshots(cls.log)
        cls.sources = verify.rebuild.source_members(cls.package / 'upstream-source.tar.gz',
            json.loads(cls.members['upstream-source-manifest.json']))

    def test_retained_package(self):
        result = verify.verify(self.package)
        self.assertEqual(result['snapshots'], 6)
        self.assertTrue(result['raw_candidate11_equal'])
        self.assertFalse(result['first_pass_introducing_direction_identified'])

    def test_changed_or_padded_raw_output_cannot_receive_attribution(self):
        for raw in (self.raw[:-1] + bytes([self.raw[-1] ^ 1]), self.raw + b'\0'):
            with self.subTest(bytes=len(raw)), self.assertRaisesRegex(ValueError, 'Raw candidate11 gate'):
                analyze.derive(self.log, raw)

    def test_complemented_machine_condition_is_rejected(self):
        text = self.parts[1][1].decode().replace('JUGT_rr %47:gpr, %22:gpr', 'JUGE_rr %47:gpr, %22:gpr')
        with self.assertRaisesRegex(ValueError, 'Expected one unsigned'):
            analyze.machine_guard(text, virtual=True)

    def test_error_edge_cannot_be_relabelled_success(self):
        text = self.parts[3][1].decode().replace('JUGT_rr $r9, $r7, %bb.34', 'JUGT_rr $r9, $r7, %bb.37')
        with self.assertRaisesRegex(ValueError, 'error 86 block'):
            analyze.machine_guard(text, virtual=False)

    def test_total_load_cannot_be_substituted_for_remaining(self):
        text = self.parts[3][1].decode().replace('from %ir.231)', 'from %ir.227)')
        with self.assertRaisesRegex(ValueError, 'Remaining-use load'):
            analyze.machine_guard(text, virtual=False)

    def test_missing_stage_is_not_silently_skipped(self):
        log = self.log.replace(self.parts[1][1], b'', 1)
        with self.assertRaisesRegex(ValueError, 'compiler stage'):
            analyze.snapshots(log)

    def test_network_enabled_build_is_rejected(self):
        state = copy.deepcopy(self.state)
        start = next(row['command'] for row in state['commands'] if row['label'] == 'start-offline-build-container')
        start[start.index('--network') + 1] = 'bridge'
        with self.assertRaisesRegex(ValueError, 'Build networking'):
            verify.derive(self.members, state, self.sources)

    def test_deployed_identity_claim_is_rejected(self):
        state = copy.deepcopy(self.state)
        state['raw']['deployed_identity_claimed'] = True
        members = dict(self.members, **{'raw-result.json': json.dumps(state['raw']).encode()})
        with self.assertRaisesRegex(ValueError, 'Raw identity scope'):
            verify.derive(members, state, self.sources)

    def test_changed_artifact_is_rejected_before_attribution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw = (self.package / '40343712336.zip').read_bytes()
            (root / '40343712336.zip').write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
            with self.assertRaisesRegex(ValueError, 'Changed evidence: artifact ZIP'):
                verify.artifact(root, self.receipt)

    def test_cpu_override_or_truncated_argv_is_rejected(self):
        original = self.members['rustc-4272.argv']
        for raw in (original[:-1], original.replace(analyze.FLAGS[0].encode(),
                    b'-Ctarget-cpu=sbfv2\0' + analyze.FLAGS[0].encode())):
            with self.subTest(raw_bytes=len(raw)), self.assertRaises(ValueError):
                analyze.invocation(raw)

    def test_changed_extracted_snapshot_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'package'
            shutil.copytree(self.package, root)
            path = root / 'snapshots/after-block-placement.txt'
            path.write_bytes(path.read_bytes().replace(b'JUGT_rr $r9, $r7', b'JUGE_rr $r9, $r7'))
            with self.assertRaisesRegex(ValueError, 'Saved snapshot differs'):
                verify.verify(root)


if __name__ == '__main__':
    unittest.main()

"""Reject unsupported claims at the final-IR/selection boundary."""
import gzip
import json
from pathlib import Path
import tempfile
import unittest

import analyze_boundary
import verify
import verify_boundary


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = Path(__file__).resolve().parent
        cls.members, _ = verify_boundary.load(cls.package)
        cls.log = cls.members['build-candidate11-isel-input.stderr.log']
        cls.raw = cls.members['token_metadata.so']
        cls.ir = (cls.package / 'snapshots/before-codegenprepare.txt').read_bytes()
        cls.machine = (cls.package / 'snapshots/before-finalize-isel.txt').read_bytes()
        receipt = json.loads(gzip.decompress((cls.package / 'receipt.json.gz').read_bytes()))
        cls.previous, _ = verify.artifact(cls.package, receipt)

    def derive(self, log=None, raw=None):
        return analyze_boundary.derive(self.log if log is None else log,
            self.raw if raw is None else raw, self.ir, self.machine)

    def test_complete_offline_boundary(self):
        result = verify_boundary.check(self.package)
        self.assertTrue(result['after_codegenprepare_equals_final_isel_input'])
        self.assertEqual(result['boundary_snapshots'], 4)
        self.assertFalse(result['internal_dag_event_observed'])

    def test_raw_difference_blocks_attribution(self):
        with self.assertRaisesRegex(ValueError, 'Raw candidate11 gate'):
            self.derive(raw=self.raw + b'\0')

    def test_final_ir_difference_is_not_normalized_away(self):
        final = analyze_boundary.ir_bodies(self.log)[2]
        changed = final[0].replace(b'  %6 = alloca %3, align 8', b'  %6 = alloca %3, align 16')
        log = self.log[:final.start()] + changed + self.log[final.end():]
        with self.assertRaisesRegex(ValueError, 'bodies differ'):
            self.derive(log=log)

    def test_complemented_combined_guard_is_rejected(self):
        log = self.log.replace(b'%233 = icmp ult i64 %232, %4', b'%233 = icmp uge i64 %232, %4')
        with self.assertRaisesRegex(ValueError, 'data/control-flow evidence'):
            self.derive(log=log)

    def test_missing_input_banner_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'IR stage banner'):
            self.derive(log=self.log.replace(b'*** Final LLVM Code input to ISel ***', b'*** Other point ***'))

    def test_changed_selected_machine_dump_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Earlier run selected-machine dump'):
            self.derive(log=self.log.replace(b'JUGT_rr %47:gpr, %22:gpr', b'JUGE_rr %47:gpr, %22:gpr'))

    def test_non_diagnostic_argument_change_is_rejected(self):
        argv = self.members['rustc-4272.argv'].replace(b'opt-level=z', b'opt-level=3')
        with self.assertRaisesRegex(ValueError, 'Non-diagnostic compiler arguments'):
            analyze_boundary.invocation(argv, self.previous['rustc-4272.argv'])

    def test_changed_compiler_source_is_rejected(self):
        root = self.package / 'isel-boundary'
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            (target / 'compiler-source-receipts.json').write_bytes((root / 'compiler-source-receipts.json').read_bytes())
            raw = (root / 'compiler-source.tar.gz').read_bytes()
            (target / 'compiler-source.tar.gz').write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
            with self.assertRaisesRegex(ValueError, 'Changed evidence: compiler source archive'):
                verify_boundary.sources(target)


if __name__ == '__main__':
    unittest.main()

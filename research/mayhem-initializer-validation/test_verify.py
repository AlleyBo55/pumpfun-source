import copy
from pathlib import Path
import unittest
import verify

ROOT = Path(__file__).resolve().parent

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.report = verify.read_json(ROOT/'runtime/vault-matrix.json.gz')
        self.runner_hash = verify.sha((ROOT/'validation_matrix.py').read_bytes())

    def check(self, report):
        return verify.check_matrix(report, verify.HASHES['vault'], 53, 0, self.runner_hash)

    def test_saved_positive_control(self):
        self.assertEqual(self.check(self.report)['mismatches'], 0)

    def test_hidden_error_difference(self):
        self.report['cases'][0]['candidate']['error'] = 'another error'
        with self.assertRaises(ValueError): self.check(self.report)

    def test_changed_initial_state(self):
        self.report['cases'][0]['candidate']['before'] = {}
        with self.assertRaises(ValueError): self.check(self.report)

    def test_missing_case(self):
        self.report['cases'].pop()
        with self.assertRaises(ValueError): self.check(self.report)

    def test_forged_signature(self):
        import base64
        row = self.report['cases'][0]
        raw = bytearray(base64.b64decode(row['original']['signed_transaction_base64']))
        raw[1] ^= 1
        replacement = base64.b64encode(raw).decode()
        row['original']['signed_transaction_base64'] = replacement
        row['candidate']['signed_transaction_base64'] = replacement
        with self.assertRaises(ValueError): self.check(self.report)

    def test_success_claim_in_rejection_matrix(self):
        row = self.report['cases'][0]
        row['original']['error'] = row['candidate']['error'] = None
        with self.assertRaises(ValueError): self.check(self.report)

    def test_changed_candidate_binding(self):
        self.report['candidate_sha256'] = verify.HASHES['baseline']
        with self.assertRaises(ValueError): self.check(self.report)

if __name__ == '__main__':
    unittest.main()

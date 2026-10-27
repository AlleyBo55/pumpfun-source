import base64
import copy
import gzip
import json
from pathlib import Path
import unittest

from solders.pubkey import Pubkey
import verify


class ReceiptRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(gzip.decompress((verify.HERE / 'corrected-pair.json.gz').read_bytes()))
        cls.harness = verify.load_harness(verify.HERE.parents[1])

    def setUp(self):
        self.data = copy.deepcopy(self.report)

    def row(self, name):
        return next(row for row in self.data['cases'] if row['case']['case'] == name)

    def test_recorded_control(self):
        self.assertEqual(verify.check_report(self.data, self.harness)['cases'], 20)

    def test_old_bug_with_valid_signature_on_both_sides(self):
        baseline = self.row('mayhem-base')['original']['signed_transaction_base64']
        for side in ('original', 'candidate'):
            self.row('zero-creator-is-rejected')[side]['signed_transaction_base64'] = baseline
        with self.assertRaisesRegex(ValueError, 'Creator input differs'):
            verify.check_report(self.data, self.harness)

    def test_matching_false_success_does_not_count(self):
        for side in ('original', 'candidate'):
            self.row('zero-creator-is-rejected')[side]['error'] = None
        with self.assertRaisesRegex(ValueError, 'did not reject'):
            verify.check_report(self.data, self.harness)

    def test_matching_wrong_persisted_creator_does_not_count(self):
        for side in ('original', 'candidate'):
            account = self.row('distinct-creator-mayhem-mode')[side]['after'][verify.CURVE]
            data = bytearray.fromhex(account['data'])
            data[49:81] = bytes(Pubkey.from_string(verify.USER))
            account['data'] = data.hex()
        with self.assertRaisesRegex(ValueError, 'Persisted creator differs'):
            verify.check_report(self.data, self.harness)

    def test_corrupt_signature(self):
        row = self.row('zero-creator-is-rejected')
        raw = bytearray(base64.b64decode(row['original']['signed_transaction_base64']))
        raw[1] ^= 1
        for side in ('original', 'candidate'):
            row[side]['signed_transaction_base64'] = base64.b64encode(raw).decode()
        with self.assertRaisesRegex(ValueError, 'Invalid signature'):
            verify.check_report(self.data, self.harness)

    def test_missing_case(self):
        self.data['cases'].pop()
        with self.assertRaisesRegex(ValueError, 'Case inventory changed'):
            verify.check_report(self.data, self.harness)


if __name__ == '__main__':
    unittest.main()

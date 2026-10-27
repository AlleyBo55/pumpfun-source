import copy
import gzip
import json
import unittest

import verify

REPO = verify.HERE.parents[1]


class RecheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = verify.creator_checker(REPO)
        cls.harness = cls.checker.load_harness(REPO)
        cls.report = json.loads(gzip.decompress((verify.HERE / 'overlay-pump-caller.json.gz').read_bytes()))

    def test_saved_evidence(self):
        self.assertEqual(verify.verify(REPO)['saved_evidence'], 'PASS')

    def test_hidden_mismatch_is_rejected(self):
        report = copy.deepcopy(self.report)
        row = next(r for r in report['cases'] if r['case']['case'] == 'mayhem-base')
        row['candidate']['after'] = {}
        with self.assertRaises(ValueError):
            self.checker.check_report(report, self.harness)

    def test_missing_case_is_rejected(self):
        report = copy.deepcopy(self.report)
        report['cases'].pop()
        with self.assertRaises(ValueError):
            self.checker.check_report(report, self.harness)


if __name__ == '__main__':
    unittest.main()

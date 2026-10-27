import copy
import unittest
import verify


class ReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=verify.read(verify.P/'fresh-runtime.json.gz')
        cls.frozen={}
        for name in cls.report['input_reports']:
            path=verify.ROOT/name
            for i,row in enumerate(verify.read(path)['cases']):
                rel=path.relative_to(verify.ROOT/'repro/donation-relay/distribution-worker-source-recovery/settlement')
                cls.frozen[str(rel)+':'+str(i)]=row
        cls.harness=verify.module('frozen_receipt_test',verify.ROOT/'repro/donation-relay/local-validation-proposal/harness_proposal.py')

    def test_positive_control(self):
        self.assertEqual(verify.check_runtime(self.report,self.frozen,self.harness)['records'],536)

    def test_missing_case(self):
        report=dict(self.report,cases=self.report['cases'][:-1])
        with self.assertRaises(AssertionError):verify.check_runtime(report,self.frozen,self.harness)

    def test_false_matching_effects(self):
        report=dict(self.report,cases=list(self.report['cases']))
        report['cases'][0]=copy.deepcopy(report['cases'][0])
        for side in ['original','candidate']:report['cases'][0][side]['error']='invented error'
        with self.assertRaises(AssertionError):verify.check_runtime(report,self.frozen,self.harness)

    def test_forged_reproduction_claim(self):
        report=dict(self.report,cases=list(self.report['cases']))
        report['cases'][0]=dict(report['cases'][0],original_reproduced=False)
        with self.assertRaises(AssertionError):verify.check_runtime(report,self.frozen,self.harness)

    def test_changed_fixture(self):
        report=dict(self.report,cases=list(self.report['cases']))
        report['cases'][0]=dict(report['cases'][0],fixture={})
        with self.assertRaises(AssertionError):verify.check_runtime(report,self.frozen,self.harness)


if __name__=='__main__':unittest.main()

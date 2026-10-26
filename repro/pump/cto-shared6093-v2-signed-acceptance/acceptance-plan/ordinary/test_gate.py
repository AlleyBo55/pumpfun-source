"""Mock-only supplemental admission/claim ordering tests. No subprocess, helper, solders or VM."""
from pathlib import Path
import contextlib,io,json,sys,tempfile,types,unittest
from unittest.mock import patch
import gate
class Tests(unittest.TestCase):
 def config(self,root):return {'lane':'ordinary','gate_output':str(root/'gate-out'),'claim':str(root/'attempt.json'),'out':str(root/'out'),'candidate_sha256':'mock','source37_sha256':'mock','python':'mock'}
 def test_missing_admission_never_claims_or_launches(self):
  with tempfile.TemporaryDirectory()as t:
   cfg=self.config(Path(t))
   with patch.object(gate,'supported_python'),patch.object(gate,'check_admission',side_effect=AssertionError('missing admission')),patch.object(gate,'launch_child')as child:
    with self.assertRaises(AssertionError):gate.execute(cfg,'seal','emitted','root')
   child.assert_not_called();self.assertFalse(Path(cfg['gate_output']).exists());self.assertFalse(Path(cfg['claim']).exists())
 def test_wrong_python_never_claims(self):
  with tempfile.TemporaryDirectory()as t:
   cfg=self.config(Path(t))
   with patch.object(gate,'supported_python',side_effect=AssertionError('wrong interpreter')),patch.object(gate,'check_admission')as adm,patch.object(gate,'launch_child')as child:
    with self.assertRaises(AssertionError):gate.execute(cfg,'seal','emitted','root')
   adm.assert_not_called();child.assert_not_called();self.assertFalse(Path(cfg['gate_output']).exists())
 def test_durable_gate_claim_before_child_nonzero_preserved_no_retry(self):
  with tempfile.TemporaryDirectory()as t:
   cfg=self.config(Path(t));out=Path(cfg['gate_output'])
   def fake_child(*args):
    self.assertTrue((out/'claim.json').is_file());self.assertTrue((out/'launch.json').is_file());self.assertTrue(Path(cfg['claim']).is_file());return types.SimpleNamespace(returncode=9)
   with patch.object(gate,'supported_python'),patch.object(gate,'check_admission',return_value={}),patch.object(gate,'plan_check',return_value=cfg),patch.object(gate,'launch_child',side_effect=fake_child)as child:
    self.assertEqual(gate.execute(cfg,'seal','emitted','root'),2)
    with self.assertRaises(FileExistsError):gate.execute(cfg,'seal','emitted','root')
   self.assertEqual(child.call_count,1);saved=json.loads((out/'exit.json').read_text());self.assertEqual(saved['child_returncode'],9);self.assertFalse(saved['acceptance_passed'])
 def test_saved_checker_failure_cannot_accept_zero_child(self):
  with tempfile.TemporaryDirectory()as t:
   cfg=self.config(Path(t));out=Path(cfg['gate_output']);fake=types.ModuleType('verify_results')
   def reject(*args):raise AssertionError('mock saved signature failure')
   fake.verify_results=reject
   with patch.dict(sys.modules,{'verify_results':fake}),patch.object(gate,'supported_python'),patch.object(gate,'check_admission',return_value={}),patch.object(gate,'plan_check',return_value=cfg),patch.object(gate,'launch_child',return_value=types.SimpleNamespace(returncode=0)):
    self.assertEqual(gate.execute(cfg,'seal','emitted','root'),2)
   self.assertFalse(json.loads((out/'exit.json').read_text())['acceptance_passed'])
 def tearDown(self):self.assertFalse(any(n=='solders'or n.startswith('solders.')for n in sys.modules));self.assertNotIn('frozen_admin_cto_helper',sys.modules)
if __name__=='__main__':unittest.main()

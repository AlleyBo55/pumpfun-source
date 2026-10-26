"""Independent actual six-case gate-path tests; no native/helper/Solders imports."""
from pathlib import Path
import contextlib,io,json,sys,tempfile,types,unittest
from unittest.mock import patch
Q=Path(__file__).resolve().parent.parent/'cto-shared6093-v2-acceptance-plan/six-case';sys.path.insert(0,str(Q))
import gate,common,controller,driver,test_plan
DATA=test_plan.DATA
class Tests(unittest.TestCase):
 def setUp(self):self.enterContext(contextlib.redirect_stdout(io.StringIO()))
 def tearDown(self):self.assertFalse(any(n=='solders'or n.startswith('solders.')for n in sys.modules));self.assertNotIn('frozen_admin_cto_helper',sys.modules)
 def exercise(self,kind):
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp);cfg={'lane':'six-case','gate_output':str(p/'gate'),'claim':str(p/'claim'),'out':str(p/'out'),'candidate_sha256':'mock','source37_sha256':'mock','python':'mock'};out=Path(cfg['out'])
   def child(*args):
    self.assertTrue((Path(cfg['gate_output'])/'claim.json').exists());self.assertTrue((Path(cfg['gate_output'])/'launch.json').exists());common.durable(Path(cfg['claim']),{'mock':True});out.mkdir()
    common.durable(out/'launch.json',{});(out/'stdout.log').write_bytes(b'');(out/'stderr.log').write_bytes(b'')
    def run(c,b):
     item=test_plan.fake_item(c,b)
     if kind=='effect-drift'and b is not None:item['after']['unexpected']='mismatch'
     if kind=='logs-only'and b is not None:item['logs'].append('candidate natural origin log differs')
     return item
    obs=driver.run_all(types.SimpleNamespace(run=run),DATA,Path('mock-candidate'),out,test_plan.mock_audit);analysis=obs['analysis'];self.assertIsNone(obs['failure'])
    common.durable(out/'driver-result.json',{'state':'FINITE_ACCEPTANCE_OBSERVATIONS_RECORDED','returncode':0,'vm_calls_attempted':12,'preservation_pass_claimed':False,'field_mapping_proven':False,'analysis':analysis,'failure':None})
    digests={f.name:gate.H(f)for f in out.iterdir()if f.is_file()};common.durable(out/'exit.json',{'state':'FINITE_ACCEPTANCE_OBSERVATIONS_RECORDED','child_returncode':0,'observations_valid':True,'inputs_source37_candidate_unchanged':True,'raw_files_sha256':digests,'analysis':analysis})
    return types.SimpleNamespace(returncode=0)
   admissions=patch.object(gate,'check_admission',side_effect=[{},AssertionError('mock root/review changed')])if kind=='post-admission-mutation'else patch.object(gate,'check_admission',return_value={})
   auditor=patch.object(controller,'audit_transaction',side_effect=AssertionError('mock bad actual signature'))if kind=='bad-signature'else patch.object(controller,'audit_transaction',side_effect=test_plan.mock_audit)
   with patch.object(gate,'supported_python'),admissions,patch.object(gate,'plan_check',return_value=cfg),patch.object(gate,'launch_child',side_effect=child)as launcher,patch.object(common,'check_plan',return_value=(cfg,DATA)),auditor:code=gate.execute(cfg,'mock-seal','mock-emitted','mock-root')
   self.assertEqual(launcher.call_count,1);saved=json.loads((Path(cfg['gate_output'])/'exit.json').read_text());ok=kind in['valid','logs-only'];self.assertEqual(code,0 if ok else 2);self.assertEqual(saved['acceptance_passed'],ok)
   self.assertTrue((out/'side-00-original.json').exists())
 def test_actual_six_gate_valid_path(self):self.exercise('valid')
 def test_logs_only_difference_allowed_separately(self):self.exercise('logs-only')
 def test_effect_drift_rejected_even_child_zero(self):self.exercise('effect-drift')
 def test_saved_bad_signature_rejected(self):self.exercise('bad-signature')
 def test_postchild_root_review_mutation_rejected(self):self.exercise('post-admission-mutation')
if __name__=='__main__':unittest.main()

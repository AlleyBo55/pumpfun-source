"""Mock-only failure tests. No frozen helper, solders, LiteSVM or target import."""
from pathlib import Path
import contextlib,copy,io,json,sys,tempfile,types,unittest
from unittest.mock import patch
import common,controller,driver
DATA=json.loads((common.P/'cases.json').read_text())
def fake_item(case,binary=None,force_none=False):
 field=next(iter(case['accounts']));p=case['accounts'][field];b=bytearray(165);b[64:72]=p['tokens'].to_bytes(8,'little');b[108]=1
 for off,value in p.get('patches',[]):b[off:off+len(bytes.fromhex(value))]=bytes.fromhex(value)
 frozen=b[108]==2 and p['tokens']>0;err='InstructionErrorCustom(6093)'if frozen and not force_none else None
 origin=660 if field=='coin_creator_vault_ata'else 719
 before={field:{'lamports':2039280,'owner':'mock TOKEN','data':b.hex()}}
 return {'case':copy.deepcopy(case),'error':err,'before':before,'after':copy.deepcopy(before),'logs':(['AnchorError at programs/pump/src/creator/admin_cto.rs:'+str(origin)+'.']if err else[]),'events':[],'inner':[],'return':None,'transaction_base64':'MOCK ONLY, never real acceptance','signatures_verified':True,'pool_authority_top_level_signer':False}
def mock_audit(item):return {'transaction_sha256':'mock','signature_count':2,'all_signatures_verified':True,'pool_authority_top_level_signer':False}
class Tests(unittest.TestCase):
 def setUp(self):self.enterContext(contextlib.redirect_stdout(io.StringIO()))
 def tearDown(self):self.assertFalse(any(n=='solders'or n.startswith('solders.')for n in sys.modules));self.assertNotIn('frozen_admin_cto_helper',sys.modules)
 def run_mock(self,fn,auditor=mock_audit):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);out=Path(t.name);calls=[]
  def call(c,b):calls.append((copy.deepcopy(c),b));return fn(c,b)
  result=driver.run_all(types.SimpleNamespace(run=call),DATA,Path('mock-candidate'),out,auditor)
  return result,out,calls
 def test_exact_twelve_sides_and_effect_acceptance(self):
  r,out,calls=self.run_mock(fake_item);self.assertIsNone(r['failure']);self.assertEqual(len(calls),12);self.assertEqual(r['vm_calls_attempted'],12);self.assertTrue(r['analysis']['all_original_hypotheses_observed']);self.assertFalse(r['analysis']['preservation_pass_claimed']);self.assertEqual(len(list(out.glob('side-*.json'))),12)
  for i,spec in enumerate(DATA['rows']):self.assertEqual(calls[2*i],(spec['case'],None));self.assertEqual(calls[2*i+1],(spec['case'],Path('mock-candidate')))
 def test_counterevidence_does_not_retry_or_stop_six_cases(self):
  r,out,calls=self.run_mock(lambda c,b:fake_item(c,b,True));self.assertIsNone(r['failure']);self.assertFalse(r['analysis']['all_original_hypotheses_observed']);self.assertEqual(len(calls),12)
 def test_malformed_return_saved_before_validation_failure(self):
  r,out,calls=self.run_mock(lambda c,b:{'case':c});self.assertEqual(len(calls),1);self.assertTrue((out/'side-00-original.json').exists());self.assertIsNotNone(r['failure'])
 def test_helper_exception_preserves_attempt_without_fabricating_side(self):
  def failure(c,b):raise RuntimeError('mock helper exception')
  r,out,calls=self.run_mock(failure);self.assertEqual(len(calls),1);self.assertTrue((out/'attempt-00-original.json').exists());self.assertFalse((out/'side-00-original.json').exists());self.assertIsNotNone(r['failure'])
 def test_bad_signature_audit_stops_after_raw_persist(self):
  def failure(item):raise AssertionError('mock invalid signature')
  r,out,calls=self.run_mock(fake_item,failure);self.assertEqual(len(calls),1);self.assertTrue((out/'side-00-original.json').exists());self.assertIsNotNone(r['failure'])
 def test_second_side_failure_keeps_first_raw_side(self):
  def failure(c,b):
   if b is not None:raise RuntimeError('mock candidate fail')
   return fake_item(c,b)
  r,out,calls=self.run_mock(failure);self.assertEqual(len(calls),2);self.assertTrue((out/'side-00-original.json').exists());self.assertEqual(r['rows'],[])
 def test_unrelated_fixture_change_rejected(self):
  def wrong(c,b):
   item=fake_item(c,b)
   if c['name'].endswith('frozen-zero'):item['before']['unrelated']=None
   return item
  r,out,calls=self.run_mock(wrong);self.assertEqual(len(calls),12);self.assertIsNotNone(r['failure']);self.assertIsNone(r['analysis'])
 def config(self,base):
  cfg=json.loads((common.P/'oracle-plan.json').read_text());cfg.update(out=str(base/'out'),claim=str(base/'claim.json'));return cfg
 def test_preexisting_output_preserved_no_claim_or_child(self):
  with tempfile.TemporaryDirectory()as t:
   cfg=self.config(Path(t));out=Path(cfg['out']);out.mkdir();(out/'sentinel').write_text('keep')
   with patch.object(controller,'supported_running_python'),patch.object(controller,'launch_child')as child:
    with self.assertRaises(AssertionError):controller.execute(cfg,DATA,'mock')
   child.assert_not_called();self.assertFalse(Path(cfg['claim']).exists());self.assertEqual((out/'sentinel').read_text(),'keep')
 def test_preexisting_claim_prevents_child(self):
  with tempfile.TemporaryDirectory()as t:
   cfg=self.config(Path(t));Path(cfg['claim']).write_text('existing')
   with patch.object(controller,'supported_running_python'),patch.object(controller,'launch_child')as child:
    with self.assertRaises(AssertionError):controller.execute(cfg,DATA,'mock')
   child.assert_not_called();self.assertEqual(Path(cfg['claim']).read_text(),'existing')
 def test_wrong_python_prevents_claim(self):
  with tempfile.TemporaryDirectory()as t:
   cfg=self.config(Path(t))
   with patch.object(controller,'supported_running_python',side_effect=AssertionError('mock unsupported interpreter')),patch.object(controller,'launch_child')as child:
    with self.assertRaises(AssertionError):controller.execute(cfg,DATA,'mock')
   child.assert_not_called();self.assertFalse(Path(cfg['claim']).exists())
 def test_durable_claim_and_launch_precede_child_and_failure_kept(self):
  with tempfile.TemporaryDirectory()as t:
   cfg=self.config(Path(t));out=Path(cfg['out']);claim=Path(cfg['claim'])
   def failure(*args):
    self.assertTrue(claim.is_file());self.assertTrue((out/'launch.json').is_file());self.assertEqual(json.loads((out/'launch.json').read_text())['claim_sha256'],common.H(claim));raise OSError('mock child launch failure')
   with patch.object(controller,'supported_running_python'),patch.object(controller,'check_plan',return_value=(cfg,DATA)),patch.object(controller,'launch_child',side_effect=failure)as child:
    self.assertEqual(controller.execute(cfg,DATA,'mock'),2)
    with self.assertRaises(AssertionError):controller.execute(cfg,DATA,'mock')
   self.assertEqual(child.call_count,1);self.assertEqual(json.loads((out/'exit.json').read_text())['state'],'FAILED_RAW_RECEIPTS_PRESERVED')
 def test_child_terminal_nonzero_and_missing_receipt_fail_closed(self):
  with tempfile.TemporaryDirectory()as t:
   cfg=self.config(Path(t));out=Path(cfg['out'])
   with patch.object(controller,'supported_running_python'),patch.object(controller,'check_plan',return_value=(cfg,DATA)),patch.object(controller,'launch_child',return_value=types.SimpleNamespace(returncode=7))as child:self.assertEqual(controller.execute(cfg,DATA,'mock'),2)
   self.assertEqual(child.call_count,1);self.assertEqual(json.loads((out/'exit.json').read_text())['child_returncode'],7)
 def terminal_test(self,counter):
  with tempfile.TemporaryDirectory()as t:
   cfg=self.config(Path(t));out=Path(cfg['out'])
   def fake_child(*args):
    helper=types.SimpleNamespace(run=lambda c,b:fake_item(c,b,counter));obs=driver.run_all(helper,DATA,Path('mock-candidate'),out,mock_audit);analysis=obs['analysis'];code=0 if (analysis['all_original_hypotheses_observed']and analysis['all_six_effects_equal'])else 2
    common.durable(out/'driver-result.json',{'state':'FINITE_ACCEPTANCE_OBSERVATIONS_RECORDED'if code==0 else'COUNTEREVIDENCE_PRESERVED','returncode':code,'vm_calls_attempted':12,'field_mapping_proven':False,'preservation_pass_claimed':False,'analysis':analysis,'failure':None});return types.SimpleNamespace(returncode=code)
   with patch.object(controller,'supported_running_python'),patch.object(controller,'check_plan',return_value=(cfg,DATA)),patch.object(controller,'audit_transaction',side_effect=mock_audit),patch.object(controller,'launch_child',side_effect=fake_child)as child:code=controller.execute(cfg,DATA,'mock')
   self.assertEqual(code,2 if counter else 0);self.assertEqual(child.call_count,1);saved=json.loads((out/'exit.json').read_text());self.assertTrue(saved['observations_valid']);self.assertFalse(saved['preservation_pass_claimed']);self.assertFalse(saved['field_mapping_proven']);self.assertEqual(saved['state'],'COUNTEREVIDENCE_PRESERVED'if counter else'FINITE_ACCEPTANCE_OBSERVATIONS_RECORDED')
 def test_valid_diagnostic_terminal_path(self):self.terminal_test(False)
 def test_valid_counterevidence_terminal_path(self):self.terminal_test(True)
 def test_zero_control_candidate_effect_mismatch_rejected(self):
  def wrong(c,b):
   item=fake_item(c,b)
   if b is not None and c['name'].endswith('frozen-zero'):item['inner']=[{'mock':'unexpected zero CPI'}]
   return item
  r,out,calls=self.run_mock(wrong);self.assertEqual(len(calls),12);self.assertIsNone(r['failure']);self.assertTrue(r['analysis']['all_original_hypotheses_observed']);self.assertFalse(r['analysis']['all_six_effects_equal'])
 def test_candidate_natural_origin_logs_may_differ(self):
  def natural(c,b):
   item=fake_item(c,b)
   if b is not None:item['logs']=['mock natural candidate origin differs']
   return item
  r,out,calls=self.run_mock(natural);self.assertEqual(len(calls),12);self.assertIsNone(r['failure']);self.assertTrue(r['analysis']['all_original_hypotheses_observed']);self.assertTrue(r['analysis']['all_six_effects_equal'])
 def test_no_native_or_frozen_helper_imported(self):
  self.assertFalse(any(n=='solders'or n.startswith('solders.')for n in sys.modules));self.assertNotIn('frozen_admin_cto_helper',sys.modules)
if __name__=='__main__':unittest.main()

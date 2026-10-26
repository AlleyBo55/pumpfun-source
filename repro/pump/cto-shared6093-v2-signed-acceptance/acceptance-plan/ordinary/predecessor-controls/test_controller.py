"""Synthetic terminal/failure tests only. Child launcher is always mocked; no harness import/execution."""
from pathlib import Path
import contextlib,copy,hashlib,importlib.util,io,json,subprocess,sys,tempfile,unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('ordinary_controller',Path(__file__).with_name('controller.py'));c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
class Tests(unittest.TestCase):
 def invoke(self,mode='ok',mutate=None):
  with tempfile.TemporaryDirectory()as td:
   p=Path(td);(p/'manifest.json').write_text('{}');out=p/'attempt';repo=p/'repo';repo.mkdir();check_calls=[]
   if mode=='existing':out.mkdir()
   data={'candidate_sha256':c.EXPECTED,'case_count':1,'mismatches':[],'cases':[{'match':True,'original':{'signatures_verified':True,'pool_authority_top_level_signer':False},'candidate':{'signatures_verified':True,'pool_authority_top_level_signer':False}}]}
   if mutate:mutate(data)
   def runner(cmd,**kwargs):
    if mode=='launch_failure':raise OSError('synthetic child launch failure')
    if mode not in ['missing','child_failure']:(out/'receipt.json').write_text('not json'if mode=='malformed'else json.dumps(data))
    return subprocess.CompletedProcess(cmd,1 if mode=='child_failure'else 0)
   def check():
    check_calls.append(1)
    if mode=='input_changed'and len(check_calls)>1:raise AssertionError('synthetic after-input mismatch')
   with patch.object(c,'P',p),patch.object(c,'R',repo),patch.object(c,'OUT',out),patch.object(c,'check',side_effect=check),patch.object(c.subprocess,'run',side_effect=runner)as child,patch.object(sys,'argv',['controller','--execute','--expected-seal',hashlib.sha256(b'{}').hexdigest()]),contextlib.redirect_stdout(io.StringIO()):
    if mode=='existing':
     with self.assertRaises(AssertionError):c.main()
     child.assert_not_called();return
    rc=c.main();result=json.loads((out/'exit.json').read_text());self.assertEqual(child.call_count,1);return rc,result
 def test_success_inherited_positive_count_semantics(self):
  rc,r=self.invoke();self.assertEqual(rc,0);self.assertTrue(r['passed'])
 def test_existing_output_prevents_launch(self):self.invoke('existing')
 def test_missing_malformed_and_child_launch_failure(self):
  for mode in ['missing','malformed','child_failure','launch_failure']:
   with self.subTest(mode=mode):rc,r=self.invoke(mode);self.assertEqual(rc,2);self.assertFalse(r['passed'])
 def test_candidate_count_mismatch_and_false_match(self):
  mutations=[lambda d:d.update(candidate_sha256='wrong'),lambda d:d.update(case_count=0),lambda d:d.update(case_count=2),lambda d:d.update(mismatches=['x']),lambda d:d['cases'][0].update(match=False)]
  for i,f in enumerate(mutations):
   with self.subTest(i=i):rc,r=self.invoke(mutate=f);self.assertEqual(rc,2);self.assertFalse(r['passed'])
 def test_signature_and_pda_flags_fail_closed(self):
  for side in ['original','candidate']:
   for flag,value in [('signatures_verified',False),('pool_authority_top_level_signer',True)]:
    with self.subTest(side=side,flag=flag):rc,r=self.invoke(mutate=lambda d:d['cases'][0][side].update({flag:value}));self.assertEqual(rc,2);self.assertFalse(r['passed'])
 def test_after_input_change(self):
  rc,r=self.invoke('input_changed');self.assertEqual(rc,2);self.assertFalse(r['inputs_unchanged'])
if __name__=='__main__':unittest.main()

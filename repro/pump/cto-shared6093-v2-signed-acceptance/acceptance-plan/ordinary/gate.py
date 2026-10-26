"""Only authorized execution entry: admission, fresh durable claim, bounded child, saved acceptance."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,traceback
sys.dont_write_bytecode=True
from admission import P,H,J,durable,plan_check,check_admission

def launch_child(command,repo,env,stdout,stderr):
 return subprocess.run(command,cwd=repo,env=env,stdout=stdout,stderr=stderr)

def supported_python(cfg):
 assert sys.version.startswith('3.12.13') and Path(sys.executable).resolve()==Path(cfg['python']).resolve() and H(Path(sys.executable).resolve())==cfg['python_binary_sha256']

def execute(cfg,seal,emitted_seal,root_admission_sha):
 supported_python(cfg)
 binding=check_admission(cfg,emitted_seal,root_admission_sha,seal)
 # Recheck freshness immediately before exclusive durable attempt creation.
 plan_check(seal)
 gateout=Path(cfg['gate_output']);gateout.mkdir(exist_ok=False)
 durable(gateout/'claim.json',{'plan_seal':seal,'lane':cfg['lane'],'candidate_sha256':cfg['candidate_sha256'],'gate_sha256':H(P/'gate.py'),'one_attempt':True,'automatic_retry':False,**binding})
 if cfg['lane']=='ordinary':durable(Path(cfg['claim']),J(gateout/'claim.json'))
 result={'state':'CLAIMED','lane':cfg['lane'],'plan_seal':seal,'candidate_sha256':cfg['candidate_sha256'],'retry_attempts':0,'acceptance_passed':False,**binding}
 try:
  command=[cfg['python'],'-B',str(P/'controller.py'),'--execute','--expected-seal',seal]
  env={'HOME':str(Path.home()),'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','DYLD_LIBRARY_PATH':'/opt/homebrew/opt/expat/lib','PYTHONDONTWRITEBYTECODE':'1'}
  durable(gateout/'launch.json',{'command':command,'environment':env,'claim_sha256':H(gateout/'claim.json'),'plan_seal':seal,'source37_sha256':cfg['source37_sha256'],**binding})
  with(gateout/'stdout.log').open('xb')as stdout,(gateout/'stderr.log').open('xb')as stderr:child=launch_child(command,P,env,stdout,stderr)
  result['child_returncode']=child.returncode
  assert child.returncode==0,'Counterevidence/failure retained; never retry or weaken assertions'
  if cfg['lane']=='ordinary':
   from verify_results import verify_results
   accepted=verify_results(Path(cfg['out']))
  else:
   from common import check_plan
   from controller import validate_output
   _,data=check_plan(seal,True);analysis,dr=validate_output_after_exit(Path(cfg['out']),data)
   assert analysis['all_original_hypotheses_observed'] and analysis['all_six_effects_equal']
   accepted={'state':'PASS_FINITE_SIX_CASE_EFFECT_ACCEPTANCE','cases':6,'sides':12,'analysis':analysis,'raw_logs_compared_for_equality':False}
  durable(gateout/'saved-acceptance.json',accepted);result['acceptance_passed']=True;result['state']='ACCEPTED_FINITE_'+cfg['lane'].upper()
 except BaseException:result['state']='FAILED_COUNTEREVIDENCE_RAW_OUTPUTS_PRESERVED';result['failure']=traceback.format_exc()
 finally:
  try:
   plan_check(seal,False);check_admission(cfg,emitted_seal,root_admission_sha,seal);result['inputs_source37_candidate_unchanged']=True
  except BaseException:result['inputs_source37_candidate_unchanged']=False;result['after_failure']=traceback.format_exc();result['acceptance_passed']=False;result['state']='FAILED_COUNTEREVIDENCE_RAW_OUTPUTS_PRESERVED'
  result['raw_gate_files_sha256']={f.name:H(f)for f in gateout.iterdir()if f.is_file()};durable(gateout/'exit.json',result)
 return 0 if result['acceptance_passed']else 2

def validate_output_after_exit(out,data):
 # Original validator intentionally expected pre-exit membership. Authenticate
 # saved exit and temporarily use no mutation: validate through explicit copied checks.
 from controller import validate_output
 exit_data=J(out/'exit.json');assert exit_data['state']=='FINITE_ACCEPTANCE_OBSERVATIONS_RECORDED' and exit_data['child_returncode']==0 and exit_data['observations_valid']is True and exit_data['inputs_source37_candidate_unchanged']is True
 expected=exit_data['raw_files_sha256'];assert set(expected)|{'exit.json'}=={f.name for f in out.iterdir()if f.is_file()}
 for name,h in expected.items():assert H(out/name)==h
 # All per-case, returned-side, signature, marker, analysis checks are replayed
 # by validator with its documented post-exit membership option.
 analysis,dr=validate_output(out,data,post_exit=True);assert analysis==exit_data['analysis']
 assert dr['returncode']==0 and dr['state']=='FINITE_ACCEPTANCE_OBSERVATIONS_RECORDED'
 return analysis,dr

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--expected-seal',required=True);ap.add_argument('--execute',action='store_true');ap.add_argument('--expected-emitted-review-seal');ap.add_argument('--expected-root-admission-sha256');args=ap.parse_args();cfg=plan_check(args.expected_seal)
 if not args.execute:print('PASS_READONLY_PLAN_ONLY: no admission fabricated, claim created, helper imported, native child or VM executed');return 0
 assert args.expected_emitted_review_seal and args.expected_root_admission_sha256,'Both separately reviewed launch pins required'
 return execute(cfg,args.expected_seal,args.expected_emitted_review_seal,args.expected_root_admission_sha256)
if __name__=='__main__':raise SystemExit(main())

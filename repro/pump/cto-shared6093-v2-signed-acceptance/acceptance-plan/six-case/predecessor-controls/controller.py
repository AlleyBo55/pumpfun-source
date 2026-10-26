"""One future signed diagnostic. Default is read-only; no automatic retry."""
from pathlib import Path
import argparse,json,os,subprocess,sys,traceback
sys.dont_write_bytecode=True
from common import P,J,H,durable,check_plan,fresh,supported_running_python
from saved_checks import validate_item,audit_transaction,analyze_observations
def launch_child(command,repo,env,stdout,stderr):return subprocess.run(command,cwd=repo,env=env,stdout=stdout,stderr=stderr)
def validate_output(out,data):
 assert not any(f.is_symlink()for f in out.rglob('*'))and all(f.is_file()for f in out.iterdir())
 observation=J(out/'observations.json');assert observation['failure']is None and observation['retry_attempts']==0 and observation['vm_calls_attempted']==12
 assert len(observation['rows'])==6 and len(observation['attempts'])==len(observation['signature_audits'])==12
 expected_attempts=[{'case_index':i,'case':r['case']['name'],'side':side,'target_call_count_in_this_side':1}for i,r in enumerate(data['rows'])for side in['original','candidate']]
 assert observation['attempts']==expected_attempts
 for i,(row,spec)in enumerate(zip(observation['rows'],data['rows'],strict=True)):
  assert(row['family'],row['variant'],row['case'])==(spec['family'],spec['variant'],spec['case'])
  for side in['original','candidate']:
   assert J(out/f'attempt-{i:02d}-{side}.json')==expected_attempts[2*i+(side=='candidate')]
   raw=J(out/f'side-{i:02d}-{side}.json');assert raw==row[side];validate_item(raw,spec['case'])
   sig=audit_transaction(raw);assert observation['signature_audits'][2*i+(side=='candidate')]=={**expected_attempts[2*i+(side=='candidate')],**sig}
 analysis=analyze_observations(observation['rows'],data);assert analysis==observation['analysis']
 dr=J(out/'driver-result.json');assert dr['analysis']==analysis and dr['failure']is None and dr['vm_calls_attempted']==12 and dr['field_mapping_proven']is False and dr['preservation_pass_claimed']is False
 expected_files={'launch.json','stdout.log','stderr.log','observations.json','driver-result.json'}|{f'{kind}-{i:02d}-{side}.json'for i in range(6)for side in['original','candidate']for kind in['attempt','side']}
 assert {f.name for f in out.iterdir()if f.is_file()}==expected_files
 assert not any(f.is_symlink()for f in out.rglob('*'))
 return analysis,dr
def execute(cfg,data,seal):
 supported_running_python(cfg);fresh(cfg);claim=Path(cfg['claim']);out=Path(cfg['out'])
 # Durable exclusive attempt claim precedes setup, child import and all VM calls.
 durable(claim,{'plan_seal':seal,'controller_sha256':H(Path(__file__)),'driver_sha256':H(P/'driver.py'),'candidate_sha256':cfg['candidate_sha256'],'cases':6,'target_sides_limit':12,'attempts':1,'retry_permitted':False})
 result={'state':'CLAIMED','plan_seal':seal,'candidate_sha256':cfg['candidate_sha256'],'preservation_pass_claimed':False,'field_mapping_proven':False,'retry_attempts':0}
 try:
  out.mkdir(exist_ok=False)
  command=[cfg['python'],'-B',str(P/'driver.py'),'--execute','--expected-seal',seal,'--claim-sha256',H(claim)]
  env={'HOME':str(Path.home()),'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','DYLD_LIBRARY_PATH':'/opt/homebrew/opt/expat/lib','PYTHONDONTWRITEBYTECODE':'1'}
  durable(out/'launch.json',{'command':command,'environment':env,'plan_seal':seal,'claim_sha256':H(claim),'source37_sha256':H(P/'controls/preservation-source37.json'),'fixed_cases':6,'target_sides_limit':12})
  with(out/'stdout.log').open('xb')as stdout,(out/'stderr.log').open('xb')as stderr:child=launch_child(command,P/'repo',env,stdout,stderr)
  result['child_returncode']=child.returncode
  analysis,dr=validate_output(out,data);result['analysis']=analysis
  expected_code=0 if analysis['all_original_hypotheses_observed']else 2
  assert child.returncode==dr['returncode']==expected_code
  assert dr['state']==('DIAGNOSTIC_OBSERVATIONS_RECORDED'if expected_code==0 else'COUNTEREVIDENCE_PRESERVED')
  result['state']=dr['state'];result['observations_valid']=True
 except BaseException:result['state']='FAILED_RAW_RECEIPTS_PRESERVED';result['failure']=traceback.format_exc()
 finally:
  try:check_plan(seal,True);result['inputs_source37_candidate_unchanged']=True
  except BaseException:result['inputs_source37_candidate_unchanged']=False;result['after_failure']=traceback.format_exc();result['state']='FAILED_RAW_RECEIPTS_PRESERVED'
  if out.is_dir():
   result['raw_files_sha256']={str(f.relative_to(out)):H(f)for f in out.rglob('*')if not f.is_symlink()and f.is_file()};durable(out/'exit.json',result)
  else:durable(Path(str(claim)+'.failure.json'),result)
 print(json.dumps({k:v for k,v in result.items()if k in['state','child_returncode','observations_valid','inputs_source37_candidate_unchanged','failure']},indent=2))
 return 0 if result['state']=='DIAGNOSTIC_OBSERVATIONS_RECORDED'and result.get('inputs_source37_candidate_unchanged')else 2
def main():
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--expected-seal',required=True);a=p.parse_args();cfg,data=check_plan(a.expected_seal,True);fresh(cfg)
 if not a.execute:print('PASS READONLY: fixed six cases/twelve sides;15 unchanged inputs;6e/source37/Python pins; no helper/native VM import or target execution.');return 0
 return execute(cfg,data,a.expected_seal)
if __name__=='__main__':raise SystemExit(main())

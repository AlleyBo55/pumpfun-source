"""One replay of an unchanged, normally signed existing ordinary CTO suite."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
P=Path(__file__).resolve().parent;R=P/'repo';E=P.parent/'cto-wallet-build-01';OUT=P.parent/'cto-wallet-preservation-01';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();J=lambda p:json.loads(p.read_text())
CAND=E/'analysis/candidate.so';EXPECTED='d75d2872c4281183e170ce7d7795d186745e2428005ceb89aa3df95fe7cab9b1';PYTHON='/Users/shawwalters/Documents/Codex/2026-10-25/go/work/validation-venv/bin/python'
def check():
 for n,h in J(P/'inputs.json').items():assert H(R/n)==h,n
 assert H(CAND)==EXPECTED
 assert not any(f.is_symlink()for f in R.rglob('*'))
def main():
 a=argparse.ArgumentParser();a.add_argument('--execute',action='store_true');a.add_argument('--expected-seal');v=a.parse_args();assert H(P/'manifest.json')==v.expected_seal
 for n,h in J(P/'manifest.json').items():assert H(P/n)==h,n
 check()
 if not v.execute:print('PASS read-only: frozen15inputs + candidate; no VM execution');return 0
 assert not OUT.exists();OUT.mkdir();result={'candidate_sha256':EXPECTED,'case_assertions_unchanged':True,'new_cases':0,'new_fixtures':0,'original_capture':'retained captured Pump with captured dependencies','transaction_signature_verification':'unchanged existing harness, no bypass','full_byte_equality':False,'source_selection_changed':False}
 cmd=[PYTHON,'-B',str(R/'scripts/pump_admin_cto_differential.py'),'--candidate',str(CAND),'--output',str(OUT/'receipt.json')];result['command']=cmd;(OUT/'launch.json').write_text(json.dumps(result,indent=2)+'\n')
 env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','DYLD_LIBRARY_PATH':'/opt/homebrew/opt/expat/lib'}
 try:
  with(OUT/'stdout.log').open('wb')as stdout,(OUT/'stderr.log').open('wb')as stderr:r=subprocess.run(cmd,cwd=R,env=env,stdout=stdout,stderr=stderr)
  result['returncode']=r.returncode
  assert r.returncode==0,'Existing suite reported a failure; do not change assertions'
  receipt=OUT/'receipt.json';assert receipt.is_file(),'Missing receipt'
  data=J(receipt);assert isinstance(data,dict)and data['candidate_sha256']==EXPECTED
  assert isinstance(data['case_count'],int)and data['case_count']>0 and isinstance(data['cases'],list)and len(data['cases'])==data['case_count']
  assert isinstance(data['mismatches'],list)and not data['mismatches']
  assert all(isinstance(row,dict)and row['match']is True for row in data['cases'])
  for row in data['cases']:
   for side in ['original','candidate']:assert row[side]['signatures_verified']is True and row[side]['pool_authority_top_level_signer']is False
  result.update(receipt_valid=True,case_count=data['case_count'],mismatches=data['mismatches'])
 except BaseException as exc:result.update(receipt_valid=False,failure=repr(exc))
 finally:
  for name in ['stdout.log','stderr.log','receipt.json']:
   result[name.replace('.','_')+'_sha256']=H(OUT/name)if(OUT/name).is_file()else None
  try:check();result['inputs_unchanged']=True
  except BaseException as exc:result.update(inputs_unchanged=False,after_error=repr(exc))
  result['passed']=result.get('returncode')==0 and result.get('receipt_valid')is True and result.get('inputs_unchanged')is True
  (OUT/'exit.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k]for k in ['returncode','passed','inputs_unchanged','case_count','mismatches','failure']if k in result},indent=2))
 return 0 if result['passed']else 2
if __name__=='__main__':sys.exit(main())

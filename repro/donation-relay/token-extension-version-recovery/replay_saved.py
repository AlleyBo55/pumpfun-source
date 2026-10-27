from pathlib import Path
import base64,gzip,hashlib,importlib.util,json,sys
from solders.pubkey import Pubkey
from solders.transaction import Transaction
root=Path.cwd();p=root/'repro/donation-relay/distribution-worker-source-recovery/settlement';h=root/'repro/donation-relay/local-validation-proposal/harness_proposal.py'
s=importlib.util.spec_from_file_location('frozen_relay_runner',h);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
candidate=Path(sys.argv[1]);output=Path(sys.argv[2]);original=root/'evidence/dependencies/donation_relay/deployed.so';token22=root/'evidence/dependencies/spl_token_2022/deployed.so';token22pid=Pubkey.from_string('TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb')
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rows=[];failed=[];files=sorted(list(p.glob('*-cases.json'))+[p/'idl-rejections.json']+list(p.glob('runtime-*/comparison.json')))
for file in files:
 report=json.loads(file.read_text())
 for i,row in enumerate(report['cases']):
  fixture=row['fixture'];saved=row.get('original',row.get('results',{}).get('original'));assert saved
  tx=Transaction.from_bytes(base64.b64decode(saved['transaction_base64']));keys={Pubkey.from_string(k)for k in saved['before']}
  results={}
  for label,binary in [('original',original),('candidate',candidate)]:
   vm=m.vm_for(binary,root,fixture['accounts']);vm.add_program_from_file(token22pid,token22);results[label]=m.run_one(vm,tx,keys)
  x,y=m.comparable(results['original']),m.comparable(results['candidate']);reproduced=x==m.comparable(saved);diff=[k for k in x if x[k]!=y[k]]
  name=str(file.relative_to(p))+':'+str(i);rows.append(dict(id=name,fixture=fixture,original_reproduced=reproduced,original=results['original'],candidate=results['candidate'],differences=diff))
  if diff or not reproduced:failed.append(dict(id=name,differences=diff,original_reproduced=reproduced));print(failed[-1],flush=True)
 print(file.name,len(rows),'rows',len(failed),'failures',flush=True)
result=dict(scope='Fresh signed replay of the 536 saved Relay fixtures with unchanged comparison exclusions; not exhaustive equivalence.',original_sha256=H(original),candidate_sha256=H(candidate),runner_sha256=H(__file__),harness_sha256=H(h),token2022_sha256=H(token22),input_reports={str(f.relative_to(root)):H(f) for f in files},cases=rows,failures=failed,case_count=len(rows));output.write_bytes(gzip.compress(json.dumps(result,separators=(',',':')).encode(),mtime=0));print('FINAL',len(rows),len(failed));sys.exit(bool(failed))

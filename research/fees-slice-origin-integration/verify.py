"""Verify source-only integration of four location records on the current frontier."""
from pathlib import Path
import gzip,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def receipt(n):return json.loads(gzip.decompress((HERE/f'receipts/{n}.json.gz').read_bytes()))
def main():
 manifest=load(HERE/'manifest.json');assert set(manifest)=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()and p.name!='manifest.json'and '__pycache__'not in p.parts}
 for n,h in manifest.items():
  p=HERE/n;assert not p.is_symlink()and p.resolve().is_relative_to(HERE)and sha(p.read_bytes())==h,n
 for n,h in load(HERE/'parents.json').items():assert sha((ROOT/n).read_bytes())==h,n
 e=load(HERE/'experiment.json');parent=load(ROOT/e['parent']/'experiment.json');base=e['variants']['control'];v=e['variants']['origins'];assert e['control_reused']and base['input_sha256']==parent['variants']['origins']['input_sha256']and base['source_paths']==parent['variants']['origins']['source_paths']
 for kind in ['candidate','symbols']:assert all(base['files'][kind][k]==parent['variants']['origins']['files'][kind][k]for k in ['sha256','bytes'])
 for row in [base,v]:
  assert len(row['input_sha256'])==36 and set(row['source_paths'])==set(row['input_sha256'])
  for n,h in row['input_sha256'].items():assert sha((ROOT/row['source_paths'][n]).read_bytes())==h,n
 state='programs/pump-fees/src/state.rs';assert {n for n,h in base['input_sha256'].items()if v['input_sha256'][n]!=h}=={state}
 old=(ROOT/base['source_paths'][state]).read_text();new=(ROOT/v['source_paths'][state]).read_text();lines=old.splitlines(keepends=True)
 for number in [393,446]:
  i=number-1;assert lines[i].strip()=='merged[offset..end].clone_from_slice(incoming);'and all(x=='\n'for x in lines[i+5:i+12]);block=lines[i:i+5];block[0]='    '+block[0];lines[i:i+12]=['\n']*5+block+['\n']*2
 assert new==''.join(lines)and ''.join(old.split())==''.join(new.split())
 prior=load(ROOT/'research/fees-slice-origin-contract/experiment.json')
 assert base['input_sha256'][state]==prior['variants']['control']['input_sha256'][state]and v['input_sha256'][state]==prior['variants']['origins']['input_sha256'][state]
 launch=load(HERE/'builds/origins-launch.json');result=load(HERE/'builds/origins-result.json');log=(HERE/'builds/origins-build.log').read_bytes()
 assert launch['inputs']==v['input_sha256']and result['compiled_root']and result['source_unchanged']and result['exit_code']==0 and sha(log)==result['log_sha256']and log.count(b'--crate-name pump_fees_candidate ')==1
 assert launch['rustc_sha256']=='c8807b7ebede8578ac5a257ea333780f9d89bd356064fd8184af7e996cb71a97'and 'sbpf-solana-solana'in launch['command']
 for kind in ['candidate','symbols']:assert result[kind+'_sha256']==v['files'][kind]['sha256']
 r=module('integrated_contract',HERE/'analyze.py').analyze();assert r==json.loads(gzip.decompress((HERE/'analysis.json.gz').read_bytes()))and r['entire_text_raw_equal']and len(r['byte_changes'])==8
 for label in ['control','origins']:
  a=r['variants'][label];assert len(a['unique_pairs'])==376 and len(a['unmatched_original'])==62 and not a['equals_original_capture']and not a['equals_original_elf_extent']
 candidate=v['files']['candidate']['sha256'];original=sha((ROOT/'evidence/original/pump_fees/deployed.so').read_bytes());full=receipt('origins-full');assert full['candidate_sha256']==candidate and full['original_sha256']==original and full['case_count']==17331 and len(full['suites'])==18 and not full['mismatches']
 for s in full['suites'].values():assert s['candidate_sha256']==candidate and s['original_sha256']==original and not s.get('mismatches',s.get('failures',[]))
 f=receipt('origins-flags');assert f['candidate_sha256']==candidate and f['original_sha256']==original and f['case_count']==len(f['cases'])==1542 and not f['failures']and not f['compute_differences']and all(x['original']==x['candidate']for x in f['cases'])
 assert {(x['cap'],x['pool'],x['flag_hex'])for x in f['cases']}=={(cap,pool,flag)for cap in (0,1000,2**128-1)for pool in (0,1)for flag in ['']+[bytes([b]).hex()for b in range(256)]}
 for name,path,fn in [('precedence','fees-exotic-growth-precedence/verify.py','check_boundary'),('optional','fees-optional-account-ownership/optional_cases.py','validate'),('seeds','fees-social-seed-vector/seed_cases.py','validate'),('logs','fees-extend-size-logs/log_cases.py','validate'),('mint','fees-crank-interface-mint/mint_cases.py','validate')]:
  f=receipt('origins-'+name);assert f['candidate_sha256']==candidate and f['original_sha256']==original;assert not getattr(module('integration_'+name,ROOT/'research'/path),fn)(f)
 print('PASS: four location contracts integrated; exactly eight data bytes; full text unchanged; 376 unique / 62 unmatched; fresh regressions')
if __name__=='__main__':main()

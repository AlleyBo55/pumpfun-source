"""Verify full-buffer source recovery, original helper and scoped test receipts."""
from pathlib import Path
import ast,gzip,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def receipt(n):return json.loads(gzip.decompress((HERE/f'receipts/{n}.json.gz').read_bytes()))
def expected_source(old,consuming):
 before='''    fn try_deserialize_unchecked(buf: &mut &[u8]) -> Result<Self> {
        if buf.len() < 2504 { return Err(ProgramError::InvalidAccountData.into()); }
        if buf.len() < 4065 { return Self::read_legacy(buf); }
        if buf.len() < 4089 { return Self::read_stable(buf); }
        Self::read_full(buf)
    }'''
 lines='        *buf = &buf[8..];\n        decode_fee_config_payload(buf)'if consuming else'        let mut data = &buf[8..];\n        decode_fee_config_payload(&mut data)'
 after='    fn try_deserialize_unchecked(buf: &mut &[u8]) -> Result<Self> {\n        if buf.len() < 8 { return Err(ProgramError::InvalidAccountData.into()); }\n'+lines+'\n\n    }'
 tail='''
#[inline(never)]
fn decode_fee_config_payload(buf: &mut &[u8]) -> Result<FeeConfig> {
    if buf.len() < 2504 { return Err(ProgramError::InvalidAccountData.into()); }
    if buf.len() < 4065 { return FeeConfig::read_legacy(buf); }
    if buf.len() < 4089 { return FeeConfig::read_stable(buf); }
    FeeConfig::read_full(buf)
}
'''
 assert old.count(before)==1 and old.count('        Self::try_deserialize_unchecked(buf)')==1
 return old.replace('        Self::try_deserialize_unchecked(buf)','        decode_fee_config_payload(buf)',1).replace(before,after)+tail
def main():
 manifest=load(HERE/'manifest.json');assert set(manifest)=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()and p.name!='manifest.json'and '__pycache__'not in p.parts}
 for n,h in manifest.items():assert sha((HERE/n).read_bytes())==h,n
 for n,h in load(HERE/'parents.json').items():assert sha((ROOT/n).read_bytes())==h,n
 e=load(HERE/'experiment.json');parent=load(ROOT/e['parent']/'experiment.json')['variants']['origins'];base=e['variants']['control'];assert e['control_reused']and base['input_sha256']==parent['input_sha256']and base['source_paths']==parent['source_paths'];name='programs/pump-fees/src/types.rs'
 for kind in ['candidate','symbols']:assert all(base['files'][kind][k]==parent['files'][kind][k]for k in ['sha256','bytes'])
 for label,v in e['variants'].items():
  assert len(v['input_sha256'])==36 and set(v['input_sha256'])==set(v['source_paths'])
  for n,h in v['input_sha256'].items():assert sha((ROOT/v['source_paths'][n]).read_bytes())==h,n
  for kind,d in v['files'].items():
   raw=gzip.decompress((HERE/d['path']).read_bytes());assert sha(raw)==d['sha256']and len(raw)==d['bytes']
  if label=='control':continue
  assert {n for n,h in base['input_sha256'].items()if v['input_sha256'][n]!=h}=={name}
  assert (ROOT/v['source_paths'][name]).read_text()==expected_source((ROOT/base['source_paths'][name]).read_text(),label=='origins')
  launch=load(HERE/f'builds/{label}-launch.json');result=load(HERE/f'builds/{label}-result.json');log=(HERE/f'builds/{label}-build.log').read_bytes();assert launch['inputs']==v['input_sha256']and result['compiled_root']and result['source_unchanged']and result['exit_code']==0 and sha(log)==result['log_sha256']and log.count(b'--crate-name pump_fees_candidate ')==1
  assert launch['rustc_sha256']=='c8807b7ebede8578ac5a257ea333780f9d89bd356064fd8184af7e996cb71a97'
  for kind in ['candidate','symbols']:assert result[kind+'_sha256']==v['files'][kind]['sha256']
 r=module('prefix_analysis',HERE/'analyze.py').analyze();assert r==json.loads(gzip.decompress((HERE/'analysis.json.gz').read_bytes()))
 assert r['deltas']==dict(local=dict(added=[],lost=[]),origins=dict(added=[18384],lost=[]))and r['raw_delta']==dict(added=[],lost=[])
 for label,u,left in [('control',394,44),('local',394,44),('origins',395,43)]:
  row=r['variants'][label];assert len(row['unique_pairs'])==u and len(row['unmatched_original'])==left and not row['whole_file_equal']
  assert r['boundaries'][label]['helper']['bytes']==(1024 if label=='control' else 1144)
 assert len(r['details']['18384']['calls'])==11 and all(c['equal']for d in r['details'].values()for c in d['calls'])
 assert all(x==r['owner_constants']['original']for x in r['owner_constants'].values())and r['owner_constants']['original']==['00'*32,'0c35ffa9055a8e568da8f7bc075615274cf1c92ca41f40009c516aa414c27c70']
 for x in r['message_records'].values():assert x['message']=='failed to fill whole buffer'and x['length']==27 and x['tail']==37 and x['relocation_info']==8 and bytes.fromhex(x['raw'])[8:]==bytes.fromhex(r['message_records']['original']['raw'])[8:]
 assert r['helper_tokens']['origins']==r['helper_tokens']['original'];a=r['helper_tokens']['original'];b=r['helper_tokens']['local'];assert len(a)==len(b);diff=[(x,y)for x,y in zip(a,b)if x!=y];assert len(diff)==22
 for x,y in diff:
  assert x[:3]==y[:3]
  assert (x[0]==7 and x[3]==y[3])or(x[0]in[121,123]and x[4]==y[4]and(10 in x[1:3]))
 for label,variant,code in [('parent','control',101),('recovered','origins',0)]:
  v=e['variants'][variant];launch=load(HERE/f'host/{label}-launch.json');result=load(HERE/f'host/{label}-result.json');log=(HERE/f'host/{label}-build.log').read_bytes();assert launch['test_sha256']==sha((HERE/'host/host-tests.rs').read_bytes())and launch['rustc'].startswith('rustc 1.94.0')and 'host: aarch64-apple-darwin'in launch['rustc']
  expected=dict(v['input_sha256']);lib='programs/pump-fees/src/lib.rs';expected[lib]=sha((ROOT/v['source_paths'][lib]).read_bytes()+launch['lib_append'].encode());assert expected==launch['inputs']
  assert result['exit_code']==result['expected_exit_code']==code and result['source_unchanged']and result['compiled_root']and sha(log)==result['log_sha256']and log.count(b'--crate-name pump_fees_candidate ')==1
  if label=='parent':assert b'test result: FAILED. 0 passed; 1 failed;'in log
  else:assert b'test result: ok. 3 passed; 0 failed;'in log and all(x in log for x in [b'PREFIX_CASES=18',b'BOUNDARY_CASES=11',b'VERSION_CASES=6'])
 ast.parse((HERE/'run_host_tests.py').read_text())
 v=e['variants']['origins'];candidate=v['files']['candidate']['sha256'];original=sha((ROOT/'evidence/original/pump_fees/deployed.so').read_bytes());full=receipt('origins-full');assert full['candidate_sha256']==candidate and full['original_sha256']==original and full['case_count']==17331 and len(full['suites'])==18 and not full['mismatches']
 for s in full['suites'].values():assert s['candidate_sha256']==candidate and s['original_sha256']==original and not s.get('mismatches',s.get('failures',[]))
 f=receipt('origins-flags');assert f['candidate_sha256']==candidate and f['original_sha256']==original and f['case_count']==len(f['cases'])==1542 and not f['failures']and not f['compute_differences']and all(x['original']==x['candidate']for x in f['cases'])
 assert {(x['cap'],x['pool'],x['flag_hex'])for x in f['cases']}=={(cap,pool,flag)for cap in (0,1000,2**128-1)for pool in (0,1)for flag in ['']+[bytes([b]).hex()for b in range(256)]}
 for name,path,fn in [('precedence','fees-exotic-growth-precedence/verify.py','check_boundary'),('optional','fees-optional-account-ownership/optional_cases.py','validate'),('seeds','fees-social-seed-vector/seed_cases.py','validate'),('logs','fees-extend-size-logs/log_cases.py','validate'),('mint','fees-crank-interface-mint/mint_cases.py','validate')]:
  f=receipt('origins-'+name);assert f['candidate_sha256']==candidate and f['original_sha256']==original;assert not getattr(module('buyback_update_'+name,ROOT/'research'/path),fn)(f)
 print('PASS: full-buffer unchecked helper; 11/11 local callees; 35 native contract cases; 395 unique / 43 unmatched; SBF regressions exclude fixed-admin initialization')
if __name__=='__main__':main()

"""Verify controlled sweep ownership recovery, complete bodies and regressions."""
from pathlib import Path
import gzip,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def receipt(n):return json.loads(gzip.decompress((HERE/f'receipts/{n}.json.gz').read_bytes()))
def changed_source(old,boxes,owned):
 start=old.index("pub struct SweepBuyback<'info>");end=old.index('\n}',start);block=old[start:end]
 if boxes:
  for a,b in [("pub buyback_vault:Account<'info,BuybackVault>","pub buyback_vault:Box<Account<'info,BuybackVault>>"),("pub buyback_vault_ata:InterfaceAccount<'info,anchor_spl::token_interface::TokenAccount>","pub buyback_vault_ata:Box<InterfaceAccount<'info,anchor_spl::token_interface::TokenAccount>>"),("pub destination_ata:InterfaceAccount<'info,anchor_spl::token_interface::TokenAccount>","pub destination_ata:Box<InterfaceAccount<'info,anchor_spl::token_interface::TokenAccount>>")]:
   assert block.count(a)==1;block=block.replace(a,b)
 for field in owned:
  a=f"pub {field}:UncheckedAccount<'info>";assert block.count(a)==1;block=block.replace(a,f"pub {field}:AccountInfo<'info>")
 return old[:start]+block+old[end:]
def main():
 manifest=load(HERE/'manifest.json');assert set(manifest)=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()and p.name!='manifest.json'and '__pycache__'not in p.parts}
 for n,h in manifest.items():assert sha((HERE/n).read_bytes())==h,n
 for n,h in load(HERE/'parents.json').items():assert sha((ROOT/n).read_bytes())==h,n
 e=load(HERE/'experiment.json');parent=load(ROOT/e['parent']/'experiment.json')['variants']['origins'];base=e['variants']['control'];assert e['control_reused']and base['input_sha256']==parent['input_sha256']and base['source_paths']==parent['source_paths']
 for kind in ['candidate','symbols']:assert all(base['files'][kind][k]==parent['files'][kind][k]for k in ['sha256','bytes'])
 name='programs/pump-fees/src/buyback.rs';old=(ROOT/base['source_paths'][name]).read_text();changes={'boxes':(True,[]),'owned':(False,['destination','event_authority','program']),'all_owned':(True,['destination','event_authority','program']),'origins':(True,['event_authority','program'])}
 for label,row in e['variants'].items():
  assert len(row['input_sha256'])==36 and set(row['source_paths'])==set(row['input_sha256'])
  for n,h in row['input_sha256'].items():assert sha((ROOT/row['source_paths'][n]).read_bytes())==h,n
  for kind,d in row['files'].items():
   raw=gzip.decompress((HERE/d['path']).read_bytes());assert sha(raw)==d['sha256']and len(raw)==d['bytes']
  if label=='control':continue
  assert {n for n,h in base['input_sha256'].items()if row['input_sha256'][n]!=h}=={name}
  assert (ROOT/row['source_paths'][name]).read_text()==changed_source(old,*changes[label])
  launch=load(HERE/f'builds/{label}-launch.json');result=load(HERE/f'builds/{label}-result.json');log=(HERE/f'builds/{label}-build.log').read_bytes();assert launch['inputs']==row['input_sha256']and result['compiled_root']and result['source_unchanged']and result['exit_code']==0 and sha(log)==result['log_sha256']and log.count(b'--crate-name pump_fees_candidate ')==1
  assert launch['rustc_sha256']=='c8807b7ebede8578ac5a257ea333780f9d89bd356064fd8184af7e996cb71a97'and 'sbpf-solana-solana'in launch['command']
  for kind in ['candidate','symbols']:assert result[kind+'_sha256']==row['files'][kind]['sha256']
 r=module('sweep_context_analysis',HERE/'analyze.py').analyze();assert r==json.loads(gzip.decompress((HERE/'analysis.json.gz').read_bytes()))
 for label in e['variants']:
  row=r['variants'][label];assert len(row['unique_pairs'])==(385 if label=='origins'else 382)and len(row['unmatched_original'])==(53 if label=='origins'else 56)and not row['equals_original_capture']and not row['equals_original_elf_extent']
  if label!='control':assert r['deltas'][label]==dict(added_original_windows=[370640,379920,651272]if label=='origins'else[],lost_original_windows=[])
 assert r['raw_delta']==dict(added_original_windows=[],lost_original_windows=[])
 details={x['original']['address']:x for x in r['details']};assert [(details[k]['original']['bytes'],len(details[k]['calls']))for k in [370640,379920,651272]]==[(9280,77),(944,12),(1320,6)]
 assert all(c['equal']for k,d in details.items()if k not in [651272,656832]for c in d['calls'])
 assert [(c['offset'],c['original_target'])for c in details[651272]['calls']if not c['equal']]==[(688,120816)]
 assert [(c['offset'],c['original_target'])for c in details[656832]['calls']if not c['equal']]==[(160,408640),(464,147944)]
 assert all(v==r['exit_data']['original']for v in r['exit_data'].values())and r['exit_data']['original']['labels']==['buyback_vault','destination_ata','buyback_vault_ata']
 t=r['exit_tokens'];assert t['original']==t['origins'];assert [(a,b)for a,b in zip(t['original'],t['boxes'])if a!=b]==[([121,2,8,240,0],[121,2,8,144,0]),([121,1,8,248,0],[121,1,8,152,0]),([121,1,8,256,0],[121,1,8,160,0])]
 assert len(r['preserved_slice_contract']['locations'])==4 and len(r['preserved_common_locations'])==2 and r['preserved_buyback_origin']==dict(path='programs/pump-fees/src/instructions/buyback/mod.rs',line=12,error=4101)
 v=e['variants']['origins'];candidate=v['files']['candidate']['sha256'];original=sha((ROOT/'evidence/original/pump_fees/deployed.so').read_bytes());full=receipt('origins-full');assert full['candidate_sha256']==candidate and full['original_sha256']==original and full['case_count']==17331 and len(full['suites'])==18 and not full['mismatches']
 for s in full['suites'].values():assert s['candidate_sha256']==candidate and s['original_sha256']==original and not s.get('mismatches',s.get('failures',[]))
 f=receipt('origins-flags');assert f['candidate_sha256']==candidate and f['original_sha256']==original and f['case_count']==len(f['cases'])==1542 and not f['failures']and not f['compute_differences']and all(x['original']==x['candidate']for x in f['cases'])
 assert {(x['cap'],x['pool'],x['flag_hex'])for x in f['cases']}=={(cap,pool,flag)for cap in (0,1000,2**128-1)for pool in (0,1)for flag in ['']+[bytes([b]).hex()for b in range(256)]}
 for name,path,fn in [('precedence','fees-exotic-growth-precedence/verify.py','check_boundary'),('optional','fees-optional-account-ownership/optional_cases.py','validate'),('seeds','fees-social-seed-vector/seed_cases.py','validate'),('logs','fees-extend-size-logs/log_cases.py','validate'),('mint','fees-crank-interface-mint/mint_cases.py','validate')]:
  f=receipt('origins-'+name);assert f['candidate_sha256']==candidate and f['original_sha256']==original;assert not getattr(module('sweep_'+name,ROOT/'research'/path),fn)(f)
 print('PASS: sweep parser/exit/wrapper; 89/89 parser+exit callees; explicit business-body frontier; 385 unique / 53 unmatched; fresh regressions')
if __name__=='__main__':main()

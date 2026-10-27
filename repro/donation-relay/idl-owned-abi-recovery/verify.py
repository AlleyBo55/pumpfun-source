#!/usr/bin/env python3
"""Offline full-body/data/receipt verification. No VM or target execution."""
import argparse,base64,copy,gzip,hashlib,importlib.util,json,re,struct,tomllib
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
H=lambda b:hashlib.sha256(b).hexdigest()
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def read_json(path):
 raw=path.read_bytes();return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
def comparable(row):
 out={k:row[k] for k in ['error','inner_instructions','return_data']}
 out['logs']=[x for x in row['logs'] if re.fullmatch(r'Program \S+ consumed \d+ of \d+ compute units',x) is None]
 relay='RLAYHr9TRFcKB2ubYQhspcnXiaGpaVzNQvHytt47RZu'
 for when in ['before','after']:
  out[when]=copy.deepcopy(row[when]);v=out[when].get(relay)
  if v:
   for field in ['data_length','data_sha256','data_base64']:v.pop(field)
   v['lamports']-=row['before'][relay]['lamports']
 return out

def main(signatures=False,current=False):
 for n,h in read_json(P/'manifest.json').items():assert H((P/n).read_bytes())==h,n
 for n,h in read_json(P/'external-inputs.json').items():assert H((ROOT/n).read_bytes())==h,n
 a=mod('framework_recovery_elf',P/'analyze.py');decoder=mod('framework_recovery_selectors',P/'selector_helpers.py');wire=mod('framework_recovery_wire',P/'receipt_helpers.py')
 original_path=ROOT/'evidence/dependencies/donation_relay/deployed.so';original=a.Elf(original_path.read_bytes());windows=read_json(P/'original-windows.json')
 frozen={x['case']['name']:x for x in read_json(ROOT/'repro/donation-relay/local-validation-proposal/fixture-blueprints.json')}
 baseline_source=read_json(ROOT/'repro/donation-relay/decoded-business-origins/message-and-tip/source-manifest.json')
 stages=read_json(P/'stages.json');summaries={r['stage']:r for r in read_json(P/'summary.json')};counts=dict(source_builds=0,receipt_cases=0,signature_fields=0)
 def check_tx(rows,fixture):
  raw=base64.b64decode(rows[0]['transaction_base64']);assert all(r['transaction_base64']==rows[0]['transaction_base64'] for r in rows)
  tx=wire.parse(raw);keys=list(map(wire.b58,tx['keys']));budget,call=tx['instructions'];assert len(tx['instructions'])==2
  assert keys[budget[0]]=='ComputeBudget111111111111111111111111111111' and budget[2]==b'\2'+(1400000).to_bytes(4,'little')
  assert keys[call[0]]==wire.RELAY and call[2].hex()==fixture['instruction_hex']
  assert [keys[i] for i in call[1]]==[x['pubkey'] for x in fixture['instruction_accounts']]
  privileges={x['pubkey']:(x['signer'],x['writable']) for x in fixture['instruction_accounts']};privileges[keys[0]]=(True,True);privileges[wire.RELAY]=(False,False);privileges[keys[budget[0]]]=(False,False);assert set(keys)==set(privileges)
  for i,k in enumerate(keys):
   signer=i<tx['required'];writable=i<tx['required']-tx['readonly_signers'] if signer else i<len(keys)-tx['readonly_unsigned'];assert (signer,writable)==privileges[k]
  for row in rows:
   assert row['signature_verification']==[True]*tx['required'] and row['metadata']['signature']==wire.b58(tx['signatures'][0])
   for field in ['logs','inner_instructions','return_data']:assert row[field]==row['metadata'][field]
   if row['error'] is not None:assert all(row['before'][k]==row['after'][k] for k in row['before'] if k!=keys[0])
   counts['signature_fields']+=tx['required']
  if signatures:
   from solders.signature import Signature
   from solders.pubkey import Pubkey
   assert all(Signature.from_bytes(s).verify(Pubkey.from_bytes(k),tx['message']) for s,k in zip(tx['signatures'],tx['keys']))
  return keys
 for entry in stages:
  name=entry['name'];d=P/name;source=read_json(d/'source-manifest.json')
  assert all(H((d/'source'/n).read_bytes())==h for n,h in source.items())
  build=read_json(d/'build-result.json');assert build['returncode']==0 and build['source_unchanged']
  assert H((d/'build.log').read_bytes())==build.get('log_sha256',build.get('build_log_sha256'))
  assert H((d/'candidate.so').read_bytes())==build['candidate_sha256']
  assert H((d/'unstripped.so').read_bytes())==build['unstripped_sha256']
  derived=a.analyze(d,original_path,P/'original-windows.json')
  for n,v in derived.items():
   path=P/(n+'.gz') if n=='original-function-ledger.json' else d/(n if n.endswith('.gz') else n+'.gz')
   assert read_json(path)==v,(name,n)
  summary=derived['comparison-summary.json'];assert not summary['whole_file_equal']
  assert summary['original_normalized_match_windows']==summaries[name]['normalized_windows']
  assert summary['original_raw_match_windows']==summaries[name]['raw_windows']
  counts['source_builds']+=1
  # All external packages remain exactly the accepted registry lock entries.
  old=tomllib.loads((ROOT/'repro/donation-relay/decoded-business-origins/message-and-tip/source/Cargo.lock').read_text())['package'];new=tomllib.loads((d/'source/Cargo.lock').read_text())['package']
  registry=lambda ps:{(v['name'],v['version'],v.get('source')):v for v in ps if 'source' in v}
  assert registry(old)==registry(new)
  proof=d/'selector-proof-all77.json'
  if proof.exists():
   records=read_json(proof);codes=read_json(d/'framework-codes.json');assert len(records)==len(codes)==77
   candidate=a.Elf((d/'unstripped.so').read_bytes());fs=derived['candidate-function-ledger.json']
   ni=next(i for i,f in enumerate(fs) if any('framework_codes9ErrorCode4name' in n for n in f['names']));mi=next(i for i,f in enumerate(fs) if any('framework_codes..ErrorCode' in n and 'core..fmt..Display' in n and '$GT$3fmt' in n for n in f['names']))
   for record,code in zip(records,codes):
    assert record['code']==code['code']
    for kind,oi,ci in [('name',296,ni),('message',298,mi)]:
     for label,e,f in [('original',original,windows[oi]),('candidate',candidate,fs[ci])]:
      result=decoder.select(e,f['start'],f['bytes'],code['code'],kind);assert e.at(result['pointer'],result['length']).decode()==code[kind]
      result['selected_bytes_sha256']=H(e.at(result['pointer'],result['length']));assert result==record['selections'][kind][label]
  program_proof=d/'program-data-proof-all34.json'
  if program_proof.exists():
   records=read_json(program_proof);codes=read_json(d/'business-codes.json');assert len(records)==len(codes)==34
   candidate=a.Elf((d/'unstripped.so').read_bytes());fs=derived['candidate-function-ledger.json']
   ni=next(i for i,f in enumerate(fs) if any('business_error_codes9ErrorCode4name' in n for n in f['names']));mi=next(i for i,f in enumerate(fs) if any('business_error_codes..ErrorCode' in n and 'core..fmt..Display' in n for n in f['names']))
   for record,code in zip(records,codes):
    assert record['code']==code['code'] and record['variant']==code['code']-6000
    for kind,oi,ci,fn in [('name',114,ni,decoder.name_value),('message',116,mi,decoder.message_value)]:
     for label,e,f in [('original',original,windows[oi]),('candidate',candidate,fs[ci])]:
      result=fn(e,f['start'],f['bytes'],code['variant']);assert result['bytes']==code[kind] and result==record['decoded'][kind][label]
  for rd in sorted(d.glob('runtime-*')):
   if not rd.is_dir():continue
   run=read_json(rd/'comparison.json');proc=read_json(rd/'process-result.json');launch=read_json(rd/'launch.json')
   assert proc['returncode']==0 and proc['candidate_unchanged'] and proc['harness_unchanged']
   assert launch['bindings']==dict(launch['old_bindings'],candidate=build['candidate_sha256'])
   assert run['candidate_sha256']==build['candidate_sha256'] and run['all_requested_completed'] and run['passed']==run['case_count']
   for result in run['cases']:
    case=result['case'];f=frozen[case['name']];assert result['fixture']==f['fixture'] and case==f['case']
    left,right=result['original'],result['candidate'];keys=check_tx([left,right],f['fixture'])
    assert not result['mismatches'] and comparable(left)==comparable(right)
    if left['error'] is None:
     assert case['expected_error'] is None
     for row in [left,right]:wire.independent_effects(case,f['fixture'],row,keys)
    counts['receipt_cases']+=1
  if (d/'header-cases.json').exists():
   report=read_json(d/'header-cases.json');assert report['all_passed'] and report['normal_signature_blockhash_history_checks'] and len(report['cases'])==6
   assert report['binary_hashes']['candidate']==build['candidate_sha256']
   assert report['binary_hashes']['original']==H(original.b) and report['binary_hashes']['baseline']=='836d2ffbec4c437cf9447138e4e54de886744cf4841aeadb34aaeaf7e0249a8f'
   for row in report['cases']:
    f=frozen[row['base_case']['name']];assert f['case']==row['base_case'] and f['fixture']==row['base_fixture']
    expected=copy.deepcopy(row['base_fixture']);mutation=row['mutation'];account=mutation['account'];raw=base64.b64decode(expected['accounts'][account]['data_base64']);assert raw[:8].hex()==mutation['old_discriminator'] and mutation['new_discriminator']=='00'*8
    expected['accounts'][account]['data_base64']=base64.b64encode(bytes(8)+raw[8:]).decode();assert expected==row['fixture']
    left,prior,right=[row['results'][n] for n in ['original','baseline','candidate']];check_tx([left,prior,right],row['fixture']);assert comparable(left)==comparable(prior)==comparable(right)
    assert 'Custom(3002)' in left['error'].replace(' ','')
    assert any(('AnchorError caused by account: '+row['expected_outer_name']+'. Error Code: AccountDiscriminatorMismatch.') in log for log in left['logs'])
    counts['receipt_cases']+=1
 d=P/'pubkey-type';report=read_json(d/'idl-rejections.json');assert report['all_requested_completed'] and report['passed']==9 and len(report['cases'])==9
 assert report['binary_hashes']['candidate']==H((d/'candidate.so').read_bytes())
 assert report['binary_hashes']['control']==H((ROOT/'repro/donation-relay/framework-crate-recovery/full-enums-v148/candidate.so').read_bytes())
 assert report['binary_hashes']['original']==H(original.b)
 for result in report['cases']:
  f=frozen[result['case']['name']];assert result['case']==f['case'] and result['base_fixture']==f['fixture']
  expected=copy.deepcopy(f['fixture']);mutation=result['mutation'];kind=mutation['kind'];account=mutation['account'];data=base64.b64decode(expected['accounts'][account]['data_base64'])
  if kind=='truncate':expected['accounts'][account]['data_base64']=base64.b64encode(data[:mutation['value']]).decode()
  elif kind=='owner':
   name='relay-local-data/rejection-wrong-owner';expected['accounts'][account]['owner']=wire.b58(hashlib.sha256(name.encode()).digest())
  elif kind=='uninitialized':expected['accounts'][account].update(owner=wire.SYSTEM,lamports=0,data_base64='')
  elif kind=='authority':
   authority=hashlib.sha256(b'relay-local-data/rejection-wrong-authority').digest();expected['accounts'][account]['data_base64']=base64.b64encode(data[:8]+authority+data[40:]).decode()
  elif kind=='readonly':expected['instruction_accounts'][0]['writable']=False
  else:raise AssertionError(kind)
  assert expected==result['fixture']
  left,control,right=[result['results'][n] for n in ['original','control','candidate']];check_tx([left,control,right],result['fixture'])
  assert comparable(left)==comparable(control)==comparable(right) and all(not x for x in result['mismatches'].values())
  assert 'Custom('+str(result['expected_code'])+')' in left['error'].replace(' ','')
  counts['receipt_cases']+=1
 assert (P/'borsh-deserialize/candidate.so').read_bytes()==(P/'pubkey-type/candidate.so').read_bytes()
 assert (P/'borsh-deserialize/unstripped.so').read_bytes()==(P/'pubkey-type/unstripped.so').read_bytes()
 prov=read_json(P/'primary-account-codegen-provenance.json');assert H((P/'primary-account-codegen.rs').read_bytes())==prov['sha256']
 assert prov['archive_sha256']==read_json(P/'primary-account-registry-entry.json')['cksum'] and prov['source_matches_archive']
 selected=P/'pubkey-type';assert summaries['pubkey-type']['normalized_windows']==243
 prior=read_json(ROOT/'repro/donation-relay/framework-crate-recovery/full-enums-v148/match-ledger.json.gz');latest=read_json(selected/'match-ledger.json.gz')
 added=[r['ordinal'] for r,o in zip(latest,prior) if r['normalized_candidate_indices'] and not o['normalized_candidate_indices']]
 lost=[r['ordinal'] for r,o in zip(latest,prior) if not r['normalized_candidate_indices'] and o['normalized_candidate_indices']]
 assert added==[281,287,346,347,352,358] and lost==[388]
 proof=P/'current-source-proof'
 if proof.exists():
  result=read_json(proof/'build-result.json');assert result['returncode']==0 and result['source_unchanged']
  assert H((proof/'build.log').read_bytes())==result['log_sha256']
  for n in ['candidate.so','unstripped.so']:assert (proof/n).read_bytes()==(selected/n).read_bytes()
  assert read_json(proof/'source-manifest.json')==read_json(selected/'source-manifest.json');counts['source_builds']+=1
 if current:assert all(H((ROOT/'programs/donation-relay'/n).read_bytes())==h for n,h in read_json(selected/'source-manifest.json').items())
 import difflib
 patch='';before=ROOT/'repro/donation-relay/framework-crate-recovery/full-enums-v148/source'
 for n in read_json(selected/'source-manifest.json'):
  old=(before/n).read_text();new=(selected/'source'/n).read_text()
  if old!=new:patch+=''.join(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile='a/'+n,tofile='b/'+n))
 assert patch==(P/'integration.patch').read_text()
 print(json.dumps(dict(verified=True,**counts,current_source_checked=current,cryptographic_signatures_checked=signatures,selected_complete_normalized_windows=243,total_original_windows=492,whole_original_byte_identity=False,new_vm_execution=False)))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--runtime',action='store_true');ap.add_argument('--current',action='store_true');args=ap.parse_args();main(args.runtime,args.current)

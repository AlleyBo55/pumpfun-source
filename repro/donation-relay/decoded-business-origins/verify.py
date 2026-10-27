#!/usr/bin/env python3
"""Offline reconstruction, ELF and saved signed-receipt verification; no VM."""
import argparse,base64,difflib,gzip,hashlib,importlib.util,json,re,struct
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
H=lambda b:hashlib.sha256(b).hexdigest()
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def comparable(row):
 out={k:row[k] for k in ['error','inner_instructions','return_data']}
 out['logs']=[x for x in row['logs'] if re.fullmatch(r'Program \S+ consumed \d+ of \d+ compute units',x) is None]
 relay='RLAYHr9TRFcKB2ubYQhspcnXiaGpaVzNQvHytt47RZu'
 for stage in ['before','after']:
  out[stage]=json.loads(json.dumps(row[stage]));a=out[stage].get(relay)
  if a:
   for field in ['data_length','data_sha256','data_base64']:a.pop(field)
   a['lamports']-=row['before'][relay]['lamports']
 return out

def main(runtime=False,current=False):
 for n,h in json.loads((P/'manifest.json').read_text()).items():assert H((P/n).read_bytes())==h,n
 for n,h in json.loads((P/'external-inputs.json').read_text()).items():assert H((ROOT/n).read_bytes())==h,n
 original=ROOT/'evidence/dependencies/donation_relay/deployed.so';raw=original.read_bytes()
 assert raw[755233:755271]==b'programs/contracts/src/tools/checks.rs'
 for at,value in [(114368,6009),(114384,55),(119240,6018),(119256,192)]:assert struct.unpack_from('<BBhi',raw,at)==(0x62,10,-128 if value in (6009,6018) else -256,value)
 for at in [114392,119264]:assert struct.unpack_from('<BBhi',raw,at)==(0x7a,10,-264,38)
 for at in [114400,119272]:assert struct.unpack_from('<BBhi',raw,at)==(0x7a,10,-280,0)
 a=module('relay_origin_analysis',P/'analyze.py')
 dis=module('relay_owned_disasm',P/'disasm.py')
 for name,lo,hi in [('message',114032,114568),('tip',118896,119440)]:
  assert (P/('original-'+name+'-constructor.asm')).read_text()==dis.render(dis.a.Elf(raw),lo,hi)
 helpers=module('relay_origin_receipt_helpers',P/'receipt_helpers.py')
 blueprints=json.loads((ROOT/'repro/donation-relay/local-validation-proposal/fixture-blueprints.json').read_text())
 frozen={r['case']['name']:r for r in blueprints}
 baseline=json.loads((P/'message-and-tip/baseline-source-manifest.json').read_text());assert len(baseline)==23
 total=0;signatures=0;newcasecount=0
 for name in ['message-only','message-and-tip']:
  d=P/name;source=json.loads((d/'source-manifest.json').read_text());assert source.keys()==baseline.keys()
  for n,h in source.items():assert H((d/'source'/n).read_bytes())==h
  changed={n for n in source if source[n]!=baseline[n]};assert changed=={'src/lib.rs','src/handlers.rs','src/error_report.rs','src/exit_error.rs'}
  patch=''
  for n in baseline:
   old=(ROOT/'repro/donation-relay/source-build-11-idl-discriminator/source'/n).read_bytes();assert H(old)==baseline[n]
   new=(d/'source'/n).read_text()
   if old.decode()!=new:patch+=''.join(difflib.unified_diff(old.decode().splitlines(keepends=True),new.splitlines(keepends=True),fromfile='a/'+n,tofile='b/'+n))
  assert patch==(d/'source.patch').read_text()
  build=json.loads((d/'build-result.json').read_text());assert build['returncode']==0 and build['source_unchanged']
  assert H((d/'build.log').read_bytes())==build['log_sha256']
  assert H((d/'candidate.so').read_bytes())==build['candidate_sha256']
  assert H((d/'unstripped.so').read_bytes())==build['unstripped_sha256']
  outputs=a.analyze(d,original,P/'original-windows.json')
  for n,result in outputs.items():
   encoded=a.encode(result);stored=(d/n).read_bytes()
   assert (gzip.decompress(stored) if n.endswith('.gz') else stored)==encoded,n
  assert not outputs['comparison-summary.json']['whole_file_equal']
  for rd in sorted(d.glob('runtime-*')):
   if not rd.is_dir():continue
   run=json.loads((rd/'comparison.json').read_text());proc=json.loads((rd/'process-result.json').read_text());launch=json.loads((rd/'launch.json').read_text())
   assert proc['harness_unchanged'] and proc['candidate_unchanged']
   assert run['candidate_sha256']==build['candidate_sha256'] and run['original_sha256']==H(raw)
   assert launch['bindings']==dict(launch['old_bindings'],candidate=build['candidate_sha256'])
   assert launch['harness_sha256']=='fd6df62699bc5732fffca65d7e6b5c1c872746180563ca3e320f7dbe11f7cb1b'
   assert run['normal_signature_blockhash_history_checks'] and not run['historical_transactions_rewritten']
   if name=='message-and-tip':assert proc['returncode']==0 and run['all_requested_completed'] and run['passed']==run['case_count']
   else:assert proc['returncode']==1 and run['passed']==1 and run['case_count']==2 and not run['all_requested_completed']
   for result in run['cases']:
    case=result['case'];f=frozen[case['name']];assert case==f['case'] and result['fixture']==f['fixture']
    left,right=result['original'],result['candidate'];assert left['transaction_base64']==right['transaction_base64']
    encoded=base64.b64decode(left['transaction_base64']);tx=helpers.parse(encoded);keys=list(map(helpers.b58,tx['keys']))
    assert keys[0]==f['fee_payer'] and set(keys[:tx['required']])==set(f['required_test_owned_signers'])
    assert len(tx['instructions'])==2
    budget,call=tx['instructions'];assert keys[budget[0]]=='ComputeBudget111111111111111111111111111111' and budget[2]==b'\2'+(1400000).to_bytes(4,'little')
    assert keys[call[0]]==helpers.RELAY and call[2].hex()==f['fixture']['instruction_hex']
    assert [keys[i] for i in call[1]]==[r['pubkey'] for r in f['fixture']['instruction_accounts']]
    mismatch=[k for k in comparable(left) if comparable(left)[k]!=comparable(right)[k]]
    assert mismatch==result['mismatches']
    if name=='message-and-tip':assert not mismatch
    elif case['name']=='donation_tip_too_large':assert mismatch==['logs']
    for row in [left,right]:
     assert row['signature_verification']==[True]*tx['required']
     assert row['metadata']['signature']==helpers.b58(tx['signatures'][0])
     for field in ['logs','inner_instructions','return_data']:assert row[field]==row['metadata'][field]
     if row['error'] is not None:
      assert all(row['before'][k]==row['after'][k] for k in row['before'] if k!=keys[0])
     elif run['group']=='ordinary':helpers.independent_effects(case,f['fixture'],row,keys)
     signatures+=tx['required']
    if runtime:
     from solders.signature import Signature
     from solders.pubkey import Pubkey
     assert all(Signature.from_bytes(s).verify(Pubkey.from_bytes(k),tx['message']) for s,k in zip(tx['signatures'],tx['keys']))
    total+=1
    if name=='message-and-tip':newcasecount+=1
 assert newcasecount==15
 d=P/'current-source-proof';r=json.loads((d/'build-result.json').read_text())
 assert r['returncode']==0 and r['source_unchanged']
 assert H((d/'build.log').read_bytes())==r['log_sha256']
 assert (d/'candidate.so').read_bytes()==(P/'message-and-tip/candidate.so').read_bytes()
 assert (d/'unstripped.so').read_bytes()==(P/'message-and-tip/unstripped.so').read_bytes()
 assert json.loads((d/'source-manifest.json').read_text())==json.loads((P/'message-and-tip/source-manifest.json').read_text())
 if current:
  assert all(H((ROOT/'programs/donation-relay'/n).read_bytes())==h for n,h in json.loads((d/'source-manifest.json').read_text()).items())
 print(json.dumps(dict(verified=True,reconstructed_source_files=23,builds=3,current_source_binding_checked=current,final_candidate_cases=15,saved_pairs_verified=total,signature_fields=signatures,cryptographic_signature_reverification=runtime,whole_original_byte_identity=False,new_execution_by_verifier=False)))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--runtime',action='store_true');ap.add_argument('--current',action='store_true');args=ap.parse_args();main(args.runtime,args.current)

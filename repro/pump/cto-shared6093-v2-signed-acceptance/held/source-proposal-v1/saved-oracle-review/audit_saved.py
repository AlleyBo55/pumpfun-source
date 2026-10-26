"""Saved oracle audit only; no VM/helper import or original decode."""
from pathlib import Path
import base64,copy,hashlib,json,re,sys
from solders.transaction import Transaction
from solders.pubkey import Pubkey
from solders.keypair import Keypair
P=Path(__file__).resolve().parent;W=P.parent;Q=W/'cto-shared6093-signed-oracle-plan';O=W/'cto-shared6093-signed-oracle-01';J=lambda p:json.loads(p.read_text());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def snap(root):return{str(f.relative_to(root)):H(f)for f in root.rglob('*')if f.is_file()}
before=snap(O);planbefore=snap(Q);seal='113b5286f1a8dc88a87f7d3b8a08a12d06f28d1c415b0a58d5c736c6a9b38cfd';assert H(Q/'manifest.json')==seal
for n,h in J(Q/'manifest.json').items():assert H(Q/n)==h
cfg=J(Q/'plan.json');data=J(Q/'cases.json');claim=J(W/'cto-shared6093-signed-oracle-attempt-01.json');assert claim['plan_seal']==seal and claim['controller_sha256']==H(Q/'controller.py')and claim['driver_sha256']==H(Q/'driver.py')and claim['attempts']==1 and claim['target_sides_limit']==12 and claim['retry_permitted']is False
launch=J(O/'launch.json');assert launch['claim_sha256']==H(W/'cto-shared6093-signed-oracle-attempt-01.json')and launch['plan_seal']==seal
inputs=J(Q/'controls/preservation-inputs.json');source=J(Q/'controls/preservation-source37.json');assert len(inputs)==15 and len(source)==37
for n,h in inputs.items():assert H(Q/'repo'/n)==h
for n,h in source.items():assert H(Path(cfg['build_source_root'])/n)==h
assert H(Path(cfg['candidate_path']))==cfg['candidate_sha256']=='6e0c9002d09e0cee6cc738b3a9e0983a8d0cd89374fa2cc7c41fa45910515b9e'
assert inputs['evidence/original/pump/deployed.so']=='7a19affaa2c6187e04a5fe0ea298cee81fa5eb8c24cfcc30d85f615e89f7b02d'
ex=J(O/'exit.json');obs=J(O/'observations.json');dr=J(O/'driver-result.json');prior=J(Q/'prior/receipt.json')
assert ex['state']==dr['state']=='DIAGNOSTIC_OBSERVATIONS_RECORDED'and ex['child_returncode']==dr['returncode']==0 and ex['observations_valid']and ex['inputs_source37_candidate_unchanged']and ex['retry_attempts']==0
for n,h in ex['raw_files_sha256'].items():assert H(O/n)==h
assert set(before)==set(ex['raw_files_sha256'])|{'exit.json'}
assert obs['failure']is None and dr['failure']is None and obs['retry_attempts']==0 and obs['vm_calls_attempted']==dr['vm_calls_attempted']==12
assert obs['analysis']==dr['analysis']==ex['analysis']and obs['analysis']['all_original_hypotheses_observed']and obs['analysis']['preservation_pass_claimed']is False and obs['analysis']['universal_static_field_mapping_proven']is False
assert len(obs['rows'])==6 and len(obs['attempts'])==len(obs['signature_audits'])==12
pump=Pubkey.from_string(J(Q/'repo/evidence/upstream/pump.json')['address']);pool=Pubkey.find_program_address([b'pool-authority',bytes([61])*32],pump)[0];payer=Keypair.from_seed(bytes([215])*32).pubkey()
rows=[];txcount=0;sigcount=0;signerrows=[];priorbefore=[];innerrows=[]
for index,(spec,row)in enumerate(zip(data['rows'],obs['rows'],strict=True)):
 assert(row['family'],row['variant'],row['case'])==(spec['family'],spec['variant'],spec['case']);family=data['families'][spec['family']]
 for side in ['original','candidate']:
  marker={'case_index':index,'case':spec['case']['name'],'side':side,'target_call_count_in_this_side':1};ix=index*2+(side=='candidate');assert J(O/f'attempt-{index:02d}-{side}.json')==obs['attempts'][ix]==marker
  item=J(O/f'side-{index:02d}-{side}.json');assert item==row[side]and item['case']==spec['case']and item['signatures_verified']is True and item['pool_authority_top_level_signer']is False
  raw=base64.b64decode(item['transaction_base64'],validate=True);tx=Transaction.from_bytes(raw);assert bytes(tx)==raw;required=tx.message.header.num_required_signatures;checks=tx.verify_with_results();assert checks and all(checks)and len(checks)==len(tx.signatures)==required
  assert tx.message.account_keys[0]==payer and pool not in tx.message.account_keys[:required]
  audited={'transaction_sha256':hashlib.sha256(raw).hexdigest(),'signature_count':required,'required_signer_pubkeys':[str(x)for x in tx.message.account_keys[:required]],'all_signatures_verified':True,'pool_authority_top_level_signer':False};assert obs['signature_audits'][ix]=={**marker,**audited};signerrows.append({**marker,**audited});txcount+=1;sigcount+=required
  inner=[]
  for outer_index,group in enumerate(item['inner']):
   for call in group:
    ins=call['instruction'];accounts=ins['accounts'];payload=ins['data'];assert isinstance(accounts[0],list)and isinstance(payload[0],list)
    
    for prefix,values in [(accounts[0],accounts[1:]),(payload[0],payload[1:])]:
     value=0;shift=0
     for k,byte in enumerate(prefix):
      assert 0<=byte<=255 and ((byte&128)!=0)==(k<len(prefix)-1);value|=(byte&127)<<shift;shift+=7
     assert value==len(values)
    inner.append({'outer_index':outer_index,'stack_height':call['stackHeight'],'program':str(tx.message.account_keys[ins['programIdIndex']]),'accounts':[str(tx.message.account_keys[n])for n in accounts[1:]],'data_hex':bytes(payload[1:]).hex(),'raw_shortvec_account_prefix':accounts[0],'raw_shortvec_data_prefix':payload[0]})
  innerrows.append({'case':spec['case']['name'],'side':side,'calls':inner})
 assert row['original']['before']==row['candidate']['before']
 base=next(x for x in obs['rows']if x['family']==spec['family']and x['variant']=='baseline');expected=copy.deepcopy(base['original']['before']);blob=bytearray.fromhex(expected[family['target_field']]['data']);assert len(blob)==165 and blob[108]==1
 if spec['variant']!='baseline':blob[108]=2
 if spec['variant']=='frozen-zero':blob[64:72]=bytes(8)
 expected[family['target_field']]['data']=blob.hex();assert row['original']['before']==expected
 if spec['variant']=='baseline':
  previous=next(x for x in prior['cases']if x['case']['name']==family['baseline_case_name']);assert row['original']['before']==previous['original']['before']==previous['candidate']['before'];assert row['original']['error']is None and row['candidate']['error']is None;priorbefore.append({'family':spec['family'],'exact_prior_before_equal_both_sides':True})
 original6093=bool(row['original']['error']and'Custom(6093)'in row['original']['error'])
 if spec['variant']=='frozen-positive':
  assert original6093 and row['candidate']['error']is None;origin='programs/pump/src/creator/admin_cto.rs:'+str(family['positive_origin_hypothesis']);assert any(re.search(re.escape(origin)+r'\b',line)for line in row['original']['logs'])
 else:assert not original6093
 differences=[k for k in ['error','before','after','events','inner','return']if row['original'][k]!=row['candidate'][k]];assert differences==obs['analysis']['comparison'][index]['different_effect_fields']
 afterdiff=[k for k in row['original']['after']if row['original']['after'][k]!=row['candidate']['after'][k]]
 rows.append({'family':spec['family'],'variant':spec['variant'],'target':family['target_field'],'amount':int.from_bytes(blob[64:72],'little'),'state108':blob[108],'original_error':row['original']['error'],'candidate_error':row['candidate']['error'],'effect_differences':differences,'after_account_differences':afterdiff,'raw_logs_equal':row['original']['logs']==row['candidate']['logs'],'original_logs':row['original']['logs'],'candidate_logs':row['candidate']['logs']})
assert txcount==12 and sigcount==24 and not any(r['raw_logs_equal']for r in rows)
assert rows[1]['effect_differences']==rows[4]['effect_differences']==['error','after','events','inner']and rows[2]['effect_differences']==['inner']and rows[5]['effect_differences']==['after','inner']
assert snap(O)==before and snap(Q)==planbefore
(P/'saved-signature-audit.json').write_text(json.dumps({'status':'PASS_SAVED12_TRANSACTIONS24_SIGNATURES_ONLY','rows':signerrows,'pool_authority':str(pool),'target_executions':0},indent=2)+'\n');(P/'observed-effects-and-logs.json').write_text(json.dumps(rows,indent=2)+'\n');(P/'saved-inner-instructions.json').write_text(json.dumps(innerrows,indent=2)+'\n')
result={'state':'PASS_SAVED_FINITE_ORACLE_AUDIT_NOT_PRESERVATION','plan_seal':seal,'case_count':6,'transactions':txcount,'actual_signature_fields':sigcount,'prior_before_extra_check':priorbefore,'all_hypotheses_observed':True,'positive_original_origins':{'A':660,'B':719},'candidate_positive_errors':None,'all_raw_logs_differ':True,'frozen_zero_A_differences':['inner'],'frozen_zero_B_differences':['after','inner'],'source15_37_capture_candidate_claim_receipts_bound':True,'raw_output_and_plan_unchanged':True,'output_files':before,'claim_sha256':H(W/'cto-shared6093-signed-oracle-attempt-01.json'),'target_VM_build_helper_import_original_decode_network_executions':0,'universal_field_mapping_ABI_or_transitive_closure':False,'source_or_candidate_application':False}
(P/'review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='output_files'},indent=2))

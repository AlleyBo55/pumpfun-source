"""Independent saved-signature/receipt audit only. Never imports helper or VM."""
from pathlib import Path,PurePosixPath
import base64,collections,copy,hashlib,importlib.metadata,json,re,sys
from solders.transaction import Transaction
from solders.pubkey import Pubkey
from solders.keypair import Keypair
assert sys.version_info[:2]==(3,12)and importlib.metadata.version('solders')=='0.27.1'
P=Path(__file__).resolve().parent;W=P.parent;PLAN=W/'cto-shared6093-v2-acceptance-plan';J=lambda p:json.loads(p.read_text());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();C='fdfdb5f27af9b8c22effd48ea523c06bd037ceedf49df0da8178cad19eed38f5';LANES={'ordinary':'9c8121167c3a755c6c4acec3151fdb79507eacd597f65e485af858fb020b4feb','six-case':'028a7f9500c2846d360c479825006ff2ea01d3f50e4149a84ad3cc780bc7ce60'}
def snap(root):return{str(f.relative_to(root)):H(f)for f in root.rglob('*')if f.is_file()}
def sealed(root,seal):
 assert H(root/'manifest.json')==seal
 if(root/'manifest.sha256').exists():assert(root/'manifest.sha256').read_text().strip()==seal
 m=J(root/'manifest.json');m=m.get('files',m);assert set(m)==set(snap(root))-{'manifest.json','manifest.sha256'}
 for n,r in m.items():
  q=PurePosixPath(n);assert not q.is_absolute()and'..'not in q.parts;f=root/n;assert not f.is_symlink();assert H(f)==(r if isinstance(r,str)else r['sha256'])
  if isinstance(r,dict):assert f.stat().st_size==r['bytes']
sealed(PLAN,'7e779eec39bdc076b11961a54cfc484422e3a776c973cf76e5d25b9d3786449a');sealed(W/'cto-shared6093-v2-emitted-independent-review','e2161fdbd2c6c96e08db4a3398d1197b2200a2c1e403ae2dc239e0abac98607e');sealed(W/'cto-shared6093-v2-cache-review','4d0b0e35067703be30a3945d7a1f9db12870e7525fb61f283754449c698de9fe')
admission_path=W/'cto-shared6093-v2-root-runtime-admission.json';admission=J(admission_path);admission_hash=H(admission_path);assert admission['state']=='ROOT_APPROVED_FINITE_V2_RUNTIME_AFTER_EMITTED_REVIEW'and admission['candidate_sha256']==C and admission['plan_seals']==LANES and admission['whole_byte_identity_claimed']is False and admission['no_candidate_promotion']is True
snapshots={str(PLAN):snap(PLAN)};configs={};gate_records={};signature_rows=[];side_rows=[];six_rows=[]
pump=Pubkey.from_string('6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P');pool=Pubkey.find_program_address([b'pool-authority',bytes([61])*32],pump)[0];payer=Keypair.from_seed(bytes([215])*32).pubkey()
def txaudit(item,lane,case,side):
 assert item['signatures_verified']is True and item['pool_authority_top_level_signer']is False
 raw=base64.b64decode(item['transaction_base64'],validate=True);tx=Transaction.from_bytes(raw);assert bytes(tx)==raw;required=tx.message.header.num_required_signatures;checks=tx.verify_with_results();assert checks and all(checks)and len(checks)==len(tx.signatures)==required
 assert tx.message.account_keys[0]==payer and pool not in tx.message.account_keys[:required]
 result={'lane':lane,'case':case,'side':side,'transaction_sha256':hashlib.sha256(raw).hexdigest(),'signature_count':required,'required_signers':[str(k)for k in tx.message.account_keys[:required]],'all_verified':True,'pool_authority_top_level_signer':False};signature_rows.append(result);return result
for lane,seal in LANES.items():
 lp=PLAN/lane;sealed(lp,seal);cfg=J(lp/'plan.json');configs[lane]=cfg;out=Path(cfg['out']);gate=Path(cfg['gate_output']);snapshots[str(out)]=snap(out);snapshots[str(gate)]=snap(gate)
 assert cfg['candidate_sha256']==H(Path(cfg['candidate_path']))==C;source=J(lp/'current-controls/source37.json');assert H(lp/'current-controls/source37.json')==admission['source37_sha256']==cfg['source37_sha256']and len(source)==37
 assert source['programs/pump/src/admin_cto.rs']==admission['source_CTO_sha256']==cfg['candidate_source_CTO']=='950d6ec8c07072a3305c905509018f95b40d53e9ab25a4c1bda96b42c2a2fe58'
 for n,h in source.items():assert H(Path(cfg['build_source_root'])/n)==h
 inputs=J(lp/'inputs.json');assert len(inputs)==15
 for n,h in inputs.items():assert H(lp/'repo'/n)==h
 assert inputs['evidence/original/pump/deployed.so']=='7a19affaa2c6187e04a5fe0ea298cee81fa5eb8c24cfcc30d85f615e89f7b02d'
 build=J(lp/'current-controls/controller-result.json');assert build['source_after']==source and build['state']=='requires-cache-review'and build['helper_exit']==build['build_sbf_aggregate_exit']==0 and build['compiler_child_exit']is None and build['strip_child_exit']is None
 assert build['proposal_manifest']==admission['build_plan_seal']==H(lp/'current-controls/build-plan-manifest.json')=='29069875549ea325beeafc10059c6893218211c327d08a6f90bce70df10e5ae2'
 ge=J(gate/'exit.json');gc=J(gate/'claim.json');gl=J(gate/'launch.json');assert ge['state']=='ACCEPTED_FINITE_'+lane.upper()and ge['child_returncode']==0 and ge['acceptance_passed']is True and ge['inputs_source37_candidate_unchanged']is True and ge['retry_attempts']==0
 for r in[ge,gc,gl]:assert r['plan_seal']==seal and r['root_admission_sha256']==admission_hash and r['emitted_review_seal']==admission['emitted_review_seal']=='e2161fdbd2c6c96e08db4a3398d1197b2200a2c1e403ae2dc239e0abac98607e'
 assert gc['gate_sha256']==H(lp/'gate.py')and gc['one_attempt']and gc['automatic_retry']is False and gl['claim_sha256']==H(gate/'claim.json')
 assert gl['command']==[cfg['python'],'-B',str(lp/'controller.py'),'--execute','--expected-seal',seal]
 for n,h in ge['raw_gate_files_sha256'].items():assert H(gate/n)==h
 assert set(ge['raw_gate_files_sha256'])|{'exit.json'}==set(snap(gate));acceptance=J(gate/'saved-acceptance.json');gate_records[lane]={'exit_state':ge['state'],'child_exit':0,'plan_seal':seal,'gate_output_hashes':snap(gate),'raw_output_hashes':snap(out),'saved_acceptance_hash':H(gate/'saved-acceptance.json'),'attempt_claim_hash':H(Path(cfg['claim']))}
 if lane=='ordinary':
  assert J(Path(cfg['claim']))==gc
  receipt=J(out/'receipt.json');ex=J(out/'exit.json');launch=J(out/'launch.json');assert ex['passed']and ex['returncode']==0 and ex['inputs_unchanged']and ex['receipt_valid']and ex['candidate_sha256']==receipt['candidate_sha256']==C
  for n in['stdout.log','stderr.log','receipt.json']:assert H(out/n)==ex[n.replace('.','_')+'_sha256']
  assert receipt['case_count']==ex['case_count']==len(receipt['cases'])==363 and receipt['mismatches']==ex['mismatches']==[]
  expected={str(lp/'repo'/n):h for n,h in inputs.items()if n!='research/imported-lab/analysis/pump_fun/config-snapshot.json'};expected[cfg['candidate_path']]=C;assert receipt['provenance']==expected
  successes=0;logs_equal=0;prior=J(PLAN/'six-case/prior/receipt.json');assert[row['case']for row in receipt['cases']]==[row['case']for row in prior['cases']]
  crypto_rows=[]
  for row in receipt['cases']:
   assert row['match']is True and row['original']['case']==row['case']==row['candidate']['case'];assert all(row['original'][k]==row['candidate'][k]for k in['error','before','after','events','inner','return']);successes+=row['original']['error']is None;logs_equal+=row['original']['logs']==row['candidate']['logs']
   for side in['original','candidate']:
    audit=txaudit(row[side],lane,row['case']['name'],side);crypto_rows.append({'case':audit['case'],'side':side,'transaction_sha256':audit['transaction_sha256'],'signatures':audit['signature_count'],'all_verified':True,'top_level_pool_authority_signer':False})
  assert successes==169 and acceptance['case_count']==363 and acceptance['original_successes']==169 and acceptance['transaction_count']==726 and acceptance['signature_fields']==1448 and acceptance['rows']==crypto_rows
  gate_records[lane].update(cases=363,original_successes=successes,transactions=len(crypto_rows),signature_fields=sum(r['signatures']for r in crypto_rows),raw_log_equal_case_count=logs_equal)
 else:
  ex=J(out/'exit.json');obs=J(out/'observations.json');dr=J(out/'driver-result.json');claim=J(Path(cfg['claim']));assert claim['controller_sha256']==H(lp/'controller.py')and claim['driver_sha256']==H(lp/'driver.py')and claim['plan_seal']==seal and claim['attempts']==1 and claim['retry_permitted']is False
  assert J(out/'launch.json')['claim_sha256']==H(Path(cfg['claim']))
  assert ex['state']==dr['state']=='FINITE_ACCEPTANCE_OBSERVATIONS_RECORDED'and ex['child_returncode']==dr['returncode']==0 and ex['observations_valid']and ex['inputs_source37_candidate_unchanged']and ex['retry_attempts']==0
  for n,h in ex['raw_files_sha256'].items():assert H(out/n)==h
  assert set(ex['raw_files_sha256'])|{'exit.json'}==set(snap(out));assert obs['analysis']==dr['analysis']==ex['analysis']==acceptance['analysis']and obs['analysis']['all_six_effects_equal']and obs['analysis']['all_original_hypotheses_observed'];assert obs['failure']is None and obs['vm_calls_attempted']==12 and len(obs['rows'])==6
  data=J(lp/'cases.json');prior=J(lp/'prior/receipt.json');old6e=J(W/'cto-shared6093-signed-oracle-01/observations.json')
  for i,(spec,row)in enumerate(zip(data['rows'],obs['rows'],strict=True)):
   assert(row['family'],row['variant'],row['case'])==(spec['family'],spec['variant'],spec['case']);family=data['families'][row['family']]
   assert all(row['original'][k]==row['candidate'][k]for k in['error','before','after','events','inner','return'])
   base=next(x for x in obs['rows']if x['family']==row['family']and x['variant']=='baseline');before_state=copy.deepcopy(base['original']['before']);b=bytearray.fromhex(before_state[family['target_field']]['data']);assert len(b)==165 and b[108]==1
   if row['variant']!='baseline':b[108]=2
   if row['variant']=='frozen-zero':b[64:72]=bytes(8)
   before_state[family['target_field']]['data']=b.hex();assert row['original']['before']==before_state
   if row['variant']=='baseline':
    pr=next(x for x in prior['cases']if x['case']['name']==row['case']['name']);assert row['original']['before']==pr['original']['before']==pr['candidate']['before']
   for side in['original','candidate']:
    marker={'case_index':i,'case':row['case']['name'],'side':side,'target_call_count_in_this_side':1};ix=i*2+(side=='candidate');assert J(out/f'attempt-{i:02d}-{side}.json')==obs['attempts'][ix]==marker
    assert J(out/f'side-{i:02d}-{side}.json')==row[side];a=txaudit(row[side],lane,row['case']['name'],side);actual={'transaction_sha256':a['transaction_sha256'],'signature_count':a['signature_count'],'required_signer_pubkeys':a['required_signers'],'all_signatures_verified':True,'pool_authority_top_level_signer':False};assert obs['signature_audits'][ix]=={**marker,**actual}
   original_origin=[];candidate_origin=[]
   if row['variant']=='frozen-positive':
    assert'Custom(6093)'in row['original']['error'];assert any('programs/pump/src/creator/admin_cto.rs:'+str(family['positive_origin_hypothesis'])in line for line in row['original']['logs'])
   else:assert row['original']['error']is None and row['candidate']['error']is None
   assert row['original']['logs']!=row['candidate']['logs'];previous=old6e['analysis']['comparison'][i];assert previous['family']==row['family']and previous['variant']==row['variant']
   six_rows.append({'family':row['family'],'variant':row['variant'],'case':row['case']['name'],'prior6e_effect_differences':previous['different_effect_fields'],'newfdf_effect_differences':[],'raw_logs_equal':False,'original_error':row['original']['error'],'candidate_error':row['candidate']['error'],'original_origin_log_lines':[x for x in row['original']['logs']if'AnchorError'in x],'candidate_origin_log_lines':[x for x in row['candidate']['logs']if'AnchorError'in x],'prior_original_complete_record_equal':old6e['rows'][i]['original']==row['original']})
  gate_records[lane].update(cases=6,transactions=12,signature_fields=sum(x['signature_count']for x in signature_rows if x['lane']==lane),all6effects_equal_everycase=True,all_raw_logs_different=True,baseline_prior_before_equal=True)
assert len(signature_rows)==738 and sum(r['signature_count']for r in signature_rows)==1472 and gate_records['ordinary']['signature_fields']==1448 and gate_records['six-case']['signature_fields']==24
for root,snapshot in snapshots.items():assert snap(Path(root))==snapshot
assert H(admission_path)==admission_hash
(P/'signature-audit.json').write_text(json.dumps({'status':'PASS_SAVED738_TRANSACTIONS1472_SIGNATURE_FIELDS','pool_authority':str(pool),'rows':signature_rows,'target_VM_executions':0},indent=2)+'\n');(P/'six-case-before-after-effects.json').write_text(json.dumps(six_rows,indent=2)+'\n');(P/'input-output-hashes.json').write_text(json.dumps(snapshots,indent=2)+'\n')
result={'state':'PASS_SAVED_ORDINARY_AND_FINITE_SIX_CASE_ACCEPTANCE','candidate':C,'source_CTO':admission['source_CTO_sha256'],'root_admission_sha256':admission_hash,'lane_records':gate_records,'total_saved_transactions':738,'total_signature_fields':1472,'all_inputs_outputs_frozen_manifests_unchanged':True,'raw_logs_not_identity':True,'new_VM_helper_compiler_original_decoder_network_executions':0,'source_default_status_or_candidate_promotion':False,'whole_original_byte_identity':False,'limits':['Finite363 ordinary preservation and sixcase effects only','Natural origins differ; raw logs excluded from equality','UniversalsharedABI/headeralias/transitive/dropOOM/tokenextensions notproved','Historical compiler/dependencies/native provenance remainopen']}
(P/'review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='lane_records'},indent=2))

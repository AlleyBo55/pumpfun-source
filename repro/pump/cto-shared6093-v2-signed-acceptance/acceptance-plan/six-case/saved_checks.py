"""Saved-result checks. Crypto imports occur only in explicit post-run audit."""
import base64,copy,hashlib,json,re
FIELDS=['error','before','after','events','inner','return']
def validate_item(item,case):
 assert isinstance(item,dict)and item['case']==case
 assert item['error']is None or isinstance(item['error'],str)
 assert isinstance(item['before'],dict)and isinstance(item['after'],dict)
 assert all(isinstance(item[k],list)for k in['logs','events','inner'])
 assert all(isinstance(v,str)for v in item['logs']+item['events'])
 assert item['signatures_verified']is True and item['pool_authority_top_level_signer']is False
 assert isinstance(item['transaction_base64'],str)and item['transaction_base64']
 for key in FIELDS:assert key in item
def audit_transaction(item):
 # Signature/PDA decoding only: this function never imports LiteSVM or the helper.
 from solders.pubkey import Pubkey
 from solders.keypair import Keypair
 from solders.transaction import Transaction
 raw=base64.b64decode(item['transaction_base64'],validate=True);tx=Transaction.from_bytes(raw);assert bytes(tx)==raw
 checks=tx.verify_with_results();required=tx.message.header.num_required_signatures
 assert checks and len(checks)==len(tx.signatures)==required and all(checks)
 # Derive cardinality from the actual signed message; never add/force AUTH.
 assert tx.message.account_keys[0]==Keypair.from_seed(bytes([215])*32).pubkey()
 pool=Pubkey.find_program_address([b'pool-authority',bytes([61])*32],Pubkey.from_string('6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P'))[0]
 assert pool not in tx.message.account_keys[:required]
 return {'transaction_sha256':hashlib.sha256(raw).hexdigest(),'signature_count':required,'required_signer_pubkeys':[str(k)for k in tx.message.account_keys[:required]],'all_signatures_verified':True,'pool_authority_top_level_signer':False}
def observed6093(item):return item['error']is not None and re.search(r'Custom\(6093\)',item['error'])is not None
def analyze_observations(rows,data):
 assert len(rows)==6
 by_key={(r['family'],r['variant']):r for r in rows};assert len(by_key)==6
 hypotheses=[];comparison=[]
 for family in['A','B']:
  spec=data['families'][family];base=by_key[(family,'baseline')]
  hypotheses.append({'family':family,'kind':'prior-baseline-success-replay','expected':'original error None','observed':base['original']['error']is None})
  for variant in['baseline','frozen-positive','frozen-zero']:
   row=by_key[(family,variant)];assert row['original']['before']==row['candidate']['before'],'Different pre-state between sides'
   expected=copy.deepcopy(base['original']['before'])
   b=bytearray.fromhex(expected[spec['target_field']]['data']);assert len(b)==165 and b[108]==1
   if variant!='baseline':b[108]=2
   if variant=='frozen-zero':b[64:72]=bytes(8)
   expected[spec['target_field']]['data']=b.hex()
   assert row['original']['before']==expected,'Fixture difference exceeds specified target state/amount'
   for side in['original','candidate']:validate_item(row[side],row['case'])
   comparison.append({'family':family,'variant':variant,'different_effect_fields':[k for k in FIELDS if row['original'][k]!=row['candidate'][k]],'raw_logs_equal':row['original']['logs']==row['candidate']['logs'],'original_error':row['original']['error'],'candidate_error':row['candidate']['error']})
   if variant=='frozen-positive':
    needle='programs/pump/src/creator/admin_cto.rs:'+str(spec['positive_origin_hypothesis'])
    origin=any(re.search(re.escape(needle)+r'\b',line)for line in row['original']['logs'])
    hypotheses.append({'family':family,'kind':'HYPOTHESIS positive-frozen guard field association','expected_error':6093,'expected_origin':spec['positive_origin_hypothesis'],'observed_error6093':observed6093(row['original']),'observed_origin':origin,'observed':observed6093(row['original'])and origin})
   elif variant=='frozen-zero':hypotheses.append({'family':family,'kind':'HYPOTHESIS zero-balance negative control','expected':'No6093 (other behavior retained)','observed':not observed6093(row['original'])})
 return {'case_count':6,'side_count':12,'hypotheses':hypotheses,'all_original_hypotheses_observed':all(x['observed']for x in hypotheses),'all_six_effects_equal':all(not x['different_effect_fields']for x in comparison),'comparison':comparison,'preservation_pass_claimed':False,'universal_static_field_mapping_proven':False,'full_original_byte_identity_proven':False,'scope':'Finite signed oracle causality only; mismatches retained as research, not preservation failure repair.'}

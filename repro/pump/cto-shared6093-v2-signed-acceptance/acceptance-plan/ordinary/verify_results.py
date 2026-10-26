"""UNEXECUTED future saved-result acceptance. Decodes/verifies signatures only; never runs a harness/VM."""
from pathlib import Path
import argparse,base64,hashlib,json
P=Path(__file__).resolve().parent;H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();J=lambda p:json.loads(p.read_text());EXPECTED='fdfdb5f27af9b8c22effd48ea523c06bd037ceedf49df0da8178cad19eed38f5'
def verify_results(root):
 # Only saved transaction decoding/signature/PDA operations; no LiteSVM import or target execution.
 from solders.pubkey import Pubkey
 from solders.transaction import Transaction
 data=J(root/'receipt.json');result=J(root/'exit.json');assert result['passed']is True and result['returncode']==0 and result['receipt_valid']is True and result['inputs_unchanged']is True
 assert data['candidate_sha256']==result['candidate_sha256']==EXPECTED and data['original_sha256']=='7a19affaa2c6187e04a5fe0ea298cee81fa5eb8c24cfcc30d85f615e89f7b02d'
 assert data['case_count']==result['case_count']==len(data['cases'])==363 and data['mismatches']==result['mismatches']==[]
 for n in ['stdout.log','stderr.log','receipt.json']:assert H(root/n)==result[n.replace('.','_')+'_sha256']
 inputs=J(P/'inputs.json');repo=P/'repo';candidate=P.parents[1]/'cto-shared6093-v2-build-01/build-01/artifacts/pump_recovered.so';expected_paths={str(repo/n):h for n,h in inputs.items()if n!='research/imported-lab/analysis/pump_fun/config-snapshot.json'};expected_paths[str(candidate)]=EXPECTED;assert data['provenance']==expected_paths
 for n,h in inputs.items():assert H(repo/n)==h
 assert H(candidate)==EXPECTED
 idl=J(repo/'evidence/upstream/pump.json');pump=Pubkey.from_string(idl['address']);mint=Pubkey.from_bytes(bytes([61])*32);authority=Pubkey.find_program_address([b'pool-authority',bytes(mint)],pump)[0];assert 'MINT=Pubkey.from_bytes(bytes([61])*32)'in(repo/'scripts/fees_donation_create_differential.py').read_text()
 txs=0;signatures=0;rows=[];original_successes=0
 for row in data['cases']:
  assert row['match']is True and row['original']['case']==row['case']==row['candidate']['case'];assert all(row['original'][k]==row['candidate'][k]for k in ['error','before','after','events','inner','return'])
  original_successes+=row['original']['error']is None
  for side in ['original','candidate']:
   item=row[side];assert item['signatures_verified']is True and item['pool_authority_top_level_signer']is False
   raw=base64.b64decode(item['transaction_base64'],validate=True);tx=Transaction.from_bytes(raw);assert bytes(tx)==raw;checks=tx.verify_with_results();required=tx.message.header.num_required_signatures;assert checks and all(checks)and len(checks)==len(tx.signatures)==required
   assert authority not in tx.message.account_keys[:required];txs+=1;signatures+=len(tx.signatures);rows.append({'case':row['case']['name'],'side':side,'transaction_sha256':hashlib.sha256(raw).hexdigest(),'signatures':len(tx.signatures),'all_verified':True,'top_level_pool_authority_signer':False})
 assert original_successes==169 and txs==726 and signatures==1448
 return {'status':'PASS_SAVED_363_ORDINARY_PRESERVATION_ONLY','case_count':363,'original_successes':169,'transaction_count':txs,'signature_fields':signatures,'rows':rows,'logs_compared_for_equality':False,'raw_logs_retained':True,'target_executions_by_this_verifier':0,'shared6093_or_changed_path_acceptance_proved':False,'full_original_byte_identity_proved':False}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--receipt-root',type=Path,default=P.parents[1]/'cto-shared6093-v2-ordinary-preservation-01');a=ap.parse_args()
 if not a.receipt_root.exists():print('UNEXECUTED: future output absent; no receipt/signature acceptance claimed')
 else:print(json.dumps(verify_results(a.receipt_root),indent=2))

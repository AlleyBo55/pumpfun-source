"""Portable passive verifier. Default stdlib only; no archived code imports or execution.
Optional --crypto imports only the declared saved-transaction adapters, never a VM.
"""
from pathlib import Path,PurePosixPath
import argparse,base64,copy,difflib,gzip,hashlib,importlib.metadata,importlib.util,json,os,stat,sys,types
P=Path(os.path.abspath(__file__)).parent
# Every publication-scoped file open is checked against actual directory-entry
# spelling before the OS can apply case-insensitive aliases. Runtime imports
# outside this publication are not evidence lookups and remain outside scope.
_CASE_VIOLATIONS=[]
def exact_component_spelling(path):
 absolute=os.path.abspath(os.fsdecode(path));current=os.path.sep
 for component in Path(absolute).parts[1:]:
  entries=os.listdir(current)
  if component not in entries:raise FileNotFoundError('EXACT_CASE_READ_REJECTED '+absolute+' component '+component+' under '+current)
  current=os.path.join(current,component)
 return absolute
exact_component_spelling(P)
def publication_read_guard(event,args):
 if event!='open'or not isinstance(args[0],(str,bytes,os.PathLike)):return
 path=os.path.abspath(os.fsdecode(args[0]));root=str(P);prefix=root.rstrip(os.sep)+os.sep
 if path.casefold()==root.casefold()or path.casefold().startswith(prefix.casefold()):
  try:exact_component_spelling(path)
  except BaseException as exc:_CASE_VIOLATIONS.append(str(exc));raise
sys.addaudithook(publication_read_guard)
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
J=lambda p:json.loads(p.read_text())
C='fdfdb5f27af9b8c22effd48ea523c06bd037ceedf49df0da8178cad19eed38f5'
U='1e088e9add0218ebf6745a7f7557a4dc55dc68e86ec97790584db7f169c14bc3'
S='950d6ec8c07072a3305c905509018f95b40d53e9ab25a4c1bda96b42c2a2fe58'
FIELDS=['error','before','after','events','inner','return']
def rel(name):
 q=PurePosixPath(name);assert not q.is_absolute()and'..'not in q.parts
 return name

def hash_rows(root,rows):
 for n,row in rows.items():
  f=root/rel(n);expected=row if isinstance(row,str)else row['sha256'];assert H(f)==expected,n
  if isinstance(row,dict):
   if'bytes'in row:assert f.stat().st_size==row['bytes']
   if'mode'in row:assert stat.S_IMODE(f.stat().st_mode)==row['mode']

def raw_result(root,exitname='exit.json',key='raw_files_sha256'):
 ex=J(root/exitname)
 if key in ex:
  rows=ex[key];assert {str(f.relative_to(root))for f in root.rglob('*')if f.is_file()}==set(rows)|{exitname};hash_rows(root,rows)
 return ex

def metadata_checks():
 assert __debug__
 m=J(P/'manifest.json');assert set(m)|{'manifest.json','manifest.sha256'}=={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()}
 for f in P.rglob('*'):
  assert not f.is_symlink()and f.name!='__pycache__'and f.suffix!='.pyc'
  if f.is_file():assert f.stat().st_size<50*1024**2
 hash_rows(P,m)
 derivation=J(P/'wrapper-derivation.json');old_manifest=J(P/derivation['original_manifest']);assert H(P/derivation['original_manifest'])==derivation['original_seal']=='96f43cf15f85ec6e27b72bd1a4cec0d0385e5b7decf9a58e1c34333f4cb6c8c2'
 unchanged=derivation['unchanged_original_payloads'];changed=derivation['changed_original_payloads'];assert set(unchanged)|{r['path']for r in changed}==set(old_manifest)
 assert set(unchanged).isdisjoint({r['path']for r in changed});hash_rows(P,unchanged)
 for name,row in unchanged.items():assert row==old_manifest[name]
 for row in changed:
  name=row['path'];assert old_manifest[name]['sha256']==row['old_sha256']==H(P/'historical96'/name)and H(P/name)==row['new_sha256']
  assert(P/'wrapper-changes'/(name+'.diff')).read_text()==''.join(difflib.unified_diff((P/'historical96'/name).read_text().splitlines(True),(P/name).read_text().splitlines(True),fromfile='original96/'+name,tofile='successor/'+name))
 failure=P/'historical96/case-failure-review';assert H(failure/'manifest.json')==(failure/'manifest.sha256').read_text().strip();hash_rows(failure,J(failure/'manifest.json'))
 for n,row in J(P/'file-copy-bindings.json').items():assert H(P/rel(n))==row['sha256'] and(P/n).stat().st_size==row['bytes'] and stat.S_IMODE((P/n).stat().st_mode)==row['mode']
 for folder,row in J(P/'copy-bindings.json').items():
  root=P/folder;hash_rows(root,row['payloads']);assert set(row['payloads'])=={str(f.relative_to(root))for f in root.rglob('*')if f.is_file()}
  if'manifest'in row:
   assert H(root/row['manifest'])==row['seal'];sub=J(root/row['manifest']);sub=sub.get('files',sub);hash_rows(root,sub)
   extras={row['manifest'],'manifest.sha256'}
   if'MANIFEST.json'in{entry.name for entry in root.iterdir()}:assert H(root/'MANIFEST.json')==row['seal'];extras.add('MANIFEST.json')
   assert {str(f.relative_to(root))for f in root.rglob('*')if f.is_file()}-set(sub)<=extras
 source=J(P/'build-input-source37.json');assert len(source)==37 and source['programs/pump/src/admin_cto.rs']==S
 assert source==J(P/'source-proposal/source-after.json')==J(P/'build-plan/source-proposed.json')
 for n,h in source.items():assert H(P/'build-input-source'/n)==H(P/'source-proposal/source'/n)==H(P/'build-plan/source'/n)==h
 before=J(P/'source-proposal/source-before.json');assert[n for n in source if source[n]!=before[n]]==['programs/pump/src/admin_cto.rs']
 assert H(P/'artifacts/candidate.so')==C and(P/'artifacts/candidate.so').stat().st_size==1590856
 assert H(P/'artifacts/unstripped.so')==U and(P/'artifacts/unstripped.so').stat().st_size==2174728
 build=J(P/'build-results/controller-result.json');attempt=J(P/'build-results/build-01/build-attempt.json');comparison=J(P/'build-results/build-01/build-comparison.json')
 assert build['state']=='requires-cache-review'and build['candidate']=='UNSELECTED'and build['helper_exit']==build['build_sbf_aggregate_exit']==attempt['returncode']==0
 assert build['compiler_child_exit']is None and build['strip_child_exit']is None and build['source_unchanged']and build['tool_sdk_before']==build['tool_sdk_after']
 assert build['source_after']==attempt['source_sha256']==attempt['source_after_sha256']==comparison['source_sha256']==source
 assert build['proposal_manifest']==H(P/'build-plan/MANIFEST.json')=='29069875549ea325beeafc10059c6893218211c327d08a6f90bce70df10e5ae2'
 assert H(P/'build-results/build-01/build.log')==attempt['build_log_sha256']==comparison['build_log_sha256']
 assert comparison['comparison']['candidate_sha256']==C and comparison['comparison']['full_byte_equality']is False
 terminal=J(P/'root-observations/cto-shared6093-v2-build-terminal-observation.json');assert terminal['actual_controller_terminal_exit']==2 and terminal['rerun_performed']is False and terminal['compiler_child_exit']is None and terminal['strip_child_exit']is None
 assert H(P/'cache-review/controller-result.json')==H(P/'build-results/controller-result.json')
 cache=J(P/'cache-review/review.json');assert cache['status']=='PASS_GENERATED_BOOKKEEPING_ONLY_UNSELECTED'and cache['controller_receipt_unchanged']
 claim=J(P/'root-observations/cto-shared6093-v2-attempt-01.json');assert claim['attempts']==1 and claim['candidate']=='UNSELECTED'and claim['proposal_manifest']==build['proposal_manifest']and claim['controller_sha256']==H(P/'build-plan/controller.py')
 assert H(P/'cache-review/manifest.json')=='4d0b0e35067703be30a3945d7a1f9db12870e7525fb61f283754449c698de9fe'
 held=J(P/'held/build-plan-hold-review/hold.json');assert held['state']=='HOLD_SOURCE_EMPTY_ACCOUNT_REGRESSION_RISK'and held['source_execution_readiness_approved']is False and held['claim_exists']is False and held['output_exists']is False and held['new_VM_or_build_executions']==0 and held['prior_case']=='stable-6'
 assert H(P/'held/build-plan-v1/MANIFEST.json')=='8d37820df5dab51cf338b65359146f2a091ede373f75718b942804d67f15b9a1'
 emitted=J(P/'emitted-review/review.json');assert emitted['state']=='PASS_BOUNDED_SHARED_V2_EMITTED_SEQUENCE_REVIEW_NOT_SEMANTIC_CERTIFICATION'and emitted['candidate_sha256']==C and emitted['symbols_sha256']==U and emitted['original1035_strongest_changes_vs6e']==0
 assert emitted['ordinary_collector_6e_only_normalized_delta']=='line174->191 atoffset568;22namedcalls equal'
 raw=J(P/'emitted-review/input-hashes.json')['raw_outputs'];assert set(raw)=={str(f.relative_to(P/'emitted-results'))for f in(P/'emitted-results').rglob('*')if f.is_file()};hash_rows(P/'emitted-results',raw)
 launches=J(P/'emitted-results/launch-results.json');assert len(launches['runs'])==7 and launches['plan_seal']==H(P/'emitted-plan/manifest.json')
 for i,r in enumerate(launches['runs']):
  assert r['returncode']==0
  for k in ['stdout','stderr']:assert H(P/'emitted-results'/f'run-{i}.{k}')==r[k+'_sha256']
 inv=json.loads(gzip.decompress((P/'emitted-results/new-inventory.json.gz').read_bytes()));proof=J(P/'emitted-results/candidate-bodies/proof.json')
 assert inv['candidate_sha256']==proof['candidate_sha256']==C and inv['symbols_sha256']==proof['symbols_sha256']==U and len(inv['original_windows'])==1035 and len(proof['functions'])==24 and proof['source37']==source
 for n in ['baseline-before','baseline-after']:assert json.loads(gzip.decompress((P/'emitted-results'/(n+'.json.gz')).read_bytes()))['baseline_replay_match']
 admission=J(P/'root-observations/cto-shared6093-v2-root-runtime-admission.json');ash=H(P/'root-observations/cto-shared6093-v2-root-runtime-admission.json')
 assert admission['state']=='ROOT_APPROVED_FINITE_V2_RUNTIME_AFTER_EMITTED_REVIEW'and admission['candidate_sha256']==C and admission['source_CTO_sha256']==S and admission['whole_byte_identity_claimed']is False and admission['no_candidate_promotion']is True
 assert admission['parent_plan_seal']==H(P/'acceptance-plan/manifest.json')and admission['independent_acceptance_review_seal']==H(P/'acceptance-plan-review/manifest.json')and admission['emitted_review_seal']==H(P/'emitted-review/manifest.json')
 for lane,folder in [('ordinary','ordinary-gate'),('six-case','six-gate')]:
  assert admission['plan_seals'][lane]==H(P/'acceptance-plan'/lane/'manifest.json')
  gate=raw_result(P/folder,key='raw_gate_files_sha256');assert gate['acceptance_passed']and gate['child_returncode']==0 and gate['inputs_source37_candidate_unchanged']and gate['retry_attempts']==0 and gate['root_admission_sha256']==ash and gate['candidate_sha256']==C
  assert J(P/folder/'claim.json')['one_attempt']is True and J(P/folder/'claim.json')['automatic_retry']is False
  inputs=J(P/'acceptance-plan'/lane/'inputs.json');assert len(inputs)==15
  assert set(inputs)=={str(f.relative_to(P/'acceptance-plan'/lane/'repo'))for f in(P/'acceptance-plan'/lane/'repo').rglob('*')if f.is_file()};hash_rows(P/'acceptance-plan'/lane/'repo',inputs)
 receipt=J(P/'ordinary-results/receipt.json');ex=J(P/'ordinary-results/exit.json');signed=J(P/'ordinary-gate/saved-acceptance.json')
 assert ex['passed']and ex['returncode']==0 and ex['receipt_valid']and ex['inputs_unchanged']and receipt['candidate_sha256']==C
 for n in ['stdout.log','stderr.log','receipt.json']:assert H(P/'ordinary-results'/n)==ex[n.replace('.','_')+'_sha256']
 assert receipt['case_count']==len(receipt['cases'])==363 and receipt['mismatches']==[]
 assert signed['original_successes']==169 and signed['transaction_count']==len(signed['rows'])==726 and signed['signature_fields']==1448
 successes=0;sigfields=0
 baseline_cases=J(P/'acceptance-plan/six-case/prior/receipt.json')['cases']
 for i,row in enumerate(receipt['cases']):
  assert row['match']and row['original']['case']==row['candidate']['case']==row['case']and all(row['original'][k]==row['candidate'][k]for k in FIELDS)
  assert row['original']['logs']!=row['candidate']['logs'];successes+=row['original']['error']is None
  for offset,side in enumerate(['original','candidate']):
   item=row[side];audit=signed['rows'][2*i+offset];rawtx=base64.b64decode(item['transaction_base64'],validate=True)
   assert audit['transaction_sha256']==hashlib.sha256(rawtx).hexdigest()and audit['case']==row['case']['name']and audit['side']==side and audit['all_verified']and audit['top_level_pool_authority_signer']is False
   assert item['signatures_verified']and item['pool_authority_top_level_signer']is False;sigfields+=audit['signatures']
 assert successes==169 and sigfields==1448
 stable=next(x for x in receipt['cases']if x['case']['name']=='stable-6');assert stable['original']['error']is None and stable['candidate']['error']is None
 obs=J(P/'six-results/observations.json');sx=raw_result(P/'six-results');assert obs['failure']is None and obs['vm_calls_attempted']==len(obs['attempts'])==len(obs['signature_audits'])==12 and len(obs['rows'])==6 and obs['retry_attempts']==0
 assert sx['state']=='FINITE_ACCEPTANCE_OBSERVATIONS_RECORDED'and sx['child_returncode']==0 and sx['observations_valid']and sx['inputs_source37_candidate_unchanged']
 cases=J(P/'acceptance-plan/six-case/cases.json');analysis=obs['analysis'];assert analysis['all_original_hypotheses_observed']and analysis['all_six_effects_equal']and analysis==J(P/'six-gate/saved-acceptance.json')['analysis']
 fields=0
 baseline_cases=J(P/'acceptance-plan/six-case/prior/receipt.json')['cases']
 for i,(row,spec)in enumerate(zip(obs['rows'],cases['rows'],strict=True)):
  family=cases['families'][row['family']];base=next(x['case']for x in baseline_cases if x['case']['name']==family['baseline_case_name']);expected=copy.deepcopy(base)
  if row['variant']!='baseline':
   expected['name']+='-'+row['variant'];expected['accounts'][family['target_field']]['patches']=[[108,'02']]
   if row['variant']=='frozen-zero':expected['accounts'][family['target_field']]['tokens']=0
  assert row['case']==expected
  baseline=next(x for x in obs['rows']if x['family']==row['family']and x['variant']=='baseline');before=copy.deepcopy(baseline['original']['before']);token=bytearray.fromhex(before[family['target_field']]['data']);assert len(token)==165 and token[108]==1
  if row['variant']!='baseline':token[108]=2
  if row['variant']=='frozen-zero':token[64:72]=bytes(8)
  before[family['target_field']]['data']=token.hex();assert row['original']['before']==row['candidate']['before']==before
  if row['variant']=='frozen-positive':assert 'Custom(6093)'in row['original']['error']and any('programs/pump/src/creator/admin_cto.rs:'+str(family['positive_origin_hypothesis'])in line for line in row['original']['logs'])
  else:assert row['original']['error']is None
  assert(row['case'],row['family'],row['variant'])==(spec['case'],spec['family'],spec['variant'])and all(row['original'][k]==row['candidate'][k]for k in FIELDS)and row['original']['logs']!=row['candidate']['logs']
  for j,side in enumerate(['original','candidate']):
   assert J(P/'six-results'/f'side-{i:02d}-{side}.json')==row[side]
   marker=J(P/'six-results'/f'attempt-{i:02d}-{side}.json');assert marker==obs['attempts'][2*i+j]and marker['target_call_count_in_this_side']==1
   audit=obs['signature_audits'][2*i+j];tx=base64.b64decode(row[side]['transaction_base64'],validate=True);assert hashlib.sha256(tx).hexdigest()==audit['transaction_sha256']and audit['all_signatures_verified']and audit['pool_authority_top_level_signer']is False;fields+=audit['signature_count']
 assert fields==24
 independent=J(P/'runtime-review/review.json');assert independent['state']=='PASS_SAVED_ORDINARY_AND_FINITE_SIX_CASE_ACCEPTANCE'and independent['candidate']==C and independent['source_CTO']==S and independent['total_saved_transactions']==738 and independent['total_signature_fields']==1472 and independent['source_default_status_or_candidate_promotion']is False and independent['whole_original_byte_identity']is False
 for lane,record in independent['lane_records'].items():
  folder='ordinary'if lane=='ordinary'else'six';hash_rows(P/(folder+'-results'),record['raw_output_hashes']);hash_rows(P/(folder+'-gate'),record['gate_output_hashes'])
 audits=J(P/'runtime-review/signature-audit.json')['rows'];assert len(audits)==738 and sum(x['signature_count']for x in audits)==1472
 saved_items=[('ordinary',r['case']['name'],side,r[side])for r in receipt['cases']for side in ['original','candidate']]+[('six-case',r['case']['name'],side,r[side])for r in obs['rows']for side in ['original','candidate']]
 for audit,(lane,name,side,item)in zip(audits,saved_items,strict=True):assert audit['lane']==lane and audit['case']==name and audit['side']==side and audit['transaction_sha256']==hashlib.sha256(base64.b64decode(item['transaction_base64'],validate=True)).hexdigest()and audit['all_verified']and audit['pool_authority_top_level_signer']is False
 adapter=J(P/'portable-crypto-adapter.json');original=P/adapter['original_checker'];derived=P/adapter['derived_checker'];assert H(original)==adapter['original_sha256']and H(derived)==adapter['derived_sha256'];text=original.read_text()
 for row in adapter['replacements']:assert text.count(row['before'])==1;text=text.replace(row['before'],row['after'])
 assert text==derived.read_text()
 assert(P/'portable-crypto-adapter.diff').read_text()==''.join(difflib.unified_diff(original.read_text().splitlines(True),text.splitlines(True),fromfile='original/verify_results.py',tofile='portable_verify_results.py'))
 assert receipt['provenance']=={n:r['sha256']for n,r in adapter['recorded_provenance_bindings'].items()}
 for row in adapter['recorded_provenance_bindings'].values():assert H(P/rel(row['packaged']))==row['sha256']
 six=adapter['six_checker'];assert H(P/six['original'])==H(P/six['copy'])==six['sha256']and six['replacements']==[]
 return {'state':'PASS_PORTABLE_PASSIVE_FINITE_V2_EVIDENCE','ordinary_cases':363,'ordinary_original_successes':169,'ordinary_saved_transactions':726,'ordinary_recorded_signature_fields':1448,'six_cases':6,'six_saved_transactions':12,'six_recorded_signature_fields':24,'all_effects_equal':True,'all_raw_logs_equal':False,'default_reperformed_crypto':False,'VM_executions':0,'candidate_selected':False,'full_ABI_semantics_or_original_identity_proven':False}

def crypto_checks():
 assert sys.version.startswith('3.12.')and importlib.metadata.version('solders')=='0.27.1'
 def load(name,path):
  m=types.ModuleType(name);m.__file__=str(path);exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
 ordinary=load('portable_ordinary_saved_crypto',P/'portable_verify_results.py').verify_results(P/'ordinary-results')
 library=load('portable_six_saved_crypto',P/'portable_saved_checks.py');obs=J(P/'six-results/observations.json');rows=[]
 for i,row in enumerate(obs['rows']):
  for j,side in enumerate(['original','candidate']):
   audit=library.audit_transaction(row[side]);record=obs['signature_audits'][2*i+j];assert all(record[k]==v for k,v in audit.items());rows.append(audit)
 assert len(rows)==12 and sum(x['signature_count']for x in rows)==24
 return {'state':'PASS_FRESH_SAVED_CRYPTO_NO_VM','ordinary_transactions':ordinary['transaction_count'],'ordinary_signature_fields':ordinary['signature_fields'],'six_transactions':12,'six_actual_signature_fields':24,'target_executions':0}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--expected-seal',required=True);ap.add_argument('--crypto',action='store_true');args=ap.parse_args();assert H(P/'manifest.json')==args.expected_seal and(P/'manifest.sha256').read_text().strip()==args.expected_seal
 result=metadata_checks()
 if args.crypto:result['fresh_saved_crypto']=crypto_checks()
 assert not _CASE_VIOLATIONS,'An exact-case rejected read was caught by executed code'
 print(json.dumps(result,indent=2))

"""Independent unexecuted build-plan/source/control audit. No native launcher or VM."""
from pathlib import Path,PurePosixPath
import json,hashlib,difflib,tomllib
P=Path(__file__).resolve().parent;W=P.parent;Q=W/'cto-shared6093-build-plan-v2';OLD=W/'cto-wallet-collector-build-plan';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();J=lambda p:json.loads(p.read_text())
seal='29069875549ea325beeafc10059c6893218211c327d08a6f90bce70df10e5ae2';assert H(Q/'MANIFEST.json')==seal
m=J(Q/'MANIFEST.json');old=J(OLD/'MANIFEST.json');assert H(OLD/'MANIFEST.json')=='ff7a857b5394b57c61eebb19cf6265fa001b18b2d0f3db4936fd00c48cbb2fa0'
assert set(m)=={str(f.relative_to(Q))for f in Q.rglob('*')if f.is_file()and f!=Q/'MANIFEST.json'}and not any(f.is_symlink()for f in Q.rglob('*'))
for n,h in m.items():
 path=PurePosixPath(n);assert not path.is_absolute()and'..'not in path.parts;assert H(Q/n)==h,n
for n,h in old.items():assert H(OLD/n)==h,n
delta=J(Q/'input-delta.json');expected=[]
for n in sorted(set(old)|set(m)):
 if n=='input-delta.json':continue
 if old.get(n)!=m.get(n):expected.append({'path':n,'before_sha256':old.get(n),'after_sha256':m.get(n),'change':'added'if n not in old else'removed'if n not in m else'modified'})
assert delta['changed_payloads']==expected and len(expected)==241 and delta['unchanged_reused_payloads']==sorted(n for n in old if old[n]==m.get(n))and len(delta['unchanged_reused_payloads'])==84
controller=(OLD/'controller.py').read_text();expected_controller=controller.replace("EXPERIMENT=P.parent/'cto-wallet-collector-build-01'","EXPERIMENT=P.parent/'cto-shared6093-v2-build-01'").replace("CLAIM=P.parent/'cto-wallet-collector-attempt-01.json'","CLAIM=P.parent/'cto-shared6093-v2-attempt-01.json'");assert(Q/'controller.py').read_text()==expected_controller and H(Q/'controller.py')=='4a901458ffda647692fac687a309364e9c1859bd5d7023a5ca11aaeadc1123bf'
for n in['POLICY.md','availability.json','cache-allowlist.json','source-baseline.json','test_controller.py','predecessor-materials-manifest.json']+[n for n in old if n.startswith('helpers/')]:assert(Q/n).read_bytes()==(OLD/n).read_bytes(),n
for name in['controller.py','verify.py','future-plan.json','source-baseline.json','source-proposed.json','POLICY.md']:assert(Q/('predecessor-'+name.lower())).read_bytes()==(OLD/name).read_bytes()
oldp=J(OLD/'future-plan.json');newp=J(Q/'future-plan.json');allowed={'state','future_experiment_root','future_attempt_claim','source_proposal_seal','source_guard_changes','immediate_source_baseline','immediate_source_baseline_role','shared6093_composed'}
assert {k:v for k,v in oldp.items()if k not in allowed}=={k:v for k,v in newp.items()if k not in allowed}
baseline=J(Q/'source-baseline.json');before=J(Q/'source-proposal/source-before.json');after=J(Q/'source-proposed.json');rel='programs/pump/src/admin_cto.rs';assert len(baseline)==len(before)==len(after)==37 and before==J(OLD/'source-proposed.json')and after==J(Q/'source-proposal/source-after.json')
assert before[rel]=='5499f2b14a7ad21ce1a4e5144882230d7bb668fce24fb735803fc78285f0f3a3'and after[rel]=='950d6ec8c07072a3305c905509018f95b40d53e9ab25a4c1bda96b42c2a2fe58'
for prior in[baseline,before]:assert[n for n in after if prior[n]!=after[n]]==[rel]
for n,h in after.items():assert H(Q/'source'/n)==H(Q/'source-proposal/source'/n)==h
for n,h in baseline.items():assert H(W/'pr8-review'/n)==h
source=(Q/'source'/rel).read_text();previous=(Q/'source-proposal/baseline-admin_cto.rs').read_text();assert H(Q/'source-proposal/baseline-admin_cto.rs')==before[rel]
assert source[source.index("fn collect_wallet_creator_fee<'info>"):]==previous[previous.index("fn collect_wallet_creator_fee<'info>"):]
assert source.count('PumpError::CtoSharedVaultFrozen')==2
first=source[source.index('let shared_amm_frozen_zero='):source.index('let wallet=')];assert first.count('data_is_empty()')==2 and first.index('token_frozen(')<first.index('token_raw_amount(')<first.index('PumpError::CtoSharedVaultFrozen')<first.index('invoke_signed(')
later=source[source.index('let (rent,amount,shared_source_frozen)='):source.index('if !shared_source_frozen&&amount>0')];assert later.index('let amount=shared_token_raw_amount(')<later.index('let frozen=shared_token_frozen(')<later.index('PumpError::CtoSharedVaultFrozen')and'if !shared_source_frozen&&amount>0'in source
assert later[later.index('}else{'):].count('Rent::get()?')==0
assert all(source.count(x)==previous.count(x)for x in['#[inline','#[noinline','line!','file!','#[path'])
assert tomllib.loads((Q/'source/programs/pump/Cargo.toml').read_text())['profile']['release']=={'panic':'abort','overflow-checks':True,'lto':False,'codegen-units':1}
for n in['programs/pump/Cargo.toml','programs/pump/Cargo.lock']:assert after[n]==baseline[n]
proposal=Q/'source-proposal';assert H(proposal/'manifest.json')=='23f2162b03a7b5b194c985f5811cb08aa8f1ee3906f4dd8e62fc5792a2704264'
for n,r in J(proposal/'manifest.json').items():assert H(proposal/n)==r['sha256']and(proposal/n).stat().st_size==r['bytes']
for folder,expected_seal in[('saved-oracle-review','4b250110db04a9cdf808286cacd45860df437bc183b882ccb2783122626b5a63'),('admitted-fieldmap','c812166749cde8a0a41d2b67f69eb99ae735493949944ee9decab4664cb49370')]:
 assert H(proposal/folder/'manifest.json')==expected_seal
 for n,r in J(proposal/folder/'manifest.json').items():assert H(proposal/folder/n)==r['sha256']and(proposal/folder/n).stat().st_size==r['bytes']
controls=Q/'oracle-controls';assert H(controls/'manifest.json')=='113b5286f1a8dc88a87f7d3b8a08a12d06f28d1c415b0a58d5c736c6a9b38cfd'
for n in['plan.json','cases.json','POLICY.md']:assert H(controls/n)==J(controls/'manifest.json')[n]
oracle=J(proposal/'saved-oracle-review/review.json');assert oracle['state']=='PASS_SAVED_FINITE_ORACLE_AUDIT_NOT_PRESERVATION'and oracle['case_count']==6 and oracle['transactions']==12 and oracle['positive_original_origins']=={'A':660,'B':719}
assert H(controls/'actual-attempt-claim.json')==oracle['claim_sha256']and oracle['output_files']=={str(f.relative_to(Q/'oracle-output')):H(f)for f in(Q/'oracle-output').rglob('*')if f.is_file()}
assert not(W/'cto-shared6093-v2-build-01').exists()and not(W/'cto-shared6093-v2-attempt-01.json').exists()
assert 'fn shared_token_raw_amount(a:&AccountInfo)->Result<u64>{if a.data_is_empty(){return Ok(0);}token_raw_amount(a)}'in source
assert 'fn shared_token_frozen(a:&AccountInfo)->Result<bool>{if a.data_is_empty(){return Ok(false);}token_frozen(a)}'in source
assert H(Q/'held-plan-manifest.json')=='8d37820df5dab51cf338b65359146f2a091ede373f75718b942804d67f15b9a1'
hold=Q/'held-plan-independent-review';assert H(hold/'manifest.json')=='08c34a535e9fa7d545cb3a89eadd9fc0d4cad35ebc0f162d3d4a9dd62af3bd28'
for n,r in J(hold/'manifest.json').items():assert H(hold/n)==r['sha256']and(hold/n).stat().st_size==r['bytes']
assert J(hold/'hold.json')['source_execution_readiness_approved']is False
assert not(W/'cto-shared6093-build-01').exists()and not(W/'cto-shared6093-attempt-01.json').exists()
result={'status':'PASS_UNEXECUTED_PARTIAL_SHARED6093_BUILD_PLAN_INDEPENDENT_REVIEW','plan_seal':seal,'controller_sha256':H(Q/'controller.py'),'predecessor_seal':H(OLD/'MANIFEST.json'),'input_delta_changed':241,'input_delta_unchanged':84,'controller_only_experiment_claim_substitutions':True,'policy_helpers_cache_tools7_SDK53_recipe_unchanged':True,'source_inputs':37,'only_changed_source':rel,'source_sha256':after[rel],'selected71ec_baseline_checked_separately_from_immediate5499':True,'signed_oracle_output_hashbound_sides':12,'new_native_compiler_VM_network_invocations':0,'new_original_body_decoder_acquisition':0,'actual_attempt_claim_or_output_exists':False,'limitations':['Partial guard/zero-route source hypothesis only; complete shared addressed-call ABI/effects, alias/header domains and historical field packing remain unproven.','Natural new error origins are not forced to original660/719 coordinates.','Current cc1.10 and possibleCCv1.52path remain unchanged measured recipe; nohistoricalcompiler/dependency identity claim.','Inherited controller records aggregate helper/build-sbf status; internal compiler/strip child exits remain unobserved; generated cache additions require separate review.','No actual build or VM run is performed by this review. Root must separately review and own any one execution.']}
saved=J(P/'result.json');assert all(saved[k]==v for k,v in result.items());print(json.dumps(result,indent=2))

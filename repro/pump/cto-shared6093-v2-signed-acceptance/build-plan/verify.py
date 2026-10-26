"""Pure source/material checks for one partial shared6093 build; no native launch."""
from pathlib import Path,PurePosixPath
import ast,hashlib,importlib.util,json,tomllib
P=Path(__file__).resolve().parent;H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();J=lambda p:json.loads(p.read_text())
def safe(n):
 p=PurePosixPath(n);assert not p.is_absolute()and'..'not in p.parts;return p

def verify(repo=None,availability=False):
 assert __debug__
 manifest=J(P/'MANIFEST.json');assert set(manifest)=={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()and f!=P/'MANIFEST.json'}
 for n,h in manifest.items():assert H(P/safe(n))==h,n
 for f in P.rglob('*'):assert not f.is_symlink()and f.name!='__pycache__'and f.suffix!='.pyc'
 old=J(P/'predecessor-manifest.json');assert H(P/'predecessor-manifest.json')=='ff7a857b5394b57c61eebb19cf6265fa001b18b2d0f3db4936fd00c48cbb2fa0'
 delta=J(P/'input-delta.json');expected_delta=[]
 for n in sorted(set(old)|set(manifest)):
  if n=='input-delta.json':continue
  if old.get(n)!=manifest.get(n):expected_delta.append({'path':n,'before_sha256':old.get(n),'after_sha256':manifest.get(n),'change':'added'if n not in old else'removed'if n not in manifest else'modified'})
 assert delta['changed_payloads']==expected_delta and delta['unchanged_reused_payloads']==sorted(n for n in old if old[n]==manifest.get(n))
 for name in['controller.py','verify.py','future-plan.json','source-baseline.json','source-proposed.json','POLICY.md']:assert H(P/('predecessor-'+name.lower()))==old[name]
 for name in['POLICY.md','availability.json','cache-allowlist.json','predecessor-materials-manifest.json','source-baseline.json','test_controller.py']:assert H(P/name)==old[name]
 for n,h in old.items():
  if n.startswith('helpers/'):assert H(P/safe(n))==h
 controller=(P/'predecessor-controller.py').read_text().replace("EXPERIMENT=P.parent/'cto-wallet-collector-build-01'","EXPERIMENT=P.parent/'cto-shared6093-v2-build-01'").replace("CLAIM=P.parent/'cto-wallet-collector-attempt-01.json'","CLAIM=P.parent/'cto-shared6093-v2-attempt-01.json'")
 assert(P/'controller.py').read_text()==controller
 oldp=J(P/'predecessor-future-plan.json');plan=J(P/'future-plan.json');allowed={'state','future_experiment_root','future_attempt_claim','source_proposal_seal','source_guard_changes','immediate_source_baseline','immediate_source_baseline_role','shared6093_composed'}
 assert{k:v for k,v in oldp.items()if k not in allowed}=={k:v for k,v in plan.items()if k not in allowed}
 assert plan['shared6093_composed']=='PARTIAL_GUARDS_ZERO_GATES_ONLY_ABI_EFFECTS_UNPROVED'
 assert H(P/'held-plan-manifest.json')=='8d37820df5dab51cf338b65359146f2a091ede373f75718b942804d67f15b9a1'
 hold=P/'held-plan-independent-review';assert H(hold/'manifest.json')=='08c34a535e9fa7d545cb3a89eadd9fc0d4cad35ebc0f162d3d4a9dd62af3bd28'
 for n,r in J(hold/'manifest.json').items():assert H(hold/n)==r['sha256']and(hold/n).stat().st_size==r['bytes']
 assert J(hold/'hold.json')['new_VM_or_build_executions']==0 and J(hold/'hold.json')['source_execution_readiness_approved']is False
 source_text=(P/'source/programs/pump/src/admin_cto.rs').read_text()
 assert 'fn shared_token_raw_amount(a:&AccountInfo)->Result<u64>{if a.data_is_empty(){return Ok(0);}token_raw_amount(a)}'in source_text
 assert 'fn shared_token_frozen(a:&AccountInfo)->Result<bool>{if a.data_is_empty(){return Ok(false);}token_frozen(a)}'in source_text
 assert plan['future_experiment_root']==str(P.parent/'cto-shared6093-v2-build-01')and plan['future_attempt_claim']==str(P.parent/'cto-shared6093-v2-attempt-01.json')
 q=P/'source-proposal';assert H(q/'manifest.json')==plan['source_proposal_seal']=='23f2162b03a7b5b194c985f5811cb08aa8f1ee3906f4dd8e62fc5792a2704264'
 for n,r in J(q/'manifest.json').items():assert H(q/safe(n))==r['sha256']and(q/n).stat().st_size==r['bytes']
 baseline=J(P/'source-baseline.json');immediate=J(P/'predecessor-source-proposed.json');proposed=J(P/'source-proposed.json');assert baseline==J(P/'predecessor-source-baseline.json')and immediate==J(q/'source-before.json')and proposed==J(q/'source-after.json')
 assert len(baseline)==len(immediate)==len(proposed)==37
 for prior in[baseline,immediate]:assert[n for n in proposed if proposed[n]!=prior[n]]==['programs/pump/src/admin_cto.rs']
 assert immediate['programs/pump/src/admin_cto.rs']=='5499f2b14a7ad21ce1a4e5144882230d7bb668fce24fb735803fc78285f0f3a3'
 assert proposed['programs/pump/src/admin_cto.rs']=='950d6ec8c07072a3305c905509018f95b40d53e9ab25a4c1bda96b42c2a2fe58'
 actual={str(f.relative_to(P/'source')):H(f)for f in(P/'source').rglob('*')if f.is_file()};assert actual==proposed
 for n,h in proposed.items():assert H(q/'source'/safe(n))==h
 if repo:
  for n,h in baseline.items():assert H(Path(repo)/safe(n))==h,n
 spec=importlib.util.spec_from_file_location('unchanged_pure_scanner',P/'helpers/scripts/build_source_manifest.py');scanner=importlib.util.module_from_spec(spec);spec.loader.exec_module(scanner)
 assert scanner.source_manifest(P/'source/programs/pump',P/'source/programs/pump',P/'source',[],cwd=P/'source')==proposed
 for n,h in plan['helper_sha256'].items():assert H(P/'helpers'/safe(n))==h;ast.parse((P/'helpers'/n).read_text())
 assert tomllib.loads((P/'source/programs/pump/Cargo.toml').read_text())['profile']['release']=={'panic':'abort','overflow-checks':True,'lto':False,'codegen-units':1}
 assert proposed['programs/pump/Cargo.lock']==baseline['programs/pump/Cargo.lock']
 lock=tomllib.loads((P/'source/programs/pump/Cargo.lock').read_text());approved={r['name']+'-'+r['version']:r['checksum']for r in lock['package']if r.get('source')};cache=J(P/'cache-allowlist.json');assert len(approved)==cache['lock_packages']==252
 for n,row in cache['files'].items():
  f=safe(n);assert f.parts[0]=='registry'and f.parts[1]in['cache','src','index']
  if f.parts[1]=='cache':assert f.name.endswith('.crate')and row['sha256']==approved[f.name[:-6]]
  if f.parts[1]=='src':assert f.parts[3]in approved
 # Authenticate subset/complete raworacle receipts without importing oracle/harness/native code.
 controls=P/'oracle-controls';assert H(controls/'manifest.json')=='113b5286f1a8dc88a87f7d3b8a08a12d06f28d1c415b0a58d5c736c6a9b38cfd'
 for n in['plan.json','cases.json','POLICY.md']:assert H(controls/n)==J(controls/'manifest.json')[n]
 review=J(q/'saved-oracle-review/review.json');assert review['state']=='PASS_SAVED_FINITE_ORACLE_AUDIT_NOT_PRESERVATION'and review['transactions']==12 and review['actual_signature_fields']==24
 assert H(controls/'actual-attempt-claim.json')==review['claim_sha256'];assert review['output_files']=={str(f.relative_to(P/'oracle-output')):H(f)for f in(P/'oracle-output').rglob('*')if f.is_file()}
 assert plan['proposed_program_build_attempts']==1 and plan['runtime_executions_permitted']==0 and plan['new_fixtures_or_probes_permitted']is False and plan['current_source_status_default_pointer_writes_permitted']is False and plan['candidate_disposition']=='UNSELECTED'
 if availability:
  a=J(P/'availability.json')
  for v in a['tools'].values():assert H(Path(v['path']))==v['sha256']
  sdk=Path(a['sdk_source']);assert{str(f.relative_to(sdk)):H(f)for f in sdk.rglob('*')if f.is_file()and'dependencies'not in f.relative_to(sdk).parts}==a['sdk_source_sha256']
  for row in cache['files'].values():assert H(Path(row['source']))==row['sha256']
 return{'state':'VERIFIED_UNEXECUTED_PARTIAL_SHARED6093_BUILD_PLAN','source_inputs':37,'other36_unchanged':True,'selected71ec_baseline_actual_checked':bool(repo),'immediate5499_baseline_bound':True,'source_proposal_seal':plan['source_proposal_seal'],'availability_rehashed':availability,'current_recipe_unchanged':True,'historical_compiler_dependency_identity_proven':False,'shared_ABI_effects_proven':False,'runtime_executions':0,'new_builds':0,'compiler_strip_children_will_remain_unobserved':True}
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path);ap.add_argument('--availability',action='store_true');a=ap.parse_args();print(json.dumps(verify(a.repo,a.availability),indent=2))

"""Pure source/material checks for one implementation build; no native launcher here."""
from pathlib import Path
import ast,hashlib,importlib.util,json,tomllib
P=Path(__file__).resolve().parent;H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();J=lambda p:json.loads(p.read_text())
def safe(n):
 p=Path(n);assert not p.is_absolute()and'..'not in p.parts;return p

def verify(repo=None,availability=False):
 m=J(P/'MANIFEST.json');assert set(m)=={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()and f.name!='MANIFEST.json'}
 for n,h in m.items():assert H(P/safe(n))==h,n
 for f in P.rglob('*'):assert not f.is_symlink()and f.name!='__pycache__'and f.suffix!='.pyc'
 predecessor=J(P/'predecessor-manifest.json');assert H(P/'predecessor-manifest.json')=='f5d2ce6218e4f56eacda6693ee60dd377c9e4854c0a889989f149cc31fad9985'
 for name in ['controller.py','verify.py','future-plan.json','source-baseline.json','source-proposed.json','POLICY.md']:
  assert H(P/('predecessor-'+name.lower()))==predecessor[name],name
 assert H(P/'POLICY.md')==predecessor['POLICY.md']
 original=(P/'predecessor-controller.py').read_text();expected_controller=original.replace("EXPERIMENT=P.parent/'cto-wallet-build-01'","EXPERIMENT=P.parent/'cto-wallet-collector-build-01'").replace("CLAIM=P.parent/'cto-wallet-attempt-01.json'","CLAIM=P.parent/'cto-wallet-collector-attempt-01.json'")
 assert (P/'controller.py').read_text()==expected_controller
 old_plan=J(P/'predecessor-future-plan.json');new_plan=J(P/'future-plan.json');allowed={'state','future_experiment_root','future_attempt_claim','source_proposal_seal','source_guard_changes','guard6092_unchanged','immediate_source_baseline','immediate_source_baseline_role','shared6093_composed'}
 assert {k:v for k,v in old_plan.items()if k not in allowed}=={k:v for k,v in new_plan.items()if k not in allowed}
 assert new_plan['shared6093_composed']is False and new_plan['guard6092_unchanged']is True
 old=J(P/'predecessor-materials-manifest.json');assert H(P/'predecessor-materials-manifest.json')=='886910366f561a776c7ddb5c910481a576d4659d8bc2e7e61a608c592dbf9146'
 for n in ['availability.json','cache-allowlist.json',*J(P/'future-plan.json')['helper_sha256']]:
  location=('helpers/'+n)if n.startswith('scripts/')else n;assert H(P/location)==old[location]
 q=P/'source-proposal';assert H(q/'manifest.json')=='f8111afc6301c0e1575ecec50046d8f589181c13974b221fa04a744096b92d02'
 for n,row in J(q/'manifest.json').items():assert H(q/n)==row['sha256']and(q/n).stat().st_size==row['bytes']
 baseline=J(P/'source-baseline.json');proposed=J(P/'source-proposed.json');assert baseline==J(P/'predecessor-source-baseline.json')and J(q/'source-before.json')==J(P/'predecessor-source-proposed.json')and proposed==J(q/'source-after.json')
 assert len(baseline)==len(proposed)==37 and[n for n in baseline if baseline[n]!=proposed[n]]==['programs/pump/src/admin_cto.rs']
 actual={str(f.relative_to(P/'source')):H(f)for f in(P/'source').rglob('*')if f.is_file()};assert actual==proposed
 for n,h in proposed.items():assert H(q/'source'/n)==h
 assert H(P/'source/programs/pump/src/admin_cto.rs')=='5499f2b14a7ad21ce1a4e5144882230d7bb668fce24fb735803fc78285f0f3a3'
 for name,h in baseline.items():
  if repo:assert H(Path(repo)/safe(name))==h,name
 # Import only the unchanged pure source scanner, never build_partial_candidate.
 sp=importlib.util.spec_from_file_location('wallet_static_scanner',P/'helpers/scripts/build_source_manifest.py');scanner=importlib.util.module_from_spec(sp);sp.loader.exec_module(scanner)
 assert scanner.source_manifest(P/'source/programs/pump',P/'source/programs/pump',P/'source',[],cwd=P/'source')==proposed
 for n,h in J(P/'future-plan.json')['helper_sha256'].items():assert H(P/'helpers'/n)==h;ast.parse((P/'helpers'/n).read_text())
 profile=tomllib.loads((P/'source/programs/pump/Cargo.toml').read_text())['profile']['release'];assert profile=={'panic':'abort','overflow-checks':True,'lto':False,'codegen-units':1}
 assert proposed['programs/pump/Cargo.lock']==baseline['programs/pump/Cargo.lock']
 lock=tomllib.loads((P/'source/programs/pump/Cargo.lock').read_text());allowed={r['name']+'-'+r['version']:r['checksum']for r in lock['package']if r.get('source')};cache=J(P/'cache-allowlist.json');assert len(allowed)==cache['lock_packages']==252
 for n,row in cache['files'].items():
  f=safe(n);assert f.parts[0]=='registry'and f.parts[1]in['cache','src','index']
  if f.parts[1]=='cache':assert f.name.endswith('.crate')and row['sha256']==allowed[f.name[:-6]]
  if f.parts[1]=='src':assert f.parts[3]in allowed
 plan=J(P/'future-plan.json');assert plan['proposed_program_build_attempts']==1 and plan['runtime_executions_permitted']==0 and not plan['current_source_status_default_pointer_writes_permitted']and plan['candidate_disposition']=='UNSELECTED'
 assert plan['baseline_candidate']=='71ec4d8a646eefc82ba177afbc3d08552deadd65cf2f80ec280862eb768d059c'and plan['source_proposal_seal']==H(q/'manifest.json')
 if availability:
  a=J(P/'availability.json')
  for v in a['tools'].values():assert H(Path(v['path']))==v['sha256']
  sdk=Path(a['sdk_source']);assert{str(f.relative_to(sdk)):H(f)for f in sdk.rglob('*')if f.is_file()and'dependencies'not in f.relative_to(sdk).parts}==a['sdk_source_sha256']
  for row in cache['files'].values():assert H(Path(row['source']))==row['sha256']
 return {'status':'VERIFIED_UNEXECUTED_WALLET_BUILD_PLAN','source_inputs':37,'other36_unchanged':True,'source_proposal_seal':H(q/'manifest.json'),'candidate_disposition':'UNSELECTED','actual_source_baseline_checked':bool(repo),'material_availability_rehashed':availability,'new_builds':0,'runtime_executions':0,'compiler_strip_child_exits_will_remain_unobserved':True}
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path);p.add_argument('--availability',action='store_true');a=p.parse_args();print(json.dumps(verify(a.repo,a.availability),indent=2))

"""Pure plan/input binding check; never imports or executes the harness or a VM."""
from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parent;H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();J=lambda p:json.loads(p.read_text())
CANDIDATE_SHA='6e0c9002d09e0cee6cc738b3a9e0983a8d0cd89374fa2cc7c41fa45910515b9e'
def verify():
 m=J(P/'manifest.json');assert set(m)=={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()and f!=P/'manifest.json'}
 for n,h in m.items():
  q=Path(n);assert not q.is_absolute()and'..'not in q.parts and not(P/q).is_symlink();assert H(P/q)==h,n
 old=J(P/'predecessor-manifest.json');assert H(P/'predecessor-manifest.json')=='fbdde096f45b9b8ffe700a5493a0fa1017a3e614d6329a3d5fee416333c9a8a8'
 for n,h in old.items():assert H(P/('predecessor-controller.py'if n=='controller.py'else n))==h,n
 s=(P/'predecessor-controller.py').read_text();expected=s.replace("E=P.parent/'cto-wallet-build-01'","E=P.parent/'cto-wallet-collector-build-01'").replace("OUT=P.parent/'cto-wallet-preservation-01'","OUT=P.parent/'cto-wallet-collector-preservation-01'").replace("CAND=E/'analysis/candidate.so'","CAND=E/'build-01/artifacts/pump_recovered.so'").replace("EXPECTED='d75d2872c4281183e170ce7d7795d186745e2428005ceb89aa3df95fe7cab9b1'","EXPECTED='"+CANDIDATE_SHA+"'")
 assert(P/'controller.py').read_text()==expected
 inputs=J(P/'inputs.json');assert len(inputs)==15 and set(inputs)=={str(f.relative_to(P/'repo'))for f in(P/'repo').rglob('*')if f.is_file()}
 for n,h in inputs.items():assert H(P/'repo'/n)==h
 b=P.parent/'cto-wallet-collector-build-01';candidate=b/'build-01/artifacts/pump_recovered.so';symbols=b/'build-01/target/sbf-solana-solana/release/pump_recovered.so';assert H(candidate)==CANDIDATE_SHA and candidate.stat().st_size==1589176;assert H(symbols)=='f09ac5696038d7ee9a2d28767b02cbae5b5504a56086d8baf4019f316b8a0c86'and symbols.stat().st_size==2172416
 r=J(P/'build-controller-result.json');assert H(P/'build-controller-result.json')==H(b/'controller-result.json');assert r['state']=='requires-cache-review'and r['helper_exit']==r['build_sbf_aggregate_exit']==0 and r['source_unchanged']and r['source_after']==J(P/'source37.json')and len(r['source_after'])==37
 assert r['proposal_manifest']==H(P/'build-plan-manifest.json')=='ff7a857b5394b57c61eebb19cf6265fa001b18b2d0f3db4936fd00c48cbb2fa0'
 for n,h in r['source_after'].items():assert H(b/'repo'/n)==h
 assert r['source_after']['programs/pump/src/admin_cto.rs']=='5499f2b14a7ad21ce1a4e5144882230d7bb668fce24fb735803fc78285f0f3a3'
 env=J(P/'python-environment.json');assert env['returncode']==0 and env['observed']['version'].startswith('3.12.13')and env['observed']['solders']=='0.27.1';assert H(Path(env['python_path']))==env['binary_sha256']and str(Path(env['python_path']).resolve())==env['resolved_python_path'];assert H(P/'python-preflight.stdout')==env['stdout_sha256']and H(P/'python-preflight.stderr')==env['stderr_sha256']
 for f in P.glob('*.py'):ast.parse(f.read_text())
 assert not(P.parent/'cto-wallet-collector-preservation-01').exists(),'existing attempt; no relaunch'
 return {'status':'PASS_UNEXECUTED_ORDINARY_PRESERVATION_PLAN','input_files':15,'candidate_sha256':CANDIDATE_SHA,'source37_sha256':H(P/'source37.json'),'ordinary_case_count_required_after_execution':363,'ordinary_original_successes_required':169,'harness_imports_or_VM_executions':0,'one_attempt_claim':'Exclusive fresh OUT.mkdir inherited unchanged','shared6093_acceptance':False,'changed_path_acceptance':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))

"""One isolated offline CTO guard build; no selection or target execution."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,re,shutil,subprocess,sys,tomllib,traceback
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
PROPOSAL=P
EXPERIMENT=P.parent/'cto-shared6093-build-01'
CLAIM=P.parent/'cto-shared6093-attempt-01.json'
BASE=P.parent/'pr8-review'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
J=lambda p:json.loads(p.read_text())
def write(path,obj):path.write_text(json.dumps(obj,indent=2)+'\n')
def load_verify():
 spec=importlib.util.spec_from_file_location('frozen_proposal_verify',PROPOSAL/'verify.py')
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return module

def path_checks():
 for root in (P,PROPOSAL,EXPERIMENT,CLAIM):
  for ancestor in [root,*root.parents]:
   if ancestor.exists():assert not ancestor.is_symlink(),str(ancestor)
 for ancestor in [EXPERIMENT,*EXPERIMENT.parents]:
  for rel in ('.cargo/config','.cargo/config.toml','rust-toolchain','rust-toolchain.toml'):
   assert not (ancestor/rel).exists(),str(ancestor/rel)
 assert not EXPERIMENT.exists() and not CLAIM.exists(),'existing attempt; never retry'

def attest():
 a=J(PROPOSAL/'availability.json')
 for v in a['tools'].values():assert H(Path(v['path']))==v['sha256']
 sdk=Path(a['sdk_source'])
 actual={str(f.relative_to(sdk)):H(f)for f in sdk.rglob('*')if f.is_file()and'dependencies'not in f.relative_to(sdk).parts}
 assert actual==a['sdk_source_sha256']
 return {'tools':{k:H(Path(v['path']))for k,v in a['tools'].items()},'sdk':actual}

def source_hashes(root):return {str(f.relative_to(root)):H(f)for f in root.rglob('*')if f.is_file()}
def run():
 verifier=load_verify();verification=verifier.verify(BASE,True);path_checks()
 pins=attest();plan=J(PROPOSAL/'future-plan.json');cache=J(PROPOSAL/'cache-allowlist.json')
 manifest_hash=H(PROPOSAL/'MANIFEST.json')
 assert manifest_hash==EXPECTED_PLAN_SEAL
 # Exclusive durable claim precedes setup and every native invocation.
 with CLAIM.open('x')as f:json.dump({'proposal_manifest':manifest_hash,'controller_sha256':H(Path(__file__)),'candidate':'UNSELECTED','attempts':1},f)
 EXPERIMENT.mkdir();result={'state':'setup','candidate':'UNSELECTED','proposal_manifest':manifest_hash,'verification':verification,'runtime_executions':0,'compiler_child_exit':None,'strip_child_exit':None,'tool_sdk_before':pins,'comparison_capture_staging':'before native build, comparison-only non-source asset; unchanged helper reads after successful compile'}
 repo=EXPERIMENT/'repo';cargo=EXPERIMENT/'cargo-home';rustup=EXPERIMENT/'rustup-seed'
 try:
  shutil.copytree(PROPOSAL/'source',repo)
  shutil.copytree(PROPOSAL/'helpers/scripts',repo/'scripts')
  expected=J(PROPOSAL/'source-proposed.json');assert {k:H(repo/k)for k in expected}==expected
  for name,row in cache['files'].items():
   path=Path(name);assert not path.is_absolute()and'..'not in path.parts
   src=Path(row['source']);assert H(src)==row['sha256']
   dest=cargo/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(src.read_bytes());assert H(dest)==row['sha256']and dest.stat().st_ino!=src.stat().st_ino
  assert source_hashes(cargo)=={k:v['sha256']for k,v in cache['files'].items()}
  host_rustup=Path.home()/'.rustup';settings=tomllib.loads((host_rustup/'settings.toml').read_text());active=settings['default_toolchain']
  (rustup/'toolchains').mkdir(parents=True)
  for entry in (host_rustup/'toolchains').iterdir():
   if entry.name!='solana':(rustup/'toolchains'/entry.name).symlink_to(entry.resolve(),target_is_directory=True)
  assert (rustup/'toolchains'/active).exists()
  (rustup/'settings.toml').write_text('version = "12"\ndefault_toolchain = '+json.dumps(active)+'\nprofile = "minimal"\n')
  (EXPERIMENT/'tmp').mkdir()
  # Comparison-only capture is read by the unchanged helper after compilation.
  original=BASE/'evidence/original/pump/deployed.so';dest=repo/'evidence/original/pump/deployed.so';dest.parent.mkdir(parents=True);dest.write_bytes(original.read_bytes());result['comparison_reference_sha256']=H(dest)
  replacements={'<experiment>':str(EXPERIMENT)}
  cmd=[x.replace('<experiment>',str(EXPERIMENT))for x in plan['build_command']]
  env={k:v.replace('<experiment>',str(EXPERIMENT))for k,v in plan['minimal_environment'].items()}
  env['HOME']=str(Path.home())
  assert not any(k.startswith('CARGO_PROFILE_')or k in ('RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER')for k in env)
  result.update(state='native-build',command=cmd,environment=env);write(EXPERIMENT/'controller-result.json',result)
  with (EXPERIMENT/'helper-stdout.log').open('wb')as out,(EXPERIMENT/'helper-stderr.log').open('wb')as err:
   child=subprocess.run(cmd,cwd=repo,env=env,stdout=out,stderr=err)
  result['helper_exit']=child.returncode
  attempt=EXPERIMENT/'build-01/build-attempt.json'
  if attempt.exists():result['build_sbf_aggregate_exit']=J(attempt).get('returncode')
  log=EXPERIMENT/'build-01/build.log'
  raw=log.read_text(errors='replace')if log.exists()else''
  clean=re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]','',raw)
  result['backend_error_lines']=[line for line in clean.splitlines()if re.match(r'^\s*Error:',line)]
  result['stack_llvm_diagnostics']=[line for line in clean.splitlines()if re.search(r'Stack offset|stack frame|LLVM ERROR|panicked at',line,re.I)]
  result['state']='build-finished' if child.returncode==0 and result.get('build_sbf_aggregate_exit')==0 and not result['backend_error_lines'] and not result['stack_llvm_diagnostics'] else 'failed'
 except BaseException:
  result['state']='failed';result['exception']=traceback.format_exc()
 finally:
  try:
   result['source_after']={k:H(repo/k)for k in J(PROPOSAL/'source-proposed.json')};result['source_unchanged']=result['source_after']==J(PROPOSAL/'source-proposed.json');assert result['source_unchanged']
   result['helpers_after']={k:H(repo/k)for k in plan['helper_sha256']};assert result['helpers_after']==plan['helper_sha256']
   result['tool_sdk_after']=attest();assert result['tool_sdk_after']==pins
   result['private_cache_existing_unchanged']=all(H(cargo/k)==v['sha256']for k,v in cache['files'].items())
   result['private_cache_additions']={k:v for k,v in source_hashes(cargo).items()if k not in cache['files']}
   # Additions require separate archive/lock authentication before acceptance.
   result['cache_additions_require_review']=bool(result['private_cache_additions'])
   assert result['private_cache_existing_unchanged']
   if result['cache_additions_require_review']and result['state']=='build-finished':result['state']='requires-cache-review'
  except BaseException:result['after_attestation_exception']=traceback.format_exc();result['state']='failed'
  write(EXPERIMENT/'controller-result.json',result)
 print(json.dumps({k:v for k,v in result.items()if k in ('state','helper_exit','build_sbf_aggregate_exit','backend_error_lines','source_unchanged','cache_additions_require_review','exception')},indent=2))
 return result
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--expected-plan-seal');args=parser.parse_args();EXPECTED_PLAN_SEAL=args.expected_plan_seal
 if args.execute:
  assert re.fullmatch('[0-9a-f]{64}',EXPECTED_PLAN_SEAL or ''),'Reviewed expected plan seal required'
  result=run();sys.exit(0 if result['state']=='build-finished' else 2)
 else:print(json.dumps(load_verify().verify(BASE,True),indent=2));path_checks();print('READ-ONLY: no claim, copy or native execution')

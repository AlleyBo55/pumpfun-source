"""Optional native Rust source tests. Creates a new output directory; no SBF VM."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.exists();out.mkdir(parents=True);e=json.loads((HERE/'experiment.json').read_text());test=HERE/'host/host-tests.rs';results={}
 for label,variant,test_filter,expected in [('parent','control','feeconfig_prefix_tests::full_buffer_prefix_is_skipped',101),('recovered','origins','feeconfig_prefix_tests',0)]:
  v=e['variants'][variant];folder=out/label;folder.mkdir()
  for name,digest in v['input_sha256'].items():
   assert not Path(name).is_absolute()and'..'not in Path(name).parts
   raw=(ROOT/v['source_paths'][name]).read_bytes();assert sha(raw)==digest
   target=folder/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
  f=folder/'programs/pump-fees/src/lib.rs';f.write_text(f.read_text()+'\n#[cfg(test)] mod feeconfig_prefix_tests { include!("'+str(test)+'"); }\n')
  before={str(f.relative_to(folder)):sha(f.read_bytes())for f in folder.rglob('*')if f.is_file()};cmd=['cargo','test','--manifest-path',str(folder/'programs/pump-fees/Cargo.toml'),'--locked','--offline','--verbose','--lib',test_filter,'--','--nocapture'];env=os.environ.copy();env.update(CARGO_TARGET_DIR=str(out/'target'),CARGO_NET_OFFLINE='true');log=out/(label+'.log')
  with log.open('w')as output:r=subprocess.run(cmd,env=env,stdout=output,stderr=subprocess.STDOUT)
  text=log.read_text();assert r.returncode==expected and before=={str(f.relative_to(folder)):sha(f.read_bytes())for f in folder.rglob('*')if f.is_file()}
  assert ('test result: FAILED. 0 passed; 1 failed;'if label=='parent'else'test result: ok. 3 passed; 0 failed;')in text
  results[label]=dict(command=cmd,exit_code=r.returncode,log_sha256=sha(log.read_bytes()),source_input_sha256=before)
 result=dict(rustc=subprocess.check_output(['rustc','-vV'],text=True),test_sha256=sha(test.read_bytes()),results=results);(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v['exit_code']for k,v in results.items()}))
if __name__=='__main__':main()

from pathlib import Path
import os,shutil,subprocess,hashlib,json,time
W=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def tree(p):return {str(f.relative_to(p)):sha(f.read_bytes())for f in sorted(p.rglob('*'))if f.is_file()}
for label,basis,filter_name,expected in [('parent','events_combined','feeconfig_prefix_tests::full_buffer_prefix_is_skipped',101),('recovered','feeconfig_consuming','feeconfig_prefix_tests',0)]:
 dst=W/f'feeconfig_host_{label}_verified';assert not dst.exists();shutil.copytree(W/basis,dst);p=dst/'programs/pump-fees/src/lib.rs';append='\n#[cfg(test)] mod feeconfig_prefix_tests { include!("'+str(W/'feeconfig-host-tests.rs')+'"); }\n';p.write_text(p.read_text()+append)
 before=tree(dst);cmd=['cargo','test','--manifest-path',str(dst/'programs/pump-fees/Cargo.toml'),'--locked','--offline','--verbose','--lib',filter_name,'--','--nocapture'];env=os.environ.copy();env.update(CARGO_TARGET_DIR=str(W/'feeconfig-host-target'),CARGO_NET_OFFLINE='true');launch=dict(basis=basis,command=cmd,inputs=before,test_sha256=sha((W/'feeconfig-host-tests.rs').read_bytes()),lib_append=append,rustc=subprocess.check_output(['rustc','-vV'],text=True));(W/f'feeconfig-host-{label}-launch.json').write_text(json.dumps(launch,indent=2)+'\n')
 log=W/f'feeconfig-host-{label}-build.log';t=time.monotonic()
 with log.open('w')as output:r=subprocess.run(cmd,env=env,stdout=output,stderr=subprocess.STDOUT)
 text=log.read_text();result=dict(exit_code=r.returncode,expected_exit_code=expected,source_unchanged=tree(dst)==before,compiled_root=text.count('--crate-name pump_fees_candidate ')==1,log_sha256=sha(log.read_bytes()),elapsed_seconds=time.monotonic()-t);(W/f'feeconfig-host-{label}-result.json').write_text(json.dumps(result,indent=2)+'\n');assert r.returncode==expected and result['source_unchanged']and result['compiled_root'],result
 if label=='parent':assert 'test result: FAILED. 0 passed; 1 failed;'in text and 'feeconfig_prefix_tests::full_buffer_prefix_is_skipped ... FAILED'in text
 else:assert 'test result: ok. 3 passed; 0 failed;'in text and all(x in text for x in ['PREFIX_CASES=18','BOUNDARY_CASES=11','VERSION_CASES=6'])
 print(label,result,flush=True)

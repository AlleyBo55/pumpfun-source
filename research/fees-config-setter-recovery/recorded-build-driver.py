from pathlib import Path
import hashlib,json,subprocess,time,shutil,sys
w=Path(__file__).resolve().parent
label=sys.argv[1];src=w/label;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(f.relative_to(src)):sha(f)for f in sorted(src.rglob('*'))if f.is_file()}
env={'PATH':'/work/sdk/rust/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin','RUSTC':'/work/sdk/rust/bin/rustc','CC':'/work/sdk/llvm/bin/clang','AR':'/work/sdk/llvm/bin/llvm-ar','CARGO_HOME':'/cargo','CARGO_TARGET_DIR':'/work/target','CARGO_BUILD_JOBS':'2','CARGO_NET_OFFLINE':'true','RUSTFLAGS':'-Zremap-cwd-prefix='}
cmd=['podman','exec']
for k,v in env.items():cmd+=['-e',k+'='+v]
cmd+=['-w','/work/'+label,'codex-fees-total-20261026','/work/sdk/rust/bin/cargo','build','--verbose','--manifest-path','/work/'+label+'/programs/pump-fees/Cargo.toml','--release','--target','sbpf-solana-solana','--locked','--offline','--jobs','2']
if label in ('located','setters','setters_padded','combined'):
 cmd[cmd.index('build')] = 'rustc'
 cmd += ['--lib', '--', f'--remap-path-prefix=/work/{label}/programs/pump-fees/src/../../../pump-fees-math/=pump-fees-math/', f'--remap-path-prefix=/work/{label}/pump-fees-math/=pump-fees-math/', '--remap-path-prefix=programs/pump-fees/src/../../../pump-fees-math/=pump-fees-math/']
launch=dict(command=cmd,inputs=inputs,rustc_sha256=sha(w/'sdk/rust/bin/rustc'));(w/(label+'-launch.json')).write_text(json.dumps(launch,indent=2)+'\n');start=time.monotonic()
with(w/(label+'-build.log')).open('wb')as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
compiled_root='--crate-name pump_fees_candidate ' in (w/(label+'-build.log')).read_text()
result=dict(compiled_root=compiled_root,exit_code=r.returncode,elapsed_seconds=time.monotonic()-start,log_sha256=sha(w/(label+'-build.log')),source_unchanged=inputs=={str(f.relative_to(src)):sha(f)for f in sorted(src.rglob('*'))if f.is_file()})
if r.returncode==0 and compiled_root:
 shutil.copyfile(w/'target/sbpf-solana-solana/release/pump_fees_candidate.so',w/(label+'-symbols.so'))
 strip=['/Users/shawwalters/.cache/solana/v1.52/platform-tools/llvm/bin/llvm-objcopy','--strip-all',str(w/(label+'-symbols.so')),str(w/(label+'-candidate.so'))];subprocess.run(strip,check=True);result.update(strip_command=strip,candidate_sha256=sha(w/(label+'-candidate.so')),symbols_sha256=sha(w/(label+'-symbols.so')),candidate_bytes=(w/(label+'-candidate.so')).stat().st_size)
(w/(label+'-result.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(r.returncode if compiled_root else 99)

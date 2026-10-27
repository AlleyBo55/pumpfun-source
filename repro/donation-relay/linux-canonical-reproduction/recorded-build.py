from pathlib import Path
import subprocess,json,hashlib,time,shutil
p=Path(__file__).resolve().parent
H=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
inputs={str(f.relative_to(p/'source')):H(f)for f in sorted((p/'source').rglob('*'))if f.is_file()}
container='codex-relay-linux-canonical-20261026'
vars={'PATH':'/sdk/rust/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin','RUSTC':'/sdk/rust/bin/rustc','CC':'/sdk/llvm/bin/clang','AR':'/sdk/llvm/bin/llvm-ar','OBJDUMP':'/sdk/llvm/bin/llvm-objdump','OBJCOPY':'/sdk/llvm/bin/llvm-objcopy','CARGO_HOME':'/cargo','CARGO_TARGET_DIR':'/work/target','CARGO_BUILD_JOBS':'3','CARGO_NET_OFFLINE':'true','CARGO_TARGET_SBPF_SOLANA_SOLANA_RUSTFLAGS':'-Zremap-cwd-prefix='}
cmd=['podman','exec']
for k,v in vars.items():cmd+=['-e',k+'='+v]
cmd+=['-w','/work/source',container,'/sdk/rust/bin/cargo','rustc','--release','--target','sbpf-solana-solana','--locked','--offline','--manifest-path','/work/source/Cargo.toml','--lib','--','--remap-path-prefix=src/=programs/contracts/src/']
(p/'launch.json').write_text(json.dumps(dict(command=cmd,inputs=inputs),indent=2)+'\n');start=time.monotonic()
with(p/'build.log').open('wb')as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
result=dict(exit_code=r.returncode,elapsed_seconds=time.monotonic()-start,build_log_sha256=H(p/'build.log'),source_unchanged=inputs=={str(f.relative_to(p/'source')):H(f)for f in sorted((p/'source').rglob('*'))if f.is_file()})
if not r.returncode:
 shutil.copyfile(p/'target/sbpf-solana-solana/release/donation_relay_source_proposal.so',p/'symbols.so')
 strip=['podman','exec',container,'/sdk/llvm/bin/llvm-objcopy','--strip-all','/work/symbols.so','/work/candidate.so'];(p/'strip-command.json').write_text(json.dumps(strip,indent=2)+'\n');subprocess.run(strip,check=True)
 result.update(candidate_sha256=H(p/'candidate.so'),symbols_sha256=H(p/'symbols.so'),candidate_bytes=(p/'candidate.so').stat().st_size)
(p/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(r.returncode)

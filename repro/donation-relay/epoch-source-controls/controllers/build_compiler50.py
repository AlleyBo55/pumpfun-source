from pathlib import Path
import os,subprocess,hashlib,json,shutil
root=Path.cwd();base=root/'work/relay-residual-20261026';source=base/'source-482';sdk=Path('/Users/shawwalters/.cache/solana/v1.48/platform-tools');compiler=Path('/Users/shawwalters/.cache/solana/v1.50/platform-tools/rust/bin/rustc');out=base/'compiler50-oldlibs';out.mkdir(exist_ok=True);target='sbpf-solana-solana';cache=base/'compiler50-target';cache.mkdir(exist_ok=True)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();inputs={str(p.relative_to(source)):H(p)for p in sorted(source.rglob('*'))if p.is_file()}
env=dict(os.environ)
for key in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','RUSTUP_TOOLCHAIN','RUSTDOCFLAGS']:env.pop(key,None)
env.update(PATH=str(sdk/'rust/bin')+os.pathsep+env.get('PATH',''),RUSTC=str(compiler),CC=str(sdk/'llvm/bin/clang'),AR=str(sdk/'llvm/bin/llvm-ar'),CARGO_HOME='/Users/shawwalters/.cargo',CARGO_TARGET_DIR=str(cache),CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='3')
env['CARGO_TARGET_SBPF_SOLANA_SOLANA_RUSTFLAGS']='-Zremap-cwd-prefix= --sysroot /Users/shawwalters/Documents/Codex/2026-10-24/pumpfun-source/work/relay-linux-v148/sdk/rust -C linker=/Users/shawwalters/.cache/solana/v1.48/platform-tools/llvm/bin/ld.lld'
cmd=[str(sdk/'rust/bin/cargo'),'rustc','-v','--release','--target',target,'--locked','--offline','--manifest-path',str(source/'Cargo.toml'),'--lib','--','--remap-path-prefix=src/=programs/contracts/src/'];version=subprocess.run([str(compiler),'-vV'],capture_output=True,check=True).stdout;(out/'rustc-version.txt').write_bytes(version)
(out/'launch.json').write_text(json.dumps(dict(command=cmd,inputs=inputs,compiler=str(compiler),compiler_sha256=H(compiler),cargo_sha256=H(sdk/'rust/bin/cargo'),linker_sha256=H(sdk/'llvm/bin/ld.lld'),target_rustflags=env['CARGO_TARGET_SBPF_SOLANA_SOLANA_RUSTFLAGS']),indent=2)+'\n')
with(out/'build.log').open('wb') as log:r=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
result=dict(exit_code=r.returncode,source_unchanged=inputs=={str(p.relative_to(source)):H(p)for p in sorted(source.rglob('*'))if p.is_file()},build_log_sha256=H(out/'build.log'))
if not r.returncode:
 binary=cache/target/'release/donation_relay_source_proposal.so';shutil.copyfile(binary,out/'symbols.so');subprocess.run([str(sdk/'llvm/bin/llvm-objcopy'),'--strip-all',str(binary),str(out/'candidate.so')],check=True);result.update(candidate_sha256=H(out/'candidate.so'),symbols_sha256=H(out/'symbols.so'),candidate_bytes=(out/'candidate.so').stat().st_size)
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True);raise SystemExit(r.returncode)

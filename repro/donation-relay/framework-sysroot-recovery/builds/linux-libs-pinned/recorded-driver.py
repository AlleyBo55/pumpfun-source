from pathlib import Path
import os,subprocess,hashlib,json,shutil,sys
root=Path.cwd();base=root/'work/relay-residual-20261026';source=base/'source';sdk=Path('/Users/shawwalters/.cache/solana/v1.48/platform-tools')
if not source.exists():shutil.copytree(root/'repro/donation-relay/distribution-worker-source-recovery/settlement/source',source)
mode=sys.argv[1] if len(sys.argv)>1 else 'legacy';source=base/'source-anchor032-pinned' if mode=='hybrid-linux-sysroot' else source;target='sbf-solana-solana' if mode=='legacy' else 'sbpf-solana-solana';out=base/mode;out.mkdir(exist_ok=True)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
inputs={str(p.relative_to(source)):H(p)for p in sorted(source.rglob('*'))if p.is_file()}
env=dict(os.environ)
for key in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','RUSTUP_TOOLCHAIN','RUSTDOCFLAGS']:env.pop(key,None)
env.update(PATH=str(sdk/'rust/bin')+os.pathsep+env.get('PATH',''),RUSTC=str(sdk/'rust/bin/rustc'),CC=str(sdk/'llvm/bin/clang'),AR=str(sdk/'llvm/bin/llvm-ar'),OBJDUMP=str(sdk/'llvm/bin/llvm-objdump'),OBJCOPY=str(sdk/'llvm/bin/llvm-objcopy'),CARGO_HOME='/Users/shawwalters/Documents/Codex/2026-10-24/pumpfun-source/work/relay-anchor-idl-scaffold/cargo-home',CARGO_TARGET_DIR=str(base/'anchor-v8/target'),CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='3')
if mode=='hybrid-linux-sysroot':env['CARGO_HOME']='/Users/shawwalters/.cargo'
env['CARGO_TARGET_'+target.upper().replace('-','_')+'_RUSTFLAGS']='-Zremap-cwd-prefix= --sysroot /Users/shawwalters/Documents/Codex/2026-10-24/pumpfun-source/work/relay-linux-v148/sdk/rust -C linker=/Users/shawwalters/.cache/solana/v1.48/platform-tools/llvm/bin/ld.lld'
cmd=[str(sdk/'rust/bin/cargo'),'rustc','--release','--target',target,'--locked','--offline','--manifest-path',str(source/'Cargo.toml'),'--lib','--','--remap-path-prefix=src/=programs/contracts/src/']
(out/'launch.json').write_text(json.dumps({'command':cmd,'inputs':inputs,'rustc_sha256':H(sdk/'rust/bin/rustc'),'target':target},indent=2)+'\n')
with (out/'build.log').open('wb')as log:r=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
result={'exit_code':r.returncode,'source_unchanged':inputs=={str(p.relative_to(source)):H(p)for p in sorted(source.rglob('*'))if p.is_file()},'log_sha256':H(out/'build.log')}
if not r.returncode:
 binary=out/'target'/target/'release/donation_relay_source_proposal.so';shutil.copyfile(binary,out/'symbols.so');subprocess.run([str(sdk/'llvm/bin/llvm-objcopy'),'--strip-all',str(binary),str(out/'candidate.so')],check=True)
 result.update(candidate_sha256=H(out/'candidate.so'),symbols_sha256=H(out/'symbols.so'),candidate_bytes=(out/'candidate.so').stat().st_size)
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));sys.exit(r.returncode)

from pathlib import Path
import subprocess,os,json,hashlib,shutil,sys
P=Path(__file__).resolve().parent;ROOT=P.parents[1];H=lambda b:hashlib.sha256(b).hexdigest()
v=sys.argv[1];assert v in ('v1.44','v1.48');out=P/v;out.mkdir(exist_ok=False)
source=ROOT/'programs/donation-relay';sdk=Path('/Users/shawwalters/.cache/solana')/v/'platform-tools'
inputs=json.loads((ROOT/'work/relay-full-errors-v148/source-manifest.json').read_text());assert all(H((source/n).read_bytes())==h for n,h in inputs.items())
(out/'source-manifest.json').write_text(json.dumps(inputs,indent=2)+'\n')
env=dict(os.environ)
for k in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTUP_TOOLCHAIN','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','RUSTDOCFLAGS','CARGO_PROFILE_RELEASE_OPT_LEVEL','CARGO_PROFILE_RELEASE_LTO','CARGO_PROFILE_RELEASE_CODEGEN_UNITS','CARGO_TARGET_SBF_SOLANA_SOLANA_LINKER']:
 env.pop(k,None)
env.update(PATH=str(sdk/'rust/bin')+os.pathsep+env.get('PATH',''),RUSTC=str(sdk/'rust/bin/rustc'),CC=str(sdk/'llvm/bin/clang'),AR=str(sdk/'llvm/bin/llvm-ar'),OBJDUMP=str(sdk/'llvm/bin/llvm-objdump'),OBJCOPY=str(sdk/'llvm/bin/llvm-objcopy'),CARGO_HOME=str(ROOT/'work/relay-idl-discriminator-build/attempt/cargo-home'),CARGO_TARGET_DIR=str(out/'target'),CARGO_TARGET_SBF_SOLANA_SOLANA_RUSTFLAGS='-Zremap-cwd-prefix=',CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='3')
selected={k:env[k] for k in ['RUSTC','CC','AR','OBJDUMP','OBJCOPY','CARGO_HOME','CARGO_TARGET_DIR','CARGO_TARGET_SBF_SOLANA_SOLANA_RUSTFLAGS','CARGO_NET_OFFLINE','CARGO_BUILD_JOBS']};(out/'build-environment.json').write_text(json.dumps(selected,indent=2)+'\n')
cmd=[str(sdk/'rust/bin/cargo'),'build','--release','--target','sbf-solana-solana','--locked','--offline','--manifest-path',str(source/'Cargo.toml')]
(out/'command.json').write_text(json.dumps(cmd,indent=2)+'\n');shutil.copyfile(__file__,out/'driver.py')
closure={str(q.relative_to(sdk)):H(q.read_bytes()) for folder in ['rust/bin','rust/lib','llvm/bin'] for q in sorted((sdk/folder).rglob('*')) if q.is_file()}
(out/'sdk-files.json').write_text(json.dumps(closure,indent=2)+'\n');(out/'version.md').write_bytes((sdk/'version.md').read_bytes());version=subprocess.check_output([str(sdk/'rust/bin/rustc'),'--version','--verbose'],text=True);(out/'rustc-version.txt').write_text(version)
with (out/'build.log').open('wb') as f:r=subprocess.run(cmd,cwd=source,env=env,stdout=f,stderr=subprocess.STDOUT)
facts=dict(returncode=r.returncode,scope='Direct pinned SDK cargo/rustc and explicit same-SDK llvm-objcopy; no rustup/CLI/sdk installer phase can switch toolchains.',source_unchanged=all(H((source/n).read_bytes())==h for n,h in inputs.items()),log_sha256=H((out/'build.log').read_bytes()))
if r.returncode==0:
 raw=out/'target/sbf-solana-solana/release/donation_relay_source_proposal.so';shutil.copyfile(raw,out/'unstripped.so');strip=[str(sdk/'llvm/bin/llvm-objcopy'),'--strip-all',str(raw),str(out/'candidate.so')];subprocess.run(strip,check=True);(out/'strip-command.json').write_text(json.dumps(strip,indent=2)+'\n');data=(out/'candidate.so').read_bytes();expected=(ROOT/('work/relay-full-errors-v148' if v=='v1.48' else 'work/relay-full-error-enums')/'candidate.so').read_bytes();facts.update(candidate_sha256=H(data),candidate_bytes=len(data),equals_previous_cli_candidate=data==expected,unstripped_sha256=H((out/'unstripped.so').read_bytes()))
(out/'result.json').write_text(json.dumps(facts,indent=2)+'\n');print(json.dumps(facts,indent=2));assert r.returncode==0 and facts['source_unchanged'] and facts['equals_previous_cli_candidate']

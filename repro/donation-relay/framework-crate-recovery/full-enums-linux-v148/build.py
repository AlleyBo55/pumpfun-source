from pathlib import Path
import json,subprocess,hashlib,shutil,time
P=Path(__file__).resolve().parent;ROOT=P.parents[1];H=lambda b:hashlib.sha256(b).hexdigest()
info=json.loads((P/'container.json').read_text());c=info['id'];source=P/'source';inputs=json.loads((P/'source-manifest.json').read_text());assert all(H((source/n).read_bytes())==h for n,h in inputs.items());assert not (source/'target').exists()
state=json.loads(subprocess.check_output(['podman','inspect',c],text=True))[0];assert state['State']['Running'];(P/'build-container-inspect.json').write_text(json.dumps(state,indent=2)+'\n')
flags=['-e','PATH=/sdk/rust/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin','-e','RUSTC=/sdk/rust/bin/rustc','-e','CC=/sdk/llvm/bin/clang','-e','AR=/sdk/llvm/bin/llvm-ar','-e','OBJDUMP=/sdk/llvm/bin/llvm-objdump','-e','OBJCOPY=/sdk/llvm/bin/llvm-objcopy','-e','CARGO_TARGET_SBF_SOLANA_SOLANA_RUSTFLAGS=-Zremap-cwd-prefix=']
cmd=['podman','exec',*flags,'-w','/build',c,'/sdk/rust/bin/cargo','build','--release','--target','sbf-solana-solana','--locked','--offline','--manifest-path','/build/Cargo.toml']
(P/'build-command.json').write_text(json.dumps(cmd,indent=2)+'\n');started=time.monotonic()
with (P/'build.log').open('wb') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
facts=dict(returncode=r.returncode,elapsed_seconds=time.monotonic()-started,source_unchanged=all(H((source/n).read_bytes())==h for n,h in inputs.items()),build_log_sha256=H((P/'build.log').read_bytes()),scope='Official Linuxv1.48 SDK in isolated Ubuntu22.04 container, explicit SDK cargo/rustc and objcopy. Only public frozen Rust source, public registry cache and read-only SDK mounts; target ELF is not mounted.')
if r.returncode==0:
 raw=source/'target/sbf-solana-solana/release/donation_relay_source_proposal.so';shutil.copyfile(raw,P/'unstripped.so');cmd=['podman','exec',c,'/sdk/llvm/bin/llvm-objcopy','--strip-all','/build/target/sbf-solana-solana/release/donation_relay_source_proposal.so','/build/linux-v148-stripped.so'];subprocess.run(cmd,check=True);(P/'strip-command.json').write_text(json.dumps(cmd,indent=2)+'\n');shutil.copyfile(source/'linux-v148-stripped.so',P/'candidate.so');b=(P/'candidate.so').read_bytes();facts.update(candidate_sha256=H(b),candidate_bytes=len(b),unstripped_sha256=H((P/'unstripped.so').read_bytes()),equals_native_v148=b==(ROOT/'work/relay-full-errors-v148/candidate.so').read_bytes())
(P/'build-result.json').write_text(json.dumps(facts,indent=2)+'\n');print(json.dumps(facts,indent=2));assert r.returncode==0 and facts['source_unchanged']

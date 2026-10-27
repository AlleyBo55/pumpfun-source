from pathlib import Path
import os,subprocess,json,hashlib,importlib.util,shutil
root=Path.cwd();base=root/'work/relay-residual-20261026';sdk=Path('/Users/shawwalters/.cache/solana/v1.48/platform-tools');H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
proposal=mod('location_proposals',root/'research/relay-location-data-audit/proposals.py');audit=mod('location_audit',root/'research/relay-location-data-audit/audit.py');analysis=mod('location_elf',root/'repro/donation-relay/distribution-worker-source-recovery/analyze.py')
original=(root/'evidence/dependencies/donation_relay/deployed.so').read_bytes();o=analysis.Elf(original);source_base=proposal.full_sources();_,groups=proposal.proposals();baseline=json.loads((base/'mint-search-tuple-old/match-ledger.json').read_text());records=[]
for label in list(groups)+['combined']:
 source=base/('source-location-'+label);out=base/('location-'+label);source.mkdir(exist_ok=True);out.mkdir(exist_ok=True);files=dict(source_base)
 for key,changes in groups.items():
  if label=='combined' or label==key:files.update(changes)
 for n,b in files.items():f=source/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
 env=dict(os.environ)
 for key in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','RUSTUP_TOOLCHAIN','RUSTDOCFLAGS']:env.pop(key,None)
 env.update(PATH=str(sdk/'rust/bin')+os.pathsep+env.get('PATH',''),RUSTC=str(sdk/'rust/bin/rustc'),CC=str(sdk/'llvm/bin/clang'),AR=str(sdk/'llvm/bin/llvm-ar'),CARGO_HOME=str(Path.home()/'.cargo'),CARGO_TARGET_DIR=str(base/'anchor-v8/target'),CARGO_BUILD_JOBS='3',CARGO_NET_OFFLINE='true',CARGO_TARGET_SBPF_SOLANA_SOLANA_RUSTFLAGS='-Zremap-cwd-prefix= --sysroot /Users/shawwalters/Documents/Codex/2026-10-24/pumpfun-source/work/relay-linux-v148/sdk/rust -C linker=/Users/shawwalters/.cache/solana/v1.48/platform-tools/llvm/bin/ld.lld')
 cmd=[str(sdk/'rust/bin/cargo'),'rustc','--verbose','--release','--target','sbpf-solana-solana','--locked','--offline','--manifest-path',str(source/'Cargo.toml'),'--lib','--','--remap-path-prefix=src/=programs/contracts/src/']
 inputs={n:hashlib.sha256(b).hexdigest()for n,b in files.items()};(out/'launch.json').write_text(json.dumps(dict(command=cmd,inputs=inputs,target='sbpf-solana-solana',rustflags=env['CARGO_TARGET_SBPF_SOLANA_SOLANA_RUSTFLAGS']),indent=2)+'\n')
 with(out/'build.log').open('wb')as log:p=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
 result=dict(exit_code=p.returncode,source_unchanged=inputs=={str(f.relative_to(source)):H(f)for f in source.rglob('*')if f.is_file()},build_log_sha256=H(out/'build.log'))
 if not p.returncode:
  shutil.copyfile(base/'anchor-v8/target/sbpf-solana-solana/release/donation_relay_source_proposal.so',out/'symbols.so');subprocess.run([str(sdk/'llvm/bin/llvm-objcopy'),'--strip-all',str(out/'symbols.so'),str(out/'candidate.so')],check=True);result.update(candidate_sha256=H(out/'candidate.so'),symbols_sha256=H(out/'symbols.so'),candidate_bytes=(out/'candidate.so').stat().st_size)
  (out/'original.so').write_bytes(original);shutil.copyfile(out/'symbols.so',out/'unstripped.so');shutil.copyfile(root/'repro/donation-relay/swap-receipt-coordinate-recovery/original-windows.json',out/'original-windows.json');analysis.write(out)
  old=json.loads((out/'original-function-ledger.json').read_text());new=json.loads((out/'candidate-function-ledger.json').read_text());ledger=json.loads((out/'match-ledger.json').read_text());c=analysis.Elf((out/'symbols.so').read_bytes());pairs=[]
  for row in ledger:
   if len(row['normalized_candidate_indices'])!=1:continue
   a=old[row['ordinal']];b=new[row['normalized_candidate_indices'][0]]
   for x,y in zip(a['data_references'],b['data_references']):
    p,q=audit.read_location(o,x['target']),audit.read_location(c,y['target'])
    if p and q:pairs.append(dict(original_ordinal=row['ordinal'],original=p,candidate=q,equal=audit.key(p)==audit.key(q)))
  location=dict(pairs=pairs,recognized=len(pairs),equal=sum(r['equal']for r in pairs),different=sum(not r['equal']for r in pairs));(out/'locations.json').write_text(json.dumps(location,indent=2)+'\n');summary=json.loads((out/'comparison-summary.json').read_text());result.update(normalized=summary['original_normalized_match_windows'],raw=summary['original_raw_match_windows'],lost=[r['ordinal']for x,r in zip(baseline,ledger)if x['normalized_candidate_indices']and not r['normalized_candidate_indices']],location_pairs=location['recognized'],location_differences=location['different'])
 (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');records.append(dict(variant=label,**result));print(json.dumps(records[-1]),flush=True);(base/'location-trials.json').write_text(json.dumps(records,indent=2)+'\n')

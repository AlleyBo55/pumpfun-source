from pathlib import Path
import os,subprocess,json,tomllib,hashlib,tarfile
base=Path('work/relay-residual-20261026').resolve();source=base/'source-anchor-v8';sdk=Path('/Users/shawwalters/.cache/solana/v1.48/platform-tools');env=dict(os.environ,RUSTC=str(sdk/'rust/bin/rustc'),CARGO_HOME='/Users/shawwalters/.cargo');cmd=[str(sdk/'rust/bin/cargo'),'metadata','--offline','--locked','--format-version','1','--filter-platform','sbpf-solana-solana','--manifest-path',str(source/'Cargo.toml')]
raw=subprocess.check_output(cmd,env=env);(base/'anchor-v8/metadata.json').write_bytes(raw);meta=json.loads(raw);lock=tomllib.loads((source/'Cargo.lock').read_text());checks={(p['name'],p['version']):p['checksum']for p in lock['package']if 'checksum'in p};H=lambda b:hashlib.sha256(b).hexdigest();rows=[]
for p in meta['packages']:
 if p['source'] is None:continue
 key=(p['name'],p['version']);digest=checks[key];archives=list(Path('/Users/shawwalters/.cargo/registry/cache').glob('*/'+p['name']+'-'+p['version']+'.crate'));archive=next(a for a in archives if H(a.read_bytes())==digest);src=Path(p['manifest_path']).parent;prefix=p['name']+'-'+p['version']+'/'
 with tarfile.open(archive)as t:files={m.name[len(prefix):]:H(t.extractfile(m).read())for m in t.getmembers()if m.isfile()}
 actual={str(f.relative_to(src))for f in src.rglob('*')if f.is_file()and f.name not in ['.cargo-ok','.cargo-checksum.json']};assert actual==set(files),(key,actual^set(files))
 for name,h in files.items():assert H((src/name).read_bytes())==h,(key,name)
 rows.append(dict(name=key[0],version=key[1],archive_sha256=digest,files=files))
result=dict(packages=rows,package_count=len(rows),file_count=sum(len(x['files'])for x in rows));(base/'anchor-v8/registry-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(result['package_count'],result['file_count'])

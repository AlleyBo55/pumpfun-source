"""Read-only official archive and framework/dependency metadata capture; source archives are data only."""
from pathlib import Path
import concurrent.futures,hashlib,json,urllib.request,urllib.error,datetime,tomllib
P=Path(__file__).resolve().parent;W=P.parent;B=W/'cto-wallet-collector-build-01';PLAN=W/'cto-wallet-collector-build-plan'
J=lambda p:json.loads(p.read_text());H=lambda b:hashlib.sha256(b).hexdigest()
NAMES=sorted({x['name']for x in J(P/'metadata-http.json')})
def fetch(task):
 name,version,role,url,file=task;r={'name':name,'version':version,'role':role,'url':url,'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};request=urllib.request.Request(url,headers={'User-Agent':'pumpfun-source-version-audit/1.0 (read-only public crate metadata)','Accept':'application/json'if role!='archive'else'application/octet-stream'})
 try:
  with urllib.request.urlopen(request,timeout=45)as response:b=response.read();r.update(status=response.status,headers=dict(response.headers),final_url=response.url)
 except urllib.error.HTTPError as e:b=e.read();r.update(status=e.code,headers=dict(e.headers),final_url=e.url)
 except BaseException as e:b=b'';r.update(status=None,error=repr(e))
 dest=P/file;assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b);r.update(file=file,bytes=len(b),sha256=H(b));return r
if __name__=='__main__':
 tasks=[]
 for name in NAMES:tasks.append((name,'0.31.1','archive',f'https://static.crates.io/crates/{name}/{name}-0.31.1.crate',f'archives/{name}-0.31.1.crate'))
 for name in ['anchor-lang','anchor-spl']:
  tasks.append((name,'0.31.1','framework-metadata',f'https://crates.io/api/v1/crates/{name}/0.31.1',f'metadata/{name}-0.31.1.json'))
  tasks.append((name,'0.31.1','dependency-metadata',f'https://crates.io/api/v1/crates/{name}/0.31.1/dependencies',f'dependencies/{name}-0.31.1.json'))
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(fetch,tasks))
 (P/'additional-http.json').write_text(json.dumps(rows,indent=2)+'\n')
 assert all(x['status']==200 for x in rows),[(x['name'],x['role'],x['status'])for x in rows]
 locked={(x['name'],x['version']):x for x in tomllib.loads((B/'repo/programs/pump/Cargo.lock').read_text())['package']};cache=J(PLAN/'cache-allowlist.json')['files'];bindings=[]
 for name,version in [(n,'0.31.2')for n in NAMES]+[(n,'0.31.1')for n in['anchor-lang','anchor-spl']]:
  meta=J(P/'metadata'/f'{name}-{version}.json')['version'];rel=f'registry/cache/index.crates.io-6f17d22bba15001f/{name}-{version}.crate';src=B/'cargo-home'/rel;b=src.read_bytes();assert H(b)==meta['checksum']==locked[name,version]['checksum']==cache[rel]['sha256'];dest=P/'archives'/f'{name}-{version}.crate';assert not dest.exists();dest.write_bytes(b);bindings.append({'name':name,'version':version,'file':str(dest.relative_to(P)),'bytes':len(b),'sha256':H(b),'source':'Authenticated copy of existing immutable current build cache; not an HTTP archive observation','cache_path':str(src),'official_archive_url':f'https://static.crates.io/crates/{name}/{name}-{version}.crate','metadata_checksum':meta['checksum'],'selected_lock_checksum':locked[name,version]['checksum']})
 for name in NAMES:
  f=P/'archives'/f'{name}-0.31.1.crate';m=J(P/'metadata'/f'{name}-0.31.1.json')['version'];assert H(f.read_bytes())==m['checksum']
 for dest,src in [('context/current-Cargo.lock',B/'repo/programs/pump/Cargo.lock'),('context/current-Cargo.toml',B/'repo/programs/pump/Cargo.toml'),('context/build-plan-manifest.json',PLAN/'MANIFEST.json'),('context/cache-allowlist.json',PLAN/'cache-allowlist.json'),('context/current-unit-analysis.json',W/'collector-current-cargo-unit-witness/record/analysis.json')]:
  f=P/dest;f.parent.mkdir(parents=True,exist_ok=True);assert not f.exists();f.write_bytes(src.read_bytes())
 (P/'cached-archive-bindings.json').write_text(json.dumps(bindings,indent=2)+'\n');print(json.dumps({'official_HTTP_reads':len(rows),'all_status200':True,'cached_archives_authenticated':len(bindings),'old0311_archives_authenticated':len(NAMES),'native_build_target_or_source_executions':0},indent=2))

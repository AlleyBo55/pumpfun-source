"""Read-only official crates.io metadata capture. No installs or source/tool execution."""
from pathlib import Path
import concurrent.futures,hashlib,json,urllib.request,urllib.error,datetime
P=Path(__file__).resolve().parent
NAMES=['anchor-attribute-access-control','anchor-attribute-account','anchor-attribute-constant','anchor-attribute-error','anchor-attribute-event','anchor-attribute-program','anchor-derive-accounts','anchor-derive-serde','anchor-derive-space','anchor-syn']
def fetch(pair):
 name,version=pair;url=f'https://crates.io/api/v1/crates/{name}/{version}';req=urllib.request.Request(url,headers={'User-Agent':'pumpfun-source-version-audit/1.0 (read-only public crate metadata)','Accept':'application/json'});result={'name':name,'requested_version':version,'url':url,'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(req,timeout=45)as response:body=response.read();result.update(status=response.status,final_url=response.url,headers=dict(response.headers))
 except urllib.error.HTTPError as e:body=e.read();result.update(status=e.code,headers=dict(e.headers),final_url=e.url)
 except BaseException as e:body=b'';result.update(status=None,error=repr(e))
 dest=P/'metadata'/f'{name}-{version}.json';dest.parent.mkdir(exist_ok=True);assert not dest.exists();dest.write_bytes(body);result.update(bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),file=str(dest.relative_to(P)));return result
if __name__=='__main__':
 pairs=[(name,version)for name in NAMES for version in['0.31.1','0.31.2']]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(fetch,pairs))
 (P/'metadata-http.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps([{'name':r['name'],'version':r['requested_version'],'status':r['status'],'bytes':r['bytes']}for r in rows],indent=2))

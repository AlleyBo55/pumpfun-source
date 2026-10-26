"""Lossless opaque-file inventory helpers; never imports archived code."""
from pathlib import Path,PurePosixPath
import os,stat,json,hashlib
H=lambda b:hashlib.sha256(b).hexdigest()
def require(ok,msg):
 if not ok:raise ValueError(msg)
def path_ok(n):
 p=PurePosixPath(n);require(n==str(p)and not p.is_absolute()and'..'not in p.parts and n not in['','.'],'unsafe path');return p

def no_links(p):
 p=Path(os.path.abspath(p))
 for f in[p,*p.parents]:require(not f.is_symlink(),'symlink ancestor '+str(f))
 return p

def safe_name(n):
 path_ok(n);parts=PurePosixPath(n).parts;require('__pycache__'not in parts and not n.endswith(('.pyc','.pyo')),'cache file');require(not any(x in n for x in['private-security-review','security-followup','audit_coverage']),'forbidden filename');require(not n.endswith('-keypair.json'),'private key filename')
def digest_file(p):
 h=hashlib.sha256();size=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b);size+=len(b)
 return {'sha256':h.hexdigest(),'bytes':size}
def normalized_manifest(raw):
 m=json.loads(raw);m=m['files']if'files'in m else m;require(isinstance(m,dict),'manifest mapping');out={}
 for n,r in m.items():
  safe_name(n);require(n not in['manifest.json','manifest.sha256'],'manifest selfbind');r={'sha256':r}if isinstance(r,str)else r;require(isinstance(r,dict)and len(r['sha256'])==64,'hashrecord');out[n]={'sha256':r['sha256']}
  if'bytes'in r:out[n]['bytes']=r['bytes']
 return out

def authenticate_group(row):
 root=no_links(Path(row['path']));require(root.is_dir(),'MISSING group '+str(root));raw=(root/'manifest.json').read_bytes();require(H(raw)==row['manifest_sha256'],'known raw manifest seal');require((root/'manifest.sha256').read_text().split()[0]==row['manifest_sha256'],'sidecar');declared=normalized_manifest(raw);actual={};dirs={}
 for base,ds,fs in os.walk(root,followlinks=False):
  for name in ds+fs:
   p=Path(base)/name;n=p.relative_to(root).as_posix();safe_name(n);st=p.lstat();require(not stat.S_ISLNK(st.st_mode),'link');mode=stat.S_IMODE(st.st_mode)
   if stat.S_ISDIR(st.st_mode):dirs[n]={'type':'directory','mode':mode}
   else:
    require(stat.S_ISREG(st.st_mode),'special file');require(st.st_nlink==1,'hardlinked file');actual[n]={'type':'file','mode':mode,**digest_file(p)}
 require(set(actual)-{'manifest.json','manifest.sha256'}==set(declared),'unmanifested/missing membership')
 for n,r in declared.items():
  require(actual[n]['sha256']==r['sha256'],'member hash '+n)
  if'bytes'in r:require(actual[n]['bytes']==r['bytes'],'member size '+n)
 return {'group':row['group'],'manifest_sha256':row['manifest_sha256'],'root_mode':stat.S_IMODE(root.stat().st_mode),'members':dict(sorted({**dirs,**actual}.items()))}

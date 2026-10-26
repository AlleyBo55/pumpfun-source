"""UNRUN real packager: explicit pinned groups only; no archive execution."""
from pathlib import Path
import argparse,json,hashlib,gzip,tarfile,io,shutil,os,sys,traceback
sys.dont_write_bytecode=True
from common import *
P=Path(__file__).resolve().parent;LIMIT=64*1024*1024
def plan_gate(seal):
 require(H((P/'manifest.json').read_bytes())==seal==(P/'manifest.sha256').read_text().split()[0],'reviewed plan seal');m=json.loads((P/'manifest.json').read_text());require(set(m)=={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()and f not in[P/'manifest.json',P/'manifest.sha256']},'plan membership')
 for n,h in m.items():require(digest_file(P/n)['sha256']==h,'planmember')
 rows=json.loads((P/'groups.json').read_text());require(len({r['group']for r in rows})==len(rows),'duplicategroup');return rows
class SplitWriter:
 def __init__(self,root,limit=LIMIT):self.root=root;self.limit=limit;self.f=None;self.parts=[];self.h=hashlib.sha256();self.total=0
 def write(self,b):
  self.h.update(b);self.total+=len(b);original=len(b)
  while b:
   if self.f is None:
    name='payload.tar.gz.part%04d'%len(self.parts);self.f=(self.root/name).open('xb');self.parts.append({'path':name,'bytes':0})
   count=min(len(b),self.limit-self.parts[-1]['bytes']);self.f.write(b[:count]);self.parts[-1]['bytes']+=count;b=b[count:]
   if self.parts[-1]['bytes']==self.limit:self.f.close();self.f=None
  return original
 def flush(self):
  if self.f:self.f.flush()
 def close(self):
  if self.f:self.f.close();self.f=None
  for r in self.parts:r['sha256']=digest_file(self.root/r['path'])['sha256']
def package(rows,out,limit=LIMIT,on_created=None):
 # Whole strict authentication occurs before output creation; missing path is fatal, never invented.
 require(len({r['group']for r in rows})==len(rows),'uniquegroups')
 for r in rows:
  safe_name(r['group']);require('/'not in r['group'],'single-component group name')
 no_links(out);require(not out.exists(),'fresh output')
 for r in rows:
  source=no_links(Path(r['path']));require(out!=source and source not in out.parents and out not in source.parents,'output/source overlap')
 snapshots=[authenticate_group(r)for r in rows];out.mkdir()
 if on_created:on_created()
 writer=SplitWriter(out,limit)
 try:
  with gzip.GzipFile(filename='',mode='wb',fileobj=writer,mtime=0,compresslevel=9)as gz:
   with tarfile.open(fileobj=gz,mode='w|',format=tarfile.PAX_FORMAT)as tar:
    for row,snap in zip(rows,snapshots):
     root=Path(row['path']);allmembers={'':{'type':'directory','mode':snap['root_mode']},**snap['members']}
     for n,r in sorted(allmembers.items()):
      name=row['group']+('/'+n if n else'');info=tarfile.TarInfo(name);info.mode=r['mode'];info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
      if r['type']=='directory':info.type=tarfile.DIRTYPE;tar.addfile(info)
      else:
       p=root/n;info.size=r['bytes'];require(digest_file(p)=={'bytes':r['bytes'],'sha256':r['sha256']},'changed during packing')
       with p.open('rb')as f:tar.addfile(info,f)
 finally:writer.close()
 require([authenticate_group(r)for r in rows]==snapshots,'before/after drift')
 inventory={'schema':'P29_LOSSLESS_GROUPS_V1','groups':snapshots,'archive':{'format':'deterministic PAX tar + gzipmtime0','bytes':writer.total,'sha256':writer.h.hexdigest(),'parts':writer.parts,'max_part_bytes':limit},'source_plan_groups_sha256':H((P/'groups.json').read_bytes())}
 (out/'inventory.json').write_text(json.dumps(inventory,sort_keys=True,indent=2)+'\n');return inventory
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--reviewed-plan-sha256',required=True);a.add_argument('--output',type=Path);a.add_argument('--execute',action='store_true');x=a.parse_args();rows=plan_gate(x.reviewed_plan_sha256)
 if not x.execute:print(json.dumps({'status':'UNRUN_PLAN_ONLY','groups':len(rows),'missing_paths':[r['path']for r in rows if not Path(r['path']).is_dir()],'actual_packaging':False}));sys.exit(0)
 require(x.output is not None,'outputrequired');x.output=x.output.absolute();no_links(x.output);require(not x.output.exists(),'fresh output before owned attempt');owned={'created':False}
 def mark_owned():owned['created']=True
 try:
  result=package(rows,x.output.absolute(),on_created=mark_owned);shutil.copyfile(P/'verify_stream.py',x.output/'verify_stream.py');shutil.copyfile(P/'common.py',x.output/'common.py');shutil.copyfile(P/'groups.json',x.output/'pinned-groups.json');files={f.name:digest_file(f)for f in sorted(x.output.iterdir())if f.is_file()};(x.output/'manifest.json').write_text(json.dumps({'files':files},sort_keys=True,indent=2)+'\n');seal=H((x.output/'manifest.json').read_bytes());(x.output/'manifest.sha256').write_text(seal+'  manifest.json\n');print(json.dumps({'status':'PACKAGED_LOSSLESS_NOT_SEMANTIC_ACCEPTANCE','manifest_sha256':seal,'groups':len(rows),'returncode':0}))
 except BaseException:
  if owned['created']and x.output.exists()and not x.output.is_symlink():
   (x.output/'failure.txt').write_text(traceback.format_exc());(x.output/'failure-exit.json').write_text(json.dumps({'status':'FAILED_PRESERVED','returncode':1,'success_seal_claimed':False})+'\n')
  raise

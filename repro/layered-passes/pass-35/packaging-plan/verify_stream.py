"""Stream-only lossless proof verification. No extraction/import/execution of archived members."""
from pathlib import Path
import argparse,json,hashlib,tarfile,gzip,io,sys
sys.dont_write_bytecode=True
from common import *
class Parts(io.RawIOBase):
 def __init__(self,root,parts):self.root=root;self.parts=iter(parts);self.f=None;self.h=hashlib.sha256();self.size=0
 def readable(self):return True
 def readinto(self,b):
  while True:
   if self.f is None:
    row=next(self.parts,None)
    if row is None:return 0
    self.f=(self.root/row['path']).open('rb')
   raw=self.f.read(len(b))
   if raw:b[:len(raw)]=raw;self.h.update(raw);self.size+=len(raw);return len(raw)
   self.f.close();self.f=None
 def close(self):
  if self.f:self.f.close()
  super().close()
def stream(root,inventory,pinned):
 require(len(inventory['groups'])==len(pinned),'groupcount');require([r['group']for r in inventory['groups']]==[r['group']for r in pinned],'pinnedgrouporder');expected={};groupdata={};sealed={}
 for r,p in zip(inventory['groups'],pinned):
  require(r['manifest_sha256']==p['manifest_sha256'],'known innerseal');name=r['group'];safe_name(name);require('/'not in name,'single-component group name');expected[name]={'type':'directory','mode':r['root_mode']};groupdata[name]={}
  for n,m in r['members'].items():safe_name(n);expected[name+'/'+n]=m
  sealed[name]=r['manifest_sha256']
 parts=inventory['archive']['parts'];require(len({r['path']for r in parts})==len(parts),'duplicateparts')
 for i,r in enumerate(parts):
  require(r['path']=='payload.tar.gz.part%04d'%i,'ordered canonical partnames');require(0<r['bytes']<=min(64*1024*1024,inventory['archive']['max_part_bytes']),'partlimit');require(i==len(parts)-1 or r['bytes']==inventory['archive']['max_part_bytes'],'nonfinal partsize');require(digest_file(no_links(root/r['path']))=={'bytes':r['bytes'],'sha256':r['sha256']},'partbytes')
 reader=Parts(root,parts);seen=set()
 with io.BufferedReader(reader)as buffered:
  with gzip.GzipFile(fileobj=buffered,mode='rb')as gz:
   with tarfile.open(fileobj=gz,mode='r|')as tar:
    for member in tar:
     name=member.name;safe_name(name);require(name in expected and name not in seen,'extra/duplicate member');seen.add(name);r=expected[name];require(member.uid==member.gid==member.mtime==0 and member.uname==member.gname=='','deterministicheaders');require(member.mode==r['mode'],'lossless mode');require(not member.issym()and not member.islnk(),'archive link')
     if r['type']=='directory':require(member.isdir()and member.size==0,'directorytype');continue
     require(member.isfile()and member.size==r['bytes'],'regular file size');h=hashlib.sha256();n=0;keep=name.split('/',1)[1]in['manifest.json','manifest.sha256'];saved=bytearray()
     with tar.extractfile(member)as f:
      for b in iter(lambda:f.read(1024*1024),b''):h.update(b);n+=len(b);saved.extend(b)if keep else None
     require(n==r['bytes']and h.hexdigest()==r['sha256'],'stream raw hash');group,relative=name.split('/',1);groupdata[group][relative]={'bytes':n,'sha256':h.hexdigest()}
     if keep:groupdata[group][relative]['raw']=bytes(saved)
   # Drain through gzip footer and all remaining compressed parts; never extract members.
   for b in iter(lambda:gz.read(1024*1024),b''):require(not b.strip(b'\0'),'nonzero trailing tar data')
  for b in iter(lambda:buffered.read(1024*1024),b''):pass
 require(seen==set(expected),'missingmembers');require(reader.size==inventory['archive']['bytes']and reader.h.hexdigest()==inventory['archive']['sha256'],'whole concatenatedarchive')
 for name,values in groupdata.items():
  manifest=values['manifest.json']['raw'];require(H(manifest)==sealed[name],'raw inner seal');require(values['manifest.sha256']['raw'].decode().split()[0]==sealed[name],'inner sidecar');declared=normalized_manifest(manifest);actual=set(values)-{'manifest.json','manifest.sha256'};require(set(declared)==actual,'strict inner membership')
  for n,r in declared.items():require(values[n]['sha256']==r['sha256']and('bytes'not in r or values[n]['bytes']==r['bytes']),'inner rawpayload')
 return {'status':'PASS_LOSSLESS_STREAM_ONLY','groups':len(pinned),'members':len(seen),'archive_bytes':reader.size,'archived_code_imports_or_execution':0,'extracted_files':0}
def verify(root,seal):
 no_links(root);require(H((root/'manifest.json').read_bytes())==seal==(root/'manifest.sha256').read_text().split()[0],'outerknownseal');m=json.loads((root/'manifest.json').read_text())['files'];require(set(m)=={f.name for f in root.iterdir()if f.is_file()and f.name not in['manifest.json','manifest.sha256']},'outermembership')
 for f in root.iterdir():require(f.is_file()and not f.is_symlink(),'outer special/dir/link')
 for n,r in m.items():safe_name(n);require(digest_file(root/n)==r,'outerrawfile')
 pinned=json.loads((root/'pinned-groups.json').read_text());inventory=json.loads((root/'inventory.json').read_text());require(H((root/'pinned-groups.json').read_bytes())==inventory['source_plan_groups_sha256'],'pinnedinventorydigest');return stream(root,inventory,pinned)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--package',type=Path,required=True);a.add_argument('--expected-seal',required=True);x=a.parse_args();print(json.dumps(verify(x.package.absolute(),x.expected_seal),indent=2))

"""Materialize official Rust crate files as data and compare source bytes; no code execution."""
from pathlib import Path,PurePosixPath
import hashlib,json,tarfile,io,difflib,tomllib
P=Path(__file__).resolve().parent;J=lambda p:json.loads(p.read_text());H=lambda b:hashlib.sha256(b).hexdigest()
def main():
 rows=[];inventories={}
 for f in sorted((P/'archives').glob('*.crate')):
  name,version=f.stem.rsplit('-',1);metadata=J(P/'metadata'/f'{name}-{version}.json')['version'];raw=f.read_bytes();assert H(raw)==metadata['checksum']and len(raw)==metadata['crate_size'];files={}
  with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz')as tar:
   for member in tar.getmembers():
    n=PurePosixPath(member.name);assert not n.is_absolute()and'..'not in n.parts and n.parts[0]==name+'-'+version
    if member.isdir():continue
    assert member.isfile();rel=PurePosixPath(*n.parts[1:]).as_posix();assert rel not in files;b=tar.extractfile(member).read();dest=P/'source'/name/version/rel;assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b);files[rel]={'sha256':H(b),'bytes':len(b),'archive_mode':member.mode,'retained_file':str(dest.relative_to(P))}
  md=tomllib.loads((P/'source'/name/version/'Cargo.toml').read_text());assert md['package']['name']==name and md['package']['version']==version
  inventories[name,version]=files;rows.append({'name':name,'version':version,'archive':str(f.relative_to(P)),'archive_sha256':H(raw),'files':files,'package_manifest':md,'vcs':J(P/'source'/name/version/'.cargo_vcs_info.json')if'.cargo_vcs_info.json'in files else None,'license_files':[n for n in files if any(x in PurePosixPath(n).name.upper()for x in['LICENSE','COPYING','NOTICE'])]})
 comparisons=[]
 for name in sorted({x['name']for x in rows if x['version']=='0.31.2'}):
  a=inventories[name,'0.31.1'];b=inventories[name,'0.31.2'];added=sorted(set(b)-set(a));removed=sorted(set(a)-set(b));changed=sorted(n for n in set(a)&set(b)if a[n]['sha256']!=b[n]['sha256']);rs_a={n for n in a if n.endswith('.rs')};rs_b={n for n in b if n.endswith('.rs')};rustchanged=sorted(n for n in rs_a&rs_b if a[n]['sha256']!=b[n]['sha256']);diffs=[]
  for n in changed:
   old=(P/a[n]['retained_file']).read_bytes();new=(P/b[n]['retained_file']).read_bytes()
   try:text=''.join(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile=f'{name}/0.31.1/{n}',tofile=f'{name}/0.31.2/{n}'))
   except UnicodeDecodeError:continue
   dest=P/'diffs'/name/(n+'.diff');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text);diffs.append(str(dest.relative_to(P)))
  comparisons.append({'name':name,'files0311':len(a),'files0312':len(b),'added':added,'removed':removed,'changed':changed,'rust_files0311':len(rs_a),'rust_files0312':len(rs_b),'rust_added':sorted(rs_b-rs_a),'rust_removed':sorted(rs_a-rs_b),'rust_changed':rustchanged,'all_rust_source_byte_identical':rs_a==rs_b and not rustchanged,'diff_files':diffs})
 (P/'source-inventory.json').write_text(json.dumps(rows,indent=2)+'\n');(P/'comparisons.json').write_text(json.dumps(comparisons,indent=2)+'\n');print(json.dumps(comparisons,indent=2))
if __name__=='__main__':main()

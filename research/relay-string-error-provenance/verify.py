#!/usr/bin/env python3
"""Recheck saved compiler probes and independently derive the ELF attribution."""
from pathlib import Path
import gzip,hashlib,importlib.util,json,re,struct
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
def H(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text())
def load(p):
    spec=importlib.util.spec_from_file_location('relay_typeid_elf',p)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def derive():
    parent=ROOT/'repro/donation-relay/token-extension-version-recovery'
    old=ROOT/'repro/donation-relay/swap-receipt-coordinate-recovery'
    a=load(old/'analyze.py')
    original_bytes=(ROOT/'evidence/dependencies/donation_relay/deployed.so').read_bytes()
    candidate_bytes=gzip.decompress((parent/'builds/anchor-v8/symbols.so.gz').read_bytes())
    assert H(original_bytes)=='367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563'
    assert H(candidate_bytes)=='f4691718db894fd7de8ae2cb7c58274428773893518527072f7fa61140071a11'
    original=a.Elf(original_bytes);candidate=a.Elf(candidate_bytes)
    windows=read(old/'original-windows.json')
    def body(elf,start):
        b=elf.at(start,56)
        assert b[0:4]==bytes.fromhex('18020000') and b[24:28]==bytes.fromhex('18020000')
        assert b[16:24]==bytes.fromhex('7b21080000000000') and b[40:]==bytes.fromhex('7b210000000000009500000000000000')
        vals=[struct.unpack_from('<I',b,o+4)[0]+(struct.unpack_from('<I',b,o+12)[0]<<32)for o in (0,24)]
        return dict(start=start,body_hex=b.hex(),sha256=H(b),halves=[hex(v)for v in vals])
    orig=[dict(ordinal=i,**body(original,windows[i]['start']))for i in [56,267,351]]
    assert len({r['sha256']for r in orig})==1
    names={s['start']:s['name']for s in candidate.symbols if s['type']==2}
    section=candidate.by_name['.data.rel.ro'];data=candidate.section_bytes(section)
    records=[]
    for s in candidate.symbols:
        if 'Error7type_id'not in s['name']:continue
        record=dict(name=s['name'],**body(candidate,s['start']));refs=[]
        needle=struct.pack('<Q',s['start']);cursor=0
        while True:
            off=data.find(needle,cursor)
            if off<0:break
            cursor=off+1
            if off<32:continue
            fields=[]
            for delta in [-32,-24,-8,0,8]:
                address=struct.unpack_from('<Q',data,off+delta)[0]
                fields.append(dict(delta=delta,address=address,symbol=names.get(address,'')))
            assert all('StringError' in fields[j]['symbol']for j in [0,1,4])
            refs.append(dict(typeid_pointer_address=section['address']+off,fields=fields))
        assert refs;record['vtables']=refs;records.append(record)
    assert len(records)==3 and len({r['sha256']for r in records})==1
    return dict(original_sha256=H(original_bytes),candidate_symbols_sha256=H(candidate_bytes),original_windows=orig,candidate_functions=records)

def halves(asm):
    x=re.search(r'(_ZN\w+Error7type_id[^:\n]*):\n(.*?)\.Lfunc_end',asm,re.S)
    assert x
    values=re.findall(r'lddw r\d+, (-?\d+)',x[2]);assert len(values)==2
    return [hex(int(v)%(1<<64))for v in values]

def verify():
    manifest=read(P/'manifest.json')
    files={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()and f.name!='manifest.json'and '__pycache__'not in f.parts}
    assert files==set(manifest)
    for name,digest in manifest.items():
        path=P/name;assert not path.is_symlink()and path.resolve().is_relative_to(P)and H(path.read_bytes())==digest,name
    parent=read(P/'parent.json')
    for path,digest in parent.items():assert H((ROOT/path).read_bytes())==digest,path
    evidence=derive();assert evidence==read(P/'elf-evidence.json')
    rows=read(P/'matrix/results.json');success=0;matched=[]
    target=sorted(evidence['original_windows'][0]['halves'])
    candidate=sorted(evidence['candidate_functions'][0]['halves'])
    for r in rows:
        directory=P/'matrix'/r['directory']
        if r['returncode']:
            assert "can't find crate for `std`"in(directory/'build.log').read_text()
            assert not(directory/'probe.s').exists();continue
        actual=halves((directory/'probe.s').read_text())
        assert actual==r['typeid_halves'];assert sorted(actual)!=target
        if sorted(actual)==candidate:matched.append(r['directory'])
        assert r['sysroot_hashes'];success+=1
    assert len(rows)==19 and success==17
    assert matched==['v1.48-sbpf-solana-solana']
    controls=read(P/'controls/results.json')
    for r in controls:
        assert r['returncode']==0
        assert halves((P/'controls'/(r['name']+'.s')).read_text())==r['halves']
    assert len(controls)==6
    print(json.dumps(dict(attempts=len(rows),successful_probes=success,matched_original=0,candidate_matches=matched,controls=len(controls),remaining_windows=22),indent=2))
if __name__=='__main__':verify()

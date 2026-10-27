#!/usr/bin/env python3
"""For each metadata_only unmatched window, extract the ORIGINAL (file, line)
its error-origin captures, and which reconstruction helper it corresponds to.
Separates line!() (small 0x62 imm) from the Anchor error code (6000-6999).
Read-only; produces a call-site map, writes no bytes to any ELF."""
import json,sys,collections,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from elf_reader import Elf
ROOT=HERE.parents[1]
orig=Elf(ROOT/'evidence/original/pump/deployed.so')
sym=Elf(ROOT/'work/head-score/symbols.so')
d=json.load(open(HERE/'pump-bodies.json'))
unm=[r for r in d['original_windows'] if not r['candidate_matches']]
bysize=collections.defaultdict(list)
for fn in sym.funcs: bysize[fn['size']].append(fn)

def read_str(elf,addr,length):
    for name,s in elf.secs.items():
        if s[3]<=addr<s[3]+s[5] and s[1]!=8:
            fo=s[4]+(addr-s[3]); return elf.b[fo:fo+length].decode('latin1')
    return None

def origin(elf,start,size):
    b=elf.b; fn=None; line=None
    for at in range(start,start+size,8):
        if b[at]==0x7a:
            L=struct.unpack_from('<i',b,at+4)[0]
            for back in range(8,72,8):
                j=at-back
                if j>=start and b[j]==0x18:
                    ptr=struct.unpack_from('<I',b,j+4)[0]|(struct.unpack_from('<I',b,j+12)[0]<<32)
                    s=read_str(elf,ptr,L) if 0<L<90 else None
                    if s and s.endswith('.rs'): fn=s
        if b[at]==0x62:
            v=struct.unpack_from('<i',b,at+4)[0]
            if 0<v<6000 and line is None: line=v   # line!(), not the 6000+ code
    return fn,line

rows=[]
for r in unm:
    s,e=r['start'],r['end']; on=orig.normalized[s:e]
    cands=bysize.get(e-s,[])
    if not cands: continue
    best=None
    for f in cands:
        cn=sym.normalized[f['start']:f['start']+f['size']]
        h=sum(a!=b for a,b in zip(on,cn))
        if best is None or h<best[0]: best=(h,f,cn)
    h,f,cn=best
    diffs=[i for i in range(e-s) if on[i]!=cn[i]]
    if not diffs or not {on[(i//8)*8] for i in diffs} <= {0x62,0x7a}: continue
    of,ol=origin(orig,s,e)
    rows.append({'off':r['start_hex'],'size':e-s,'orig_file':of,'orig_line':ol,'helper':f['name']})

byfile=collections.Counter(r['orig_file'] for r in rows)
bysz=collections.Counter(r['size'] for r in rows)
print("metadata_only windows mapped:",len(rows))
print("--- original call-site FILES (count of windows) ---")
for fpath,c in byfile.most_common(): print("  %-55s %d"%(fpath,c))
print("--- window sizes (one dominant helper?) ---")
for sz,c in bysz.most_common(8): print("  size=%-6d %d"%(sz,c))
json.dump(rows,open(HERE/'metadata-callsite-map.json','w'),indent=2)
print("wrote metadata-callsite-map.json")

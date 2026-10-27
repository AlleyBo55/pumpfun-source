#!/usr/bin/env python3
"""Classify each unmatched original window by the nature of its best same-size
candidate's differences:
  - metadata_only: every differing byte lies in the immediate field of a
    stw(0x62)/stdw(0x7a) store-immediate instruction -> file!()/line!() origin
    metadata (body logic already byte-identical).
  - body_diff: at least one differing byte is in a real logic instruction.
  - no_same_size_candidate: no candidate function of that size (missing/wrong).
Read-only."""
import json,sys,collections
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

def classify(on,cn):
    diffs=[i for i in range(len(on)) if on[i]!=cn[i]]
    for off in diffs:
        ins=(off//8)*8
        op=on[ins]
        inimm = (off-ins)>=4            # byte 4..7 = immediate field
        if not (op in (0x62,0x7a) and inimm):
            return False
    return True

cats=collections.Counter(); meta_bytes=0; body_windows=[]; meta_windows=[]
for r in unm:
    s,e=r['start'],r['end']; on=orig.normalized[s:e]
    cands=bysize.get(e-s,[])
    if not cands:
        cats['no_same_size_candidate']+=1; continue
    best=None
    for fn in cands:
        cn=sym.normalized[fn['start']:fn['start']+fn['size']]
        h=sum(a!=b for a,b in zip(on,cn))
        if best is None or h<best[0]: best=(h,cn,fn['name'])
    h,cn,name=best
    if classify(on,cn):
        cats['metadata_only']+=1; meta_windows.append((r['start_hex'],e-s,h,name))
    else:
        cats['body_diff']+=1; body_windows.append((r['start_hex'],e-s,h,name))

print("unmatched windows:",len(unm))
for k,v in cats.most_common(): print("  %-26s %d"%(k,v))
meta_sz=sum(sz for _,sz,_,_ in meta_windows)
print("metadata_only total body bytes (already correct logic):",meta_sz)
json.dump({'counts':dict(cats),
           'metadata_only':[{'off':o,'bytes':sz,'ham':h} for o,sz,h,_ in meta_windows],
           'body_diff_sample':[{'off':o,'bytes':sz,'ham':h,'name':n[:70]} for o,sz,h,n in sorted(body_windows,key=lambda x:x[1])[:40]]},
          open(HERE/'frontier-classification.json','w'),indent=2)
print("wrote frontier-classification.json")

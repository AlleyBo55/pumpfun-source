#!/usr/bin/env python3
"""Full audit spec for every unmatched Pump .text window. Extracts measurable
signals only (sizes, call structure, external symbols, Anchor error codes,
original file!()/line!()); reproduces no proprietary logic. Read-only."""
import json,sys,re,struct,collections
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

def short(name):  # pull the readable rust path out of a mangled symbol
    m=re.search(r'(pump_recovered|anchor_lang|anchor_spl|spl_token_2022|spl_token|solana_program)[0-9a-zA-Z_$.]*',name or '')
    s=m.group(0) if m else (name or '')
    s=re.sub(r'17h[0-9a-f]{16}E?$','',s); return s[:90]

def read_str(elf,addr,length):
    for nm,s in elf.secs.items():
        if s[3]<=addr<s[3]+s[5] and s[1]!=8:
            fo=s[4]+(addr-s[3]); return elf.b[fo:fo+length].decode('latin1')
    return None

def origin_and_codes(elf,start,size):
    b=elf.b; fn=None; line=None; codes=set()
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
            if 6000<=v<7000: codes.add(v)
            elif 0<v<6000 and line is None: line=v
    return fn,line,sorted(codes)

def classify(on,cn):
    diffs=[i for i in range(len(on)) if on[i]!=cn[i]]
    return 'metadata_only' if diffs and {on[(i//8)*8] for i in diffs}<={0x62,0x7a} else 'body_diff'

rows=[]
for r in unm:
    s,e=r['start'],r['end']; sz=e-s; on=orig.normalized[s:e]
    ext=sorted({x['symbol'] for x in r['external_calls'] if x.get('symbol')})
    fn,line,codes=origin_and_codes(orig,s,sz)
    cands=bysize.get(sz,[])
    if not cands:
        cat='no_same_size_candidate'; best_name=None; ham=None
    else:
        best=None
        for f in cands:
            cn=sym.normalized[f['start']:f['start']+f['size']]
            h=sum(a!=b for a,b in zip(on,cn))
            if best is None or h<best[0]: best=(h,f['name'],cn)
        ham=best[0]; best_name=short(best[1]); cat=classify(on,best[2])
    rows.append({'off':r['start_hex'],'size':sz,'category':cat,'closest_candidate':best_name,
                 'normalized_hamming':ham,'orig_file':fn,'orig_line':line,'anchor_error_codes':codes,
                 'direct_calls':len(r['direct_calls']),'indirect_calls':len(r['indirect_calls']),
                 'data_refs':len(r['data_references']),'external_calls':ext})

json.dump(rows,open(HERE/'frontier-spec.json','w'),indent=2)
# ---- summaries ----
cat=collections.Counter(x['category'] for x in rows)
print("unmatched windows:",len(rows),dict(cat))
bd=[x for x in rows if x['category']=='body_diff']
print("\n== body_diff: closest-candidate clusters (reconstruction fn nearest to an unmatched original) ==")
cl=collections.defaultdict(lambda:[0,0,[]])
for x in bd:
    c=cl[x['closest_candidate']]; c[0]+=1; c[1]+=x['size']; c[2].append(x['normalized_hamming'])
for name,(n,tb,hams) in sorted(cl.items(),key=lambda kv:-kv[1][0])[:18]:
    print("  n=%-3d bytes=%-7d minham=%-4d %s"%(n,tb,min(hams),name))
ns=[x for x in rows if x['category']=='no_same_size_candidate']
print("\n== no_same_size_candidate: size distribution (top) ==")
for sz,n in collections.Counter(x['size'] for x in ns).most_common(12):
    print("  size=%-6d n=%d"%(sz,n))
print("\n== no_same_size_candidate: by recovered original file ==")
for f,n in collections.Counter(x['orig_file'] for x in ns if x['orig_file']).most_common(12):
    print("  %-55s %d"%(f,n))
print("\n== most-referenced external calls among unmatched windows ==")
ec=collections.Counter(s for x in rows for s in x['external_calls'])
for s,n in ec.most_common(12): print("  %-40s %d"%(s,n))
print("\nwrote frontier-spec.json")

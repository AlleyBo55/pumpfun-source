#!/usr/bin/env python3
"""Full audit spec for every unmatched Pump .text window: size, category,
closest same-size reconstruction function and normalized Hamming distance, the
original file!()/line!() of every Anchor error-origin site (line!() read from
the Source slot paired with the file-length store), program error codes, call
and data-reference counts, external call symbols. Closest-size symbols suggest
but do not establish function attribution. Requires explicit trusted inputs
and a fresh JSON output; no ELF is modified.
"""
import argparse, collections, importlib.util, json, re, struct, sys
from pathlib import Path

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--elf-reader', type=Path, required=True, help='Explicit trusted elf_reader.py implementation; not bundled')
ap.add_argument('--original', type=Path, required=True, help='Explicit captured original; inspected only on deliberate invocation')
ap.add_argument('--symbols', type=Path, required=True, help='Matching unstripped reconstruction ELF')
ap.add_argument('--catalog', type=Path, required=True, help='Matching pump-bodies.json scorer catalog')
ap.add_argument('--output', type=Path, required=True, help='Fresh output JSON path; existing evidence is never replaced')
args = ap.parse_args()
for name in ['elf_reader', 'original', 'symbols', 'catalog']:
    path = getattr(args, name).resolve()
    if not path.is_file():
        ap.error('--' + name.replace('_', '-') + ': missing explicit input: ' + str(path))
    setattr(args, name, path)
args.output = args.output.absolute()
if args.output.exists() or args.output.is_symlink():
    ap.error('--output must be fresh; preserve the existing file')
if not args.output.parent.is_dir():
    ap.error('--output parent directory must already exist')
# Import no decoder until all explicit inputs and output admission are valid.
spec = importlib.util.spec_from_file_location('_explicit_frontier_elf_reader', args.elf_reader)
reader = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = reader
spec.loader.exec_module(reader)
Elf = reader.Elf
orig = Elf(args.original)
sym = Elf(args.symbols)
with args.catalog.open() as stream:
    d = json.load(stream)
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

def source_sites(elf,start,size):
    """Anchor error-origin Source{filename,line} sites inside one window, in
    instruction order. A site is a stdw (0x7a) of the file!() length whose
    preceding lddw (0x18, <=8 instructions back) points at a '.rs' string of
    that length, paired with the stw (0x62) of line!() into the adjacent slot
    (same base register, length slot + 8) within 8 instructions. Pairing by
    slot keeps Anchor framework error codes (100-5999, e.g. 2006, 3002, 4101),
    which are stored with the same opcode, from being read as line numbers."""
    b=elf.b; sites=[]
    for at in range(start,start+size,8):
        if b[at]!=0x7a: continue
        L=struct.unpack_from('<i',b,at+4)[0]
        if not 0<L<90: continue
        fn=None
        for back in range(8,72,8):
            j=at-back
            if j>=start and b[j]==0x18:
                ptr=struct.unpack_from('<I',b,j+4)[0]|(struct.unpack_from('<I',b,j+12)[0]<<32)
                s=read_str(elf,ptr,L)
                if s and s.endswith('.rs'): fn=s; break
        if fn is None: continue
        reg=b[at+1]&15; slot=struct.unpack_from('<h',b,at+2)[0]+8; line=None
        for k in sorted(range(-64,72,8),key=abs):
            j=at+k
            if start<=j<start+size and b[j]==0x62 and b[j+1]&15==reg and struct.unpack_from('<h',b,j+2)[0]==slot:
                line=struct.unpack_from('<i',b,j+4)[0]; break
        sites.append((fn,line))
    return sites

def origin_and_codes(elf,start,size):
    sites=source_sites(elf,start,size)
    fn,line=sites[0] if sites else (None,None)
    codes=sorted({v for at in range(start,start+size,8) if elf.b[at]==0x62
                  for v in [struct.unpack_from('<i',elf.b,at+4)[0]] if 6000<=v<7000})
    return fn,line,codes,['%s:%s'%x for x in sites]

def classify(on,cn):
    diffs=[i for i in range(len(on)) if on[i]!=cn[i]]
    return 'metadata_only' if diffs and all(on[(i//8)*8] in (0x62,0x7a) and i%8>=4 for i in diffs) else 'body_diff'

rows=[]
for r in unm:
    s,e=r['start'],r['end']; sz=e-s; on=orig.normalized[s:e]
    ext=sorted({x['symbol'] for x in r['external_calls'] if x.get('symbol')})
    fn,line,codes,sites=origin_and_codes(orig,s,sz)
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
                 'normalized_hamming':ham,'orig_file':fn,'orig_line':line,'source_sites':sites,'anchor_error_codes':codes,
                 'direct_calls':len(r['direct_calls']),'indirect_calls':len(r['indirect_calls']),
                 'data_refs':len(r['data_references']),'external_calls':ext})

json.dump(rows,args.output.open('x'),indent=2)
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
print("\nwrote",args.output)

#!/usr/bin/env python3
"""For each metadata_only unmatched window, extract the ORIGINAL error-origin
sites (file!() path and line!()) from the original binary, the closest
same-size reconstruction function, and which error-origin stores differ
(file!() length, line!(), or both). line!() is read from the Source slot paired
with the file-length store, not from the first small stw immediate. Requires
explicit trusted inputs and a fresh JSON output; no ELF is modified.
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

def read_str(elf,addr,length):
    for name,s in elf.secs.items():
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

def short(name):  # drop the build-specific legacy-mangling hash suffix
    return re.sub(r'17h[0-9a-f]{16}E$','',name)

rows=[]
for r in unm:
    s,e=r['start'],r['end']; sz=e-s; on=orig.normalized[s:e]
    cands=bysize.get(sz,[])
    if not cands: continue
    best=None
    for f in cands:
        cn=sym.normalized[f['start']:f['start']+sz]
        h=sum(a!=b for a,b in zip(on,cn))
        if best is None or h<best[0]: best=(h,f,cn)
    h,f,cn=best
    diffs=[i for i in range(sz) if on[i]!=cn[i]]
    if not diffs or not all(on[(i//8)*8] in (0x62,0x7a) and i%8>=4 for i in diffs): continue
    ops={on[(i//8)*8] for i in diffs}
    differs={frozenset({0x62,0x7a}):'file+line',frozenset({0x62}):'line',frozenset({0x7a}):'file'}[frozenset(ops)]
    code_diff=any(on[at]==0x62 and max(struct.unpack_from('<i',orig.b,s+at+4)[0],struct.unpack_from('<i',sym.b,f['start']+at+4)[0])>=6000
                  for at in {(i//8)*8 for i in diffs})
    sites=source_sites(orig,s,sz)
    of,ol=sites[0] if sites else (None,None)
    rows.append({'off':r['start_hex'],'size':sz,'orig_file':of,'orig_line':ol,
                 'source_sites':['%s:%s'%x for x in sites],'differs':differs,
                 'error_code_also_differs':code_diff,'helper':short(f['name'])})

byfile=collections.Counter(r['orig_file'] for r in rows)
bysz=collections.Counter(r['size'] for r in rows)
print("metadata_only windows mapped:",len(rows))
print("--- which error-origin stores differ from the best same-size candidate ---")
for k in ('file+line','line','file'): print("  %-10s %d"%(k,sum(r['differs']==k for r in rows)))
print("  (of which also differ in an Anchor error code: %d)"%sum(r['error_code_also_differs'] for r in rows))
print("--- original call-site FILES (first Source site; count of windows) ---")
for fpath,c in byfile.most_common(): print("  %-60s %d"%(fpath,c))
print("--- window sizes (one dominant helper?) ---")
for sz,c in bysz.most_common(8): print("  size=%-6d %d"%(sz,c))
# Stronger check than the closest candidate: does ANY same-size reconstruction
# function differ from ANY unmatched window only in file!()-length immediates?
# If none does, relocating source files alone cannot flip a window.
file_only=0
for r in unm:
    s,e=r['start'],r['end']; on=orig.normalized[s:e]
    for f in bysize.get(e-s,[]):
        cn=sym.normalized[f['start']:f['start']+e-s]
        diffs=[i for i in range(e-s) if on[i]!=cn[i]]
        if diffs and all(on[(i//8)*8]==0x7a and i%8>=4 for i in diffs): file_only+=1; break
print("unmatched windows with any same-size candidate differing only in file!() length:",file_only,"of",len(unm))
json.dump(rows,args.output.open('x'),indent=2)
print("wrote",args.output)

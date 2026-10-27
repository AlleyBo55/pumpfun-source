#!/usr/bin/env python3
"""Classify normalized nearest-size body differences using a store-immediate heuristic.
The metadata_only name is historical: immediate similarity does not establish
source metadata or correct logic. Missing/mis-sized candidates are not proof of
missing source functions. Requires explicit trusted inputs; writes a fresh JSON.
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

def classify(on,cn):
    diffs=[i for i in range(len(on)) if on[i]!=cn[i]]
    if not diffs:
        return False
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
print("metadata_only total body bytes (heuristic classification):",meta_sz)
json.dump({'counts':dict(cats),
           'metadata_only':[{'off':o,'bytes':sz,'ham':h} for o,sz,h,_ in meta_windows],
           'body_diff_sample':[{'off':o,'bytes':sz,'ham':h,'name':n[:70]} for o,sz,h,n in sorted(body_windows,key=lambda x:x[1])[:40]]},
          args.output.open('x'),indent=2)
print("wrote",args.output)

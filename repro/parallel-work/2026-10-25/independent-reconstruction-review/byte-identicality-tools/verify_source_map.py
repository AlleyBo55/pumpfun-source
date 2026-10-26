#!/usr/bin/env python3
"""Verification oracle for byte-identicality reconstruction: compare a CANDIDATE
.so's panic/Location source map to the ORIGINAL's recovered map (from
extract_source_map.py). Tells you, per original source file, whether the
candidate reproduces the same set of Location (line, column) sites.

Usage: verify_source_map.py <program> <candidate.so> [original-source-maps.json]
A file is MATCH only when the candidate contains a file of the SAME path with
the SAME (line,col) set — i.e. the reconstruction's module layout AND statement
line positions match the original. Use it as a progress meter while restructuring.
"""
import json, re, struct, sys
from pathlib import Path

PROJ = re.compile(rb'(?:programs/[A-Za-z0-9_\-]+|[A-Za-z0-9_\-]+-math|[A-Za-z0-9_\-]+-vault)/src/[A-Za-z0-9_/\-]+\.rs')

def sections(b):
    shoff = struct.unpack_from('<Q', b, 40)[0]
    entsize, count, idx = struct.unpack_from('<HHH', b, 58)
    raw = [struct.unpack_from('<IIQQQQIIQQ', b, shoff + i * entsize) for i in range(count)]
    names = b[raw[idx][4]:raw[idx][4] + raw[idx][5]]
    return {names[r[0]:].split(b'\0', 1)[0].decode(): {'offset': r[4], 'size': r[5]} for r in raw}

def extract_map(b):
    secs = sections(b)
    rel = secs['.rel.dyn']
    relocs = {struct.unpack_from('<Q', b, o)[0]: struct.unpack_from('<Q', b, o + 8)[0]
              for o in range(rel['offset'], rel['offset'] + rel['size'], 16)}
    data = secs['.data.rel.ro']; d0, d1 = data['offset'], data['offset'] + data['size']
    files = {}
    for m in PROJ.finditer(b):
        for nul in (False, True):
            if nul and (m.end() >= len(b) or b[m.end()] != 0):
                continue
            needle = struct.pack('<QQ', m.start() << 32, len(m[0]) + int(nul))
            off = d0
            while (off := b.find(needle, off, d1)) >= 0:
                if relocs.get(off) == 8:
                    line, col = struct.unpack_from('<II', b, off + 16)
                    if 0 < line < 100000 and 0 < col < 1000:
                        files.setdefault(m[0].decode(), set()).add((line, col))
                off += 1
    return files

prog = sys.argv[1]
cand = Path(sys.argv[2]).read_bytes()
mapfile = Path(sys.argv[3]) if len(sys.argv) > 3 else Path('/tmp/original-source-maps.json')
orig = {k: set(tuple(x) for x in v) for k, v in json.load(open(mapfile))[prog].items()}
cm = extract_map(cand)

orig_sites = sum(len(v) for v in orig.values())
cand_sites = sum(len(v) for v in cm.values())
exact_files = sum(1 for f in orig if f in cm and cm[f] == orig[f])
exact_sites = sum(len(orig[f] & cm.get(f, set())) for f in orig)
print(f"{prog}: original {len(orig)} files / {orig_sites} sites ; candidate {len(cm)} files / {cand_sites} sites")
print(f"  files fully matching (path + exact line/col set): {exact_files}/{len(orig)}")
print(f"  (file,line,col) sites matched: {exact_sites}/{orig_sites}")
print("  per original file:")
for f in sorted(orig):
    c = cm.get(f)
    if c is None:
        st = "MISSING (not a file in candidate)"
    elif c == orig[f]:
        st = "MATCH"
    else:
        st = f"PARTIAL {len(orig[f] & c)}/{len(orig[f])} (cand extra {sorted(c - orig[f])[:3]})"
    print(f"    [{st:40}] {f}  lines {sorted({l for l,_ in orig[f]})}")

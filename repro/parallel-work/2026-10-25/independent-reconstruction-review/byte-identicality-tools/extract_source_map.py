#!/usr/bin/env python3
"""Extract the ORIGINAL programs' panic/track_caller Location records for the
PROJECT's own source files (not just stdlib), producing a per-file source map
file -> sorted unique (line, column). This is the recovered "source map":
where every Location-bearing statement sits in the original source tree.

Read-only against evidence/original/<prog>/deployed.so. Record format (proven by
repro/compiler-fingerprints/analyze.py): a 24-byte &Location static laid out as
  [filename_ptr:u64 = file_offset<<32][filename_len:u64][line:u32][col:u32]
with an R_SBF_64_RELATIVE (info==8) relocation at the record offset.
"""
import json, re, struct, sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
PROGRAMS = ['pump', 'pump_amm', 'pump_fees', 'mayhem']
# project source path roots (anchored so concatenated string blobs resolve to the real start)
PROJ = re.compile(rb'(?:programs/[A-Za-z0-9_\-]+|[A-Za-z0-9_\-]+-math|[A-Za-z0-9_\-]+-vault)/src/[A-Za-z0-9_/\-]+\.rs')

def sections(b):
    shoff = struct.unpack_from('<Q', b, 40)[0]
    entsize, count, idx = struct.unpack_from('<HHH', b, 58)
    raw = [struct.unpack_from('<IIQQQQIIQQ', b, shoff + i * entsize) for i in range(count)]
    names = b[raw[idx][4]:raw[idx][4] + raw[idx][5]]
    return {names[r[0]:].split(b'\0', 1)[0].decode(): {'offset': r[4], 'size': r[5]} for r in raw}

out = {}
summary = {}
for name in PROGRAMS:
    p = ROOT / 'evidence/original' / name / 'deployed.so'
    if not p.exists():
        continue
    b = p.read_bytes()
    secs = sections(b)
    rel = secs['.rel.dyn']
    relocs = {struct.unpack_from('<Q', b, o)[0]: struct.unpack_from('<Q', b, o + 8)[0]
              for o in range(rel['offset'], rel['offset'] + rel['size'], 16)}
    data = secs['.data.rel.ro']
    d0, d1 = data['offset'], data['offset'] + data['size']
    files = {}
    seen_paths = set()
    for m in PROJ.finditer(b):
        path = m[0].decode()
        start = m.start()
        for nul in (False, True):
            if nul and (m.end() >= len(b) or b[m.end()] != 0):
                continue
            length = len(m[0]) + int(nul)
            needle = struct.pack('<QQ', start << 32, length)
            off = d0
            while (off := b.find(needle, off, d1)) >= 0:
                if relocs.get(off) == 8:
                    line, col = struct.unpack_from('<II', b, off + 16)
                    if 0 < line < 100000 and 0 < col < 1000:
                        files.setdefault(path, set()).add((line, col))
                        seen_paths.add(path)
                off += 1
    files = {k: sorted(v) for k, v in sorted(files.items())}
    out[name] = files
    summary[name] = {
        'project_files': len(files),
        'total_location_sites': sum(len(v) for v in files.values()),
        'per_file': {k: {'sites': len(v), 'line_min': v[0][0], 'line_max': v[-1][0]} for k, v in files.items()},
    }

dest = ROOT / 'scratchpad_out' if False else Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()
(Path(sys.argv[2]) if len(sys.argv) > 2 else Path('/tmp')).mkdir(parents=True, exist_ok=True) if len(sys.argv) > 2 else None
outdir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('/tmp')
(outdir / 'original-source-maps.json').write_text(json.dumps(out, indent=1) + '\n')
(outdir / 'original-source-maps-summary.json').write_text(json.dumps(summary, indent=1) + '\n')
for n in out:
    print(f"\n=== {n}: {summary[n]['project_files']} project files, {summary[n]['total_location_sites']} Location sites ===")
    for f, info in summary[n]['per_file'].items():
        print(f"  {info['sites']:3} sites  lines {info['line_min']}-{info['line_max']}  {f}")

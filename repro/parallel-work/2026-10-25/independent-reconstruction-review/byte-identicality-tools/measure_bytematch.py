#!/usr/bin/env python3
"""Quantify whole-binary byte-match of candidate ELFs vs the original deployed ELF.
Reports: whole-ELF offset-aligned equal bytes, per-section sizes + equal bytes, and
exact original source-path-string recovery. Compares BEFORE (committed candidate,
standalone) and AFTER (new build) so the delta is explicit.

Usage: measure_bytematch.py <prog> <dir> <original.so> <before.so> <after.so>
  <dir> = original crate dir (pump|pump-amm|pump-fees|mayhem-program) for path strings.
"""
import sys, json, struct, hashlib, re

def sections(b):
    # returns {name: (offset,size,address)} and elf_extent
    e_shoff = struct.unpack_from('<Q', b, 40)[0]
    e_shentsize, e_shnum, e_shstrndx = struct.unpack_from('<HHH', b, 58)
    raw = [struct.unpack_from('<IIQQQQIIQQ', b, e_shoff + i*e_shentsize) for i in range(e_shnum)]
    strtab = raw[e_shstrndx][4]
    secs = {}
    end = 0
    for r in raw:
        name = b[strtab + r[0]:].split(b'\0', 1)[0].decode('latin1')
        off, size, addr, typ = r[4], r[5], r[3], r[1]
        if name:
            secs[name] = (off, size, addr)
        if typ != 8 and off + size > end:  # SHT_NOBITS(8) occupies no file space
            end = off + size
    end = max(end, e_shoff + e_shnum*e_shentsize)
    return secs, end

def eqbytes(x, y):
    n = min(len(x), len(y))
    return sum(1 for i in range(n) if x[i] == y[i]), n

def whole_elf(orig, cand):
    _, eo = sections(orig); _, ec = sections(cand)
    o, c = orig[:eo], cand[:ec]
    n = min(len(o), len(c))
    eq = sum(1 for i in range(n) if o[i] == c[i])
    first = next((i for i in range(n) if o[i] != c[i]), None)
    return {'orig_elf': eo, 'cand_elf': ec, 'shared': n, 'equal': eq,
            'pct_of_orig': round(100*eq/eo, 4), 'first_diff': first,
            'elf_sha_equal': hashlib.sha256(o).hexdigest() == hashlib.sha256(c).hexdigest()}

def per_section(orig, cand):
    so, _ = sections(orig); sc, _ = sections(cand)
    rows = {}
    for name, (oo, osz, _) in so.items():
        if name in sc:
            co, csz, _ = sc[name]
            eq, shared = eqbytes(orig[oo:oo+osz], cand[co:co+csz])
            rows[name] = {'orig_size': osz, 'cand_size': csz, 'equal': eq, 'shared': shared,
                          'pct': round(100*eq/osz, 2) if osz else None}
        else:
            rows[name] = {'orig_size': osz, 'cand_size': None, 'equal': 0, 'shared': 0, 'pct': 0.0}
    return rows

def path_strings(b, d):
    pat = re.compile(('programs/' + re.escape(d) + r'/src/[A-Za-z0-9_/]+\.rs').encode())
    return set(m.decode() for m in pat.findall(b))

def section_equal(x, y):
    """For each section name common to both, is the content byte-identical? (size + bytes)"""
    sx, _ = sections(x); sy, _ = sections(y)
    rows = {}
    for name in sorted(set(sx) | set(sy)):
        if name in sx and name in sy:
            ox, szx, _ = sx[name]; oy, szy, _ = sy[name]
            same = (szx == szy and x[ox:ox+szx] == y[oy:oy+szy])
            rows[name] = {'size_x': szx, 'size_y': szy, 'identical': same}
        else:
            rows[name] = {'size_x': sx.get(name, (0,0,0))[1] if name in sx else None,
                          'size_y': sy.get(name, (0,0,0))[1] if name in sy else None,
                          'identical': False}
    return rows

def main():
    prog, d, op, bp, ap = sys.argv[1:6]
    orig = open(op, 'rb').read(); before = open(bp, 'rb').read(); after = open(ap, 'rb').read()
    opaths = path_strings(orig, d)
    out = {
        'program': prog, 'dir': d,
        'whole_elf': {'before': whole_elf(orig, before), 'after': whole_elf(orig, after)},
        'path_strings': {
            'original_count': len(opaths),
            'before_present': len(opaths & path_strings(before, d)),
            'after_present': len(opaths & path_strings(after, d)),
        },
        'before_vs_after_identical': hashlib.sha256(before).hexdigest() == hashlib.sha256(after).hexdigest(),
        'before_vs_after_sections': section_equal(before, after),
        'sections': {'before': per_section(orig, before), 'after': per_section(orig, after)},
    }
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()

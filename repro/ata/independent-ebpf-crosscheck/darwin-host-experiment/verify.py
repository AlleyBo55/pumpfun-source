#!/usr/bin/env python3
"""Offline verifier for the Darwin-host ATA build experiment (negative result).

Re-derives, from the retained build output and the deployed program, every fact
claimed in REPORT.md, using only the standard library. Exits non-zero on drift.

    python3 verify.py          # assert recorded facts
    python3 verify.py --json   # machine-readable result
"""

import hashlib
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

DEPLOYED = os.path.join(ROOT, "evidence/dependencies/associated_token/deployed.so")
CANDIDATE2 = os.path.join(ROOT, "repro/ata/monomorph-order-proof/candidate2.so")
DARWIN = os.path.join(HERE, "darwin-x86_64-f5ce86.so")

EXPECTED = {
    "deployed_sha256": "6804554e69fd3a58caa191dc4a58f4c67223d30ca28ab8987f39fc18d2f7374d",
    "candidate2_sha256": "ba8dd8a42ca7bff4b668c72e1b5614e9363b271924d520253f5724760ba2d65b",
    "darwin_sha256": "c6957a0eca84a9e36835fe9956de6deca0be64fedf95794adb61cae5fd067c86",
    "file_bytes": 105032,
    "darwin_vs_deployed_diffs": 3288,
    "darwin_vs_candidate2_diffs": 2981,
    "candidate2_vs_deployed_diffs": 307,
    "darwin_diffs_by_section": {".text": 3267, ".rel.dyn": 21},
    "rodata_identical": True,
    "section_layout_identical": True,
    # the two reserve_for_push bodies (call-masked), deployed-binary file offsets
    "pair_windows": {"AccountMeta": [28592, 29032], "u8": [29032, 29384]},
    "pair_order": {"deployed": "AccountMeta->u8", "candidate2": "u8->AccountMeta", "darwin": "u8->AccountMeta"},
    "masked_text_insn_multiset_only_in_each": 9,
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sections(d):
    shoff = struct.unpack("<Q", d[40:48])[0]
    shentsize, shnum, shstrndx = struct.unpack("<HHH", d[58:64])
    raw = []
    for i in range(shnum):
        o = shoff + i * shentsize
        name, _typ, _flags, _addr, off, size = struct.unpack("<IIQQQQ", d[o:o + 40])
        raw.append((name, off, size))
    stro = raw[shstrndx][1]
    out = {}
    for name, off, size in raw:
        n = d[stro + name:d.index(b"\0", stro + name)].decode()
        if n:
            out[n] = (off, size)
    return out


def mask_calls(b):
    out = bytearray(b)
    for p in range(0, len(out) - 7, 8):
        if out[p] == 0x85:
            out[p + 4:p + 8] = b"\0\0\0\0"
    return bytes(out)


def diff_positions(a, b):
    n = min(len(a), len(b))
    return [i for i in range(n) if a[i] != b[i]]


def by_section(diffs, secs):
    out = {}
    for i in diffs:
        hit = "(other)"
        for n, (off, size) in secs.items():
            if off <= i < off + size:
                hit = n
                break
        out[hit] = out.get(hit, 0) + 1
    return out


def find_body(buf, body, text):
    lo, hi = text
    return [p for p in range(lo, hi - len(body) + 1, 8) if mask_calls(buf[p:p + len(body)]) == body]


def pair_order(buf, am_body, u8_body, text):
    am = find_body(buf, am_body, text)
    u8 = find_body(buf, u8_body, text)
    if not am or not u8:
        return "missing"
    return "AccountMeta->u8" if am[0] < u8[0] else "u8->AccountMeta"


def main(argv):
    emit_json = "--json" in argv
    for p in (DEPLOYED, CANDIDATE2, DARWIN):
        if not os.path.exists(p):
            sys.stderr.write(
                f"missing {os.path.relpath(p, ROOT)}\n"
                "materialize with: git sparse-checkout add repro/ata/monomorph-order-proof "
                "repro/ata/independent-ebpf-crosscheck\n")
            return 3

    A = open(DEPLOYED, "rb").read()
    C = open(CANDIDATE2, "rb").read()
    D = open(DARWIN, "rb").read()
    sa, sd = sections(A), sections(D)

    d_ad = diff_positions(A, D)
    d_cd = diff_positions(C, D)
    d_ac = diff_positions(A, C)

    text_a = (sa[".text"][0], sa[".text"][0] + sa[".text"][1])
    am_body = mask_calls(A[28592:29032])
    u8_body = mask_calls(A[29032:29384])

    def insns(buf, secs):
        off, size = secs[".text"]
        return [mask_calls(buf[p:p + 8]) for p in range(off, off + size - 7, 8)]

    from collections import Counter
    ma, md = Counter(insns(A, sa)), Counter(insns(D, sd))
    only_a = sum((ma - md).values())
    only_d = sum((md - ma).values())

    ro_a, ro_d = sa[".rodata"], sd[".rodata"]
    measured = {
        "deployed_sha256": sha(A),
        "candidate2_sha256": sha(C),
        "darwin_sha256": sha(D),
        "file_bytes": len(D) if len(A) == len(D) else None,
        "darwin_vs_deployed_diffs": len(d_ad),
        "darwin_vs_candidate2_diffs": len(d_cd),
        "candidate2_vs_deployed_diffs": len(d_ac),
        "darwin_diffs_by_section": by_section(d_ad, sa),
        "rodata_identical": A[ro_a[0]:ro_a[0] + ro_a[1]] == D[ro_d[0]:ro_d[0] + ro_d[1]],
        "section_layout_identical": sa == sd,
        "pair_windows": EXPECTED["pair_windows"],
        "pair_order": {
            "deployed": pair_order(A, am_body, u8_body, text_a),
            "candidate2": pair_order(C, am_body, u8_body, text_a),
            "darwin": pair_order(D, am_body, u8_body, text_a),
        },
        "masked_text_insn_multiset_only_in_each": only_a if only_a == only_d else [only_a, only_d],
    }

    checks = {k: measured[k] == v for k, v in EXPECTED.items()}
    passed = all(checks.values())
    report = {
        "experiment": "ata-darwin-host-build",
        "verdict": "NEGATIVE: Darwin x86_64 host does not reproduce the deployed ATA",
        "measured": measured,
        "checks": checks,
        "pass": passed,
    }
    if emit_json:
        print(json.dumps(report, indent=2))
    else:
        m = measured
        print(f"deployed   {m['deployed_sha256'][:16]}")
        print(f"candidate2 {m['candidate2_sha256'][:16]}  diffs vs deployed: {m['candidate2_vs_deployed_diffs']}")
        print(f"darwin     {m['darwin_sha256'][:16]}  diffs vs deployed: {m['darwin_vs_deployed_diffs']}  "
              f"vs candidate2: {m['darwin_vs_candidate2_diffs']}")
        print(f"darwin diffs by section: {m['darwin_diffs_by_section']}")
        print(f".rodata identical: {m['rodata_identical']}  section layout identical: {m['section_layout_identical']}")
        print(f"pair order: {m['pair_order']}")
        print(f"call-masked .text instructions unique to each side: {m['masked_text_insn_multiset_only_in_each']}")
        for k, ok in checks.items():
            print(f"  [{'OK' if ok else 'FAIL'}] {k}")
        print(f"PASS={passed}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

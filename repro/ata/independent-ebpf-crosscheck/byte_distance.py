#!/usr/bin/env python3
"""Independent byte-distance measurement for the ATA reconstruction residual.

This is a dependency-free cross-check of the repository's headline claim that the
closest Associated-Token-Account (ATA) candidate differs from the deployed program
by exactly 307 bytes, and that the difference is a compiler monomorphization-order
artifact (two `RawVec::reserve_for_push` instances swapped), not a behavioral one.

It re-derives the number and its localization directly from the two binaries, using
nothing but `hashlib`. It makes no attempt to reduce the residual and modifies no
file. It exits non-zero if the measured facts drift from what is recorded here, so
it doubles as a regression check for the residual.

The candidate/original pair lives under `repro/ata/monomorph-order-proof/` which is
sparse-excluded by default in this checkout. Materialize it first with:

    git sparse-checkout add repro/ata/monomorph-order-proof

Usage:
    python3 byte_distance.py                 # check the recorded ATA pair (asserts)
    python3 byte_distance.py A.so B.so        # measure an arbitrary pair (no asserts)
    python3 byte_distance.py --json           # emit machine-readable JSON
"""

import hashlib
import json
import os
import sys

# Recorded facts for the ATA pair, independently measured from the two .so files.
# original.so = deployed ATA (evidence/dependencies/associated_token/deployed.so)
# candidate2.so = closest reconstruction candidate.
ATA_ORIGINAL_SHA256 = "6804554e69fd3a58caa191dc4a58f4c67223d30ca28ab8987f39fc18d2f7374d"
ATA_CANDIDATE_SHA256 = "ba8dd8a42ca7bff4b668c72e1b5614e9363b271924d520253f5724760ba2d65b"
ATA_FILE_BYTES = 105032
ATA_TOTAL_DIFF = 307

# The two swapped monomorphization windows in the .text (file offsets), from the
# ordering analysis in REPORT.md. AccountMeta precedes u8 in the deployed binary.
ATA_WINDOWS = {
    "AccountMeta": (28592, 29032),
    "u8": (29032, 29384),
}
# Of the 307 differing bytes, this many fall inside the two windows above; the rest
# are the call-site and relocation fixups that move because the two bodies swapped.
ATA_IN_WINDOW_DIFFS = 282
ATA_OUT_WINDOW_DIFFS = 25


def repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    # .../repro/ata/independent-ebpf-crosscheck -> repo root is three up.
    return os.path.abspath(os.path.join(here, "..", "..", ".."))


def contiguous_runs(positions):
    """Collapse a sorted list of offsets into (start, end) inclusive runs."""
    runs = []
    if not positions:
        return runs
    start = prev = positions[0]
    for off in positions[1:]:
        if off == prev + 1:
            prev = off
        else:
            runs.append((start, prev))
            start = prev = off
    runs.append((start, prev))
    return runs


def measure(original_path, candidate_path):
    a = open(original_path, "rb").read()
    b = open(candidate_path, "rb").read()
    n = min(len(a), len(b))
    diffs = [i for i in range(n) if a[i] != b[i]]
    length_delta = abs(len(a) - len(b))
    runs = contiguous_runs(diffs)
    return {
        "original": os.path.relpath(original_path, repo_root()),
        "candidate": os.path.relpath(candidate_path, repo_root()),
        "original_sha256": hashlib.sha256(a).hexdigest(),
        "candidate_sha256": hashlib.sha256(b).hexdigest(),
        "original_bytes": len(a),
        "candidate_bytes": len(b),
        "length_delta": length_delta,
        "common_extent_diffs": len(diffs),
        "total_differing_positions": len(diffs) + length_delta,
        "contiguous_runs": len(runs),
        "first_diff_offset": diffs[0] if diffs else None,
        "diff_offsets": diffs,
        "runs": runs,
    }


def localize(diffs, windows):
    """Count how many diff offsets fall inside the named windows (union)."""
    lo = min(w[0] for w in windows.values())
    hi = max(w[1] for w in windows.values())
    inside = sum(1 for i in diffs if lo <= i < hi)
    per = {}
    for name, (wlo, whi) in windows.items():
        per[name] = sum(1 for i in diffs if wlo <= i < whi)
    return {"window_span": [lo, hi], "inside": inside, "outside": len(diffs) - inside, "per_window": per}


def check_ata(emit_json):
    root = repo_root()
    original = os.path.join(root, "repro/ata/monomorph-order-proof/original.so")
    candidate = os.path.join(root, "repro/ata/monomorph-order-proof/candidate2.so")
    missing = [p for p in (original, candidate) if not os.path.exists(p)]
    if missing:
        sys.stderr.write(
            "ATA proof pair not materialized. Run:\n"
            "    git sparse-checkout add repro/ata/monomorph-order-proof\n"
            "missing: " + ", ".join(os.path.relpath(p, root) for p in missing) + "\n"
        )
        return 3

    m = measure(original, candidate)
    loc = localize(m["diff_offsets"], ATA_WINDOWS)

    checks = {
        "lengths_equal_and_expected": m["original_bytes"] == m["candidate_bytes"] == ATA_FILE_BYTES,
        "original_sha256_matches": m["original_sha256"] == ATA_ORIGINAL_SHA256,
        "candidate_sha256_matches": m["candidate_sha256"] == ATA_CANDIDATE_SHA256,
        "total_diff_is_307": m["total_differing_positions"] == ATA_TOTAL_DIFF,
        "in_window_diffs_match": loc["inside"] == ATA_IN_WINDOW_DIFFS,
        "out_window_diffs_match": loc["outside"] == ATA_OUT_WINDOW_DIFFS,
    }
    passed = all(checks.values())

    report = {
        "target": "associated_token_account",
        "measurement": {k: m[k] for k in (
            "original", "candidate", "original_sha256", "candidate_sha256",
            "original_bytes", "candidate_bytes", "length_delta",
            "common_extent_diffs", "total_differing_positions",
            "contiguous_runs", "first_diff_offset",
        )},
        "localization": loc,
        "checks": checks,
        "pass": passed,
        "interpretation": (
            "The 307-byte residual is dominated by the two swapped RawVec::reserve_for_push "
            "monomorphizations; the out-of-window bytes are call-site and relocation fixups "
            "that shift because the two bodies exchanged order. The order is not recorded in "
            "the stripped binary, and the default f5ce86 recipe selects the candidate2 order. "
            "Non-historical ordering inputs (repro/ata/reconstructed-order, "
            "repro/ata/synthetic-ordering-exact-build) close the residual to exact raw bytes; "
            "the historical input that selected the deployed order remains unknown."
        ),
    }

    if emit_json:
        print(json.dumps(report, indent=2))
    else:
        print(f"ATA original  {m['original_sha256'][:16]}  {m['original_bytes']} B")
        print(f"ATA candidate {m['candidate_sha256'][:16]}  {m['candidate_bytes']} B")
        print(f"total differing bytes: {m['total_differing_positions']} "
              f"(common-extent {m['common_extent_diffs']}, length delta {m['length_delta']})")
        print(f"contiguous diff runs:  {m['contiguous_runs']}, first at offset {m['first_diff_offset']}")
        print(f"inside RawVec windows {loc['window_span']}: {loc['inside']}  "
              f"(AccountMeta {loc['per_window']['AccountMeta']}, u8 {loc['per_window']['u8']})")
        print(f"outside windows (call/reloc fixups): {loc['outside']}")
        for name, ok in checks.items():
            print(f"  [{'OK' if ok else 'FAIL'}] {name}")
        print(f"PASS={passed}")

    return 0 if passed else 1


def main(argv):
    emit_json = "--json" in argv
    args = [a for a in argv if a != "--json"]
    if len(args) == 2:
        # Arbitrary pair, descriptive only (no asserts).
        m = measure(args[0], args[1])
        print(json.dumps(m, indent=2) if emit_json else
              f"{m['total_differing_positions']} differing positions "
              f"(common-extent {m['common_extent_diffs']}, length delta {m['length_delta']}), "
              f"{m['contiguous_runs']} runs, first at {m['first_diff_offset']}")
        return 0
    return check_ata(emit_json)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

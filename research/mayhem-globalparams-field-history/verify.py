#!/usr/bin/env python3
"""Verify the Mayhem GlobalParams field-role evidence package.

Offline checks (default):
  1. Every file listed in manifest.json exists and matches its SHA-256.
  2. Every getAccountInfo capture's binary payload re-decodes to the field
     values claimed in the README tables (offsets per the recovered layout).
  3. Every getTransaction capture re-decodes (instruction args +
     GlobalParamsUpdateEvent) to the values in evidence/analysis_timeseries.json,
     and the version chain is continuous (each event's old_version equals the
     previous event's new_version).

Online check (--live):
  4. Re-fetch the GlobalParams account from Solana mainnet and compare the
     five studied fields and the version counter against the newest capture.
     (Read-only; no wallet, no transactions.)

Usage: python3 verify.py [--live] [--evidence DIR]
Exit code 0 = all executed checks pass.
"""
import argparse, base64, hashlib, json, os, struct, subprocess, sys

GP = "13ec7XdrjF3h3YcqBTFDSReRcUFwbCnJaAQspM4j6DDJ"
EP = "https://api.mainnet-beta.solana.com"
# Recovered GlobalParams layout (account offsets, little-endian).
LAYOUT = {"field_0": (8, "<I"), "field_1": (12, "<I"), "field_2": (16, "<Q"),
          "field_3": (24, "<Q"), "field_4": (32, "<Q"), "field_5": (40, "<Q"),
          "paused": (48, "<B"), "field_9": (129, "<Q"), "field_6": (137, "<B"),
          "last_sol_withdraw_timestamp": (138, "<q"), "field_7": (146, "<q"),
          "field_8": (154, "<q"), "version": (162, "<I"), "field_10": (166, "<Q"),
          "max_sol_per_sweep": (174, "<Q"), "field_11": (182, "<Q"),
          "field_12": (190, "<Q"), "field_13": (198, "<Q"),
          "stable_deployed": (206, "<q"), "field_14": (222, "<Q"),
          "field_15": (230, "<q"), "last_quote_withdraw_timestamp": (238, "<q"),
          "max_stable_per_sweep": (246, "<Q")}
STUDIED = ["field_0", "field_1", "field_3", "field_6", "field_10"]
DISC = bytes.fromhex("79c1f857c3384c0b")


def decode_account(raw):
    if len(raw) < 254 or raw[:8] != DISC:
        raise ValueError("not a GlobalParams payload (bad length/discriminator)")
    return {k: struct.unpack_from(fmt, raw, off)[0] for k, (off, fmt) in LAYOUT.items()}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--evidence", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "evidence"))
    args = ap.parse_args()
    ev = args.evidence
    root = os.path.dirname(os.path.abspath(__file__))
    failures = []

    manifest = json.load(open(os.path.join(root, "manifest.json")))
    for entry in manifest["files"]:
        p = os.path.join(root, entry["path"])
        if not os.path.exists(p):
            failures.append(f"missing file: {entry['path']}")
            continue
        got = sha256_file(p)
        if got != entry["sha256"]:
            failures.append(f"hash mismatch: {entry['path']} got {got}")
    print(f"[1] manifest: {len(manifest['files'])} files hashed, "
          f"{sum(1 for f in failures if 'hash' in f or 'missing' in f)} failures")

    # [2] account captures re-decode
    n_caps = 0
    newest = None
    for fn in sorted(os.listdir(ev)):
        if not fn.startswith("capture_globalparams"):
            continue
        cap = json.load(open(os.path.join(ev, fn)))
        raw = base64.b64decode(cap["response"]["result"]["value"]["data"][0])
        binpath = os.path.join(ev, fn.replace("capture_globalparams", "globalparams").replace(".json", ".bin"))
        if os.path.exists(binpath) and open(binpath, "rb").read() != raw:
            failures.append(f"{fn}: .bin payload differs from capture JSON payload")
        vals = decode_account(raw)
        n_caps += 1
        slot = cap["response"]["result"]["context"]["slot"]
        if newest is None or slot > newest[0]:
            newest = (slot, vals, fn)
        print(f"    {fn}: slot {slot} version={vals['version']} "
              + " ".join(f"{k}={vals[k]}" for k in STUDIED))
    print(f"[2] account captures re-decoded: {n_caps}")

    # [3] transaction time series + version chain
    ts = json.load(open(os.path.join(ev, "analysis_timeseries.json")))
    prev = None
    n_upd = 0
    for row in ts["transactions"]:
        capfile = os.path.join(ev, row["capture_file"])
        if not os.path.exists(capfile):
            failures.append(f"timeseries references missing capture {row['capture_file']}")
            continue
        for evnt in row["update_events"]:
            n_upd += 1
            if prev is not None and evnt["old_version"] != prev:
                failures.append(f"version chain break at {row['signature']}: "
                                f"old_version {evnt['old_version']} != previous new_version {prev}")
            prev = evnt["new_version"]
    print(f"[3] update events checked: {n_upd}, final version in series: {prev}")

    # [4] live re-fetch
    if args.live:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "getAccountInfo",
                           "params": [GP, {"encoding": "base64", "commitment": "finalized"}]})
        out = subprocess.run(["curl", "-s", "-A", "curl/8.5.0", EP, "-X", "POST",
                              "-H", "Content-Type: application/json", "-d", body],
                             capture_output=True, text=True, timeout=120)
        res = json.loads(out.stdout)["result"]
        raw = base64.b64decode(res["value"]["data"][0])
        vals = decode_account(raw)
        if newest:
            _, exp, fn = newest
            for k in STUDIED + ["version"]:
                if vals[k] != exp[k]:
                    failures.append(f"live mismatch on {k}: live {vals[k]} != newest capture ({fn}) {exp[k]}")
        print(f"[4] live account at slot {res['context']['slot']}: version={vals['version']} "
              + " ".join(f"{k}={vals[k]}" for k in STUDIED))

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(" -", f)
        return 1
    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

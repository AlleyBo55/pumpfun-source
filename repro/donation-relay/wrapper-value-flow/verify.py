#!/usr/bin/env python3
"""Recompute conditional caller value-flow observations from pinned binary bytes."""

from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text())


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def manifest(folder):
    expected = read(folder / "manifest.json")
    actual = {
        str(p.relative_to(folder))
        for p in folder.rglob("*")
        if p.is_file() and p.name != "manifest.json" and "__pycache__" not in p.parts
    }
    assert actual == set(expected)
    for name, digest in expected.items():
        file = folder / name
        assert not file.is_symlink() and file.resolve().is_relative_to(folder)
        assert sha(file.read_bytes()) == digest, name


def load():
    for name, digest in read(HERE / "parents.json").items():
        assert sha((ROOT / name).read_bytes()) == digest, name
    parent = ROOT / "repro/donation-relay/burn-mint-ownership-recovery"
    manifest(parent)
    summary = read(parent / "builds/recovered/comparison-summary.json")
    descriptor = read(parent / "metadata.json")["variants"]["recovered"]["artifacts"][
        "symbols"
    ]
    symbols = gzip.decompress((parent / descriptor["path"]).read_bytes())
    original = (ROOT / "evidence/dependencies/donation_relay/deployed.so").read_bytes()
    assert sha(original) == summary["original_sha256"]
    assert sha(symbols) == summary["unstripped_sha256"]
    parser = module(
        "wrapper_elf",
        ROOT / "repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py",
    )
    model = module("wrapper_model", HERE / "model.py")
    o, c = parser.Elf(original), parser.Elf(symbols)
    windows = read(
        ROOT
        / "repro/donation-relay/swap-receipt-coordinate-recovery/original-windows.json"
    )
    normalized = {}
    for row in windows:
        f = o.function(row["start"], row["bytes"], [])
        assert f["raw_sha256"] == row["sha256"]
        normalized.setdefault(f["normalized_sha256"], []).append(row["ordinal"])
    om = {row["start"]: [row["ordinal"]] for row in windows}
    cm = {
        s["start"]: normalized.get(
            c.function(s["start"], s["size"], [])["normalized_sha256"], []
        )
        for s in c.symbols
        if s["type"] == 2 and s["size"]
    }
    worker = [s for s in c.symbols if "shared_donation13donate_shared" in s["name"]]
    assert len(worker) == 1
    # This is a named stop/call-summary boundary, not a claim of body equality.
    cm[worker[0]["start"]] = [112]
    subjects = {}
    for ordinal, fragment in [
        (94, "donation_handlers17donate_v1_handler"),
        (95, "donation_handlers45donate_pubkey_config_id_with_payer_v1_handler"),
    ]:
        candidates = [s for s in c.symbols if fragment in s["name"]]
        assert len(candidates) == 1
        original_row = windows[ordinal]
        candidate_row = candidates[0]
        assert original_row["ordinal"] == ordinal and original_row["bytes"] == 2568
        assert candidate_row["size"] == 2552
        subjects[ordinal] = (original_row, candidate_row)
    return parser, model, o, c, om, cm, subjects


def derive():
    _, model, o, c, om, cm, subjects = load()
    reports = {}
    for ordinal, (ow, cw) in subjects.items():
        modes = {}
        for mode in ("success", "error"):
            left = model.trace(o, ow["start"], ow["bytes"], om, mode)
            right = model.trace(c, cw["start"], cw["size"], cm, mode)
            context_differences = [
                i
                for i in left["boundary"]["context"]
                if left["boundary"]["context"][i] != right["boundary"]["context"][i]
            ]
            argument_differences = [
                i
                for i, value in enumerate(left["boundary"]["arguments"])
                if value != right["boundary"]["arguments"][i]
            ]
            output_differences = [
                i
                for i, value in enumerate(left["output"])
                if value != right["output"][i]
            ]
            assert (
                not context_differences
                and not argument_differences
                and not output_differences
            )
            assert len(left["assumptions"]) == len(right["assumptions"]) == 8
            assert (
                len(left["boundary"]["context"])
                == len(right["boundary"]["context"])
                == 204
            )
            assert (
                len(left["boundary"]["arguments"])
                == len(right["boundary"]["arguments"])
                == 68
            )
            assert (
                len(left["output"])
                == len(right["output"])
                == (153 if mode == "success" else 24)
            )
            assert (
                len(left["calls"])
                == len(right["calls"])
                == (3 if mode == "success" else 2)
            )
            modes[mode] = dict(
                original=left,
                candidate=right,
                context_differences=context_differences,
                argument_differences=argument_differences,
                output_differences=output_differences,
            )
        reports[ordinal] = modes
    return dict(
        wrappers=reports,
        nodes=model.NODES,
        original_sha256=sha(o.b),
        candidate_symbols_sha256=sha(c.b),
        scope="Four conditional traces only. Distinct symbolic input-address expressions; eight nonwrapping increments; abstract String clone, memcpy and identical shared-worker result summaries. Not a runtime or all-state equivalence claim.",
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    if not args.write:
        manifest(HERE)
    report = derive()
    if args.write:
        (HERE / "report.json").write_bytes(encoded(report))
        files = {
            str(p.relative_to(HERE)): sha(p.read_bytes())
            for p in sorted(HERE.rglob("*"))
            if p.is_file()
            and p.name != "manifest.json"
            and "__pycache__" not in p.parts
        }
        (HERE / "manifest.json").write_bytes(encoded(files))
    else:
        assert json.loads(encoded(report)) == read(HERE / "report.json")
    print(
        "PASS: 4 conditional caller traces; 204 context, 68 argument and 153/24 return bytes agree; no body match claimed"
    )


if __name__ == "__main__":
    main()

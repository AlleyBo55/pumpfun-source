#!/usr/bin/env python3
"""Verify root profile and Result-helper controls without widening matching rules."""

from pathlib import Path
import argparse
import collections
import gzip
import hashlib
import importlib.util
import json
import tempfile

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
        p = folder / name
        assert not p.is_symlink() and p.resolve().is_relative_to(folder)
        assert sha(p.read_bytes()) == digest, name


def parent():
    for name, digest in read(HERE / "parents.json").items():
        assert sha((ROOT / name).read_bytes()) == digest, name
    folder = ROOT / "repro/donation-relay/burn-mint-ownership-recovery"
    manifest(folder)
    old = module("profile_parent", folder / "verify.py")
    parser, base = old.parent()
    base["src/settlement_handlers.rs"] = old.recovered_source(base)
    assert len(base) == 56
    return parser, base


def sources(base, record):
    result = dict(base)
    assert set(record["source_overrides"]) <= {
        "src/settlement_handlers.rs",
        "src/shared_donation.rs",
        "src/business_error_codes.rs",
    }
    for name, filename in record["source_overrides"].items():
        result[name] = gzip.decompress((HERE / filename).read_bytes())
    return result


def derive():
    parser, base = parent()
    metadata = read(HERE / "metadata.json")
    assert len(metadata["variants"]) == 12
    groups = collections.Counter(r["group"] for r in metadata["variants"].values())
    assert groups == {
        "profile": 5,
        "generic-result": 3,
        "unit-result": 1,
        "unit-increment": 3,
    }
    old = ROOT / "repro/donation-relay/burn-mint-ownership-recovery/builds/recovered"
    baseline = read(old / "comparison-summary.json")
    before = {
        r["ordinal"]
        for r in read(old / "match-ledger.json")
        if r["normalized_candidate_indices"]
    }
    compiler = read(old / "launch.json")["rustc_sha256"]
    original = (ROOT / "evidence/dependencies/donation_relay/deployed.so").read_bytes()
    assert sha(original) == baseline["original_sha256"]
    target_helper = parser.Elf(original).function(152048, 504, [])
    windows = (
        ROOT
        / "repro/donation-relay/swap-receipt-coordinate-recovery/original-windows.json"
    ).read_bytes()
    flags = {
        "control": ["-C", "opt-level=3"],
        "opt2": ["-C", "opt-level=2"],
        "size": ["-C", "opt-level=s"],
        "minsize": ["-C", "opt-level=z"],
        "cgu2": ["-C", "codegen-units=2"],
    }
    counts = {"control": 482, "opt2": 382, "size": 316, "minsize": 314, "cgu2": 372}
    control_command = read(HERE / "builds/root-profile-control/launch.json")["command"]
    result, cache = {}, {}
    for label, record in metadata["variants"].items():
        folder = HERE / "builds" / label
        source = sources(base, record)
        launch, build = read(folder / "launch.json"), read(folder / "result.json")
        assert launch["inputs"] == {name: sha(raw) for name, raw in source.items()}
        assert launch["rustc_sha256"] == compiler
        assert build["exit_code"] == 0 and build["source_unchanged"]
        log = (folder / "build.log").read_bytes()
        assert sha(log) == build["log_sha256"]
        assert (
            b"Compiling donation-relay-source-proposal" in log
            and b"--crate-name donation_relay_source_proposal" in log
        )
        if record["group"] == "profile":
            suffix = label.removeprefix("root-profile-")
            assert not record["source_overrides"]
            assert launch["command"][-2:] == flags[suffix]
            assert launch["command"][:-2] == control_command[:-2]
        images = {}
        for kind, descriptor in record["artifacts"].items():
            raw = gzip.decompress((HERE / descriptor["path"]).read_bytes())
            assert sha(raw) == descriptor["sha256"] == build[kind + "_sha256"]
            assert len(raw) == descriptor["bytes"]
            images[kind] = raw
        key = (sha(images["candidate"]), sha(images["symbols"]))
        if key not in cache:
            with tempfile.TemporaryDirectory() as temp:
                d = Path(temp)
                for name, raw in [
                    ("original.so", original),
                    ("candidate.so", images["candidate"]),
                    ("unstripped.so", images["symbols"]),
                    ("original-windows.json", windows),
                ]:
                    (d / name).write_bytes(raw)
                cache[key] = parser.analyze(d)
        analysis = cache[key]
        summary = analysis["comparison-summary.json"]
        after = {
            r["ordinal"]
            for r in analysis["match-ledger.json"]
            if r["normalized_candidate_indices"]
        }
        gains, losses = sorted(after - before), sorted(before - after)
        assert not gains
        helpers = [
            dict(
                bytes=f["bytes"],
                normalized_sha256=f["normalized_sha256"],
                matches_original_115=f["normalized_sha256"]
                == target_helper["normalized_sha256"],
            )
            for f in analysis["candidate-function-ledger.json"]
            if any("business_error_codes7failure17h" in name for name in f["names"])
        ]
        if record["group"] == "profile":
            assert summary["original_normalized_match_windows"] == counts[suffix]
        else:
            assert not losses and summary["original_normalized_match_windows"] == 482
            if record["group"] in ("unit-result", "unit-increment"):
                assert (
                    len(helpers) == 1
                    and helpers[0]["matches_original_115"]
                    and helpers[0]["bytes"] == 504
                )
            else:
                assert helpers and not any(
                    row["matches_original_115"] for row in helpers
                )
        result[label] = dict(
            summary=summary, gained_windows=gains, lost_windows=losses, helpers=helpers
        )
    assert result["root-profile-control"]["summary"] == baseline
    return dict(
        groups=dict(groups),
        variants=result,
        scope="No new original body matches. Unit Result helpers duplicate an already-matched local shape; they do not identify a unique source return type. No candidate promotion or new runtime acceptance.",
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--materialize", type=Path)
    ap.add_argument("--variant")
    args = ap.parse_args()
    if not args.write:
        manifest(HERE)
    if args.materialize:
        assert args.variant and not args.materialize.exists()
        _, base = parent()
        record = read(HERE / "metadata.json")["variants"][args.variant]
        for name, raw in sources(base, record).items():
            p = args.materialize / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
        return
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
        assert read(HERE / "report.json") == report
    print(
        "PASS: 12 profile/Result controls; control reproduces baseline, no gained windows; no promotion"
    )


if __name__ == "__main__":
    main()

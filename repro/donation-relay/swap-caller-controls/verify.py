#!/usr/bin/env python3
"""Verify swap-caller source controls and reproduced compiler layout output."""

from pathlib import Path
import argparse
import re
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
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


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
        "src/lib.rs",
        "src/settlement_handlers.rs",
    }
    for name, filename in record["source_overrides"].items():
        result[name] = gzip.decompress((HERE / filename).read_bytes())
    return result


def layouts(log):
    result = {}
    for name in (
        "anchor_framework::JustSwapV1<'_>",
        "settlement_handlers::BurnCloseContext<'_>",
    ):
        pattern = (
            r"print-type-size type: `"
            + re.escape(name)
            + r"`: (\d+) bytes, alignment: (\d+) bytes\n"
        )
        match = re.search(pattern, log)
        assert match, name
        total, align = map(int, match.groups())
        offset, fields = 0, []
        for line in log[match.end() :].splitlines():
            if line.startswith("print-type-size type:") or not line.startswith(
                "print-type-size "
            ):
                break
            field = re.fullmatch(
                r"print-type-size     field `\.([^`]+)`: (\d+) bytes", line
            )
            padding = re.fullmatch(
                r"print-type-size\s+(?:end )?padding: (\d+) bytes", line
            )
            if field:
                size = int(field[2])
                fields.append(dict(name=field[1], offset=offset, bytes=size))
                offset += size
            elif padding:
                offset += int(padding[1])
            else:
                raise AssertionError(line)
        assert offset == total
        result[name] = dict(bytes=total, alignment=align, fields=fields)
    return result


def derive():
    parser, base = parent()
    meta = read(HERE / "metadata.json")
    assert len(meta["variants"]) == 6
    folder = ROOT / "repro/donation-relay/burn-mint-ownership-recovery/builds/recovered"
    baseline = read(folder / "comparison-summary.json")
    before = {
        row["ordinal"]
        for row in read(folder / "match-ledger.json")
        if row["normalized_candidate_indices"]
    }
    compiler = read(folder / "launch.json")["rustc_sha256"]
    original = (ROOT / "evidence/dependencies/donation_relay/deployed.so").read_bytes()
    assert sha(original) == baseline["original_sha256"]
    windows = (
        ROOT
        / "repro/donation-relay/swap-receipt-coordinate-recovery/original-windows.json"
    ).read_bytes()
    result = {}
    for label, record in meta["variants"].items():
        source = sources(base, record)
        d = HERE / "builds" / label
        launch, build = read(d / "launch.json"), read(d / "result.json")
        assert launch["inputs"] == {name: sha(raw) for name, raw in source.items()}
        assert launch["rustc_sha256"] == compiler
        assert build["exit_code"] == 0 and build["source_unchanged"]
        log = (d / "build.log").read_bytes()
        assert sha(log) == build["log_sha256"]
        assert (
            b"Compiling donation-relay-source-proposal" in log
            and b"--crate-name donation_relay_source_proposal" in log
        )
        if label == "layout-probe":
            assert (
                not record["source_overrides"]
                and launch["command"][-1] == "-Zprint-type-sizes"
            )
            layout = layouts(log.decode())
        images = {}
        for kind, descriptor in record["artifacts"].items():
            raw = gzip.decompress((HERE / descriptor["path"]).read_bytes())
            assert sha(raw) == descriptor["sha256"] == build[kind + "_sha256"]
            assert len(raw) == descriptor["bytes"]
            images[kind] = raw
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            for name, raw in [
                ("original.so", original),
                ("candidate.so", images["candidate"]),
                ("unstripped.so", images["symbols"]),
                ("original-windows.json", windows),
            ]:
                (d / name).write_bytes(raw)
            analysis = parser.analyze(d)
        after = {
            row["ordinal"]
            for row in analysis["match-ledger.json"]
            if row["normalized_candidate_indices"]
        }
        worker = [
            row
            for row in analysis["candidate-function-ledger.json"]
            if any("settlement_handlers9just_swap17h" in name for name in row["names"])
        ]
        assert (
            len(worker) == 1
            and not analysis["match-ledger.json"][99]["normalized_candidate_indices"]
        )
        om = {
            row["start"]: row["ordinal"]
            for row in analysis["original-function-ledger.json"]
        }
        norm = {}
        for row in analysis["original-function-ledger.json"]:
            norm.setdefault(row["normalized_sha256"], []).append(row["ordinal"])
        targets = {
            row["start"]: norm.get(row["normalized_sha256"], [])
            for row in analysis["candidate-function-ledger.json"]
        }
        calls = [
            dict(offset=row["offset"], original_ordinals=targets.get(row["target"], []))
            for row in worker[0]["direct_calls"]
        ]
        result[label] = dict(
            summary=analysis["comparison-summary.json"],
            gained_windows=sorted(after - before),
            lost_windows=sorted(before - after),
            worker_bytes=worker[0]["bytes"],
            worker_normalized_sha256=worker[0]["normalized_sha256"],
            direct_calls=calls,
            memcpy_calls=sum(473 in row["original_ordinals"] for row in calls),
        )
        assert not result[label]["gained_windows"]
    assert result["layout-probe"]["summary"] == baseline
    assert result["burn-caller-order"]["worker_bytes"] == 4408
    assert result["layout-probe"]["memcpy_calls"] == 2
    assert result["burn-caller-order"]["memcpy_calls"] == 1
    assert all(not row["lost_windows"] for row in result.values())
    original_calls = [
        dict(offset=row["offset"], original_ordinals=[om[row["target"]]])
        for row in analysis["original-function-ledger.json"][99]["direct_calls"]
    ]
    return dict(
        layouts=layout,
        original_calls=original_calls,
        variants=result,
        scope="Compiler layouts describe the reconstructed source only. Corrected constructor ordering removes a copy, but no full original body is recovered and no candidate is promoted.",
    )


def check_replay(report):
    receipt = read(HERE / "builds/burn-caller-order/fresh-replay.json.gz")
    assert (
        receipt["candidate_sha256"]
        == report["variants"]["burn-caller-order"]["summary"]["candidate_sha256"]
    )
    assert receipt["runner_sha256"] == sha((HERE / "replay_saved.py").read_bytes())
    frozen = {}
    root = ROOT / "repro/donation-relay/distribution-worker-source-recovery/settlement"
    for name, digest in receipt["input_reports"].items():
        file = ROOT / name
        assert sha(file.read_bytes()) == digest
        for i, row in enumerate(read(file)["cases"]):
            frozen[str(file.relative_to(root)) + ":" + str(i)] = row
    helper = module(
        "swap_replay_check",
        ROOT / "repro/donation-relay/swap-receipt-coordinate-recovery/verify.py",
    )
    helper.EXPECTED["recovered"] = receipt["candidate_sha256"]
    path = ROOT / "repro/donation-relay/local-validation-proposal/harness_proposal.py"
    assert receipt["harness_sha256"] == sha(path.read_bytes())
    assert receipt["token2022_sha256"] == sha(
        (ROOT / "evidence/dependencies/spl_token_2022/deployed.so").read_bytes()
    )
    return helper.check_runtime(receipt, frozen, module("swap_replay_harness", path))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument(
        "--static",
        action="store_true",
        help="Skip the solders-based signed-receipt verification",
    )
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
        assert report == read(HERE / "report.json")
    if args.static:
        print("PASS: structural checks only; signed-receipt verification skipped")
    else:
        runtime = check_replay(report)
        print(
            "PASS: six controls; layout reproduces baseline; no recovered window;",
            runtime,
        )


if __name__ == "__main__":
    main()

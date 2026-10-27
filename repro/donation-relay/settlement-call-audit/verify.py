#!/usr/bin/env python3
"""Inventory matched direct callees without asserting caller equivalence."""

from pathlib import Path
import argparse
import collections
import gzip
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TERMS = {
    97: "16distribute_after17h",
    98: "19distribute_non_swap17h",
    99: "9just_swap17h",
    100: "20swap_then_distribute17h",
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text())


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def manifest(folder):
    values = read(folder / "manifest.json")
    actual = {
        str(p.relative_to(folder))
        for p in folder.rglob("*")
        if p.is_file() and p.name != "manifest.json" and "__pycache__" not in p.parts
    }
    assert actual == set(values)
    for name, digest in values.items():
        p = folder / name
        assert not p.is_symlink() and p.resolve().is_relative_to(folder)
        assert sha(p.read_bytes()) == digest, name


def load():
    for name, digest in read(HERE / "parents.json").items():
        assert sha((ROOT / name).read_bytes()) == digest
    path = ROOT / "repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py"
    spec = importlib.util.spec_from_file_location("settlement_elf", path)
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    raw = (ROOT / "evidence/dependencies/donation_relay/deployed.so").read_bytes()
    assert (
        sha(raw) == "367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563"
    )
    original = parser.Elf(raw)
    windows = read(
        ROOT
        / "repro/donation-relay/swap-receipt-coordinate-recovery/original-windows.json"
    )
    rows = []
    for row in windows:
        f = original.function(row["start"], row["bytes"], [])
        assert f["raw_sha256"] == row["sha256"]
        rows.append(dict(f, ordinal=row["ordinal"]))
    images = {}
    for label, directory, variant in [
        ("baseline", "burn-mint-ownership-recovery", "recovered"),
        ("constructor-order", "swap-caller-controls", "burn-caller-order"),
    ]:
        folder = ROOT / "repro/donation-relay" / directory
        manifest(folder)
        descriptor = read(folder / "metadata.json")["variants"][variant]["artifacts"][
            "symbols"
        ]
        raw = gzip.decompress((folder / descriptor["path"]).read_bytes())
        assert sha(raw) == descriptor["sha256"] and len(raw) == descriptor["bytes"]
        images[label] = parser.Elf(raw)
    return parser, original, rows, images


def key(row):
    return (row["bytes"], row["normalized_sha256"])


def calls(elf, function, functions, original_groups):
    result = []
    for call in function["direct_calls"]:
        assert call["target"] in functions, ("target is not a function start", call)
        callee = functions[call["target"]]
        body_key = key(callee)
        assert body_key in original_groups, ("unmatched callee", call)
        result.append(
            dict(
                offset=call["offset"],
                target=call["target"],
                callee_bytes=body_key[0],
                normalized_sha256=body_key[1],
                matching_original_ordinals=original_groups[body_key],
                candidate_names=callee.get("names", []),
            )
        )
    return result


def counts(rows):
    return collections.Counter(
        (r["callee_bytes"], r["normalized_sha256"]) for r in rows
    )


def compare(original_calls, candidate_calls):
    left, right = counts(original_calls), counts(candidate_calls)
    difference = [
        dict(
            callee_bytes=k[0],
            normalized_sha256=k[1],
            original_count=left[k],
            candidate_count=right[k],
        )
        for k in sorted(left.keys() | right.keys())
        if left[k] != right[k]
    ]
    return dict(
        multiset_equal=not difference,
        differences=difference,
        same_linear_sequence=[
            (r["callee_bytes"], r["normalized_sha256"]) for r in original_calls
        ]
        == [(r["callee_bytes"], r["normalized_sha256"]) for r in candidate_calls],
    )


def derive():
    _, original, originals, images = load()
    original_functions = {row["start"]: row for row in originals}
    groups = {}
    for row in originals:
        groups.setdefault(key(row), []).append(row["ordinal"])
    result = {}
    for label, image in images.items():
        functions = {}
        for symbol in image.symbols:
            if symbol["type"] != 2 or not symbol["size"]:
                continue
            address = symbol["start"]
            if address not in functions:
                functions[address] = image.function(address, symbol["size"], [])
                functions[address]["names"] = []
            functions[address]["names"].append(symbol["name"])
        per_function = {}
        for ordinal, term in TERMS.items():
            candidates = [
                f
                for f in functions.values()
                if any("settlement_handlers" + term in name for name in f["names"])
            ]
            assert len(candidates) == 1
            left, right = originals[ordinal], candidates[0]
            oc = calls(original, left, original_functions, groups)
            cc = calls(image, right, functions, groups)
            relation = compare(oc, cc)
            assert key(left) != key(right)
            if label == "baseline" and ordinal == 99:
                assert len(relation["differences"]) == 1
                difference = relation["differences"][0]
                assert (
                    473
                    in groups[
                        (difference["callee_bytes"], difference["normalized_sha256"])
                    ]
                )
                assert difference["candidate_count"] == difference["original_count"] + 1
            else:
                assert relation["multiset_equal"]
            per_function[ordinal] = dict(
                original_bytes=left["bytes"],
                candidate_bytes=right["bytes"],
                caller_body_matched=False,
                original_calls=oc,
                candidate_calls=cc,
                comparison=relation,
                original_external_calls=left["external_calls"],
                candidate_external_calls=right["external_calls"],
                original_indirect_calls=left["indirect_calls"],
                candidate_indirect_calls=right["indirect_calls"],
            )
        result[label] = dict(image_sha256=sha(image.b), functions=per_function)
    return dict(
        images=result,
        scope="Counts and linear sequences of direct calls to matched local bodies only; no caller, data-flow, CFG, indirect-target or all-state equivalence claim.",
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    if not args.write:
        manifest(HERE)
    report = derive()
    if args.write:
        (HERE / "report.json").write_bytes(encode(report))
        values = {
            str(p.relative_to(HERE)): sha(p.read_bytes())
            for p in sorted(HERE.rglob("*"))
            if p.is_file()
            and p.name != "manifest.json"
            and "__pycache__" not in p.parts
        }
        (HERE / "manifest.json").write_bytes(encode(values))
    else:
        assert json.loads(encode(report)) == read(HERE / "report.json")
    print(
        "PASS: eight caller comparisons; all direct callees have matched bodies; baseline just_swap has one additional memcpy"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Verify this package or one retained no-op gate attempt without rebuilding."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Optional

sys.dont_write_bytecode = True

from elf_utils import Elf64, GateError, require, sha256_bytes, sha256_file

PACKAGE = Path(__file__).resolve().parent
SOURCE_REVISION = "58519a8e601ed17bc6d931483686a08ee656233d"
BASELINE_SHA256 = "6c44d9f2ffe9b18c79a6344b256d8acd7a34c10e77b894c51f46512a447b8ce6"
BASELINE_BYTES = 863800
V144_ARCHIVE_SHA256 = "6719b889d60677a8a2fcf4c82f68441a1afe0ab093edd2efe9f84a67a808b3e9"
V152_ARCHIVE_SHA256 = "8b3861e93daf085ec12b65c4fac374d9bec4587a3de16871da6b08ab0c1d907e"
V152_OBJCOPY_SHA256 = "673b3b86f0b1b8eadd755e29e2f66a7582248ef3bda7a267fbb370b733c1cb69"
IMAGE = "solanafoundation/solana-verifiable-build@sha256:6c73adc767ee7ff212f2532d4695472b12f3d4ac20aea3db22b89d8c614dac50"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_sha256(value) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def verify_package() -> dict:
    policy = read_json(PACKAGE / "policy.json")
    source_inputs = read_json(PACKAGE / "source-inputs.json")
    require(policy["schema"] == 1, "Wrong policy schema")
    require(policy["source"]["revision"] == SOURCE_REVISION, "Wrong source revision policy")
    require(policy["source"]["branch"] == "main", "Wrong source branch policy")
    require(policy["source"]["tracked_input_count"] == len(source_inputs) == 26, "Wrong source receipt count")
    require(policy["baseline"] == {"bytes": BASELINE_BYTES, "sha256": BASELINE_SHA256}, "Wrong baseline policy")
    require(policy["elf"]["machine"] == 263 and policy["elf"]["machine_name"] == "EM_SBF", "Wrong ELF machine policy")
    require(policy["compile"]["version"] == "v1.44", "Wrong compile phase")
    require(policy["compile"]["archive_sha256"] == V144_ARCHIVE_SHA256, "Wrong v1.44 archive pin")
    require(policy["compile"]["ordering_option"] == "--symbol-ordering-file", "Wrong linker option")
    require(policy["strip"]["version"] == "v1.52", "Wrong strip phase")
    require(policy["strip"]["archive_sha256"] == V152_ARCHIVE_SHA256, "Wrong v1.52 archive pin")
    require(policy["strip"]["objcopy_sha256"] == V152_OBJCOPY_SHA256, "Wrong objcopy pin")
    require(policy["strip"]["arguments"] == ["--strip-all"], "Wrong strip arguments")
    require(policy["container"]["image"] == IMAGE and policy["container"]["platform"] == "linux/amd64", "Wrong host container policy")
    require(policy["safety"] == {
        "deployed_artifact_allowed": False,
        "target_order_allowed": False,
        "binary_patching_allowed": False,
        "symbol_swaps": 0,
        "ordered_extra_link_args": 1,
    }, "Safety policy changed")
    require(all(len(name) > 0 and len(digest) == 64 for name, digest in source_inputs.items()), "Malformed source receipt")
    require(not any(name.startswith(("evidence/original/", "evidence/dependencies/")) for name in source_inputs), "A reference artifact entered source inputs")

    manifest_path = PACKAGE / "manifest-sha256.json"
    if manifest_path.is_file():
        manifest = read_json(manifest_path)
        actual_names = {
            path.relative_to(PACKAGE).as_posix()
            for path in PACKAGE.rglob("*")
            if path.is_file()
            and path != manifest_path
            and "__pycache__" not in path.parts
        }
        require(actual_names == set(manifest), "Package file inventory differs from manifest")
        for name, expected in manifest.items():
            path = PACKAGE / name
            require(not path.is_symlink(), f"Symlinked package file: {name}")
            require(path.stat().st_size == expected["bytes"], f"Package size differs: {name}")
            require(sha256_file(path) == expected["sha256"], f"Package hash differs: {name}")
    return {
        "package_verified": True,
        "source_revision": SOURCE_REVISION,
        "source_inputs": len(source_inputs),
        "policy_sha256": sha256_file(PACKAGE / "policy.json"),
        "source_inputs_sha256": canonical_sha256(source_inputs),
        "manifest_checked": manifest_path.is_file(),
    }


def artifact(path: Path, label: str) -> tuple[bytes, Elf64]:
    require(path.is_file() and not path.is_symlink(), f"Missing retained artifact: {path.name}")
    data = path.read_bytes()
    return data, Elf64(data, label)


def verify_terminal_packet() -> dict:
    """Re-derive the retained no-op gate's terminal duplicate-symbol blocker."""
    retained = PACKAGE / "results"
    result = read_json(retained / "result.json")
    require(
        result["status"] == "NOT_APPLICABLE_DUPLICATE_LOCAL_SYMBOL_NAMES",
        "Wrong terminal status",
    )
    require(result["source_revision"] == SOURCE_REVISION, "Terminal source revision differs")
    require(result["build_returncode"] == 0, "Retained baseline build did not succeed")
    require(result["source_unchanged"] is True, "Terminal result says source changed")
    for key in (
        "ordered_build_started",
        "symbol_order_emitted",
        "deployed_artifact_read",
        "target_order_derived",
        "binary_patching",
    ):
        require(result[key] is False, f"Terminal safety field differs: {key}")

    unstripped_bytes, unstripped = artifact(
        retained / "baseline.unstripped.so", "retained baseline unstripped"
    )
    stripped_bytes, stripped = artifact(
        retained / "baseline.stripped.so", "retained baseline stripped"
    )
    require(len(stripped_bytes) == BASELINE_BYTES, "Retained baseline length differs")
    require(sha256_bytes(stripped_bytes) == BASELINE_SHA256, "Retained baseline hash differs")
    require(
        result["baseline"]["unstripped_bytes"] == len(unstripped_bytes)
        and result["baseline"]["unstripped_sha256"] == sha256_bytes(unstripped_bytes),
        "Unstripped baseline receipt differs",
    )
    require(
        result["baseline"]["stripped_bytes"] == len(stripped_bytes)
        and result["baseline"]["stripped_sha256"] == sha256_bytes(stripped_bytes)
        and result["baseline"]["equals_expected_linux_candidate"] is True,
        "Stripped baseline receipt differs",
    )
    require(
        unstripped.allocated_sections() == stripped.allocated_sections(),
        "Retained v1.52 strip changed allocated sections",
    )

    symbol_section = unstripped.section(".symtab")
    rows = [
        row
        for row in unstripped._symbols(symbol_section)
        if row["type"] == 2 and row["section_index"] != 0
    ]
    groups: dict[str, list[dict]] = collections.defaultdict(list)
    for row in rows:
        groups[row["name"]].append(row)
    duplicates = {name: values for name, values in sorted(groups.items()) if len(values) > 1}
    measured = {
        "defined_function_symbols": len(rows),
        "unique_function_names": len(groups),
        "duplicate_names": len(duplicates),
        "duplicate_rows": sum(len(values) for values in duplicates.values()),
        "all_duplicate_groups_single_extent": all(
            len({(row["section_index"], row["address"], row["size"]) for row in values}) == 1
            for values in duplicates.values()
        ),
    }
    duplicate_receipt = read_json(retained / "duplicate-functions.json")
    require(
        {key: duplicate_receipt[key] for key in measured} == measured,
        "Duplicate-symbol summary differs",
    )
    require(duplicate_receipt["groups"] == duplicates, "Duplicate-symbol rows differ")
    require(result["symbol_inventory"] == measured, "Terminal symbol inventory differs")
    require(
        measured
        == {
            "defined_function_symbols": 647,
            "unique_function_names": 635,
            "duplicate_names": 8,
            "duplicate_rows": 20,
            "all_duplicate_groups_single_extent": False,
        },
        "Pinned duplicate-symbol finding differs",
    )

    help_bytes = (retained / "rust-lld-help-v144.txt").read_bytes()
    require(b"--symbol-ordering-file" in help_bytes, "Retained linker help lacks option")
    require(result["linker_option_advertised"] is True, "Linker support receipt differs")
    require(
        read_json(retained / "source-manifest.json") == read_json(PACKAGE / "source-inputs.json"),
        "Retained source manifest differs",
    )
    raw = read_json(retained / "raw-attempt-result.json")
    require(raw["build_attempts"] == 1, "Raw attempt build count differs")
    require(raw["ordered_build_started"] is False, "Raw attempt started ordered build")
    require(raw["source_unchanged"] is True, "Raw attempt changed source")
    build_log = (retained / "baseline-build-v144.log").read_text(
        encoding="utf-8", errors="replace"
    )
    require(
        re.search(r"Finished (?:`release` profile|release) \[optimized\] target\(s\)", build_log)
        is not None,
        "Retained baseline log lacks success",
    )
    require("link-arg=" not in build_log, "Baseline unexpectedly used a link argument")
    return {
        "status": result["status"],
        "baseline_sha256": BASELINE_SHA256,
        "baseline_bytes": BASELINE_BYTES,
        **measured,
        "linker_option_advertised": True,
        "ordered_build_started": False,
        "deployed_artifact_read": False,
    }


def command_by_name(commands: list[dict], name: str) -> dict:
    matches = [row for row in commands if row.get("name") == name]
    require(len(matches) == 1, f"Expected one command receipt: {name}")
    require(matches[0].get("returncode") == 0, f"Retained command failed: {name}")
    return matches[0]


def verify_success(output: Path, host: dict, result: dict, policy: dict) -> dict:
    run = output / "run"
    artifacts = run / "artifacts"
    evidence = run / "evidence"
    baseline_bytes, baseline = artifact(artifacts / "baseline.unstripped.so", "baseline unstripped")
    baseline_stripped_bytes, baseline_stripped = artifact(artifacts / "baseline.stripped.so", "baseline stripped")
    ordered_bytes, ordered = artifact(artifacts / "ordered.unstripped.so", "ordered unstripped")
    ordered_stripped_bytes, ordered_stripped = artifact(artifacts / "ordered.stripped.so", "ordered stripped")

    require(len(baseline_stripped_bytes) == BASELINE_BYTES, "Baseline stripped length differs")
    require(sha256_bytes(baseline_stripped_bytes) == BASELINE_SHA256, "Baseline stripped hash differs")
    require(ordered_stripped_bytes == baseline_stripped_bytes, "Ordered stripped bytes differ")
    require(baseline.allocated_sections() == baseline_stripped.allocated_sections(), "Baseline strip binding differs")
    require(ordered.allocated_sections() == ordered_stripped.allocated_sections(), "Ordered strip binding differs")

    baseline_evidence = baseline.evidence()
    ordered_evidence = ordered.evidence()
    require(read_json(evidence / "baseline-elf.json") == baseline_evidence, "Baseline ELF receipt differs")
    require(read_json(evidence / "ordered-elf.json") == ordered_evidence, "Ordered ELF receipt differs")
    require(ordered_evidence["function_symbol_map"] == baseline_evidence["function_symbol_map"], "Function symbol map differs")
    require(ordered_evidence["text"] == baseline_evidence["text"], "Text receipt differs")
    require(ordered.section_bytes(".text") == baseline.section_bytes(".text"), "Text bytes differ")
    require(ordered_evidence["relocations"] == baseline_evidence["relocations"], "Relocations differ")

    order_bytes = (evidence / "symbol-order.txt").read_bytes()
    require(order_bytes == baseline.symbol_order_bytes(), "Order file was not regenerated from the baseline map")
    order = read_json(evidence / "symbol-order.json")
    names = [row["name"] for row in baseline_evidence["function_symbol_map"]]
    require(order["baseline_address_order"] == order["requested_order"] == names, "Requested order contains a swap")
    require(order["function_symbols"] == len(names) and order["symbol_swaps"] == 0, "Wrong no-op order count")
    require(order["order_sha256"] == sha256_bytes(order_bytes), "Order hash differs")
    require(order["source"] == "fresh exact baseline .symtab only", "Order source claim differs")
    require(order["deployed_artifact_read"] is False and order["target_symbol_order_derived"] is False, "Order used forbidden target data")

    help_bytes = (evidence / "rust-lld-help-v144.txt").read_bytes()
    require(b"--symbol-ordering-file" in help_bytes, "Actual rust-lld help lacks the required option")
    tools = read_json(run / "toolchain.json")
    require(tools["compile_archive_sha256"] == V144_ARCHIVE_SHA256, "Compile archive receipt differs")
    require(tools["strip_archive_sha256"] == V152_ARCHIVE_SHA256, "Strip archive receipt differs")
    require(tools["llvm-objcopy"]["sha256"] == V152_OBJCOPY_SHA256, "Strip tool receipt differs")
    require(tools["rust_lld_help_sha256"] == sha256_bytes(help_bytes), "Linker help receipt differs")
    require(tools["ordering_option_advertised"] is True, "Linker support receipt differs")

    comparisons = read_json(evidence / "comparisons.json")
    required_true = {
        "function_symbol_map_equal",
        "text_equal",
        "relocations_equal",
        "stripped_bytes_equal",
        "ordered_stripped_expected_sha256",
        "requested_order_equal_baseline_address_order",
    }
    require(all(comparisons.get(name) is True for name in required_true), "A required equality is false")
    require(comparisons.get("symbol_swaps") == 0, "Comparison records a symbol swap")

    commands = read_json(run / "commands.json")
    baseline_build = command_by_name(commands, "baseline-build-v144")
    ordered_build = command_by_name(commands, "ordered-build-v144")
    baseline_strip = command_by_name(commands, "baseline-strip-v152")
    ordered_strip = command_by_name(commands, "ordered-strip-v152")
    require(baseline_build["command"] == ordered_build["command"], "Build command changed beyond environment link flags")
    base_flags = baseline_build["environment"]["CARGO_TARGET_SBF_SOLANA_SOLANA_RUSTFLAGS"]
    ordered_flags = ordered_build["environment"]["CARGO_TARGET_SBF_SOLANA_SOLANA_RUSTFLAGS"]
    require(base_flags == policy["compile"]["baseline_target_rustflags"], "Baseline target flags differ")
    expected_link_arg = f"--symbol-ordering-file=/gate/run/evidence/symbol-order.txt"
    require(ordered_flags == f"{base_flags} -C link-arg={expected_link_arg}", "Ordered flags contain more than the supported link argument")
    for row in (baseline_strip, ordered_strip):
        require(row["command"][1] == "--strip-all" and len(row["command"]) == 4, "Strip command differs from v1.52 phase")
    require(read_json(evidence / "baseline-root-command.json")["observed_link_args"] == [], "Baseline root command has a link argument")
    ordered_root = read_json(evidence / "ordered-root-command.json")
    require(ordered_root["only_supported_link_arg"] is True, "Ordered root command has another link argument")
    require(set(ordered_root["observed_link_args"]) == {expected_link_arg}, "Observed link arguments differ")

    source_inputs = read_json(PACKAGE / "source-inputs.json")
    require(read_json(output / "source-manifest.json") == source_inputs, "Exported source manifest differs")
    require(read_json(run / "source-before.json") == read_json(run / "source-after.json") == source_inputs, "Source changed during run")
    require(result["status"] == "APPLICABLE_NOOP" and result["baseline_exact"] is True, "Success result differs")
    require(result["build_attempts"] == 2 and result["ordered_build_started"] is True, "Wrong build count")
    require(result["compile_version"] == "v1.44" and result["strip_version"] == "v1.52", "Phase versions differ")
    require(result["only_supported_link_arg"] is True and result["symbol_swaps"] == 0, "No-op method differs")
    require(result["function_symbols"] == len(names), "Function count differs")
    require(host["status"] == "COMPLETE" and host["container_returncode"] == 0, "Host result differs")
    return {
        "applicable": True,
        "baseline_sha256": BASELINE_SHA256,
        "baseline_bytes": BASELINE_BYTES,
        "function_symbols": len(names),
        "symbol_swaps": 0,
        "function_symbol_map_equal": True,
        "text_equal": True,
        "relocations_equal": True,
        "stripped_bytes_equal": True,
    }


def verify_output(output: Path) -> dict:
    output = output.resolve()
    require(output.is_dir() and not output.is_symlink(), "Attempt output is not a regular directory")
    policy = read_json(PACKAGE / "policy.json")
    source_inputs = read_json(PACKAGE / "source-inputs.json")
    host = read_json(output / "host-attempt.json")
    for key in ("deployed_artifact_exported", "deployed_artifact_mounted", "deployed_artifact_read", "target_symbol_order_derived"):
        require(host.get(key) is False, f"Host safety receipt differs: {key}")
    require(host["checkout"]["revision"] == SOURCE_REVISION and host["checkout"]["branch"] == "main", "Host checkout receipt differs")
    require(read_json(output / "source-manifest.json") == source_inputs, "Host source export differs")
    require(not any(name.startswith(("evidence/original/", "evidence/dependencies/")) for name in source_inputs), "Reference artifact was exported")
    inspected = read_json(output / "image-inspect.json")
    require(len(inspected) == 1 and inspected[0]["Architecture"] == "amd64" and inspected[0]["Os"] == "linux", "Wrong container receipt")

    result_path = output / "run/result.json"
    if not result_path.is_file():
        require(host["status"] == "BLOCKED" and host.get("blocker"), "Missing inner result without exact host blocker")
        return {"applicable": False, "valid_blocked_attempt": True, "blocker": host["blocker"]}
    result = read_json(result_path)
    for key in (
        "deployed_artifact_exported",
        "deployed_artifact_mounted",
        "deployed_artifact_read",
        "target_symbol_order_derived",
        "binary_patching",
    ):
        require(result.get(key) is False, f"Inner safety receipt differs: {key}")
    require(result["source_revision"] == SOURCE_REVISION, "Inner source revision differs")
    require(result["compile_version"] == "v1.44" and result["strip_version"] == "v1.52", "Inner phase versions differ")
    if result["status"] == "APPLICABLE_NOOP":
        return verify_success(output, host, result, policy)

    require(result["status"] == "NOT_APPLICABLE", "Unknown inner result status")
    require(isinstance(result.get("blocker"), dict) and result["blocker"].get("message"), "Blocked attempt lacks an exact blocker")
    if result.get("baseline"):
        baseline = result["baseline"]["stripped"]
        expected = baseline.get("bytes") == BASELINE_BYTES and baseline.get("sha256") == BASELINE_SHA256
        if not expected:
            require(result.get("baseline_exact") is not True, "Mismatched baseline was accepted")
            require(result["ordered_build_started"] is False, "Ordered build started after baseline mismatch")
            require(not (output / "run/evidence/symbol-order.txt").exists(), "Order was derived after baseline mismatch")
    return {
        "applicable": False,
        "valid_blocked_attempt": True,
        "stage": result.get("stage"),
        "blocker": result["blocker"],
        "ordered_build_started": result["ordered_build_started"],
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    result.add_argument("--output", type=Path, help="Retained ignored run output")
    result.add_argument(
        "--allow-blocked",
        action="store_true",
        help="Return success when a fail-closed attempt receipt is internally valid",
    )
    return result


def main(arguments: Optional[list[str]] = None) -> int:
    args = parser().parse_args(arguments)
    try:
        summary = verify_package()
        if (PACKAGE / "results/result.json").is_file():
            summary["terminal"] = verify_terminal_packet()
        if args.output:
            run_summary = verify_output(args.output)
            summary["run"] = run_summary
            if not run_summary["applicable"] and not args.allow_blocked:
                print(json.dumps(summary, indent=2, sort_keys=True))
                return 3
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (GateError, OSError, KeyError, ValueError, json.JSONDecodeError) as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

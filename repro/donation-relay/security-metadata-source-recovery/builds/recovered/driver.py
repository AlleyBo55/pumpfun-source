#!/usr/bin/env python3
"""Reviewed source-only build driver. Default is a plan; --execute needs approval.

No target-original ELF is opened or loaded by this driver. No VM/RPC runs occur.
The platform-tools archive must be separately authenticated and extracted first.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import shutil
import time

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "work/relay-build-482/source"
CARGO_HOME = ROOT / "work/relay-482-cargo-home"
RECEIPTS = ROOT / "work/relay-build-482"
EXPECTED_TOOLS = {
    "rust/bin/rustc": "89fd4ccdd6e678a24c2cda074b498b46a352fcfce21018119c9526751afc678d",
    "rust/bin/cargo": "5614db715dddef5793dc5dc6403fea384993ea429337620aab9020438356d8ca",
    "llvm/bin/llvm-objcopy": "3a871eab7279dee53f2580e8a022c980305738b575755b7d3529a6230ec4f672",
}
EXPECTED_SDK_ARCHIVE = "a9d3157f937d5f6faf4321a35a8035e0f827114a663b0150db492e893ec27597"
EXPECTED_SDK_INSPECTION = "6403b709a271914dd0c0ede876cf5d3e320f1d2b0964153cc0b243910be25cdb"


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def files(root):
    out = {}
    for p in sorted(root.rglob("*")):
        assert not p.is_symlink(), p
        if p.is_file():
            out[str(p.relative_to(root))] = sha(p)
    return out


def save(path, value):
    with path.open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write("\n")


def verify_sdk(sdk):
    """Authenticate all extracted SDK bytes and links against the reviewed archive map."""
    inspection = ROOT / "work/toolchains/v1.48-inspection.json"
    extraction = ROOT / "work/toolchains/platform-tools-v1.48-extraction.json"
    assert sha(inspection) == EXPECTED_SDK_INSPECTION
    recorded = json.loads(inspection.read_text())
    receipt = json.loads(extraction.read_text())
    assert receipt["archive_sha256"] == recorded["archive_sha256"] == EXPECTED_SDK_ARCHIVE
    assert receipt["inspection_sha256"] == EXPECTED_SDK_INSPECTION
    assert Path(receipt["output"]).resolve() == sdk and receipt["extracted"]
    members = recorded["members"]
    actual = {str(p.relative_to(sdk)) for p in sdk.rglob("*")} | {"."}
    assert actual == set(members), "SDK membership differs from reviewed archive"
    counts = {"files": 0, "directories": 0, "links": 0, "verified_file_bytes": 0}
    for name, entry in members.items():
        path = sdk / name
        if entry["type"] == "0":
            assert path.is_file() and not path.is_symlink(), name
            assert path.stat().st_size == entry["size"] and sha(path) == entry["sha256"], name
            counts["files"] += 1
            counts["verified_file_bytes"] += entry["size"]
        elif entry["type"] == "5":
            assert path.is_dir() and not path.is_symlink(), name
            counts["directories"] += 1
        elif entry["type"] == "2":
            assert path.is_symlink() and os.readlink(path) == entry["target"], name
            assert path.resolve().is_relative_to(sdk), name
            counts["links"] += 1
        else:
            raise AssertionError((name, entry["type"]))
    return {"archive_sha256": EXPECTED_SDK_ARCHIVE, "inspection_sha256": EXPECTED_SDK_INSPECTION,
            "extraction_receipt_sha256": sha(extraction), "members": len(members), **counts}


def main():
    global SOURCE, CARGO_HOME, RECEIPTS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--cargo-home", type=Path, default=CARGO_HOME)
    parser.add_argument("--receipts", type=Path, default=RECEIPTS)
    parser.add_argument("--source-inputs", type=Path, help="Exact reviewed trial source hash map (JSON with files key)")
    parser.add_argument("--seed-target", type=Path, required=True, help="Completed verified baseline target; copied, never modified")
    parser.add_argument("--sdk", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute", action="store_true", help="Run native toolchain/build scripts; only after approval")
    args = parser.parse_args()
    SOURCE, CARGO_HOME, RECEIPTS = args.source.resolve(), args.cargo_home.resolve(), args.receipts.resolve()
    sdk, output = args.sdk.resolve(), args.output.absolute()
    source_receipt = (args.source_inputs or (RECEIPTS / "source-inputs.json")).resolve()
    seed_target = args.seed_target.resolve()
    expected = json.loads(source_receipt.read_text())["files"]
    source_before = files(SOURCE)
    assert source_before == expected, "Source differs from exact recorded latest build inputs"
    target = "sbpf-solana-solana"
    env = {
        "PATH": os.pathsep.join([str(sdk / "rust/bin"), str(sdk / "llvm/bin"), "/usr/bin", "/bin"]),
        "HOME": str(output / "home"),
        "CARGO_HOME": str(CARGO_HOME),
        "CARGO_TARGET_DIR": str(output / "target"),
        "CARGO_NET_OFFLINE": "true",
        "CARGO_TERM_COLOR": "never",
        "CARGO_BUILD_JOBS": "3",
        "CARGO_TARGET_SBPF_SOLANA_SOLANA_RUSTFLAGS": "-Zremap-cwd-prefix=",
        "RUSTC": str(sdk / "rust/bin/rustc"),
        "RUSTDOC": str(sdk / "rust/bin/rustdoc"),
        "CC": str(sdk / "llvm/bin/clang"),
        "AR": str(sdk / "llvm/bin/llvm-ar"),
        "OBJDUMP": str(sdk / "llvm/bin/llvm-objdump"),
        "OBJCOPY": str(sdk / "llvm/bin/llvm-objcopy"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
    }
    command = [str(sdk / "rust/bin/cargo"), "rustc", "--release", "--target", target, "--locked", "--offline", "--verbose", "--manifest-path", str(SOURCE / "Cargo.toml"), "--lib", "--", "--remap-path-prefix=src/=programs/contracts/src/"]
    plan = {"source": str(SOURCE), "source_hashes": expected, "sdk": str(sdk), "output": str(output), "command": command, "cwd": str(SOURCE), "environment": env, "expected_tool_hashes": EXPECTED_TOOLS, "driver_sha256": sha(Path(__file__)), "source_receipt_sha256": sha(source_receipt), "network": "Cargo offline; no download command; not an OS network sandbox", "native_dependency_execution": "Cargo may run pinned dependency build scripts and proc-macros", "controller_reads_captured_program_bytes": False, "captured_programs_in_compiler_input_manifest": False, "filesystem_isolates_captured_programs": False, "process_trace_attestation": False, "target_program_executed": False, "execute_requested": args.execute, "seed_target": str(seed_target), "root_artifact_policy": "Fresh copied target, explicit cargo clean root package, require actual root rustc invocation"}
    if not args.execute:
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0
    assert not output.exists(), "Choose a fresh output: never reuse target files or overwrite receipts"
    summary = json.loads((RECEIPTS / "preparation/summary.json").read_text())
    assert summary["registry_packages_prepared"] == summary["locked_registry_packages"] > 0
    # Check all lockfile dependency inputs, not just compiled package names.
    registry_hashes = {}
    registry_inputs = {}
    for receipt in sorted((RECEIPTS / "preparation/packages").glob("*.json")):
        package = json.loads(receipt.read_text())
        name = package["name"] + "-" + package["version"]
        base = CARGO_HOME / "registry/src/index.crates.io-6f17d22bba15001f" / name
        actual = files(base)
        actual.pop(".cargo-checksum.json", None)
        actual.pop(".cargo-ok", None)
        assert actual == package["source_files"], name
        archive = CARGO_HOME / "registry/cache/index.crates.io-6f17d22bba15001f" / (name + ".crate")
        assert sha(archive) == package["sha256"], name
        registry_hashes[name] = package["sha256"]
        registry_inputs[name] = (base, package["source_files"])
    assert len(registry_hashes) == summary["locked_registry_packages"]
    for path, expected_hash in EXPECTED_TOOLS.items():
        assert sha(sdk / path) == expected_hash, path
    sdk_verification = verify_sdk(sdk)
    seed_inputs = files(seed_target)
    assert seed_inputs and not output.resolve().is_relative_to(seed_target)
    output.mkdir(parents=True)
    shutil.copytree(seed_target, output / "target")
    assert files(output / "target") == seed_inputs
    (output / "driver.py").write_bytes(Path(__file__).read_bytes())
    (output / "home").mkdir()
    save(output / "launch.json", plan)
    save(output / "registry-before.json", registry_hashes)
    save(output / "tool-hashes.json", {p: sha(sdk / p) for p in EXPECTED_TOOLS})
    save(output / "sdk-verification.json", sdk_verification)
    for label, cmd in [
        ("rustc-version", [str(sdk / "rust/bin/rustc"), "--version", "--verbose"]),
        ("cargo-version", [str(sdk / "rust/bin/cargo"), "--version", "--verbose"]),
        ("target-spec", [str(sdk / "rust/bin/rustc"), "-Z", "unstable-options", "--print", "target-spec-json", "--target", target]),
    ]:
        with (output / (label + ".log")).open("xb") as log:
            probe = subprocess.run(cmd, cwd=SOURCE, env=env, stdout=log, stderr=subprocess.STDOUT)
        save(output / (label + ".json"), {"command": cmd, "returncode": probe.returncode, "log_sha256": sha(output / (label + ".log"))})
        if probe.returncode:
            save(output / "result.json", {"stage": "toolchain-preflight", "failed_probe": label, "returncode": probe.returncode, "compilation_started": False})
            return 1
    save(output / "cache-seed.json", {"source": str(seed_target), "files": len(seed_inputs), "content_map_sha256": hashlib.sha256(json.dumps(seed_inputs, sort_keys=True).encode()).hexdigest(), "copy_exact": True, "hardlinks_used": False})
    clean = [str(sdk / "rust/bin/cargo"), "clean", "--manifest-path", str(SOURCE / "Cargo.toml"), "--release", "--target", target, "--package", "donation-relay-source-proposal", "--locked", "--offline"]
    with (output / "clean-root.log").open("xb") as log:
        cleaned = subprocess.run(clean, cwd=SOURCE, env=env, stdout=log, stderr=subprocess.STDOUT)
    leftovers = [str(p.relative_to(output / "target")) for p in (output / "target").rglob("*") if p.is_file() and ("donation_relay_source_proposal" in p.name or any(part.startswith("donation-relay-source-proposal-") for part in p.parts))]
    save(output / "clean-root.json", {"command": clean, "returncode": cleaned.returncode, "log_sha256": sha(output / "clean-root.log"), "remaining_root_artifacts": leftovers})
    if cleaned.returncode or leftovers:
        save(output / "result.json", {"stage": "root-cache-removal", "returncode": cleaned.returncode, "remaining_root_artifacts": leftovers, "compilation_started": False})
        return 1
    started = time.monotonic()
    with (output / "build.log").open("xb") as log:
        result = subprocess.run(command, cwd=SOURCE, env=env, stdout=log, stderr=subprocess.STDOUT)
    log_text = (output / "build.log").read_text(errors="replace")
    backend_errors = [line for line in log_text.splitlines() if re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", line).lstrip().startswith("Error:")]
    root_calls = [line for line in log_text.splitlines() if "Running `" in line and "--crate-name donation_relay_source_proposal " in line]
    seed_unchanged = files(seed_target) == seed_inputs
    changed_registry_sources = []
    for name, (base, expected_source) in registry_inputs.items():
        actual = files(base)
        actual.pop(".cargo-checksum.json", None)
        actual.pop(".cargo-ok", None)
        if actual != expected_source:
            changed_registry_sources.append(name)
    record = {"actual_root_rustc_invocations": len(root_calls), "root_rustc_commands": root_calls, "seed_target_unchanged": seed_unchanged, "returncode": result.returncode, "elapsed_seconds": time.monotonic() - started, "source_unchanged": files(SOURCE) == source_before, "registry_sources_unchanged": not changed_registry_sources, "changed_registry_sources": changed_registry_sources, "build_log_sha256": sha(output / "build.log"), "backend_error_lines": backend_errors, "controller_reads_captured_program_bytes": False, "captured_programs_in_compiler_input_manifest": False, "filesystem_isolates_captured_programs": False, "process_trace_attestation": False, "target_program_executed": False}
    if result.returncode == 0 and not backend_errors and record["source_unchanged"] and record["registry_sources_unchanged"] and seed_unchanged and len(root_calls) == 1:
        unstripped = output / "target" / target / "release/donation_relay_source_proposal.so"
        assert unstripped.is_file() and not unstripped.is_symlink()
        with (output / "symbols.so").open("xb") as dst:
            dst.write(unstripped.read_bytes())
        strip = [str(sdk / "llvm/bin/llvm-objcopy"), "--strip-all", str(unstripped), str(output / "candidate.so")]
        save(output / "strip-command.json", strip)
        with (output / "strip.log").open("xb") as log:
            stripped = subprocess.run(strip, cwd=SOURCE, env=env, stdout=log, stderr=subprocess.STDOUT)
        record["strip_returncode"] = stripped.returncode
        record["symbols_sha256"] = sha(output / "symbols.so")
        if stripped.returncode == 0:
            record["candidate_sha256"] = sha(output / "candidate.so")
            record["candidate_bytes"] = (output / "candidate.so").stat().st_size
    save(output / "result.json", record)
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0 if record.get("strip_returncode") == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Run the Pump Fees v1.44 no-op symbol-ordering applicability gate.

The default host mode exports only the exact current-source inputs and this
candidate-only driver into a pinned Linux/amd64 container. The internal mode
performs one control build and, only after every prerequisite passes, one build
with the linker's supported symbol-ordering option. No deployed artifact path
is accepted, exported, mounted, or read.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import posixpath
import re
import shutil
import subprocess
import sys
import tarfile
import time
import traceback
from typing import Optional
import urllib.request

sys.dont_write_bytecode = True

from elf_utils import Elf64, GateError, artifact_record, require, sha256_bytes, sha256_file

PACKAGE = Path(__file__).resolve().parent
POLICY_PATH = PACKAGE / "policy.json"
SOURCE_INPUTS_PATH = PACKAGE / "source-inputs.json"
ALLOWED_UNTRACKED_PREFIX = "repro/pump_fees/symbol-order-noop-v144/"
ORDER_CONTAINER_PATH = "/gate/run/evidence/symbol-order.txt"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def canonical_sha256(value) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(encoded)


def command_output(command: list[str], cwd: Optional[Path] = None) -> str:
    return subprocess.check_output(command, cwd=cwd, text=True).strip()


def source_hashes(root: Path, expected: dict[str, str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for name in sorted(expected):
        relative = PurePosixPath(name)
        require(
            not relative.is_absolute() and ".." not in relative.parts,
            f"Unsafe source input path: {name}",
        )
        path = root.joinpath(*relative.parts)
        require(path.is_file() and not path.is_symlink(), f"Missing source input: {name}")
        result[name] = sha256_file(path)
    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    require(actual == set(expected), "Source snapshot file inventory differs from policy")
    return result


def package_repository() -> Path:
    for candidate in PACKAGE.parents:
        if (candidate / ".git").exists() and (candidate / "programs/pump-fees/Cargo.toml").is_file():
            return candidate
    raise GateError("Cannot locate pumpfun-source repository")


def validate_policy(policy: dict, source_inputs: dict[str, str]) -> None:
    require(policy["schema"] == 1, "Unsupported policy schema")
    require(policy["source"]["tracked_input_count"] == len(source_inputs) == 26, "Wrong source input count")
    require(policy["elf"] == {"class": 2, "data": 1, "type": 3, "machine": 263, "machine_name": "EM_SBF"}, "ELF policy changed")
    require(policy["compile"]["version"] == "v1.44", "Compile phase must remain v1.44")
    require(policy["strip"]["version"] == "v1.52", "Strip phase must remain v1.52")
    require(policy["strip"]["arguments"] == ["--strip-all"], "Strip arguments changed")
    require(policy["compile"]["ordering_option"] == "--symbol-ordering-file", "Ordering option changed")
    require(policy["safety"]["symbol_swaps"] == 0, "This gate permits no symbol swaps")
    require(policy["safety"]["ordered_extra_link_args"] == 1, "Exactly one supported link argument is required")


def validate_checkout(repository: Path, policy: dict) -> dict:
    revision = command_output(["git", "rev-parse", "HEAD"], repository)
    branch = command_output(["git", "branch", "--show-current"], repository)
    require(revision == policy["source"]["revision"], "Wrong repository revision")
    require(branch == policy["source"]["branch"], "Wrong repository branch")
    require(
        subprocess.run(["git", "diff", "--quiet"], cwd=repository).returncode == 0,
        "Tracked worktree changes are not allowed",
    )
    require(
        subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repository).returncode == 0,
        "Staged changes are not allowed",
    )
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=repository,
    )
    entries = [entry.decode("utf-8") for entry in status.split(b"\0") if entry]
    rejected = [
        entry
        for entry in entries
        if not (entry.startswith("?? ") and entry[3:].startswith(ALLOWED_UNTRACKED_PREFIX))
    ]
    require(not rejected, "Checkout has changes outside this additive package: " + ", ".join(rejected))
    return {"revision": revision, "branch": branch, "status": entries}


def export_source(repository: Path, destination: Path, expected: dict[str, str], revision: str) -> dict[str, str]:
    destination.mkdir(parents=True, exist_ok=False)
    exported: dict[str, str] = {}
    for name in sorted(expected):
        relative = PurePosixPath(name)
        require(
            not relative.is_absolute()
            and ".." not in relative.parts
            and not name.startswith(("evidence/original/", "evidence/dependencies/")),
            f"Forbidden source export path: {name}",
        )
        metadata = command_output(["git", "ls-tree", revision, "--", name], repository)
        fields = metadata.split(None, 3)
        require(
            len(fields) == 4 and fields[0] == "100644" and fields[1] == "blob" and fields[3] == name,
            f"Source input is not one regular Git blob: {name}",
        )
        data = subprocess.check_output(["git", "show", f"{revision}:{name}"], cwd=repository)
        digest = sha256_bytes(data)
        require(digest == expected[name], f"Pinned source blob differs: {name}")
        target = destination.joinpath(*relative.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        exported[name] = digest
    require(exported == expected, "Exported source manifest differs")
    return exported


def copy_driver(destination: Path) -> dict[str, dict[str, object]]:
    destination.mkdir(parents=True, exist_ok=False)
    records: dict[str, dict[str, object]] = {}
    for name in ("run.py", "elf_utils.py", "policy.json", "source-inputs.json"):
        source = PACKAGE / name
        require(source.is_file() and not source.is_symlink(), f"Missing package input: {name}")
        target = destination / name
        shutil.copyfile(source, target)
        records[name] = {"bytes": target.stat().st_size, "sha256": sha256_file(target)}
    return records


def output_path(repository: Path, requested: Path) -> Path:
    lexical = requested if requested.is_absolute() else repository / requested
    lexical = Path(os.path.abspath(lexical))
    work = Path(os.path.abspath(repository / "work"))
    require(work in lexical.parents, "Run output must be a fresh directory below repository work/")
    require(not lexical.exists(), "Run output already exists; attempts are immutable")
    return lexical


def run_host(args: argparse.Namespace) -> int:
    policy = read_json(POLICY_PATH)
    source_inputs = read_json(SOURCE_INPUTS_PATH)
    validate_policy(policy, source_inputs)
    repository = package_repository()
    checkout = validate_checkout(repository, policy)
    output = output_path(repository, args.output)
    cache = args.cache
    if not cache.is_absolute():
        cache = repository / cache
    cache = Path(os.path.abspath(cache))
    work = Path(os.path.abspath(repository / "work"))
    require(cache == work or work in cache.parents, "Download cache must stay below repository work/")
    require(cache != output and output not in cache.parents and cache not in output.parents, "Cache and attempt output overlap")
    output.mkdir(parents=True)
    cache.mkdir(parents=True, exist_ok=True)

    host = {
        "schema": 1,
        "status": "STARTED",
        "started_utc": utc_now(),
        "repository": str(repository),
        "output": str(output),
        "cache": str(cache),
        "checkout": checkout,
        "platform": list(platform.uname()),
        "python": sys.version,
        "commands": [],
        "deployed_artifact_exported": False,
        "deployed_artifact_mounted": False,
        "deployed_artifact_read": False,
        "target_symbol_order_derived": False,
    }

    def save() -> None:
        write_json(output / "host-attempt.json", host)

    save()
    try:
        exported = export_source(
            repository,
            output / "input/source",
            source_inputs,
            policy["source"]["revision"],
        )
        write_json(output / "source-manifest.json", exported)
        driver = copy_driver(output / "driver")
        write_json(output / "driver-manifest.json", driver)
        image = policy["container"]["image"]
        inspect_command = ["docker", "image", "inspect", image]
        host["commands"].append(inspect_command)
        inspected = subprocess.run(inspect_command, capture_output=True, text=True)
        if inspected.returncode != 0:
            pull_command = [
                "docker",
                "pull",
                "--platform",
                policy["container"]["platform"],
                image,
            ]
            host["commands"].append(pull_command)
            with (output / "image-pull.log").open("wb") as log:
                pulled = subprocess.run(pull_command, stdout=log, stderr=subprocess.STDOUT)
            require(pulled.returncode == 0, "Pinned container image pull failed")
            inspected = subprocess.run(inspect_command, capture_output=True, text=True)
        require(inspected.returncode == 0, "Pinned container image is unavailable")
        image_data = json.loads(inspected.stdout)
        require(len(image_data) == 1, "Unexpected Docker image inspection result")
        require(
            image_data[0].get("Architecture") == "amd64" and image_data[0].get("Os") == "linux",
            "Pinned container is not Linux amd64",
        )
        write_json(output / "image-inspect.json", image_data)

        docker_command = [
            "docker",
            "run",
            "--rm",
            "--platform",
            policy["container"]["platform"],
            "--network",
            "bridge",
            "--mount",
            f"type=bind,source={output},target=/gate",
            "--mount",
            f"type=bind,source={cache},target=/cache",
            "-w",
            "/gate",
            image,
            "python3",
            "/gate/driver/run.py",
            "--inside",
            "--root",
            "/gate",
        ]
        host["commands"].append(docker_command)
        save()
        with (output / "container.log").open("wb") as log:
            execution = subprocess.run(docker_command, stdout=log, stderr=subprocess.STDOUT)
        host["container_returncode"] = execution.returncode
        host["container_log_sha256"] = sha256_file(output / "container.log")
        inner_result_path = output / "run/result.json"
        if inner_result_path.is_file():
            inner = read_json(inner_result_path)
            host["inner_status"] = inner.get("status")
            host["status"] = "COMPLETE" if execution.returncode == 0 else "BLOCKED"
        else:
            host["status"] = "BLOCKED"
            host["blocker"] = "Container exited without an inner result receipt"
        save()
        return execution.returncode
    except BaseException as error:
        host.update(
            status="BLOCKED",
            blocker=f"{type(error).__name__}: {error}",
            traceback=traceback.format_exc(),
        )
        return 1
    finally:
        host["finished_utc"] = utc_now()
        save()


def safe_extract(archive: Path, destination: Path) -> None:
    require(not destination.exists(), f"Extraction destination already exists: {destination}")
    destination.mkdir(parents=True)
    with tarfile.open(archive, "r:*") as stream:
        members = stream.getmembers()
        require(members, f"Empty archive: {archive.name}")
        for member in members:
            name = member.name.removeprefix("./")
            path = PurePosixPath(name)
            if name in ("", ".") and member.isdir():
                continue
            require(
                name not in ("", ".") and not path.is_absolute() and ".." not in path.parts,
                f"Unsafe archive member: {member.name}",
            )
            require(
                member.isfile() or member.isdir() or member.issym() or member.islnk(),
                f"Unsupported archive member type: {member.name}",
            )
            if member.issym():
                require(not posixpath.isabs(member.linkname), f"Absolute archive symlink: {member.name}")
                resolved = posixpath.normpath(
                    posixpath.join(posixpath.dirname(name), member.linkname)
                )
                require(
                    resolved != ".." and not resolved.startswith("../"),
                    f"Escaping archive symlink: {member.name}",
                )
            if member.islnk():
                target = posixpath.normpath(member.linkname.removeprefix("./"))
                require(
                    not posixpath.isabs(member.linkname)
                    and target != ".."
                    and not target.startswith("../"),
                    f"Escaping archive hardlink: {member.name}",
                )
        stream.extractall(destination)


def download_verified(cache: Path, name: str, specification: dict, downloads: list[dict]) -> Path:
    target = cache / name
    record = {
        "name": name,
        "url": specification["url"],
        "expected_bytes": specification["bytes"],
        "expected_sha256": specification["sha256"],
        "started_utc": utc_now(),
    }
    downloads.append(record)
    if target.exists():
        require(target.is_file() and not target.is_symlink(), f"Invalid cached archive: {name}")
        record["source"] = "verified-cache"
    else:
        partial = target.with_name(target.name + ".partial")
        require(not partial.exists(), f"Partial download already exists: {partial}")
        request = urllib.request.Request(
            specification["url"],
            headers={"User-Agent": "pump-fees-symbol-order-noop-v144"},
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response, partial.open("xb") as output:
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    output.write(block)
            partial.replace(target)
        except BaseException:
            record["partial_available"] = partial.exists()
            raise
        record["source"] = "download"
    record.update(bytes=target.stat().st_size, sha256=sha256_file(target), finished_utc=utc_now())
    require(record["bytes"] == specification["bytes"], f"Wrong archive size: {name}")
    require(record["sha256"] == specification["sha256"], f"Wrong archive hash: {name}")
    return target


class InnerAttempt:
    def __init__(self, root: Path, policy: dict) -> None:
        self.root = root
        self.run = root / "run"
        require(not self.run.exists(), "Inner run directory already exists")
        self.run.mkdir()
        (self.run / "logs").mkdir()
        (self.run / "artifacts").mkdir()
        (self.run / "evidence").mkdir()
        self.commands: list[dict] = []
        self.downloads: list[dict] = []
        self.result = {
            "schema": 1,
            "status": "STARTED",
            "stage": "preflight",
            "started_utc": utc_now(),
            "source_revision": policy["source"]["revision"],
            "compile_version": policy["compile"]["version"],
            "strip_version": policy["strip"]["version"],
            "build_attempts": 0,
            "ordered_build_started": False,
            "deployed_artifact_exported": False,
            "deployed_artifact_mounted": False,
            "deployed_artifact_read": False,
            "target_symbol_order_derived": False,
            "binary_patching": False,
            "symbol_swaps": 0,
        }
        self.save()

    def save(self) -> None:
        write_json(self.run / "commands.json", self.commands)
        write_json(self.run / "downloads.json", self.downloads)
        write_json(self.run / "result.json", self.result)

    def run_logged(
        self,
        name: str,
        command: list[str],
        cwd: Path,
        env: dict[str, str],
        *,
        check: bool = True,
    ) -> int:
        log = self.run / "logs" / f"{name}.log"
        row = {
            "name": name,
            "command": command,
            "cwd": str(cwd),
            "environment": {
                key: env[key]
                for key in sorted(env)
                if key
                in {
                    "AR",
                    "CC",
                    "CARGO_HOME",
                    "CARGO_NET_OFFLINE",
                    "CARGO_TARGET_DIR",
                    "CARGO_TARGET_SBF_SOLANA_SOLANA_RUSTFLAGS",
                    "HOME",
                    "OBJCOPY",
                    "OBJDUMP",
                    "RUSTC",
                    "RUSTDOC",
                }
            },
            "started_utc": utc_now(),
            "returncode": None,
            "log": str(log.relative_to(self.run)),
        }
        self.commands.append(row)
        self.save()
        started = time.monotonic()
        with log.open("xb") as output:
            execution = subprocess.run(command, cwd=cwd, env=env, stdout=output, stderr=subprocess.STDOUT)
        row.update(
            returncode=execution.returncode,
            seconds=time.monotonic() - started,
            log_sha256=sha256_file(log),
            finished_utc=utc_now(),
        )
        self.save()
        if check:
            require(execution.returncode == 0, f"{name} failed with {execution.returncode}; see {log}")
        return execution.returncode


def minimal_environment(
    tools: Path,
    run: Path,
    target: Path,
    target_rustflags: str,
    *,
    offline: bool,
) -> dict[str, str]:
    llvm = tools / "llvm/bin"
    rust = tools / "rust/bin"
    home = run / "home"
    cargo_home = run / "cargo-home"
    home.mkdir(exist_ok=True)
    cargo_home.mkdir(exist_ok=True)
    return {
        "HOME": str(home),
        "PATH": os.pathsep.join((str(rust), str(llvm), "/usr/bin", "/bin")),
        "LANG": "C",
        "LC_ALL": "C",
        "CARGO_HOME": str(cargo_home),
        "CARGO_TARGET_DIR": str(target),
        "CARGO_NET_OFFLINE": "true" if offline else "false",
        "CARGO_TERM_COLOR": "never",
        "CARGO_INCREMENTAL": "0",
        "RUSTC": str(rust / "rustc"),
        "RUSTDOC": str(rust / "rustdoc"),
        "CARGO_TARGET_SBF_SOLANA_SOLANA_RUSTFLAGS": target_rustflags,
        "CC": str(llvm / "clang"),
        "AR": str(llvm / "llvm-ar"),
        "OBJDUMP": str(llvm / "llvm-objdump"),
        "OBJCOPY": str(llvm / "llvm-objcopy"),
    }


def verify_root_rustc_log(log: Path, expected_link_arg: Optional[str]) -> dict:
    text = log.read_text(encoding="utf-8", errors="replace")
    root_lines = [
        line
        for line in text.splitlines()
        if "--crate-name pump_fees_candidate" in line and "rustc" in line
    ]
    require(len(root_lines) == 1, "Expected exactly one Pump Fees root rustc command")
    root = root_lines[0]
    required = (
        "--target sbf-solana-solana",
        "opt-level=3",
        "panic=abort",
        "codegen-units=1",
        "overflow-checks=on",
        "strip=debuginfo",
        "-Zremap-cwd-prefix=",
    )
    require(all(token in root for token in required), "Root rustc command differs from v1.44 baseline recipe")
    observed = re.findall(r"link-arg=([^\s\"'`]+)", text)
    if expected_link_arg is None:
        require(not observed, "Baseline unexpectedly contains a link-arg")
    else:
        require(observed, "Ordered build did not pass the symbol-ordering link argument")
        require(set(observed) == {expected_link_arg}, "Ordered build contains another link argument")
        require(root.count("link-arg=") == 1 and expected_link_arg in root, "Root crate must receive exactly one ordering link argument")
    return {
        "root_command": root,
        "expected_link_arg": expected_link_arg,
        "observed_link_args": observed,
        "only_supported_link_arg": not observed if expected_link_arg is None else set(observed) == {expected_link_arg},
    }


def copy_artifact(source: Path, destination: Path) -> dict:
    require(source.is_file() and not source.is_symlink(), f"Missing compiler output: {source}")
    require(not destination.exists(), f"Artifact already exists: {destination}")
    shutil.copyfile(source, destination)
    return artifact_record(destination)


def strip_artifact(
    attempt: InnerAttempt,
    label: str,
    objcopy: Path,
    unstripped: Path,
    stripped: Path,
    env: dict[str, str],
    cwd: Path,
) -> dict:
    command = [str(objcopy), "--strip-all", str(unstripped), str(stripped)]
    attempt.run_logged(f"{label}-strip-v152", command, cwd, env)
    return artifact_record(stripped)


def build_command(cargo: Path, manifest: Path, target: str) -> list[str]:
    return [
        str(cargo),
        "build",
        "--manifest-path",
        str(manifest),
        "--release",
        "--target",
        target,
        "--locked",
        "--offline",
        "--verbose",
        "--config",
        'profile.release.strip="debuginfo"',
    ]


def run_inside(root: Path) -> int:
    root = root.resolve()
    policy = read_json(root / "driver/policy.json")
    source_inputs = read_json(root / "driver/source-inputs.json")
    validate_policy(policy, source_inputs)
    attempt = InnerAttempt(root, policy)
    source = root / "input/source"
    source_before: Optional[dict[str, str]] = None
    try:
        require(platform.system() == "Linux", "Gate requires Linux")
        require(platform.machine() == "x86_64", "Gate requires Linux x86_64")
        require(root == Path("/gate"), "Container evidence root must be /gate")
        source_before = source_hashes(source, source_inputs)
        require(source_before == source_inputs, "Exported source differs from pinned current source")
        write_json(attempt.run / "source-before.json", source_before)

        cache = Path("/cache")
        require(cache.is_dir() and not cache.is_symlink(), "Verified download cache mount is unavailable")
        compile_spec = {
            "url": policy["compile"]["archive_url"],
            "bytes": policy["compile"]["archive_bytes"],
            "sha256": policy["compile"]["archive_sha256"],
        }
        strip_spec = {
            "url": policy["strip"]["archive_url"],
            "bytes": policy["strip"]["archive_bytes"],
            "sha256": policy["strip"]["archive_sha256"],
        }
        attempt.result["stage"] = "acquire-tools"
        attempt.save()
        compile_archive = download_verified(
            cache,
            "platform-tools-v1.44-linux-x86_64.tar.bz2",
            compile_spec,
            attempt.downloads,
        )
        attempt.save()
        strip_archive = download_verified(
            cache,
            "platform-tools-v1.52-linux-x86_64.tar.bz2",
            strip_spec,
            attempt.downloads,
        )
        attempt.save()

        toolchains = attempt.run / "toolchains"
        toolchains.mkdir()
        compiler = toolchains / "v1.44"
        stripper = toolchains / "v1.52"
        safe_extract(compile_archive, compiler)
        safe_extract(strip_archive, stripper)
        rustc = compiler / "rust/bin/rustc"
        cargo = compiler / "rust/bin/cargo"
        rustdoc = compiler / "rust/bin/rustdoc"
        objcopy = stripper / "llvm/bin/llvm-objcopy"
        for tool in (rustc, cargo, rustdoc, objcopy):
            require(tool.is_file(), f"Missing extracted tool: {tool}")
        for relative, expected in policy["compile"]["selected_sha256"].items():
            require(sha256_file(compiler / relative) == expected, f"Wrong v1.44 tool: {relative}")
        require(sha256_file(objcopy) == policy["strip"]["objcopy_sha256"], "Wrong v1.52 llvm-objcopy")
        linkers = list((compiler / "rust/lib/rustlib").glob("*/bin/rust-lld"))
        require(len(linkers) == 1, "Expected exactly one v1.44 host rust-lld")
        linker = linkers[0]

        base_flags = policy["compile"]["baseline_target_rustflags"]
        probe_env = minimal_environment(
            compiler,
            attempt.run,
            attempt.run / "probe-target",
            base_flags,
            offline=False,
        )
        attempt.result["stage"] = "linker-capability"
        attempt.save()
        attempt.run_logged("rustc-version-v144", [str(rustc), "--version", "--verbose"], source, probe_env)
        attempt.run_logged("cargo-version-v144", [str(cargo), "--version", "--verbose"], source, probe_env)
        attempt.run_logged("objcopy-version-v152", [str(objcopy), "--version"], source, probe_env)
        attempt.run_logged("rust-lld-version-v144", [str(linker), "-flavor", "gnu", "--version"], source, probe_env)
        help_log = attempt.run / "logs/rust-lld-help-v144.log"
        attempt.run_logged("rust-lld-help-v144", [str(linker), "-flavor", "gnu", "--help"], source, probe_env)
        help_bytes = help_log.read_bytes()
        help_destination = attempt.run / "evidence/rust-lld-help-v144.txt"
        help_destination.write_bytes(help_bytes)
        help_text = help_bytes.decode("utf-8", errors="replace")
        option = policy["compile"]["ordering_option"]
        require(
            re.search(r"(?:^|\s)--symbol-ordering-file(?:=|\s)", help_text, re.MULTILINE) is not None,
            "Actual v1.44 rust-lld help does not advertise --symbol-ordering-file",
        )
        tools_receipt = {
            "compile_archive_sha256": sha256_file(compile_archive),
            "strip_archive_sha256": sha256_file(strip_archive),
            "rustc": {"path": str(rustc), "sha256": sha256_file(rustc)},
            "cargo": {"path": str(cargo), "sha256": sha256_file(cargo)},
            "rust-lld": {"path": str(linker), "sha256": sha256_file(linker)},
            "llvm-objcopy": {"path": str(objcopy), "sha256": sha256_file(objcopy)},
            "rust_lld_help_sha256": sha256_bytes(help_bytes),
            "ordering_option_advertised": True,
        }
        write_json(attempt.run / "toolchain.json", tools_receipt)
        attempt.result["linker_option_supported"] = True

        manifest = source / policy["source"]["manifest"]
        fetch_env = minimal_environment(
            compiler,
            attempt.run,
            attempt.run / "fetch-target",
            base_flags,
            offline=False,
        )
        fetch_command = [str(cargo), "fetch", "--manifest-path", str(manifest), "--locked"]
        attempt.result["stage"] = "locked-fetch"
        attempt.save()
        attempt.run_logged("locked-fetch-v144-cargo", fetch_command, source, fetch_env)
        require(source_hashes(source, source_inputs) == source_before, "Locked fetch changed source")

        artifacts = attempt.run / "artifacts"
        evidence = attempt.run / "evidence"
        target = policy["compile"]["target"]
        baseline_target = attempt.run / "baseline-target"
        baseline_env = minimal_environment(
            compiler,
            attempt.run,
            baseline_target,
            base_flags,
            offline=True,
        )
        command = build_command(cargo, manifest, target)
        attempt.result.update(stage="baseline-build", build_attempts=1)
        attempt.save()
        attempt.run_logged("baseline-build-v144", command, source, baseline_env)
        baseline_flags = verify_root_rustc_log(
            attempt.run / "logs/baseline-build-v144.log", None
        )
        write_json(evidence / "baseline-root-command.json", baseline_flags)
        baseline_compiled = baseline_target / target / "release" / policy["source"]["library"]
        baseline_unstripped = artifacts / "baseline.unstripped.so"
        baseline_unstripped_record = copy_artifact(baseline_compiled, baseline_unstripped)
        baseline_stripped = artifacts / "baseline.stripped.so"
        baseline_stripped_record = strip_artifact(
            attempt,
            "baseline",
            objcopy,
            baseline_unstripped,
            baseline_stripped,
            baseline_env,
            source,
        )
        attempt.result["baseline"] = {
            "unstripped": baseline_unstripped_record,
            "stripped": baseline_stripped_record,
        }
        attempt.save()

        expected_baseline = policy["baseline"]
        require(
            baseline_stripped_record["bytes"] == expected_baseline["bytes"]
            and baseline_stripped_record["sha256"] == expected_baseline["sha256"],
            "Fresh Linux current-source v1.44 baseline differs; symbol order was not derived and ordered build was not started",
        )
        attempt.result["baseline_exact"] = True
        baseline_elf = Elf64.from_path(baseline_unstripped, "baseline unstripped")
        baseline_stripped_elf = Elf64.from_path(baseline_stripped, "baseline stripped")
        baseline_evidence = baseline_elf.evidence()
        require(
            baseline_elf.allocated_sections() == baseline_stripped_elf.allocated_sections(),
            "v1.52 baseline strip changed allocated sections",
        )
        write_json(evidence / "baseline-elf.json", baseline_evidence)

        functions = baseline_evidence["function_symbol_map"]
        order_bytes = baseline_elf.symbol_order_bytes()
        requested_names = [row["name"] for row in functions]
        require(
            order_bytes == ("".join(name + "\n" for name in requested_names)).encode("utf-8"),
            "No-op order encoding differs from the complete function map",
        )
        order_path = evidence / "symbol-order.txt"
        order_path.write_bytes(order_bytes)
        order_receipt = {
            "source": "fresh exact baseline .symtab only",
            "function_symbols": len(functions),
            "baseline_address_order": requested_names,
            "requested_order": requested_names,
            "symbol_swaps": 0,
            "order_sha256": sha256_bytes(order_bytes),
            "deployed_artifact_read": False,
            "target_symbol_order_derived": False,
        }
        write_json(evidence / "symbol-order.json", order_receipt)
        attempt.result.update(
            stage="ordered-build",
            ordered_build_started=True,
            build_attempts=2,
            function_symbols=len(functions),
            order_sha256=sha256_bytes(order_bytes),
        )
        attempt.save()

        expected_link_arg = f"{option}={ORDER_CONTAINER_PATH}"
        ordered_flags = f"{base_flags} -C link-arg={expected_link_arg}"
        ordered_target = attempt.run / "ordered-target"
        ordered_env = minimal_environment(
            compiler,
            attempt.run,
            ordered_target,
            ordered_flags,
            offline=True,
        )
        attempt.run_logged("ordered-build-v144", command, source, ordered_env)
        ordered_flags_receipt = verify_root_rustc_log(
            attempt.run / "logs/ordered-build-v144.log", expected_link_arg
        )
        write_json(evidence / "ordered-root-command.json", ordered_flags_receipt)
        ordered_log = (attempt.run / "logs/ordered-build-v144.log").read_text(
            encoding="utf-8", errors="replace"
        )
        lowered = ordered_log.lower()
        require(
            "unable to order" not in lowered and "symbol ordering file:" not in lowered,
            "rust-lld reported a symbol-ordering warning",
        )
        ordered_compiled = ordered_target / target / "release" / policy["source"]["library"]
        ordered_unstripped = artifacts / "ordered.unstripped.so"
        ordered_unstripped_record = copy_artifact(ordered_compiled, ordered_unstripped)
        ordered_stripped = artifacts / "ordered.stripped.so"
        ordered_stripped_record = strip_artifact(
            attempt,
            "ordered",
            objcopy,
            ordered_unstripped,
            ordered_stripped,
            ordered_env,
            source,
        )
        ordered_elf = Elf64.from_path(ordered_unstripped, "ordered unstripped")
        ordered_stripped_elf = Elf64.from_path(ordered_stripped, "ordered stripped")
        ordered_evidence = ordered_elf.evidence()
        require(
            ordered_elf.allocated_sections() == ordered_stripped_elf.allocated_sections(),
            "v1.52 ordered strip changed allocated sections",
        )
        write_json(evidence / "ordered-elf.json", ordered_evidence)

        comparisons = {
            "function_symbol_map_equal": ordered_evidence["function_symbol_map"]
            == baseline_evidence["function_symbol_map"],
            "text_equal": ordered_evidence["text"] == baseline_evidence["text"]
            and ordered_elf.section_bytes(".text") == baseline_elf.section_bytes(".text"),
            "relocations_equal": ordered_evidence["relocations"]
            == baseline_evidence["relocations"],
            "stripped_bytes_equal": ordered_stripped.read_bytes()
            == baseline_stripped.read_bytes(),
            "ordered_stripped_expected_sha256": ordered_stripped_record["sha256"]
            == expected_baseline["sha256"],
            "requested_order_equal_baseline_address_order": [
                row["name"] for row in ordered_evidence["function_symbol_map"]
            ]
            == requested_names,
            "symbol_swaps": 0,
        }
        write_json(evidence / "comparisons.json", comparisons)
        require(all(value is True for key, value in comparisons.items() if key != "symbol_swaps"), "No-op applicability equality failed")
        require(comparisons["symbol_swaps"] == 0, "No-op gate observed a symbol swap")
        require(source_hashes(source, source_inputs) == source_before, "Builds changed source")
        write_json(attempt.run / "source-after.json", source_before)

        attempt.result.update(
            status="APPLICABLE_NOOP",
            stage="complete",
            source_unchanged=True,
            only_supported_link_arg=True,
            ordered={
                "unstripped": ordered_unstripped_record,
                "stripped": ordered_stripped_record,
            },
            equalities=comparisons,
        )
        print(json.dumps(attempt.result, indent=2, sort_keys=True))
        return 0
    except BaseException as error:
        attempt.result.update(
            status="NOT_APPLICABLE",
            blocker={"type": type(error).__name__, "message": str(error)},
            traceback=traceback.format_exc(),
        )
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1
    finally:
        if source_before is not None:
            try:
                after = source_hashes(source, source_inputs)
                write_json(attempt.run / "source-after.json", after)
                attempt.result["source_unchanged"] = after == source_before
                if after != source_before and attempt.result["status"] == "APPLICABLE_NOOP":
                    attempt.result.update(
                        status="NOT_APPLICABLE",
                        blocker={"type": "GateError", "message": "Source changed during gate"},
                    )
            except BaseException as source_error:
                attempt.result["source_unchanged"] = False
                attempt.result["source_check_error"] = f"{type(source_error).__name__}: {source_error}"
                if attempt.result["status"] == "APPLICABLE_NOOP":
                    attempt.result.update(
                        status="NOT_APPLICABLE",
                        blocker={"type": "GateError", "message": "Final source verification failed"},
                    )
        attempt.result["finished_utc"] = utc_now()
        attempt.save()


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    result.add_argument(
        "--output",
        type=Path,
        help="Fresh ignored output directory below repository work/ (host mode)",
    )
    result.add_argument(
        "--cache",
        type=Path,
        default=Path("work/symbol-order-noop-v144-cache"),
        help="Hash-verified archive cache below repository work/ (host mode)",
    )
    result.add_argument("--inside", action="store_true", help=argparse.SUPPRESS)
    result.add_argument("--root", type=Path, help=argparse.SUPPRESS)
    return result


def main(arguments: Optional[list[str]] = None) -> int:
    args = parser().parse_args(arguments)
    try:
        if args.inside:
            require(args.root is not None and args.output is None, "Internal mode requires only --root")
            return run_inside(args.root)
        require(args.output is not None and args.root is None, "Host mode requires --output")
        return run_host(args)
    except BaseException as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

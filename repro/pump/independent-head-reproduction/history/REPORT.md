# Pump: independent HEAD build + window-match baseline (Windows/WSL)

An independent, from-scratch reproduction of the Pump reconstruction build on a
clean machine (Windows 11 + WSL2 Debian), to test the repository's core
reproducibility premise — *clean managed-source builds reproduce the tested
executables and symbols* — from source present at the current `main` HEAD, and
to record the resulting instruction-window baseline.

This packet establishes **L0–L1 only** (reproducible toolchain + a scored,
normalized-body baseline). It is **not** a byte-identity result, **not** a
source recovery, and **not** a security claim. No original bytes were used as
a compiler input. No executable was edited or padded.

## Environment

- Windows 11 (26200) host; build in WSL2 Debian.
- `cargo-build-sbf` (solana-cli) **3.1.10**, selected compile toolchain
  `--tools-version v1.44` (auto-fetched to `~/.cache/solana/v1.44`).
- Host toolchain for `cargo metadata`: rust **1.87.0** (x86_64).
- Profile from `programs/pump/Cargo.toml`: `panic=abort`, `overflow-checks=true`,
  `lto=false`, `codegen-units=1`; Anchor `=0.31.1`.

## Exact recipe

```sh
export RUSTUP_TOOLCHAIN=1.87-x86_64-unknown-linux-gnu   # host cargo metadata only
export CARGO_TARGET_DIR=<native-ext4-path>              # off /mnt/c for speed
cargo-build-sbf \
  --manifest-path programs/pump/Cargo.toml \
  --tools-version v1.44 \
  --sbf-out-dir <out>/artifacts -- --locked
```

Two real-world gotchas on a fresh machine, documented so others can reproduce:

1. **No default rustup toolchain** → `cargo-build-sbf` fails immediately with
   *"rustup could not choose a version of cargo to run"*. Set `RUSTUP_TOOLCHAIN`
   (host layer only; it does not affect sBPF codegen, which is pinned by
   `--tools-version`).
2. **A corrupt `1.89.0-x86_64-unknown-linux-gnu` cargo** on this machine
   (`ldd`: "not a dynamic executable", empty `--version`) makes
   `cargo metadata` emit no JSON. `1.87.0` / `1.96.0` / nightly all work.

## Results

Built from `main` HEAD source (37 source inputs under `programs/pump/`).

| Artifact | Bytes | SHA256 |
| --- | ---: | --- |
| Stripped candidate | 1,583,992 | `c74037604a67a80cd1bfec7af99a620ccd66ac93848f4de0f7d0ca1997638c4d` |
| Unstripped (symbols) | 2,165,264 | `9191b55447368fdd1e41500a5915296b32fd20d192f6f0fc6a929be4ebd6abbe` |

**Determinism:** two independent builds into separate fresh target directories
produced the identical stripped SHA256 above.

**Byte-size fidelity to the canonical pipeline:** both sizes match the published
`remaining-guards-main-fortyeight` artifacts exactly (candidate 1,583,992;
unstripped 2,165,264), despite this host using `cargo-build-sbf` 3.1.10 versus
that checkpoint's 2.1.21 — evidence that the wrapper version does not change the
emitted byte-size structure for this recipe. Hashes differ only because HEAD
source differs from that checkpoint's frozen source (all 37 inputs changed).

### Whole-file comparison (`scripts/compare.py`, padded to allocation)

- `original_bytes` 10,485,715, `candidate_bytes` 10,485,715
- `full_byte_equality` **false**
- `different_positions_in_shared_length` **1,022,808**

See [`whole-file-comparison.json`](whole-file-comparison.json).

### Instruction-window baseline (repo scorer `catalog.py`)

Scored with the repository's own `work/.../catalog.py` + `elf_reader.py`
(candidate = stripped build, symbols = unstripped build), against
`evidence/original/pump/deployed.so`.

| Metric | Published `374fcf0` | **HEAD (this build)** |
| --- | ---: | ---: |
| original inferred windows | 1,035 | 1,035 |
| raw-exact body match | 97 | **106** |
| normalized body match | 522 | **533** |
| direct-call-consistent match | 479 | **491** |
| without normalized match | 513 | **502** |
| matched body bytes | 365,544 | **401,032** |

HEAD is slightly ahead of the published baseline. Full summary in
[`window-match-summary.json`](window-match-summary.json).

## Scope and honesty

- "Normalized match" masks only ELF relocation and direct-call immediates; it
  proves body opcodes match, not transitive semantics or final link layout.
- 502 windows remain without a normalized match — the real recovery frontier.
  This packet does not move any of them; it only measures where they stand.
- Reproduced on one machine; the `cargo-build-sbf` 2.1.21 vs 3.1.10 difference
  is argued harmless from matching byte-sizes but is not proven byte-identical
  against a historical checkpoint here.

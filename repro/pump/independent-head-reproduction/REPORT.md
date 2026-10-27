# Pump: independent HEAD build + window-match baseline (Windows/WSL)

An author-reported, from-scratch reproduction of the Pump reconstruction build on a
clean machine (Windows 11 + WSL2 Debian), to test the repository's core
reproducibility premise — *clean managed-source builds reproduce the tested
executables and symbols* — from source present at the current `main` HEAD, and
to record the resulting instruction-window baseline.

This packet records the author's toolchain run and scored normalized-body
baseline. The WSL binaries and raw build logs are not bundled, so the WSL
hashes and the two-build determinism below are author-reported. Review checked
what it could without them (see "Same size, different bytes" and the
cross-host comparison): the source is pinned, and the per-window results are
consistent with an independent rebuild. It is **not** a byte-identity result, **not** a
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

Built from `main` HEAD source: the packet's base commit `0b29240a`, whose 37
compiler inputs under `programs/pump/` are byte-identical to the
`remaining-guards-main-fortyeight` checkpoint's recorded `source_sha256` map.

| Artifact | Bytes | SHA256 |
| --- | ---: | --- |
| Stripped candidate | 1,583,992 | `c74037604a67a80cd1bfec7af99a620ccd66ac93848f4de0f7d0ca1997638c4d` |
| Unstripped (symbols) | 2,165,264 | `9191b55447368fdd1e41500a5915296b32fd20d192f6f0fc6a929be4ebd6abbe` |

**Determinism (author-reported):** two independent builds into separate fresh target directories
produced the identical stripped SHA256 above.

**Same size, different bytes from the canonical pipeline:** both sizes match the
published `remaining-guards-main-fortyeight` artifacts exactly (candidate
1,583,992; unstripped 2,165,264), but the hashes do not, and the source is
**not** the reason: all 37 compiler inputs at this HEAD are byte-identical to
that checkpoint's recorded `source_sha256`. A review rebuild of this source on
macOS with the canonical pipeline (`cargo-build-sbf` 2.1.21, aarch64-darwin,
`--tools-version v1.44 --offline -- --locked --offline`) reproduces the
checkpoint's stripped SHA256 `71ec4d8a646eefc82ba177afbc3d08552deadd65cf2f80ec280862eb768d059c`
exactly. So the WSL build's `c7403760…` differs from the canonical build
because of the build host and/or wrapper (x86_64 Linux, `cargo-build-sbf`
3.1.10), not because of source. See the cross-host comparison below.

### Whole-file comparison (`scripts/compare.py`, padded to allocation)

- `original_bytes` 10,485,715, `candidate_bytes` 10,485,715
- `full_byte_equality` **false**
- `different_positions_in_shared_length` **1,022,808**

See [`whole-file-comparison.json`](whole-file-comparison.json).

### Instruction-window baseline (repo scorer `catalog.py`)

Scored with the repository's own
`repro/function-inventory/2026-10-24-374fcf0/work/pump-amm-current-body-inventory/catalog.py`
+ `elf_reader.py` (candidate = stripped build, symbols = unstripped build),
against `evidence/original/pump/deployed.so`.
[`score_pump.py`](score_pump.py) runs that scorer unmodified with its pump
candidate pointed at any build:
`python3 score_pump.py <stripped.so> <unstripped.so> <out-dir>` (writes
`pump-bodies.json`, the input of the later frontier packets, and
`body-summary.json`).

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

### Cross-host comparison (review)

The same source, scored the same way, gives different window counts on
different build hosts:

| Metric | macOS canonical rebuild (`71ec4d8a…`) | **WSL, this packet (`c7403760…`)** |
| --- | ---: | ---: |
| raw-exact body match | 98 | **106** |
| normalized body match | 528 | **533** |
| direct-call-consistent match | 486 | **491** |
| without normalized match | 507 | **502** |
| matched body bytes | 400,752 | **401,032** |

The five extra normalized matches on Linux are 56-byte
`core::error::Error::type_id` windows (`0xce50`, `0x188cc8`, `0x19a1a0`,
`0x1a8e28`, `0x1ab9b8`). They are unmatched in the macOS rebuild and absent
from the Linux build's unmatched list in
[`../frontier-spec`](../frontier-spec/REPORT.md). On macOS each differs from
the original only in its 16-byte `TypeId` constant (two `lddw` immediates).
`TypeId` hashes depend on crate metadata, which cargo derives partly from the
compiler's verbose version string, and that string names the host triple. The Darwin platform-tools also embed
`/Users/runner/...` standard-library paths where the original and the Linux
tools embed `/home/runner/...`. Both fit an x86_64-Linux-hosted original build.
That is consistent evidence, not proof of the historical host. For pump window
scoring, a Linux host is the closer reference.

## Scope and honesty

- "Normalized match" masks only ELF relocation and direct-call immediates; it
  proves body opcodes match, not transitive semantics or final link layout.
- 502 windows remain without a normalized match — the real recovery frontier.
  This packet does not move any of them; it only measures where they stand.
- Reproduced on one machine. The host/wrapper difference is **not** harmless:
  identical source gives different bytes (and 5 more matched windows) on this
  Linux host than on the macOS canonical pipeline, at identical file sizes.

The original author report is retained unchanged in `history/REPORT.md`. The
two JSON summaries are the author's WSL measurements, unchanged.

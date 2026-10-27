# ATA Darwin-host build experiment — NEGATIVE

One controlled source build of the Associated Token Account program, testing the
pre-registered hypothesis in [HYPOTHESIS.md](HYPOTHESIS.md): that the 307-byte
residual between the deployed ATA and the closest Linux candidate is explained by
the uploader having built on an `x86_64-apple-darwin` host.

**Result: the hypothesis is rejected.** The Darwin build differs from the deployed
program at 3,288 positions (10.7x the Linux residual), and the differences are a
broad re-ordering of code, not confined to the known two-function swap.

## Fixed inputs (no flag, version or path experimentation)

| Input | Identity |
| --- | --- |
| Source | solana-program-library `f5ce86d43dd31ddefb96d4e8cdd67dd073dc5dca` (release tree) |
| Lockfile | `3c8f402f…` — equals the authentic upstream lock; **unchanged after the build** |
| Solana CLI | official v1.10.33 `solana-release-x86_64-apple-darwin.tar.bz2`, sha256 `0bfefa7a…` |
| BPF toolchain | bpf-tools v1.27 osx, sha256 `c8e5d445…`, selected by the SDK's own immutable `install.sh` |
| rustc / cargo | `1.59.0-dev` LLVM 13.0.0, cargo 1.59.0 — rust `e2df8fa5`, cargo `49d8809d` (same commits as the Linux candidate) |
| **Host** | **`x86_64-apple-darwin`** (Apple Silicon via Rosetta) — the one input that differs from every prior candidate |
| Invocation | plain `cargo-build-bpf` from `associated-token-account/program`; child command `cargo +bpf build --target bpfel-unknown-unknown --release` (identical to candidate2 minus `--locked`) |

Full input hashes: [inputs.sha256](inputs.sha256). Toolchain identity as executed:
[toolchain.txt](toolchain.txt). Complete build output: [build.log](build.log).
Retained artifact: [darwin-x86_64-f5ce86.so](darwin-x86_64-f5ce86.so), 105,032 bytes,
sha256 `c6957a0eca84a9e36835fe9956de6deca0be64fedf95794adb61cae5fd067c86`.

## Measurements

```
deployed   6804554e69fd3a58
candidate2 ba8dd8a42ca7bff4  diffs vs deployed: 307
darwin     c6957a0eca84a9e3  diffs vs deployed: 3288  vs candidate2: 2981
darwin diffs by section: {'.text': 3267, '.rel.dyn': 21}
.rodata identical: True   section layout identical: True
pair order: deployed AccountMeta->u8 | candidate2 u8->AccountMeta | darwin u8->AccountMeta
call-masked .text instructions unique to each side: 9
```

Of 1,438 call-masked 64-byte chunks of the deployed `.text`, 1,314 (91.4%) are
byte-identical at the same offset in the Darwin build and 1,354 (94.2%) exist
somewhere in it; 40 chunks moved and 84 have no match. The instruction multiset
differs by only 9 instructions per side (address-bearing `lddw` immediates that
follow relocated functions), so the Darwin output is the same code, re-ordered
far more widely than the single pair.

The two `RawVec::reserve_for_push` bodies are present in the Darwin build at the
same offsets and in the same (wrong) order as candidate2.

## Interpretation

The result is consistent with the mechanism in the hypothesis: changing only the
host triple (which the pinned Cargo source hashes into every unit's `-C metadata`;
the metadata values themselves were not captured) re-ordered dozens of functions.
That is the expected signature of a *global* metadata perturbation.

The deployed program differs from the Linux candidate by a *single* pair. This
one pinned Darwin recipe did not reproduce that residual or the deployed bytes.
It does not prove that every global metadata perturbation must move many
functions: hash-based ordering can preserve relative order, and other historical
inputs remain unknown. The historical host is therefore unresolved. A
single-crate metadata difference is a possible explanation to investigate, not a
uniquely established cause or permission for a flag/version/path sweep.

What this does **not** do: reduce the 307-byte residual, recover the historical
recipe, or justify a flag/version/path sweep. It rejects the tested pinned Darwin recipe as an exact reproduction; it does not
exclude other Darwin contexts or establish a historical single-crate input.

Review note (2026-10-26):
[`../../synthetic-ordering-exact-build/`](../../synthetic-ordering-exact-build/REPORT.md)
later produced the exact deployed bytes on a Linux image by adding an empty Cargo
feature to ATA, `spl-token` and `spl-token-2022` (a narrow, non-historical
metadata input). That is consistent with a narrow metadata difference, but it
does not identify the historical input or host.

## Side observation: `cargo test-bpf` cannot be the missing input

The upstream CI script (`ci/cargo-test-bpf.sh`) runs `cargo test-bpf`. Reading the
v1.10.33 `cargo-test-bpf` source: it invokes `cargo-build-bpf` with only
`--manifest-path` and `--bpf-out-dir`, and passes `--features test-bpf` *only* to
the subsequent host `cargo test`, never to the BPF build. The produced `.so` is
therefore identical to a plain `cargo build-bpf`, and `test-bpf` is excluded as an
explanation without needing a build.

## Verification

```bash
git sparse-checkout add repro/ata/monomorph-order-proof repro/ata/independent-ebpf-crosscheck
python3 repro/ata/independent-ebpf-crosscheck/darwin-host-experiment/verify.py
```

`verify.py` is standard-library only, offline, reads three ELF files and asserts
every number above. It modifies nothing and exits non-zero on drift.

## Environment restoration

The build ran in a scratch directory outside the repository. The `bpf` rustup
toolchain link created by `cargo-build-bpf` and the `~/.cache/solana` directory it
populated were removed afterwards; no global toolchain was changed.

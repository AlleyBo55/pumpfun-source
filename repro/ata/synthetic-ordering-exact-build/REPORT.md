# ATA: exact deployed bytes from f5ce86 source with one synthetic metadata input

**Result.** A fresh, air-gapped source build of solana-program-library
`f5ce86d43dd31ddefb96d4e8cdd67dd073dc5dca` with the pinned Solana 1.10.33 /
bpf-tools v1.27 toolchain produces the deployed Associated Token Account program
**byte for byte**: 105,032 bytes, SHA-256
`6804554e69fd3a58caa191dc4a58f4c67223d30ca28ab8987f39fc18d2f7374d`, zero differing
positions. An independent rerun reproduces the same bytes.

**What was changed, in full.** Compared with the repository's closest prior
candidate (candidate2, `ba8dd8a4…`, 307 differing positions), exactly one input
differs: an empty feature `ordering-probe-b2 = []` is declared in the manifests of
`spl-associated-token-account`, `spl-token` and `spl-token-2022`, enabled on the
root with `cargo build-bpf --features ordering-probe-b2` and on the two path
dependencies from ATA's dependency lines. [source.patch](source.patch) is the
complete diff: three `Cargo.toml` files, five added lines, two modified dependency
lines, no `.rs` file. The flag is referenced by no `cfg()`, so no compiled code
changes. The authentic lockfile (`3c8f402f…`) is unchanged before and after every
build; `--locked` passed.

**What this establishes.** The deployed ATA is fully explained by the public
`f5ce86` source and the official toolchain. The 307-byte residual the repository
has carried was not a source, dependency-version or compiler difference: it was the
order of two same-definition `RawVec::reserve_for_push` monomorphizations, decided
by a symbol-hash tie-break that Cargo's `-C metadata` seeds. Changing that seed
with a no-op input re-rolls the tie-break and lands the deployed order.

**What this does not establish, stated plainly.** The historical recipe. The
uploader did not add a feature named `ordering-probe-b2`; some other, unknown
metadata input in the 2022 build environment produced the same tie-break outcome.
A match obtained by a synthetic input proves "this documented recipe compiles to
these bytes", not "this is what was run in 2022". Consistent with the repository's
stated rule that an arbitrary metadata override does not establish historical
identity, **this package changes no completion count**: `repro/status.json`,
`README.md` and `docs/COMPLETION.md` are untouched, and ATA stays recorded as
307-position candidate2 there. This is a labeled synthetic-recipe artifact.

## Mechanism (measured, not inferred)

| Step | Evidence |
| --- | --- |
| Cargo hashes enabled features into each unit's `-C metadata` | measured on the bpf-tools v1.27 cargo (`49d8809d`): adding an empty enabled feature changes the hash ([PR 36 report](../independent-ebpf-crosscheck/REPORT.md)) |
| `-C metadata` seeds the crate's `StableCrateId`, which enters the legacy symbol hash of every generic instance it emits | rustc `legacy.rs` `get_symbol_hash`: instantiating-crate `StableCrateId` is hashed for generic instances |
| Items in a codegen unit are ordered by `(def index, symbol name)`; same-definition instances tie on the first key | rustc `mono.rs` `items_in_deterministic_order` |
| The deployed/candidate2 difference is exactly one such tie group | [PR 36 byte-distance](../independent-ebpf-crosscheck/REPORT.md): 282 bytes inside the two `reserve_for_push` bodies, 25 call/relocation fixups; from the retained unstripped `spl_token_2022` object, this is the only order-sensitive group that survives in the binary |

So each fresh metadata seed is a fair coin on the pair's order, and a hit reproduces
all 307 bytes because every other byte already matched.

## Attempt ledger (all retained under `results/`)

| Attempt | Perturbation | Output | vs deployed | Reading |
| --- | --- | --- | ---: | --- |
| `control` | none | `ba8dd8a4…` = candidate2 | 307 | rig reproduces the repository's candidate exactly, offline |
| `a1` | empty feature on `spl-token-2022` only | `ba8dd8a4…` | 307 | metadata changed (fingerprint shows the feature), coin landed on the same order |
| `b1` | empty feature on ATA root only | `ba8dd8a4…` | 307 | deterministic non-event: ATA's own id does not enter the pair's hashes |
| `b2` | empty feature on ATA + spl-token + spl-token-2022 | **`6804554e…` = deployed** | **0** | hit |
| `b2r` | identical rerun of `b2`, fresh tree and container | `6804554e…` | 0 | deterministic |

`a1`'s null result is what a 50% coin produces half the time; it is not evidence
against the `spl_token_2022` attribution. `b2` perturbed three crates at once and
does not isolate which crate's metadata was sufficient; the minimal lever is not
claimed.

## Recipe (identical to candidate2's, plus offline inputs and the flag)

- Image: `solanafoundation/solana-verifiable-build@sha256:ee9ad7809009a99a70f659f7cba959e0c3c124e10f771b524914fd42f2b605a8`
  (amd64; ships `solana-cli 1.10.33 src:fcb85858`) — [image-inspect.json](image-inspect.json).
- Toolchain: bpf-tools v1.27 Linux, official asset SHA-256 `8a2d6a7d…`
  (rust `e2df8fa5`, cargo `49d8809d`), pre-seeded into `~/.cache/solana` so the
  SDK's own `install.sh` reuses it; criterion v2.3.3 likewise — [inputs.sha256](inputs.sha256).
- Source: official `f5ce86` tarball, SHA-256 `1b324f4c…`; lock `3c8f402f…`.
- Crates: all 632 lock entries vendored with `cargo vendor --locked` and used via
  source replacement, which keeps crates.io package identities (`--locked` still
  verifies the lock) — pinned by `.crate` hash in [vendor-manifest.json](vendor-manifest.json).
- Container: `--network none`. Command, as recorded in `results/b2/result.json`:
  `cargo build-bpf --offline --features ordering-probe-b2 --manifest-path /build/associated-token-account/program/Cargo.toml -- --locked`
  with `RUSTFLAGS=-D warnings` and the image's `rustup` active toolchain, exactly as
  `scripts/pump_build_token_dependency.py` runs candidate2.
- Executed driver: [probe.py](probe.py) (retained as run; its constants are the
  executing machine's paths). Build output: [results/b2/spl_associated_token_account.so](results/b2/spl_associated_token_account.so).

## Verify

```bash
python3 repro/ata/synthetic-ordering-exact-build/verify.py
```

Standard library only, offline. Checks the output's SHA-256 and a raw byte
comparison against `evidence/dependencies/associated_token/deployed.so`, the
determinism rerun, the control's equality with candidate2, both retained negatives,
that the patch touches only the three manifests and only adds the flag, and the
pinned input, image and vendor hashes. 24 assertions.

## Relation to prior ATA work

Builds on PR 36's measurements: the 307-position localization, the Darwin-host
negative (a global metadata change re-orders dozens of functions, so the historical
host was x86_64 Linux), and the single surviving order-sensitive tie group. Those
narrowed the residual to one Cargo metadata coin; this package flips it under a
documented input. Historical attribution still requires an uploader-side artifact
(build log, `target/` directory or unstripped object from 2022-08-03).

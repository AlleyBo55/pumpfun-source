# Pre-registered hypothesis: ATA 307-byte residual is a build-host artifact

Written BEFORE any download or build. Scratch directory, outside the repository.

## Observation
Closest ATA candidate (candidate2, `ba8dd8a4…`) differs from the deployed
program (`6804554e…`) by exactly 307 bytes: the two spl_token_2022
`RawVec::reserve_for_push` monomorphizations (u8, AccountMeta) are emitted in
swapped order; the other 25 bytes are the resulting call/relocation fixups.

## Mechanism
rustc sorts items in a codegen unit by `(local def index, symbol name)`
(rustc_middle mono.rs). The two instances share a definition, so their order is
decided by the legacy symbol-hash suffix, which includes the instantiating
crate's `StableCrateId`, itself derived from Cargo's `-C metadata`.

Cargo at the exact commit shipped in bpf-tools v1.27 (49d8809d,
`compilation_files.rs::hash_rustc_version`) hashes, for a `-dev` compiler,
the channel segment AND **`rustc -vV` host triple** into every unit's metadata.

## What all five prior candidates share
Host `x86_64-unknown-linux-gnu` (solana-verifiable-build amd64 image or Linux
CI). No prior candidate was built on a Darwin host.

## Why Darwin is the principled next input (not a sweep)
- Release asset uploaded 2022-08-03T22:12Z, *before* the first commit (22:24Z)
  and PR (22:26Z): a local maintainer build, not a CI artifact.
- 2022 Solana Labs engineering workstations were Macs. The v1.27 osx bpf-tools
  are `x86_64-apple-darwin` (also what an M1 ran under Rosetta).
- Changing only the host triple changes every user crate's `-C metadata`,
  re-drawing the ordering of the pair while (if LLVM codegen is host-invariant)
  leaving all other bytes unchanged.

## Prediction
If the uploader built on x86_64-apple-darwin with bpf-tools v1.27 from source
f5ce86 / lock 3c8f402f, a Darwin build reproduces the deployed bytes exactly.
If the build differs at exactly the same 307 positions, Darwin host is
excluded as the sole missing input. If it differs elsewhere, the osx sysroot is
not layout-equivalent to the Linux one and that is recorded as the finding.

## Fixed inputs (no flag/version/path experimentation)
- Solana CLI v1.10.33 official darwin release (`cargo-build-bpf`, `sdk/bpf`).
- bpf-tools v1.27 osx, fetched by the SDK's own immutable install.sh.
- Source: solana-program-library @ f5ce86d43dd31ddefb96d4e8cdd67dd073dc5dca.
- Invocation: plain `cargo build-bpf` from `associated-token-account/program`,
  exactly as candidate2 (minus `--locked`; lock hash verified unchanged after).
- Host: this Mac, x86_64 via Rosetta (`arch -x86_64`).

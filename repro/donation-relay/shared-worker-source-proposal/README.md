# Shared donation worker: source-only recovery proposal

The ordinary Rust change in `source.patch` recovers the complete **10,248-byte
worker window 112** under the repository's existing call/relocation normalization.
Local source builds measured **483/492 normalized windows (98.17%)**, up from 482
with no losses, and **130 raw local-body matches**. This is not raw whole-binary
identity: the isolated research candidate has 818,016 bytes versus 830,448 captured
bytes. Windows 92–100 remain unmatched in this isolated source state.

## Exactly what is published

This packet contains only readable source, a source patch, hash maps, verifier
code, tests and this recipe. There are **no compiled artifacts, replay cases,
compressed payloads, encoded binary payloads or archived replay derivatives**.
Local independent source builds and a fresh offline replay were performed. The
archived replay receipt's publication is blocked, so this packet is **not
self-contained or downloadable replay evidence**. Default verification does not
claim to recheck those local build/replay results.

The 56-file baseline is reconstructed by the already-published
[security-metadata parent's `sources()`](../security-metadata-source-recovery/verify.py)
using its **before-metadata** source state. This is the pinned 482-window
burn/mint baseline at `b55a3ade09e20c7f8755d777df3d69a5312dd3b8`, not a composition
with later metadata, location or epoch changes. `parent-inputs.json` pins the
public source-loader inputs; `source-inputs.json` records all 56 expected input
hashes before and after the single-file override.

## Source change

`source/shared_donation.rs` is ordinary Rust, not an output patch:

* A private mint-admission helper borrows `AccountInfo` and clones it **inside**
  the helper, retaining its mint key independently. Native-mint `Pubkey` checks
  return early before the typed-mint safety check.
* State accesses use context fields directly; config equality iterates the
  stored config first.
* A private checked increment helper returns `Result<()>`; tip division is
  bound before the increment and final epoch load.

This isolates a source-ownership/stack-placement boundary. No assembly, copied
program instructions, forced register/stack masks or post-build byte patch is
used. The recovered source is not asserted to be the unique historical source.

## Static verification and materialization

From the repository root, with Python 3.11 or newer:

```sh
P=repro/donation-relay/shared-worker-source-proposal
python3 -I -B "$P/verify.py"
python3 -I -B "$P/test_verify.py"
python3 -I -B "$P/verify.py" --materialize work/worker-source-fresh
```

Default verification checks the complete source maps, exact one-file patch,
parent hashes and packet manifest. Materialization creates a new directory and
writes only the verified 56 source inputs. Neither path reads program ELF bytes,
executes a compiler/VM, accesses a live chain, or consumes runtime receipts. A
regression test guards those read boundaries. Existing output directories,
unsafe names and source symlinks are rejected.

## Portable local compilation recipe

Use the official **Linux x86_64 Anza platform-tools v1.48**, including its target
libraries. The release URL is
<https://github.com/anza-xyz/platform-tools/releases/download/v1.48/platform-tools-linux-x86_64.tar.bz2>.
The observed archive SHA-256 is
`a9d3157f937d5f6faf4321a35a8035e0f827114a663b0150db492e893ec27597`;
this is an observed pin, not a publisher signature. Authenticate and prepare the
SDK separately. Use a Cargo registry cache containing all **253 locked public
packages**, with archives and extracted inputs verified against `Cargo.lock`.
Do not copy original program files into the source tree or use them as compiler
inputs. Native dependency build scripts/proc macros will execute during a build.

Set absolute paths for `SDK`, `CARGO_CACHE` and `SOURCE` below. `OUTPUT` must be a
new directory outside `SOURCE`. The fresh target avoids stale root artifacts;
keep the existing release profile (`overflow-checks=true`, `lto=false`,
`codegen-units=1`, `panic="abort"`) and default features unchanged.

```sh
SDK=/absolute/path/to/platform-tools-v1.48
CARGO_CACHE=/absolute/path/to/checksummed/cargo-home
SOURCE=/absolute/path/to/worker-source-fresh
OUTPUT=/absolute/path/to/new-worker-build
[ ! -e "$OUTPUT" ] && mkdir -p "$OUTPUT/home" || exit 1
cd "$SOURCE"
env -i \
  PATH="$SDK/rust/bin:$SDK/llvm/bin:/usr/bin:/bin" \
  HOME="$OUTPUT/home" CARGO_HOME="$CARGO_CACHE" \
  CARGO_TARGET_DIR="$OUTPUT/target" CARGO_NET_OFFLINE=true \
  CARGO_TERM_COLOR=never CARGO_BUILD_JOBS=3 \
  CARGO_TARGET_SBPF_SOLANA_SOLANA_RUSTFLAGS=-Zremap-cwd-prefix= \
  RUSTC="$SDK/rust/bin/rustc" RUSTDOC="$SDK/rust/bin/rustdoc" \
  CC="$SDK/llvm/bin/clang" AR="$SDK/llvm/bin/llvm-ar" \
  OBJDUMP="$SDK/llvm/bin/llvm-objdump" OBJCOPY="$SDK/llvm/bin/llvm-objcopy" \
  LANG=C.UTF-8 LC_ALL=C.UTF-8 \
  "$SDK/rust/bin/cargo" rustc --release --target sbpf-solana-solana \
  --locked --offline --verbose --manifest-path "$SOURCE/Cargo.toml" --lib \
  -- --remap-path-prefix=src/=programs/contracts/src/ \
  >"$OUTPUT/build.log" 2>&1 || exit 1
SYMBOLS="$OUTPUT/target/sbpf-solana-solana/release/donation_relay_source_proposal.so"
"$SDK/llvm/bin/llvm-objcopy" --strip-all "$SYMBOLS" "$OUTPUT/candidate.so"
```

Require the actual root `rustc --crate-name donation_relay_source_proposal`
invocation in the verbose log. Recheck all source and locked registry input
hashes before and after compilation. This recipe does not download dependencies,
install tools or establish an OS network/filesystem sandbox. Local observations
used root-clean dependency-cache reuse; a fresh all-dependency build at relocated
paths must be checked independently rather than assumed identical. Never repair
an output-hash discrepancy by copying or patching an archived binary.

## Optional comparison of your own outputs

After compilation, return to the repository root and provide both local ELF
paths. These paths are **comparison inputs only**, never compiler inputs:

```sh
python3 -I -B "$P/verify.py" \
  --candidate /absolute/path/to/new-worker-build/candidate.so \
  --symbols /absolute/path/to/new-worker-build/target/sbpf-solana-solana/release/donation_relay_source_proposal.so
```

The optional comparison pins the existing public ELF parser and 492-window
inventory, hashes both supplied outputs, recomputes full-window matches and raw
whole-file differences, verifies allocated stripped/symbol bytes agree, and
checks all 51 worker direct-call targets against complete normalized bodies. It
checks the public 482-window baseline to prove the gain is exactly worker112
with no losses. It does **not** verify replay, complete relocated-data extents,
transitive data semantics, indirect behavior or arbitrary-state equivalence.

Expected locally measured hashes, provided as checks rather than binary payloads:

| Object | SHA-256 |
| --- | --- |
| Stripped | `bdd03c7765c65d5c7ea9f1c16900f766e38c97fcec3071e29678f0ae52772399` |
| Symbols | `1ca9e99a37864a75d854d815848c7ce7cae838a719591dfac0286addf2193120` |
| Normalized worker | `c2d4d9828ae9e8b49c789dbabf13c8321fc0381d006f5f9e66f8f2e445b8200a` |

Normalization masks only established local direct-call displacements and
relocated `lddw` addresses, never registers, opcodes or stack offsets. The worker
itself is normalized, not raw, equal. Overall byte-identical completion remains
unestablished; 98.17% describes this isolated window inventory only.

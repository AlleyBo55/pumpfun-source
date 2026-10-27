# Pump: `file!()` workspace-prefix recovery (+5 normalized windows, 0 regressions)

A build-environment experiment. The committed scores are the author's Linux
(WSL) measurements of the packet's base source (`0b29240a`); the window-level
effect (+5, the same five windows, 0 regressions) was independently reproduced
in review on a second host (see "Independent check" below). The reconstruction builds `programs/pump` as its
own crate (its `Cargo.toml` declares an empty `[workspace]`), so cargo roots the
crate at itself and `file!()` expands to `src/<module>.rs`. The original path strings are consistent with a monorepo workspace; the
historical workspace recipe has not been established. Its Anchor
error macros captured `programs/pump/src/<module>.rs`. That string, length and
all, is baked into every error site, so the reconstruction's `.text` differs
from the original at a scatter of single bytes across many functions.

Building pump as a workspace member (preserving pump's own `Cargo.lock`) makes
`file!()` emit the monorepo-relative path, flipping **5** instruction windows
from unmatched to normalized-match with **0 regressions**.

## Evidence of the mechanism

The smallest single near-miss, `toggle_mayhem_mode` (672 bytes), differs from
the original in exactly one normalized byte — the immediate of a
`stdw [r10-0x100], IMM` store:

```
original: 7a 0a 00ff 18000000   ; store u64 0x18 = 24
rebuild : 7a 0a 00ff 0a000000   ; store u64 0x0a = 10
```

The preceding `lddw r1, <addr>` loads a string pointer and this store writes its
length — i.e. an Anchor error `Source { filename, line }` `&str`. The original
filename is 24 bytes; the standalone rebuild's is 10:

- `programs/pump/src/lib.rs` → 24
- `src/lib.rs` → 10

Confirmed directly: the original binary contains `programs/pump/src/*.rs` path
strings; the standalone rebuild contains bare `src/*.rs`.

## Result (repo scorer `catalog.py`, vs `evidence/original/pump/deployed.so`)

| Metric | standalone | workspace-member | Δ |
| --- | ---: | ---: | ---: |
| normalized body match | 533 | **538** | +5 |
| direct-call-consistent match | 491 | **500** | +9 |
| without normalized match | 502 | **497** | −5 |
| matched body bytes | 401,032 | **405,304** | +4,272 |
| raw-exact body match | 106 | 106 | 0 |

Raw-exact is unchanged, as expected: raw identity additionally needs the global
function layout (absolute pointer values, call immediates) to line up, which a
local source/build change does not provide.

Flipped windows (all whose module path now matches the original):
`toggle_mayhem_mode` (`lib.rs`), and `QuoteControl::{space, remove_mint,
set_mint_reserves}` + `QuoteControl as AccountDeserialize::try_deserialize`
(`quote_control/state.rs`). See [`flipped-windows.json`](flipped-windows.json)
and [`window-match-before-after.json`](window-match-before-after.json).

Independent check (review): rebuilding the base source `0b29240a` on macOS with
the canonical pipeline (`cargo-build-sbf` 2.1.21, v1.44), standalone vs this
workspace-member wrapper, gives 528 -> 533 normalized, 486 -> 495
direct-call-consistent, +4,272 matched bytes, raw-exact 98 unchanged. The five
flipped windows are exactly the five above, with no regressions. The deltas
match this packet; the absolute counts are host-dependent (the Linux build
scores 5 higher, see
[`../independent-head-reproduction`](../independent-head-reproduction/REPORT.md)).
`build_prefix.sh` (with a `sed -i` shim for BSD sed) reproduces that macOS
workspace-member build byte-for-byte (stripped `0912d0ef…`, unstripped
`803f56c7…`).

## Reproduce

`bash build_prefix.sh <repo-root> <fresh-out-dir>` (WSL/Linux with GNU `sed`;
needs the v1.44 platform-tools, auto-fetched by `cargo-build-sbf`). It builds
pump in a throwaway parent workspace with pump's own `Cargo.lock`, so only the
`file!()` rooting changes — deps are untouched. The stripped artifact lands in
`<out>/artifacts/` and the unstripped build in `<out>/target/` (unless
`CARGO_TARGET_DIR` is set). Score the pair with
[`../independent-head-reproduction/score_pump.py`](../independent-head-reproduction/score_pump.py).

Main's later
[`pump-restructured`](../../parallel-work/2026-10-25/independent-reconstruction-review/restructure/pump-restructured/README.md)
tree uses the same workspace-member wrapper (its `workspace-Cargo.toml` is
identical to the one this script writes) plus `#[path]` relocations, and
measures embedded path strings and panic-`Location` records. This packet is
the window-level measurement of the prefix alone.

## Why only 5, and the roadmap to more

Only functions whose **module file path** already matches the original flip once
the prefix is added. The original's module layout (recovered from its embedded
`file!()` strings) differs from the reconstruction's flat split. Paths present in
the original but not the reconstruction, each a cluster of error sites that would
match after the same rename + prefix:

```
buy.rs  sell.rs  trade_v3.rs  extend_account.rs  fee_recipient.rs
pump_quote.rs  multi_hop_curve_swap.rs  admin_set_idl_authority.rs
set_reserved_fee_recipients.rs  sweep_fees.rs
creator/{admin_cto, collect_creator_fee, distribute_creator_fees,
         distribute_creator_fee_v2, distribute_fee_to_holders,
         migrate_bonding_curve_creator, set_creator, set_metaplex_creator}.rs
token_incentives/{claim_token_incentives, init_user_volume_accumulator,
                  volume_accumulator}.rs
util/{constant_product, fee, transfer_fee}.rs
```

Reorganizing the reconstruction's source into this layout (the module paths
embedded in the original binary) corrects those embedded path strings. It is
not enough to flip further windows, though: the follow-up
[`../metadata-callsite-map`](../metadata-callsite-map/REPORT.md) shows that
every remaining window whose body otherwise matches also differs in `line!()`,
and that no unmatched window has any same-size reconstruction function that
differs from it only in `file!()` length. This packet does not perform the
reorganization.

## Scope and honesty

Build-environment recovery only. No source logic changed, no byte-identity
achieved, no original bytes used as a compiler input. The `file!()` prefix is one
necessary condition among many; the 497 remaining unmatched windows stand.

## Review and caller inputs

`build_prefix.sh` requires an existing repository root and a nonexistent output
path whose parent already exists. Relative output paths are resolved before
changing directories. The caller must record the exact source commit and source
hash map, local modifications, lockfile, selected compiler and strip tools before
claiming a reproduction; this packet does not pin a historical source revision.
The build helper is opt-in; the second review ran it (see "Independent
check"). The original report and script are preserved unchanged in `history/`.
The score JSON files remain the author's unchanged Linux measurements. No `file!()` or `line!()` source
coordinates are forced by this helper, and no source/artifact is selected.

## Fresh target directory admission

The helper resolves a caller-supplied `CARGO_TARGET_DIR` against the invocation
working directory before entering the throwaway workspace. Its parent must
already exist. The target must be nonexistent, distinct from OUT, and not an
existing symlink (including a dangling symlink). Exclusive directory creation
claims it before any compiler invocation. Existing caches or outputs are
preserved and rejected. With no explicit target, the helper uses fresh
`<absolute-out>/target`. The compiler recipe and source inputs are unchanged.

`test_build_prefix_paths.py` uses temporary dummy Cargo files and a shell
sentinel in place of the compiler. It checks default/relative target resolution,
existing-target rejection and dangling-symlink rejection. No Rust/SBF compiler,
VM, native package, original binary or decoder runs in these tests. Historical
reports, score JSON and receipts are not regenerated by this admission fix.

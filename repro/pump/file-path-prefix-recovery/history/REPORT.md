# Pump: `file!()` workspace-prefix recovery (+5 normalized windows, 0 regressions)

A build-environment recovery. The reconstruction builds `programs/pump` as its
own crate (its `Cargo.toml` declares an empty `[workspace]`), so cargo roots the
crate at itself and `file!()` expands to `src/<module>.rs`. The original
pump.fun program was built as a member of a monorepo workspace, so its Anchor
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

## Reproduce

`bash build_prefix.sh <repo-root> <out-dir>` (WSL/Linux; needs the v1.44
platform-tools, auto-fetched by `cargo-build-sbf`). It builds pump in a throwaway
parent workspace with pump's own `Cargo.lock`, so only the `file!()` rooting
changes — deps are untouched.

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

Reorganizing the reconstruction's source into this layout (the original monorepo
structure, now known from the binary) is the follow-up that would flip the error
sites in those modules. This packet does not perform that reorganization.

## Scope and honesty

Build-environment recovery only. No source logic changed, no byte-identity
achieved, no original bytes used as a compiler input. The `file!()` prefix is one
necessary condition among many; the 497 remaining unmatched windows stand.

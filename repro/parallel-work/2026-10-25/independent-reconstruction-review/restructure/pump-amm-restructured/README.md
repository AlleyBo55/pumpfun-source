# pump_amm — restructured toward the recovered original module tree (compiling)

_2026-10-26. Companion to `pump-fees-restructured/` and `mayhem-restructured/`. Reference artifact under
`repro/` — NOT active main source._

## Approach: `#[path]` relocation (zero body change)
pump_amm's `#[program]` dispatcher already delegates almost every handler to a separate module
(`legacy_buy::execute`, `multi_hop::execute`, `create::execute`, …). So instead of merging/splitting
bodies, each already-separate module file is **physically moved to its recovered original path** and
lib.rs points at it with `#[path = "..."]`, keeping the module identifier. This changes the `file!()`
path recorded at every panic/`require!`/`unwrap` site **without touching the code**, so it recovers the
embedded `.data.rel.ro` source-path strings with no body-codegen regression.

Built as a **workspace member** (crate dir `pump-amm`, already matches the original) with platform-tools
**v1.44**, so paths embed as `programs/pump-amm/src/...` rather than bare `src/...`.

### Clean 1:1 relocations applied (10)
| module | → recovered path |
|---|---|
| `legacy_buy` | `instructions/swap/buy.rs` |
| `legacy_sell` | `instructions/swap/sell.rs` |
| `multi_hop` | `instructions/swap/multi_hop_swap.rs` |
| `create` | `instructions/create_pool.rs` |
| `boost` | `instructions/boost.rs` |
| `sweep` | `instructions/sweep_fees.rs` |
| `extend` | `instructions/extend_account.rs` |
| `creator_reassignment` | `instructions/coin_creator/set_coin_creator.rs` |
| `collect` | `instructions/coin_creator/collect_coin_creator_fee.rs` |
| `transfer_creator` | `instructions/coin_creator/transfer_creator_fees_to_pump.rs` |

`instructions/admin/create_config.rs` and `instructions/token_incentives/init_user_volume_accumulator.rs`
already sat at their recovered paths; `lib.rs` and `state/global_config.rs` also match.

## Result (path-string recovery)
| build | exact original path strings present | oracle files w/ decoded Location |
|---|---|---|
| standalone (committed-candidate style) | **0 / 33** | 0 / 10 |
| **this (workspace member + relocations)** | **13 / 33** | **9 / 10** |

`(file,line,col)` sites still 0/41 — line positions are source-bound. See `oracle.txt`.

## Why not 33/33
The recovered original tree is a **lower bound** (only files with a Location site appear) and is
**regroup-heavy**: the remaining ~20 files need splits/extractions the current flat source doesn't provide
1:1 — the admin group is split per-handler (`admin_cto_pool.rs`, `toggle_boost.rs`, `toggle_mayhem_mode.rs`,
`set_reserved_fee_recipients.rs`, `update_buyback_config.rs`), plus `curve/{constant_product,fees}.rs`,
`instructions/liquidity/{deposit,withdraw}.rs`, `utils/{math,token,transfer_fee}.rs`, `state/pool.rs`,
`state/volume_accumulator.rs`, `instructions/swap/trade_v2.rs`, `instructions/token_incentives/claim.rs`.
Those placements are **inferred** (the authentic source is needed to split faithfully), so only the
determinable 1:1 relocations are materialized here. `transfer_creator_fees_to_pump.rs` is placed but has no
surviving Location site, so its path string does not appear (13, not 14).

## Build
From the workspace root: `cargo build-sbf --manifest-path programs/pump-amm/Cargo.toml --tools-version
v1.44 --offline --sbf-sdk <sdk> --sbf-out-dir OUT -- --locked --offline` → `pump_amm_recovered.so` (rc=0).
Note the `[patch.crates-io] solana-pubkey` must move to the workspace-root Cargo.toml, and the package's
`Cargo.lock` must be copied to the workspace root (else offline resolve fails). See `build.log`.

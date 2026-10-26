# pump — restructured toward the recovered original module tree (compiling)

_2026-10-26. Companion to `pump-fees-restructured/`, `mayhem-restructured/`, `pump-amm-restructured/`.
Reference artifact under `repro/` — NOT active main source._

## Approach: `#[path]` relocation (zero body change) + workspace-member build
pump's `#[program]` dispatcher delegates each handler to a separate module. Each already-separate module
file is physically moved to its recovered original path and lib.rs points at it with `#[path = "..."]`
(module identifier unchanged), so the `file!()` path recorded at every panic/`require!`/`unwrap` site
changes **without touching the code** — recovering the embedded `.data.rel.ro` source-path strings with no
body-codegen regression. Built as a **workspace member** (crate dir `pump`, matches the original) with
platform-tools **v1.44**, so paths embed as `programs/pump/src/...` not bare `src/...`.

### Clean relocations applied (14)
`multi_hop_curve`→`multi_hop_curve_swap.rs`, `legacy_buy`→`buy.rs`, `legacy_sell`→`sell.rs`,
`extend`→`extend_account.rs`, `idl_authority`→`admin_set_idl_authority.rs`,
`volume_sync`→`token_incentives/volume_accumulator.rs`, `sweep`→`sweep_fees.rs`,
`admin_cto`→`creator/admin_cto.rs`, `set_creator`→`creator/set_creator.rs`,
`distribution`→`creator/distribute_creator_fees.rs`, `holder_distribution`→`creator/distribute_fee_to_holders.rs`,
`collect_v2`→`creator/collect_creator_fee.rs`, `trade`→`trade_v3.rs`,
`creator_migration`→`creator/migrate_bonding_curve_creator.rs`.
Already at their recovered paths (no move): `create_v2.rs`, `migrate.rs`, `migrate_v2.rs`, `buy_v2.rs`,
`sell_v2.rs`, `lib.rs`, `quote_control/{initialize_quote_control,state,update_quote_control_mints}.rs`,
`token_incentives/claim_token_incentives.rs`.

## Result — strongest of the four programs
| metric | standalone | this (workspace member + relocations) |
|---|---|---|
| exact original path strings present | 0 / 33 | **23 / 33** |
| oracle files w/ decoded Location | 0 / 15 | **25 present** |
| oracle files fully matching (path + **line + col**) | 0 | **1 / 15** (`quote_control/state.rs:16`) |

`quote_control/state.rs:16` is the **first exact Location-record match** achieved in any of the four
restructures — path, line, AND column all equal to the original. It happens because that file already sat
at its recovered path and its single `require!` site lands on the original's line. This is a concrete
byte-level match of a panic-`Location` record (a small piece of `.data.rel.ro`), proving the residual is
genuinely closable where the module path + statement line coincide.

## Why not 33/33 / why only 1 exact site
Remaining misses need **inferred splits** the current flat source doesn't provide 1:1: the `creator/`
group splits further (`distribute_creator_fee_v2.rs`, `set_metaplex_creator.rs`), `util/{constant_product,
fee,transfer_fee}.rs` are inline helpers, and `fee_recipient.rs`, `set_reserved_fee_recipients.rs`,
`pump_quote.rs`, `token_incentives/init_user_volume_accumulator.rs` have no clean current counterpart. The
(line,col) positions for the other 22 present files differ because statement line layout is **source-bound**
(lost original source). See `oracle.txt`.

## Build
From the workspace root: `cargo build-sbf --manifest-path programs/pump/Cargo.toml --tools-version v1.44
--offline --sbf-sdk <sdk> --sbf-out-dir OUT -- --locked --offline` → `pump_recovered.so` (rc=0). The
package `Cargo.lock` must be copied to the workspace root or offline resolve fails. See `build.log`.

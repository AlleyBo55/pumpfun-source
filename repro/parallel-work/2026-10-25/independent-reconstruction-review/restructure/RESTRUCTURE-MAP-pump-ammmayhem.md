# Restructure maps — pump, pump_amm, mayhem (recovered targets + current→recovered)

_2026-10-26. Companion to the pump_fees restructure. Recovered module files come from decoding each
deployed binary's panic-`Location` paths (`../source-maps/original-source-maps.json`). Current files are
the reconstruction's `programs/<crate>/src`. These maps are the spec for reorganizing each crate toward
its original tree._

## IMPORTANT caveats (why these differ from pump_fees)
1. **The recovered tree is PARTIAL** — only files that contain a panic/`require!`/`unwrap` `Location`
   appear. Files with no such site are invisible, so the recovered list is a *lower bound*, not the full
   original tree. (pump shows 15 files but the current crate has ~30; the rest aren't revealed.)
2. **Different grouping** — the reconstruction groups by operation (buy.rs, sell.rs, buy_v2.rs…), the
   original groups by interface (pump_interface.rs, pump_interface_v2.rs, pump_amm_interface.rs). Merging
   several current files into one recovered file is required.
3. **fn-name collisions** — each current instruction file names its handler `handler` (disambiguated by
   module path). Merging two into one recovered file requires renaming them (e.g. `handler`→`buy`/`sell`).
4. Therefore a *faithful* compiling tree here is **partly inferred** (by name/semantics), unlike pump_fees'
   near-1:1 mapping. The determinable placements are below; exact placement of Location-free functions needs
   the authentic source.

## mayhem (crate mayhem-program) — most determinable
| recovered file | current source (handlers) |
|---|---|
| instructions/pump_interface.rs | instructions/buy.rs + sell.rs (legacy `buy`/`sell`) |
| instructions/pump_interface_v2.rs | instructions/buy_v2.rs + sell_v2.rs |
| instructions/pump_amm_interface.rs | instructions/buy_pump_swap.rs + sell_pump_swap.rs |
| instructions/burn.rs | instructions/burn.rs (`burn_tokens`) |
| instructions/extend_account.rs | lib.rs inline `extend_account` |
| instructions/fee_recipients.rs | lib.rs inline `initialize_fee_recipient`, `sweep_fees`, `sweep_fees_admin`, `withdraw_quote_admin`, `withdraw_admin` |
| instructions/admin.rs | lib.rs inline `initialize_global_params`, `update_global_params`, `update_admin`, `update_trader`, `update_max_sol_per_sweep`, `update_max_stable_per_sweep`, `reset_sol_deployed`, `reset_stable_deployed`, `reset_state`, `stop_trading`, `resume_trading` |
| state.rs / lib.rs | state.rs / lib.rs (keep); helpers `checked_program.rs`, `instructions/pump_swap_types.rs` stay |

## pump_amm (crate pump-amm-recovered)
| recovered file | current source |
|---|---|
| instructions/swap/buy.rs | legacy_buy.rs / trade.rs (buy path) |
| instructions/swap/sell.rs | legacy_sell.rs / trade.rs (sell path) |
| instructions/swap/multi_hop_swap.rs | multi_hop.rs |
| instructions/coin_creator/set_coin_creator.rs | creator_reassignment.rs / transfer_creator.rs |
| instructions/extend_account.rs | extend.rs |
| state/global_config.rs | state/global_config.rs (exists) |
| state/volume_accumulator.rs | instructions/token_incentives/* / state.rs (accumulator) |
| utils/math.rs, utils/token.rs | math/token helpers (currently inline) |
| lib.rs | lib.rs (+ boost, cashback, collect, sweep, incentives have no recovered Location file → stay) |

## pump (crate pump-recovered) — largest, least complete recovered tree (15 of ~30 files)
| recovered file | current source |
|---|---|
| create_v2.rs, migrate.rs, migrate_v2.rs | same names (exist) |
| quote_control/state.rs | quote_control/state.rs (exists) |
| sell.rs | sell_v2.rs / legacy_sell.rs (sell path) |
| multi_hop_curve_swap.rs | multi_hop_curve.rs |
| admin_set_idl_authority.rs | idl_authority.rs |
| extend_account.rs | extend.rs |
| token_incentives/volume_accumulator.rs | volume_sync.rs |
| creator/{set_creator, set_metaplex_creator, distribute_creator_fees, distribute_creator_fee_v2, distribute_fee_to_holders}.rs | set_creator.rs, distribution.rs, holder_distribution.rs (regroup under creator/) |
| lib.rs | lib.rs (+ buy_v2, cashback, collect_v2, create, creator_migration, global_init, legacy_buy, minimum, nested_create, set_params, sweep, trade, trade_types — no recovered Location file → stay) |

## Recommendation
Materialize compiling trees per-program on demand (mayhem is the cleanest to do faithfully; pump_amm and
pump involve more inference). The maps + the pump_fees worked example + the `analyze_fn.py`/`verify_source_map.py`
tooling are the durable, reusable assets; full byte-identity still requires the authentic source.

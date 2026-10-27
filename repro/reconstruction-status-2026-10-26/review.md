# Comprehensive reconstruction review

Reviewed merged evidence: `e2d7855848a3411d665deb915077ef20672e7cdd`. Selected builds remain bound to `1463bd22fb7811825c5e7acf1cb963eb39ab68d9`.

**No core program or Relay is whole-file byte-identical. No public handler is proved exhaustively perfect.**

## How to read the classifications

- **Exact local bytes:** an entire inferred original window has a raw-byte counterpart. Calls, referenced data, placement and duplicate identity still need verification.
- **Normalized only:** complete local body matches under the owning study’s masks. This is reconstructed machine structure, with masked operands and transitive behavior still unresolved.
- **Unmatched:** no complete counterpart under that matcher. This can include extensive existing source; it does not mean every instruction is missing.
- **Opaque:** no admitted normalized comparison and no raw counterpart. Investigate source attribution before claiming recovery.
- **Bounded handler:** source has retained finite execution evidence. It can still have known discrepancies. Public handlers and compiler-generated windows are different inventories.

## All programs: remaining machine-code scope

| Build | Exact local windows | Normalized only | Unmatched | Opaque | Unmatched + opaque bytes / original text |
| --- | ---: | ---: | ---: | ---: | ---: |
| donation_relay | 33 | 89 | 370 | 0 | 735,984 / 752,488 (97.8%) |
| donation_relay_research | 130 | 352 | 10 | 0 | 52,616 / 752,488 (7.0%) |
| mayhem | 58 | 131 | 7 | 245 | 636,128 / 706,744 (90.0%) |
| pump | 98 | 430 | 507 | 0 | 1,391,456 / 1,792,208 (77.6%) |
| pump_amm | 93 | 395 | 297 | 0 | 734,392 / 1,162,040 (63.2%) |
| pump_fees | 102 | 363 | 120 | 0 | 418,392 / 799,648 (52.3%) |
| pump_fees_research | 118 | 424 | 43 | 0 | 248,904 / 799,648 (31.1%) |

These byte totals count entire unresolved original windows, not differing bytes or development effort. Raw and normalized matches can still contain unresolved references. Do not add selected and research rows: they represent alternative builds of the same programs. Mayhem has 257 source-ledger opaque windows; 12 have raw counterparts and therefore appear in the exact column.

Fees research has 395 unique structural pairs, 65 additional call-attributed pairs and 85 unattributed duplicate windows. Its encoded-call ledger has 3,145 bound-target edges and 18 different-body frontier edges. A bound edge is not a full semantic proof. Selected Fees retains two call-conflicting rows.

## Every public handler: source/behavior status

All 150 names appear below. The detailed [handler ledger](../reconstruction-audit-2026-10-26/handlers.md) contains source links and per-handler gaps. Unaccepted includes source that exists only in overlays, as well as static-only implementation; it must not be read as universally absent source.

| Program | Classification | Count | Handler names |
| --- | --- | ---: | --- |
| pump | Bounded; perfection unproved | 48 | `add_quote_control_mint`, `add_quote_mint`, `admin_cto`, `admin_set_idl_authority`, `buy`, `buy_exact_quote_in_v2`, `buy_exact_sol_in`, `buy_v2`, `claim_cashback`, `claim_cashback_v2`, `close_user_volume_accumulator`, `collect_creator_fee`, `collect_creator_fee_v2`, `create`, `distribute_creator_fees`, `distribute_creator_fees_v2`, `distribute_fee_to_holders`, `extend_account`, `get_minimum_distributable_fee`, `init_user_volume_accumulator`, `initialize`, `initialize_quote_control`, `migrate`, `migrate_bonding_curve_creator`, `migrate_v2`, `remove_quote_control_mint`, `remove_quote_mint`, `sell`, `sell_v2`, `set_creator`, `set_max_curve_depth`, `set_metaplex_creator`, `set_params`, `set_quote_control_admin`, `set_quote_control_mint_reserves`, `set_quote_control_reserves_admin`, `set_reserved_fee_recipients`, `set_virtual_quote_reserves`, `sweep_creator_fee`, `sweep_protocol_fee`, `sync_user_volume_accumulator`, `toggle_cashback_enabled`, `toggle_create_v2`, `toggle_mayhem_mode`, `update_buyback_config`, `update_creator_fee_config`, `update_global_authority`, `update_holder_reward_config` |
| pump | Partial | 5 | `buy_exact_quote_in_v3`, `buy_v3`, `create_v2`, `multi_hop_curve_swap`, `sell_v3` |
| pump | Unaccepted / unrecovered | 3 | `admin_update_token_incentives`, `claim_token_incentives`, `set_mayhem_virtual_params` |
| pump_amm | Bounded; perfection unproved | 37 | `admin_cto_pool`, `admin_update_token_incentives`, `boost_buy_and_burn`, `buy`, `buy_exact_quote_in`, `buy_exact_quote_in_v2`, `buy_v2`, `claim_cashback`, `claim_token_incentives`, `close_user_volume_accumulator`, `collect_coin_creator_fee`, `create_pool`, `deposit`, `disable`, `extend_account`, `init_boost`, `init_user_volume_accumulator`, `migrate_pool_coin_creator`, `multi_hop_swap`, `sell`, `sell_v2`, `set_boost_authority`, `set_coin_creator`, `set_reserved_fee_recipients`, `sweep_creator_fee`, `sweep_protocol_fee`, `sync_user_volume_accumulator`, `toggle_boost`, `toggle_cashback_enabled`, `toggle_mayhem_mode`, `transfer_creator_fees_to_pump`, `transfer_creator_fees_to_pump_v2`, `update_admin`, `update_buyback_config`, `update_creator_fee_config`, `update_fee_config`, `withdraw` |
| pump_amm | Unaccepted / unrecovered | 1 | `create_config` |
| pump_fees | Bounded; perfection unproved | 31 | `admin_cto_sharing_config`, `claim_social_fee_pda`, `claim_social_fee_pda_v2`, `crank_donation_fee_pda`, `create_donation_fee_pda`, `create_fee_sharing_config`, `create_social_fee_pda`, `extend_fee_config`, `get_fees`, `get_fees_with_quote_mint`, `initialize_buyback`, `initialize_fee_config`, `initialize_fee_program_global`, `revoke_fee_sharing_authority`, `set_authority`, `set_claim_rate_limit`, `set_disable_flags`, `set_exotic_flat_fees`, `set_social_claim_authority`, `sweep_buyback`, `transfer_fee_sharing_authority`, `update_admin`, `update_buyback_authority`, `update_buyback_claim_rate_limit`, `update_fee_config`, `update_fee_shares`, `update_fee_shares_v2`, `update_stable_fee_config`, `upsert_fee_tiers`, `upsert_stable_fee_tiers`, `withdraw` |
| mayhem | Bounded; perfection unproved | 24 | `initialize_global_params`, `update_global_params`, `update_admin`, `update_trader`, `update_max_sol_per_sweep`, `update_max_stable_per_sweep`, `reset_sol_deployed`, `reset_stable_deployed`, `reset_state`, `stop_trading`, `resume_trading`, `initialize_fee_recipient`, `extend_account`, `withdraw_admin`, `withdraw_quote_admin`, `sweep_fees`, `sweep_fees_admin`, `burn_tokens`, `sell`, `buy`, `sell_v2`, `buy_v2`, `buy_pump_swap`, `sell_pump_swap` |
| mayhem | Unaccepted / unrecovered | 1 | `initialize_mayhem_state` |

Exact local matches are individually listed in [raw-body-matches.md](raw-body-matches.md); every normalized match, original address, candidate name and correspondence is in [functions.tsv](functions.tsv). A stripped original does not supply authoritative source names, so no unverified name is presented as certain.

## Largest unresolved bodies

The five largest unresolved windows per build focus the next investigation. Empty candidate names are deliberately not replaced with guessed source names. All residuals, including smaller windows, are in [remaining-windows.md](remaining-windows.md).

| Build | Original address | Bytes | Classification |
| --- | ---: | ---: | --- |
| donation_relay | 436,696 | 18,568 | no_complete_body_match |
| donation_relay | 469,568 | 16,632 | no_complete_body_match |
| donation_relay | 402,000 | 15,496 | no_complete_body_match |
| donation_relay | 372,816 | 15,464 | no_complete_body_match |
| donation_relay | 204,856 | 14,824 | no_complete_body_match |
| donation_relay_research | 131,136 | 10,248 | no_complete_body_match |
| donation_relay_research | 70,200 | 6,272 | no_complete_body_match |
| donation_relay_research | 76,472 | 6,272 | no_complete_body_match |
| donation_relay_research | 97,096 | 5,696 | no_complete_body_match |
| donation_relay_research | 107,240 | 5,328 | no_complete_body_match |
| mayhem | 287,608 | 19,256 | opaque_unassessed |
| mayhem | 314,520 | 18,656 | opaque_unassessed |
| mayhem | 140,512 | 18,648 | no_complete_body_match |
| mayhem | 159,160 | 18,096 | no_complete_body_match |
| mayhem | 400,192 | 17,704 | opaque_unassessed |
| pump | 141,840 | 27,400 | no_complete_body_match |
| pump | 849,744 | 24,312 | no_complete_body_match |
| pump | 875,248 | 23,608 | no_complete_body_match |
| pump | 746,872 | 23,440 | no_complete_body_match |
| pump | 672,632 | 23,360 | no_complete_body_match |
| pump_amm | 700,376 | 17,368 | no_complete_body_match |
| pump_amm | 284,992 | 16,912 | no_complete_body_match |
| pump_amm | 632,488 | 15,624 | no_complete_body_match |
| pump_amm | 264,712 | 15,512 | no_complete_body_match |
| pump_amm | 785,040 | 14,120 | no_complete_body_match |
| pump_fees | 502,096 | 16,880 | no_complete_body_match |
| pump_fees | 484,816 | 16,112 | no_complete_body_match |
| pump_fees | 147,944 | 15,976 | no_complete_body_match |
| pump_fees | 163,920 | 13,800 | no_complete_body_match |
| pump_fees | 177,720 | 12,384 | no_complete_body_match |
| pump_fees_research | 502,096 | 16,880 | no_complete_body_match |
| pump_fees_research | 484,816 | 16,112 | no_complete_body_match |
| pump_fees_research | 147,944 | 15,976 | no_complete_body_match |
| pump_fees_research | 163,920 | 13,800 | no_complete_body_match |
| pump_fees_research | 177,720 | 12,384 | no_complete_body_match |

## Remaining acceptance gates

1. **Behavior:** finish partial/unaccepted public handlers and known discrepancies. Pump `sell_v2` remains a bounded implementation with a known transfer-fee discrepancy. Mayhem field roles, initialization and diagnostic contracts remain unresolved. Existing stopped lanes remain stopped.
2. **Complete bodies:** recover the ten Relay donation/settlement/worker windows and 58 Fees residuals; complete Pump/AMM reconstruction and attribute Mayhem opaque windows. Small helper matches alone do not close callers.
3. **Identity:** establish referenced data, call targets, duplicate attribution, indirect calls, layout, relocations, full ELF equality and allocation-padding accounting for each exact proposed build.
4. **Build provenance:** retain source hashes, dependency/toolchain inputs and reproducible recipes. A synthetic exact recipe does not establish the historical recipe.
5. **Selection:** research candidates require explicit selected-source integration, rebuilt artifacts, bound validation and guard transitions. Current research gains do not update selected checkpoints.

The next practical work is targeted Relay value/lifetime recovery and Fees caller/ownership recovery, with regression checks against the retained frontier. Avoid repeating the documented rejected source/compiler variants. Pump/AMM and Mayhem remain substantial independent workstreams. See [the prioritized work list](../../docs/REMAINING-WORK.md). No reliable total effort percentage or ETA follows from these counts.

## Evidence and validation

This report derives from the full window inventory, current call ledger and immutable selected-handler audit. It does not rerun runtime cases or claim new execution coverage. Current Fees retains 17,331 suite comparisons, 1,542 exact outcome/log/compute comparisons and 24 exotic-growth boundary cases, plus 32 signed optional-account and 20 social-claim user-ID cases, plus 8 extension program-log cases and 30 crank mint cases. Relay retains 536 records / 534 unique fixtures per tested recipe. Their exclusions and observation scopes remain those of their owning packets.

Verify inventory/binary bindings with `python3 -B repro/reconstruction-status-2026-10-26/refresh.py --check`, then this report with `python3 -B repro/reconstruction-status-2026-10-26/review.py --check`. The [current analysis](../../docs/RECONSTRUCTION-STATUS.md) links the recovery studies and dependency evidence.

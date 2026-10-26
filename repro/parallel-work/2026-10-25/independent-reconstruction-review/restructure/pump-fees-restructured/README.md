# pump_fees — restructured source tree (structural-fidelity reference, COMPLETE)

_2026-10-26. A COMPILING (v1.44, `--offline --locked`) snapshot of the pump_fees reconstruction fully
reorganized into the recovered original module tree (see `../../source-maps/` and `../RESTRUCTURE-MAP.md`).
A **reference artifact**, not active program source: it is not byte-closing, and the reconciliation
policy reverts restructured active source from `main`, so it lives here under `repro/`._

## Status: all mapped moves materialized, tree compiles
Every recovered module file is now present (`TREE.txt`):
- `instructions/withdraw.rs`, `instructions/buyback/mod.rs`, `instructions/common/mod.rs`
- `instructions/fee_sharing/{create_social_fee_pda, claim_social_fee_pda, create_donation_fee_pda,
  admin_cto_sharing_config, create_fee_sharing_config, update_fee_shares, update_fee_shares_v2}.rs`
- `instructions/admin/{initialize_fee_config, initialize_fee_program_global, update_fee_config,
  upsert_fee_tiers, update_fee_program_global}.rs`

Two kinds of moves were applied, per the validated mechanism:
- **Clean (body preserved):** the already-delegated handlers (fee_sharing group, buyback, withdraw) —
  their module files were relocated/split to the recovered paths, bodies unchanged.
- **Structural-only (body regresses):** the inline admin handlers were delegated into `instructions/admin/*`
  (as the `set_authority` experiment showed, newly delegating an inline handler perturbs its body codegen).
  Shared helpers (`validate_fees`, `validate_tiers`, `upsert_tiers`, `select_fee_tier`) moved to
  `common/mod.rs` as `pub(crate)`.

`contexts.rs` / `types.rs` / `state.rs` / `pump_global.rs` / `sharing.rs` keep the account contexts,
events and shared types (imported by the handler modules), matching the reconstruction's layering.

## Oracle result (`verify_source_map.py pump_fees <build> original-source-maps.json`)
`2/30` Location sites now match exactly (both in `lib.rs`), up from `0` before the restructure; and
`admin_cto_sharing_config.rs`, `claim_social_fee_pda.rs`, `create_fee_sharing_config.rs` moved
MISSING → PARTIAL (recovered path present; `(line,col)` not yet positioned). Files that remain MISSING
(e.g. `update_fee_config.rs`, `upsert_fee_tiers.rs`, `common/mod.rs`) emit no `Location` at the recovered
path because the reconstruction routes those checks through `common` helpers rather than inline — a
genuine structural difference from the original.

## What would turn PARTIAL → MATCH (needs the authentic source)
Per-file line positioning so each `Location` lands on the original `(line, col)`, and matching where each
check originates (inline vs helper). Both require the original source layout; the body prologue/scheduling
residuals remain regardless. This tree is the scaffold to drop that source into if it surfaces.

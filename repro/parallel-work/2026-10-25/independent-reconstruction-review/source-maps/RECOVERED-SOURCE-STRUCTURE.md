# Recovered original source structure + panic-Location source maps (all 4 contracts)

_2026-10-25. Extracted read-only from `evidence/original/<prog>/deployed.so` by decoding every
`core::panic::Location` static (`[file_offset<<32 : u64][len : u64][line : u32][col : u32]`, with an
`R_SBF_64_RELATIVE` reloc at the record). This recovers, for each contract, the ORIGINAL source FILE
TREE and the exact `(line, column)` of every Location-bearing statement — a blueprint for restructuring
the reconstruction to mirror the original (the prerequisite for closing the panic-Location portion of
the byte gap), and a verification oracle. Data: `original-source-maps.json` (+ `-summary.json`).
Tools: `../byte-identicality-tools/extract_source_map.py`, `verify_source_map.py`._

## Why this matters
The reconstruction FLATTENED each program (mostly into `lib.rs`). Byte-identity requires the original's
file layout because panic `Location` records embed the source path + line + column, and `.text`
addressing depends on item ordering. These maps are the recovered target. (They do not by themselves
close byte-identity — see `../BYTE-IDENTICALITY-DEEP-DIVE.md` for the full bound — but they are the
richest recoverable guide, independent of whether the authentic source resurfaces.)

## Recovered file trees (project source only; Location-site count · line range)

### pump — 15 files, 54 sites
- `src/lib.rs` (12 · 83–2664), `src/create_v2.rs` (4 · 27–488), `src/sell.rs` (2 · 76–77)
- `src/token_incentives/volume_accumulator.rs` (21 · 8–436)
- `src/creator/{distribute_creator_fee_v2.rs, distribute_creator_fees.rs, distribute_fee_to_holders.rs, set_creator.rs, set_metaplex_creator.rs}`
- `src/admin_set_idl_authority.rs`, `src/extend_account.rs`, `src/migrate.rs`, `src/migrate_v2.rs`, `src/multi_hop_curve_swap.rs`, `src/quote_control/state.rs`

### pump_amm — 10 files, 41 sites
- `src/lib.rs` (3), `src/instructions/swap/{buy.rs, sell.rs, multi_hop_swap.rs (12 · 233–815)}`
- `src/state/{volume_accumulator.rs (17 · 8–398), global_config.rs}`
- `src/instructions/coin_creator/set_coin_creator.rs`, `src/instructions/extend_account.rs`, `src/utils/{math.rs, token.rs}`

### pump_fees — 11 files, 30 sites
- `src/lib.rs` (3 · 27–38), `src/state.rs` (10 · 50–451), `src/common/mod.rs` (4 · 21–33)
- `src/instructions/admin/{update_fee_config.rs, upsert_fee_tiers.rs}`
- `src/instructions/fee_sharing/{create_fee_sharing_config.rs, create_social_fee_pda.rs, admin_cto_sharing_config.rs, claim_social_fee_pda.rs, update_fee_shares.rs, update_fee_shares_v2.rs}`
- (the deep-dive also recovered admin files without Location sites: `initialize_fee_config.rs`,
  `initialize_fee_program_global.rs`, `update_fee_program_global.rs`, `update_buyback_authority.rs`,
  `buyback/mod.rs`, `withdraw.rs`, and a separate `pump-fees-math` crate)

### mayhem — crate is `mayhem-program` — 9 files, 64 sites
- `src/lib.rs` (2), `src/state.rs` (20 · 12–578)
- `src/instructions/{admin.rs, burn.rs (4), extend_account.rs, fee_recipients.rs (22 · 13–378), pump_amm_interface.rs (4), pump_interface.rs (5), pump_interface_v2.rs (4)}`

## Using the oracle
`verify_source_map.py <program> <candidate.so> original-source-maps.json` reports, per original file,
whether the candidate reproduces the same `(line, col)` set (MATCH / PARTIAL / MISSING) — a progress
meter for restructuring. On the current flat reconstruction it reads 0/11 files for pump_fees (expected:
the module tree isn't there yet); the per-file target lines above are what each reconstructed file must
hit.

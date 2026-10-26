# pump_fees restructure map — reconstruction → recovered original module tree

_2026-10-26. The reconstruction flattened pump_fees into `lib.rs` + a few ad-hoc modules
(`social.rs`, `sharing*.rs`, `donation.rs`, `buyback.rs`, `withdrawal.rs`). The original (recovered
from the deployed binary's panic-`Location` paths — see `../source-maps/`) used the module tree below.
This maps every `#[program]` handler to the original file its body belonged in, so the reconstruction
can be reorganized to mirror the original. It is a **structural-fidelity reference**: it is NOT
byte-closing (bodies carry residual prologue/scheduling diffs) and would not survive as active `main`
source (the reconciliation policy reverts non-byte-equal active source), so it lives under `repro/`._

## Mechanism (validated)
Handlers the reconstruction **already delegates** (lib.rs → a module fn) can be moved to their recovered
path by relocating the module file + re-pointing the delegation — the body codegen is preserved and the
panic-`Location` path corrects (demonstrated on `create_social`). Handlers that are **inline** in the
`#[program]` body regress if newly delegated (demonstrated on `set_authority`), so for those the move is
structural-only. (Full byte-match additionally needs each `Location` to land on the original line — a
per-file positioning step not done here.)

## Map (handler → recovered file ← current location)

### instructions/fee_sharing/
| handler(s) | recovered file | current body |
|---|---|---|
| create_social_fee_pda | create_social_fee_pda.rs | social::create_social (delegated) |
| claim_social_fee_pda, claim_social_fee_pda_v2 | claim_social_fee_pda.rs | social::claim, social::claim_v2 (delegated) |
| create_fee_sharing_config | create_fee_sharing_config.rs | sharing::create_sharing (delegated; file already exists) |
| admin_cto_sharing_config | admin_cto_sharing_config.rs | sharing_admin::admin_cto_sharing_config (delegated) |
| update_fee_shares | update_fee_shares.rs | sharing_update::update_fee_shares (delegated) |
| update_fee_shares_v2 | update_fee_shares_v2.rs | sharing_update::update_fee_shares_v2 (delegated) |
| create_donation_fee_pda, crank_donation_fee_pda | create_donation_fee_pda.rs | donation::create, donation::crank (delegated) |

### instructions/admin/
| handler(s) | recovered file | current body |
|---|---|---|
| initialize_fee_config | initialize_fee_config.rs | inline in lib.rs |
| initialize_fee_program_global | initialize_fee_program_global.rs | inline in lib.rs |
| update_fee_config, update_stable_fee_config | update_fee_config.rs | inline in lib.rs |
| upsert_fee_tiers, upsert_stable_fee_tiers | upsert_fee_tiers.rs | inline in lib.rs (+ common::upsert_tiers) |
| set_authority, set_claim_rate_limit, set_disable_flags, set_social_claim_authority, update_admin, set_exotic_flat_fees | update_fee_program_global.rs | inline in lib.rs (set_authority Location path confirmed = this file, 70 chars) |
| update_buyback_authority, update_buyback_claim_rate_limit | update_buyback_authority.rs | buyback::* (delegated) |

### instructions/buyback/
| handler(s) | recovered file | current body |
|---|---|---|
| initialize_buyback, sweep_buyback | buyback/mod.rs | buyback::* (delegated; rename buyback.rs) |

### other
| handler(s) / items | recovered file | current body |
|---|---|---|
| withdraw | instructions/withdraw.rs | withdrawal::execute (delegated; rename withdrawal.rs) |
| validate_fees, validate_tiers, select_fee_tier, upsert_tiers | common/mod.rs | helpers in lib.rs |
| account struct impls (FeeConfig, FeeProgramGlobal, SocialFeePda, …) | state.rs | state.rs (already) |
| get_fees, get_fees_with_quote_mint, extend_fee_config, revoke_/transfer_fee_sharing_authority | lib.rs | inline in lib.rs (no distinct recovered file with Location sites) |

## Clean vs. structural-only moves
- **Clean (preserve body, fix path):** all the "delegated" rows above — fee_sharing group, buyback, withdraw. Relocate the module file + re-point the delegation.
- **Structural-only (will perturb body codegen):** the admin "inline" rows — moving them to `instructions/admin/*.rs` improves file-tree fidelity but regresses their byte-match, as proven. Do these only for structural organization, not byte-closing.

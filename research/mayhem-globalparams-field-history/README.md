# Mayhem `GlobalParams`: the five unknown field roles: an on-chain evidence package

**Question.** `docs/COMPLETION.md` and `repro/layered-passes/pass-01/followup-results/mayhem-field-crosswalk/REPORT.md` list five `GlobalParams` fields of the Mayhem program (`MAyhSmzXzV1pTf7LsNkrNwkWKTo4ougAJ1PPg47MD4e`) whose roles remain unknown: `field_0`, `field_1`, `field_3`, `field_6`, `field_10`. The repo's own static review (`repro/mayhem/global-params-remaining-field-review/REPORT.md`) established only the transport contract for them (setter, event, reset and codec behavior) and concluded that no semantic name can be recovered from the recovered sources alone. This package supplies the missing half: **the complete on-chain configuration history of the account**, from which each field's value trajectory, change pattern and value class are proven, and its role is resolved as far as that evidence honestly goes.

**Scope discipline.** Claims below are labeled **proven** (directly in a capture), **strongly indicated** (the evidence admits no plausible rival we could construct), or **still open**. Nothing is renamed on a guess. Where a role stays open, the capture that would close it is named.

## Subjects

| Item | Value |
|---|---|
| Program | `MAyhSmzXzV1pTf7LsNkrNwkWKTo4ougAJ1PPg47MD4e` |
| `GlobalParams` account (PDA, seeds `["global-params"]`, bump 253) | `13ec7XdrjF3h3YcqBTFDSReRcUFwbCnJaAQspM4j6DDJ` |
| Serialized size | 254 bytes (account extended on-chain to 318 bytes; tail zero) |
| Account discriminator | `79c1f857c3384c0b` = `sha256("account:GlobalParams")[:8]` |
| Admin (held by a Squads vault, see Method) | `FFWtrEQ4B4PKQoVuHYzZq8FabGkVatYzDpEVHsK5rrhF` |
| Trader | `Gygj9QQby4j2jryqyqBHvLP7ctv2SaANgh4sCb69BUpA` |
| Event authority PDA | `8FoNgzmjuSmiy86EPCWxvv1q7oJSu2WGA7wPymwki2LJ` |

The five studied fields, per the corrected crosswalk (account byte offsets):

| Field | Bytes | Width | Storage class (recovered source) |
|---|---|---|---|
| `field_0` | [8, 12) | u32 | `reset_prefix[0..4]`, zeroed by `reset_state` |
| `field_1` | [12, 16) | u32 | `reset_prefix[4..8]`, zeroed by `reset_state` |
| `field_3` | [24, 32) | u64 | `reset_prefix[16..24]`, zeroed by `reset_state` |
| `field_6` | [137, 138) | u8 | `reset_middle[0]`, zeroed by `reset_state` |
| `field_10` | [166, 174) | u64 | dedicated field, **preserved** by `reset_state` |

Transport (from the recovered source, `programs/mayhem/src/lib.rs`): `update_global_params` takes one `Option` per field (all-`None` is legal), writes each `Some`, increments `version` by exactly 1 per call, and emits `GlobalParamsUpdateEvent` (discriminator `63a75c9898e32629`) carrying the **post-update values of all fields** via an event-CPI carrier instruction (carrier discriminator `e445a52e51cb9a1d`, accounts = `[event_authority]`). `initialize_global_params` takes **no arguments** (8-byte instruction, discriminator `0d127fea3b28ccda`).

## Method: how the history was located

The account is written by every Mayhem trade, so its signature history is unusable directly (measured 2026-10-26: ~12.9 signatures/second; 20,000 signatures span ~26 minutes). Instead, the writers were enumerated from the signer side:

1. `version` in the live account is **10**, and `version` increments only in `update_global_params`. Therefore **exactly ten** successful update calls have ever occurred (plus the initializer). The target set is finite and small.
2. The current admin's own signature history (2,000 signatures, `evidence/sigs_admin_p*.json`) was scanned transaction-by-transaction, top-level and inner instructions: **zero** Mayhem invocations. The admin never signs directly.
3. Program deploys/upgrades are executed through a Squads multisig (`8EujzwPFNhZ5m4Kpa2XtrumNgwCbhgWwny9YWLCKA5at`, threshold 3 of 4, fee payer/executor `6W6qsDbocrEs3vjri5Di15bf9PLRYhfxekPk25MhVHWz`). The multisig account was captured and its four members read from the account bytes (all permission mask 7): `4tbEe4AquJWyMh7f7yE5poFChhsuPbeGh7EHVQCvq2N8`, `5sFJMw5dC59oKGKA9LgeYQCSmYS6rLeCegxMkcM2Pwby`, `6W6qsDbocrEs3vjri5Di15bf9PLRYhfxekPk25MhVHWz`, `7zc8kzBr5wbsQKxYYv9uCMgfcW5zjxLEopvmuf3ig6iw`. The `GlobalParams` admin `FFWtrEQ4…` is the multisig's vault: in every located configuration transaction it appears as the admin signer inside a Squads `vault_execute` CPI.
4. The **complete** signature histories of all four members (709 + 3,042 + 1,550 + 1,227 = **6,528 transactions**) were fetched and scanned for Mayhem involvement (top-level or inner). Eight configuration transactions were found this way.
5. Independently, all 65 `VaultTransaction` accounts of the multisig (indexes 1–65, PDA seeds `["multisig", multisig, "transaction", index_le]`, scheme calibrated against the known index-59 account) were swept for embedded Mayhem instructions (`evidence/squads_tx_sweep.json`, captures `evidence/capture_squads_tx_*.json`). Thirteen reference Mayhem; their instruction mixes are in `evidence/squads_tx_instruction_scan.json`. The two methods agree exactly, and together they account for **all ten** updates: Squads indexes 23 (genesis + v1), 28 (v2), 32 (v3), 33 (v4), 37 (v5), 38 (v6), 50 (v7), 51 (v8), 58 (v9), 59 (v10).
6. Every located transaction was captured in full (`getTransaction`, finalized) with its retrieval metadata inside the capture file, and decoded against the recovered discriminators and the event layout. Decoded output: `evidence/analysis_timeseries.json` (regenerable with the study's `decode_config_txs.py`).

No `reset_state`, `reset_sol_deployed` or `reset_stable_deployed` instruction appears in any located operations transaction or in any of the multisig's 65 stored transactions that reference Mayhem.

## Findings: the complete configuration history

Post-update state after each version (from the emitted `GlobalParamsUpdateEvent`; `—` = field not present in that era's event schema). Native amounts are in lamports (20 SOL = 20,000,000,000).

| Version | Date (UTC) | Squads idx / executor | f0 | f1 | f2 (known: per-trade cap) | **f3** | f4 (overall) | f5 (per-coin) | **f6** | f7 (trade interval) | f8 (SOL wd interval) | f9 (min reserves) | **f10** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v1 | 2025-11-08 18:29 | 23 / member …6W6qsD | 8000 | 10 | 20e9 | **20e9** | 200e9 | 30e9 | **24** | 0 | 3600 | 200e6 | **86400** |
| v2 | 2025-11-10 16:18 | 28 / …6W6qsD | 8000 | 100 | 20e9 | **20e9** | 200e9 | 200e9 | **24** | 0 | 3600 | 200e6 | **86400** |
| v3 | 2025-11-12 21:49 | 32 / …7zc8kz | 8000 | 100 | 20e9 | **20e9** | 6e12 | 6e12 | **24** | 0 | 3600 | 200e6 | **86400** |
| v4 | 2025-11-13 15:17 | 33 / …6W6qsD | 8000 | 100 | 20e9 | **20e9** | 6e12 | 6e12 | **24** | 0 | 3600 | 50e6 | **86400** |
| v5 | 2025-11-19 12:17 | 37 / …4tbEe4 | 8000 | 50 | 20e9 | **20e9** | 6e12 | 6e12 | **24** | 0 | 3600 | 50e6 | **86400** |
| v6 | 2025-12-04 19:16 | 38 / …7zc8kz | 8000 | 0 | 20e9 | **20e9** | 6e12 | 6e12 | **24** | 0 | 3600 | 50e6 | **86400** |
| v7 | 2026-04-29 21:29 | 50 / …5sFJMw | 8000 | 0 | 20e9 | **20e9** | 6e12 | 6e12 | **24** | 0 | 3600 | 50e6 | **86280** |
| v8 | 2026-05-02 20:09 | 51 / …5sFJMw | 8000 | 0 | 20e9 | **20e9** | 12e12 | 12e12 | **24** | 0 | 3600 | 50e6 | **86280** |
| v9 | 2026-06-15 14:09 | 58 / …5sFJMw | 8000 | 0 | 20e9 | **20e9** | 50e12 | 50e12 | **24** | 0 | 3600 | 50e6 | **86280** |
| v10 | 2026-07-15 16:04 | 59 / …6W6qsD | 8000 | 0 | 20e9 | **20e9** | 50e12 | 50e12 | **24** | 0 | 3600 | 50e6 | **86280** |

Change pattern (**proven** from the decoded instruction arguments, not just the events): v1–v6 are **full rewrites**: every field is `Some` in the arguments, including fields whose value does not change. v7 is a **single-field** update (`field_10` only). v8 and v9 set `field_4`+`field_5` only. v10 sets the then-new `field_11`–`field_15` only (see Schema archaeology).

Current state (captured twice, slots 461,857,236 and 461,863,638, 2026-10-26/27; `evidence/capture_globalparams_current*.json`, whose base64 `data` payload carries the raw account bytes): identical to the v10 event snapshot in every configuration field, `version = 10`; only the activity counters (`sol_deployed`, `stable_deployed`) moved between captures. The five studied fields do not move with trading.

### Per-field findings

**`field_0` (u32): value and constancy proven; role still open.**
Value **8000** at every version, v1 through v10, with no exception. It is re-written as `Some(8000)` in all six full rewrites and left untouched by all four surgical updates: operations treat it as a fixed constant of the configuration, never as a tuning knob. That behavior excludes a balance, counter or timestamp. The value is compatible with a basis-point rate (8000 = 80.00%), a fixed-point factor, or a count, and no on-chain observation distinguishes those. A name would be a guess; the field stays open. What would close it: a consumer: the recovered trade handlers read `reset_prefix` fields 2/4/5 by offset, and the repo's review found no identified read of [0..8); a differential case that perturbs [8,12) and observes a behavior change, or the off-chain agent's config schema, would settle it.

**`field_1` (u32): trajectory proven; role still open, with a documented lifecycle.**
**10 → 100 → 50 → 0**: set to 10 at genesis (v1), raised to 100 in v2, held through v3–v4, halved to 50 in v5, and set to **0 in v6 (2025-12-04)**, where it has remained. The arc (tuned in round steps during the first month of operation, then switched off and never re-enabled) is the signature of an auxiliary/experimental parameter rather than a structural constant. In this configuration's own conventions 0 is the "inactive" value (the crosswalk documents exactly that for `field_2`). The values are compatible with a small count or a basis-point rate (10/100/50 bps = 0.10%/1.00%/0.50%). Evidence does not distinguish count from rate; the field stays open, but any proposed role must now explain a parameter that was live for the first month and has been disabled since.

**`field_3` (u64): value, unit family and lockstep proven; role strongly indicated, exact semantics open.**
**20,000,000,000 (20 SOL) at every version**, exactly equal to `field_2` (the proven native per-trade quote budget cap) at all ten snapshots, and re-written in lockstep with it in every full rewrite, even in updates whose purpose was to change other fields (v3: overall/per-coin limits ×30; v5: `field_1`, `field_9`). It is therefore proven to be a **native-quote-denominated quantity administered as part of the native limit family** (fields 2–5), not an independent counter. The caution from the repo applies with full force, and this history is its illustration: `field_4` and `field_5` also held equal values from v3 onward while their proven roles differ (overall vs per-coin deployment limit), so equality with `field_2` does **not** prove `field_3` shares `field_2`'s role. Within the family layout (per-trade cap, `field_3`, overall limit, per-coin limit) the indicated reading is a second native quote limit paired with the per-trade cap; which check consumes it is not determinable from configuration history alone. What would close it: a differential trade case at the boundary of a candidate check, with `field_3` perturbed independently: the account history proves ops never perturbed it independently on mainnet.

**`field_6` (u8): value and constancy proven; boolean/enum readings excluded in production; role still open.**
Value **24** at every version, never changed, re-written as `Some(24)` in all six full rewrites. Production use therefore excludes the "unrestricted byte that might be a boolean" ambiguity in one direction: whatever it is, it is **not** operated as a flag (a flag would not sit at 24 for the account's entire life). As a bare value, 24 is compatible with a small count or a duration in hours; its neighbours invite the hours reading (`field_10` directly below it in the preserved block is a near-day seconds value, and 24 h = 86,400 s), but with a single observed value and zero variation, that remains a hypothesis. The field stays open. What would close it: any mainnet change (none in ten versions), or a differential case perturbing [137] alone.

**`field_10` (u64): duration-in-seconds strongly indicated; exact process open.**
**86,400** from genesis through v6; changed to **86,280** in v7 (2026-04-29), and the v6→v7 transaction sets `field_10` **alone**, the only single-field update of the 11-field era: a deliberate −120 s adjustment of exactly this value. 86,400 is one day in seconds; 86,280 is 23 h 58 m, one day minus two minutes. A quantity that launches at exactly 86,400 and is later shaved by 120 is a **duration denominated in seconds, held just under one day**: the same value class and storage class as the two statically attributed withdrawal intervals (`field_8` = 3600, `field_15` = 3600): like them, `field_10` sits in the reset-preserved configuration block (it is the only studied field `reset_state` does not zero). Confidence: the *class* (seconds duration ≈ 1 day) is strongly indicated; *which* process it paces (a window, a period, a cooldown) is not determinable from configuration evidence and is left open rather than named.

### Schema archaeology (a by-product finding)

* Through v9 (2026-06-15), `update_global_params` carries **11** option arguments and `GlobalParamsUpdateEvent` serializes to **89 bytes** (fields 0–10).
* At v10 (2026-07-15) both grow: **16** arguments, **129-byte** event. v10 is the first update that sets `field_11`–`field_15` (the non-native family: 1,600,000,000 / 4,000,000,000,000 / 4,000,000,000,000 / 4,000,000 / 3600), and it also sets `max_stable_per_sweep` = 160,000,000,000 via its dedicated instruction in the same Squads batch.
* So the non-native parameter family became configurable only in July 2026; any account-state fixture captured before then cannot speak to fields 11–15, and pre-extension event decoders must not expect them.

### Neighbouring operations (context, all captured)

* 2025-11-11 (Squads 29): `update_trader` → `Gygj9QQb…` (still the trader today) and `update_max_sol_per_sweep` = 500,000,000,000.
* 2025-11-14 (Squads 34): seven `initialize_fee_recipient` calls.
* 2026-04-26 (Squads 43): `update_max_sol_per_sweep` = 2,000,000,000,000 (the current value).
* Full transaction list with slots, signatures and decodes: `evidence/analysis_timeseries.json`.

## How to verify

```
python3 verify.py            # manifest hashes + re-decode of every capture + version-chain continuity
python3 verify.py --live     # additionally re-fetches the account and compares the studied fields
```

Every capture file carries its own retrieval metadata (endpoint, request, slot, UTC retrieval time) inside the file. `manifest.json` lists SHA-256 for every file in this package except itself. Raw account bytes are the base64 `data` payload in `evidence/capture_globalparams_current.json` / `evidence/capture_globalparams_current2.json`.

## What this does not claim

* No field is renamed. The five placeholder names stand; this package attaches a proven value history, a change pattern, and (for `field_3` and `field_10`) an evidence-bounded class attribution.
* The event snapshots are post-update states by construction of the event; the instruction arguments in the same captures independently show which fields each call set, and the two agree everywhere.
* Signature-history scans are only as complete as the public RPC's index: the four members' histories were paginated to their oldest signatures (counts above), and the Squads stored-transaction sweep is an independent second channel that produced the identical set of configuration transactions.

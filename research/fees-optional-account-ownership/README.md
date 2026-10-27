# Optional AMM event-authority ownership recovery

One source-type change recovers **two complete original Fees windows**, with no
lost body matches: **370 unique structural pairs, 149 original windows in
ambiguous groups, 66 unmatched**. This is a research candidate, not a selected
checkpoint or whole-program identity claim.

| Original address | Bytes | Recovered body | Equality |
| --- | ---: | --- | --- |
| 10,232 | 528 | Optional owned account parser | Complete normalized body; both direct local callee bodies match |
| 41,560 | 160 | `Option<AccountInfo>` cleanup | Exact raw local bytes; no calls |

The parser for `CreateFeeSharingConfig` calls both bodies in the original and
candidate. Its optional `pump_amm_event_authority` field changes from
`Option<UncheckedAccount<'info>>` to `Option<AccountInfo<'info>>`. The seed
constraint and all other source tokens are unchanged. This causes Rust/Anchor
to generate the observed optional parser and ownership cleanup; no artificial
uncalled helper or emitted machine-code patch is used.

The enclosing account parser still differs: 11,016 original bytes versus 10,200
candidate bytes. Its recovery remains open. A local helper's exact bytes do not
establish all referenced data, transitive semantics, source authenticity or a
complete instruction handler.

## Build and regression evidence

The parent is `research/fees-exotic-growth-precedence`. Its candidate is reused
as the control and all 35 source inputs are hash-checked. The new Linux v1.44
root compilation is retained with source hashes, compiler hash, exact command,
log, symbols and stripped ELF. Only the one context source differs.

- Candidate: 861,456 bytes, SHA-256 `1cf0911cfc8402ca43c0842bdbfc22b1012dd8d306b1845683d248b112efc5e6`.
- 17,331 fresh comparisons across the existing 18 suites pass.
- 1,542 fresh optional-byte/pool/cap comparisons pass with exact outcome, logs and compute.
- All 24 exotic-growth precedence cases pass.
- 32 new signed create-sharing cases cross pool presence, incorrect optional
  account keys and prefixes ending at each optional account. They compare error,
  state, lamports, events and inner instructions. Logs are retained but are not
  an equality claim in this matrix; neither is compute.

The full 585-window partition is **117 raw local / 402 normalized-only / 66
unmatched**. Current incoming-call refinement yields 433 attributed pairs,
including 63 additional duplicate-body pairs; 86 duplicates remain unattributed.
The unresolved original body spans total 319,616 of 799,648 bytes (40.0%).

Run `python3 -B research/fees-optional-account-ownership/verify.py` to recompute
body comparisons, source/build hashes, direct-call closure and receipt checks.
This offline verifier does not rebuild or rerun the programs. Runtime cases can
be rerun using the retained driver and the scripts named by `parents.json`.

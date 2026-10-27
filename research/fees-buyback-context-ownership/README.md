# Buyback initializer context ownership

Correcting the initializer context recovers **three complete normalized
original windows**, with no lost normalized or raw coverage. Fees advances from
376 unique structural pairs / 62 unmatched to **379 pairs / 59 unmatched**.

| Original address | Bytes | Recovered component | Direct callee bodies |
| --- | ---: | --- | --- |
| 351,128 | 7,184 | `InitializeBuyback::try_accounts` | 57/58 match; one initialization closure remains unmatched |
| 364,568 | 5,512 | Generated initialization closure | All 22 match |
| 370,080 | 560 | `InitializeBuyback::exit` | All 7 match |

The unmatched closure called at parser offset 2,992 is original window 358,312
(6,256 bytes). It is not included in the newly recovered 7,184-byte window.
The parser's normalized match does not establish full transitive behavior.

## Source change and intermediate control

Only the `InitializeBuyback` fields in the research `buyback.rs` change:

- `buyback_vault` becomes `Box<Account<BuybackVault>>`.
- `buyback_vault_ata` becomes `Box<InterfaceAccount<TokenAccount>>`.
- `event_authority` and `program` become owned `AccountInfo` fields.

The account attributes, field names, other contexts and handler code remain
unchanged. A retained box-only variant recovers the 5,512-byte closure but leaves
the parser and exit unmatched. Adding the two owned account fields recovers
those bodies as well. No helper is inserted solely to match an unused body.

The exit reader also checks its actual owner bytes and both error field strings
(`buyback_vault`, `buyback_vault_ata`) against the original. The current tier-copy
and common-helper source-location contracts remain equal after rebuilding.
Other data and indirect/transitive contracts remain open.

## Build and bounded regression

Parent: `research/fees-slice-origin-integration`, explicitly reused as the
control. Both variants have freshly compiled Linux v1.44 root crates and exact
36-file source maps. The corrected candidate is 861,000 bytes, SHA-256
`b3951968d3c2f4a1ba8adb9a09e620d657e61e136f928ae68974fcfc08c2b533`.

Fresh validation passes 17,331 comparisons across 18 suites, including the
buyback suite; 1,542 exact outcome/log/compute cases; and the retained 24 growth,
32 optional-account, 20 user-ID, 8 extension-log and 30 crank-mint cases. Each
harness retains its stated limits. The intermediate box-only variant is kept
as structural evidence, not newly runtime-accepted. Allocator exhaustion and
exhaustive behavior are not claimed.

The full partition is **118 raw-local / 408 normalized-only / 59 unmatched**.
The unmatched windows span 304,760 / 799,648 original text bytes (38.1%). Current
call refinement yields 440 correspondences (379 unique plus 61 additional
attributed duplicates), with 86 duplicates still unattributed. Its 21
unmatched-body call edges include the newly exposed closure edge; this does
not represent lost body coverage. Whole-file equality remains false and no
selected checkpoint changes.

Run `python3 -B research/fees-buyback-context-ownership/verify.py` to recompute
source/build bindings, full-body and callee comparisons, retained location
contracts and receipt integrity. It does not build or execute target programs.

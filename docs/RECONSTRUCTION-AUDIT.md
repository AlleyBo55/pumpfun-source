# Reconstruction audit — 26 October 2026

For the latest research frontier and all current handler/window classifications, see the
[comprehensive review](../repro/reconstruction-status-2026-10-26/review.md).
This page retains the immutable selected-checkpoint audit; its older research
counts are historical.

Audited repository snapshot: `1463bd22fb7811825c5e7acf1cb963eb39ab68d9`, including
the PR #71–#94 review batch. This report separates selected artifacts from newer
research. It does not promote a source tree or change an acceptance decision.

The [current review](RECONSTRUCTION-STATUS.md) and [refreshed full inventory](../repro/reconstruction-status-2026-10-26/README.md)
supersede the research frontier below: **Relay 482/492, 10 unmatched; Fees 368
unique pairs, 68 unmatched**. Selected checkpoint tables below retain their dated
snapshot. Subsequent gains are tracked in the [progress log](BYTE-IDENTITY-PROGRESS.md).

**No core program, and no selected Relay program, is a complete byte-identical
reconstruction. No public handler has an exhaustive semantic-equivalence proof.**
There is substantial verified progress below those two thresholds.

The [generated audit](../repro/reconstruction-audit-2026-10-26/README.md) binds its
inputs by SHA-256 and rechecks the actual binary bytes. It includes:

- [All 150 public-handler dispositions](../repro/reconstruction-audit-2026-10-26/handlers.md), rebound to current selected candidates.
- [Every exact local body-byte match](../repro/reconstruction-audit-2026-10-26/raw-body-matches.md), with original addresses and candidate symbol labels.
- [All 4,415 function-window rows](../repro/reconstruction-audit-2026-10-26/functions.tsv): 3,338 selected rows, 585 newer Fees rows and 492 newer Relay rows.
- [Machine-readable counts, binary comparisons and input hashes](../repro/reconstruction-audit-2026-10-26/audit.json).

## What “recreated” means

| Evidence | What it establishes | What remains unproved |
| --- | --- | --- |
| Whole raw file equals captured file | Every captured byte is reproduced by that output | Historical source/recipe uniqueness and security can still be unknown |
| Raw ELF equals the meaningful captured ELF prefix | Executable file equality before an allocation tail | Equality to the full captured account allocation without separately generating the tail |
| Complete local function-window bytes equal | Every byte within that inferred window equals a candidate window | Original function identity/boundaries; destinations of position-relative calls; referenced data; all behavior |
| Normalized body match | Full window matches under the owning study’s declared call/relocation masks | Masked addresses, transitive calls/data, indirect calls, semantics and whole-file identity |
| Bounded handler validation | Specified original/candidate cases agree on the compared effects | Untested inputs, modes, validation precedence, logs/compute omitted by a comparator and security |
| No complete body match | The selected inventory has no full normalized counterpart | This alone does not mean the source is absent: code generation, inlining or layout can differ |

“Perfect” is therefore not used as a blanket status. The exact-byte appendix
answers the narrow byte question. The handler ledger answers the public API
question. Neither is an exhaustive-equivalence certificate.

## 1. Whole-program and dependency identity

These are direct comparisons of the retained files. “Common differences” means
unequal positions in the overlapping file extent; “length gap” is the difference
in file lengths. Their sum is a positional count, not a reconstruction percentage.

| Selected program | Captured bytes | Candidate bytes | Common differences | Length gap | Whole capture equal |
| --- | ---: | ---: | ---: | ---: | --- |
| Pump | 10,485,715 | 1,583,992 | 882,980 | 8,901,723 | No |
| PumpSwap | 10,485,715 | 1,200,384 | 673,181 | 9,285,331 | No |
| Fees | 948,944 | 863,808 | 468,986 | 85,136 | No |
| Mayhem | 777,408 | 599,784 | 323,386 | 177,624 | No |
| Donation Relay | 830,448 | 477,512 | 261,790 | 352,936 | No |

The captured Pump and AMM files include large allocation tails. Their meaningful
ELF extents are 1,934,800 and 1,268,504 bytes respectively; Fees is 873,256,
Mayhem 775,416 and Relay 818,280. The audit records tail lengths and whether their
bytes are all zero. A large file-length gap must not be described as that many
bytes of missing program logic.

| Dependency | Verified byte result | Remaining work |
| --- | --- | --- |
| SPL Token | Full 108,600-byte file equals the capture | Preserve the source/build proof; security and historical uniqueness are separate questions |
| Token-2022 | Raw 611,056-byte ELF equals the captured ELF prefix; a separately padded 1,382,016-byte allocation image equals the full capture | Keep raw-file and allocation-image claims separate; 770,960 tail bytes are generated zeros |
| Associated Token Account | Two research outputs equal all 105,032 captured bytes: explicit linker order and an empty Cargo feature | The historical input/recipe remains unknown; selected dependency status still points to the older 307-byte-different output |
| Metaplex Token Metadata | No exact output: 1,509 differing positions (1,477 text, 30 source-coordinate, 2 relocation); raw ELF 707,448 bytes | Recover the 5,104-byte Utilize body/compiler selection behavior and residual metadata/relocations; 86,543 allocation-tail bytes are separate |

ATA’s two exact-byte recipes are real byte matches, but are explicitly
non-historical. Do not collapse “raw bytes reproduced,” “historical build recipe
recovered,” and “selected dependency promoted” into one claim.

## 2. Selected function windows

The following columns partition each selected original inventory. Raw matches
are freshly recomputed against complete candidate windows. Normalized-only
matches exclude rows already in the raw column. Candidate symbol names label
possible counterparts, not authenticated original source names.

| Selected program | Original windows | Exact local bytes | Normalized only | No complete body match | Opaque without a raw match |
| --- | ---: | ---: | ---: | ---: | ---: |
| Pump | 1,035 | 98 | 430 | 507 | 0 |
| PumpSwap | 785 | 93 | 395 | 297 | 0 |
| Fees | 585 | 102 | 363 | 120 | 0 |
| Mayhem | 441 | 58 | 131 | 7 | 245 |
| Donation Relay | 492 | 33 | 89 | 370 | 0 |
| **Total** | **3,338** | **384** | **1,408** | **1,301** | **245** |

The original ledgers retain additional distinctions:

- **Pump:** 528 original windows have a normalized candidate; 454 have a
  call-consistent candidate under that ledger’s fixed-point test. Its 617 raw
  *pairs* represent 98 distinct original windows. Duplicate candidates are not
  extra recovered functions.
- **AMM:** 488 have normalized matches: 328 single correspondences and 160
  ambiguous rows. There are 297 unmatched original windows. The current ledger
  finds call-supported candidates for 433 rows; referenced data and semantics
  remain separate obligations.
- **Fees:** 461 rows are mapped patterns, 122 are unattributed and two have call
  conflicts. A body may still match at an alternative address; that does not
  erase the conflicting-call disposition. The table counts raw/body existence,
  whereas the source ledger preserves the stronger relation and its failures.
- **Mayhem:** the study admits 184 original windows for normalized analysis:
  177 match and seven do not. It leaves 257 opaque. Twelve opaque rows happen to
  have raw local matches, so the partition above shows 58 raw and 245 remaining
  opaque rows. Those twelve have not acquired semantic or source attribution.
- **Relay:** the selected source-15 inventory has 122 normalized windows,
  including 33 raw matches; 370 remain without a complete counterpart.

Examples of literally equal local bodies include `core::str::count::do_count_chars`
and `core::fmt::write` in the selected Pump/AMM/Fees outputs, numeric/runtime
helpers in Mayhem, and Relay’s `__floatundidf`. The appendix lists every match,
including tiny helpers and duplicate bodies; it does not silently call a whole
trade handler perfect because one of its helpers matches.

## 3. Research at the audit snapshot, kept separate from selection

### Fees: parser, layout, sysroot and call attribution

At this audit snapshot, the stable-sort research output is 852,656 bytes, SHA-256
`f6d23ea00a81b97b6f75d036287a326936cd76534cf6b68a40540e338851ae66`.
It is not the selected `2387f813…` output and still differs from the capture.

- 340 unique structural body pairs; another 147 original windows belong to
  duplicate-body groups; 98 original windows have no full normalized match.
- Encoded calls resolve 53 additional duplicate-body pairs, giving **393
  attributed pairs**, 2,208 consistent aligned call edges and **94 still
  unattributed duplicate-body windows**. Another 26 edges reach different-body
  frontiers. These are edges, not 26 distinct missing functions.
- Fresh raw-body comparison finds **107 original windows with some exact local
  candidate body**. That includes ambiguous duplicates. The stricter unique
  structural-pair count contains 57 raw-equal pairs. Those two counts answer
  different questions.
- The complete 1,248-byte first-account parser and 2,648-byte unchecked decoder
  have the explicitly masked matches documented in PRs #81/#83. Their CALL and
  verified-pointer masks prevent a raw-byte-equality claim.
- The full 5,016-byte dispatcher structure, generated account decoders, the
  2,864-byte initializer scheduling, both 520-byte deprecated handlers, and the
  5,272-byte merge-sort/32-byte memmove wrapper are further bounded structural
  matches. The four `type_id` bodies also have unmasked raw matches in the
  canonical-target experiment, with three repeated bodies still ambiguous.
- Both stable-sort control and proposal passed 17,331 cases. This is finite
  behavior coverage, not all-state equivalence. The surrounding shareholder
  validators still differ.

The initializer scheduling match is static evidence. The 17,331-case Fees corpus
does not invoke `initialize_fee_config`; its initialization suite exercises
`initialize_fee_program_global`. Passing that corpus is not a runtime validation
of the reconstructed initializer.

The exact compiler is not identified. Canonical `sbpf-solana-solana` and legacy
`sbf-solana-solana` can select different prebuilt sysroot code despite equal
target-spec JSON. The v1.52 counterexample also invalidates an upper compiler
bound inferred solely from ELF machine/flags. See the
[attribution study](../research/fees-call-target-attribution/README.md) and
[stable-sort build provenance](../research/fees-stable-share-sort/README.md).

### Relay: generated source is far beyond selected source 15

The distribution-worker research output is 813,968 bytes, SHA-256
`fb4fcb3a95211ff2b3b4dde34257eb6632876a2d0ad4658fd32d45f159c7d518`.
It has **465/492 normalized original windows**, including **86 raw local body
matches**, leaving **27 without a complete match**. Source-15 selection remains
477,512 bytes with only 122 normalized windows; neither output is whole-file equal.

Matched structures include the full 8,264-byte distribution worker, fair
distribution math and its 14 direct calls, growth, eleven generated business
wrappers, the dispatcher, and settlement parser/program/exit layers. Native
vendor source paths still differ; direct callees can have unmatched transitive
callees. A matching wrapper is not proof that the wrapped business logic matches.

The 27 residual windows are enumerated in
[remaining-windows.json](../repro/donation-relay/distribution-worker-source-recovery/remaining-windows.json):
Jupiter builder (90); native donation handlers (92/93); donation/payer handlers
(94/95); epoch-close (96); post-swap, non-swap, just-swap and swap-distribution
handlers (97–100); mint policy (106); burn/close (109); shared donation worker
(112); token serialization (244); account close (282); signed CPI (300); resize
(332); plus ten unclassified helpers. Addresses and candidate alternatives are
in the complete TSV.

Its saved runtime evidence comprises **536 named records / 534 unique fixtures**,
with 3,107 signature fields. Successful fixed-relayer/Jupiter settlement,
arbitrary allocator/borrow behavior and complete security acceptance remain
unproved. PR #94 restored three predecessor packages byte-for-byte; that repairs
verification dependencies, not byte identity or selection. See the
[distribution-worker study](../repro/donation-relay/distribution-worker-source-recovery/README.md).

### Pump and Mayhem overlay

The [overlay](../repro/behavioral-recovery/README.md) dispatches all 56 Pump and
25 Mayhem instructions, but dispatch presence is not completion. It adds three
unaccepted Pump handlers and one Mayhem handler and extends four partial Pump
handlers. The selected 140/150 count does not increase until a new checkpoint is
explicitly built, selected and validated.

PR #79 corrects Mayhem mint/signature validation order and existing-vault
handling: 53 standalone rejection cases and 17 existing real Pump-CPI cases
match. PR #80 repairs the creator fixture: the 20-case retained pair genuinely
tests zero and distinct creators, rather than serializing the payer in every
case. That retained pair uses older overlay candidates; it is not automatically
evidence for every later build. A [follow-up recheck](../research/mayhem-overlay-cpi-recheck/README.md)
retains the same 20 cases for the corrected Mayhem `8e6a5f8c` with the `5392c9a9`
and captured Pump callers: 0 mismatches each. The updated Mayhem overlay itself remains
695,448 bytes and byte-unequal.

Pump’s workspace-member research has 538 normalized windows. Its 497 residual
rows comprise 233 different-body, 192 no-same-size and 72 store-immediate-only
heuristic rows. One of those 72 changes error code 6025 to 6109, so **“72 metadata
differences” is incorrect**; the other 71 are reported origin-only observations.
This research build is not the selected 528-normalized-window build. See the
[frontier classification](../repro/pump/frontier-classification/REPORT.md).

## 4. Public handlers: implemented, partial and unrecovered

| Program | Bounded selected implementation | Partial | Unrecovered / not accepted |
| --- | ---: | ---: | ---: |
| Pump | 48 | 5 | 3 |
| PumpSwap | 37 | 0 | 1 |
| Fees | 31 | 0 | 0 |
| Mayhem | 24 | 0 | 1 |
| **Total** | **140** | **5** | **5** |

The selected core artifacts retain 53,787 bounded comparisons, with another
1,024 Pump Surfpool comparisons recorded separately. These counts include
repeated fixtures and do not measure exhaustive coverage. Fees' 31 includes two
deprecated rejection dispatches, not 31 active business flows.

All 150 names and dispositions are in the handler ledger. The ten uncompleted
selected dispositions are:

| Handler | Current evidence | Work still needed |
| --- | --- | --- |
| `pump.admin_update_token_incentives` | Unselected overlay; 299 finite comparisons | Current selected build/bindings, broader validation, acceptance |
| `pump.claim_token_incentives` | Unselected recovered source; older build-bound receipt | Rebind/replay the current overlay and select it deliberately |
| `pump.set_mayhem_virtual_params` | Static recovery and 84 signer-stub comparisons | Genuine caller/ownership contract and selected-source acceptance |
| `pump.buy_v3` | Partial selected implementation; overlay extends transfer-fee quotes | Other routes, extension/account combinations, full event suffix |
| `pump.sell_v3` | Same category as buy_v3 | Same unresolved coverage dimensions |
| `pump.buy_exact_quote_in_v3` | Partial selected implementation and overlay extensions | Nested routes, transfer-fee and all account-validation combinations |
| `pump.create_v2` | Partial selected implementation; newer real Mayhem-CPI comparisons | Exhaustive ancestry, modes and Token-2022 interactions |
| `pump.multi_hop_curve_swap` | Finite ordinary one/two/three-hop coverage | Arbitrary depth, native/WSOL/other quotes, migration, resizing and mode/extension combinations |
| `pump_amm.create_config` | Compiled/static structural reconstruction | Authentic successful fixed-admin initialization and validation |
| `mayhem.initialize_mayhem_state` | Corrected unselected overlay with rejection/CPI evidence | Selected build and broader initializer behavior |

Additionally, **selected `pump.sell_v2` has a known quote transfer-fee
minimum-output/event mismatch despite belonging to the 48 bounded handlers**.
Mayhem has known error/diagnostic differences and five unknown GlobalParams field
roles. “Bounded implementation” must never be displayed as “no known defects.”

## 5. Remaining work, in practical order

1. **Keep evidence and selection synchronized.** Choose whether the product needs
   a behaviorally useful overlay or only the current strict byte-evidence tier.
   Promotion needs a new source/build/receipt binding and guard transition; this
   audit does not silently perform that promotion.
2. **Close named behavior gaps.** Address the ten dispositions above and the known
   sell_v2 discrepancy; retain successful and rejected fixtures with exact
   transaction inputs. Existing stopped-lane rules are not changed by this report.
3. **Finish the strongest source-recovery paths.** Current Fees: 84 unmatched
   windows; retain the refreshed 61 duplicate attributions, close calls/data
   and shareholder bodies. Current Relay: its [10 explicit residuals](RECONSTRUCTION-STATUS.md#relay-the-complete-remaining-body-list)
   and successful privileged settlement.
   These are bounded frontiers, not estimates of days or percent effort remaining.
4. **Recover the remaining selected Pump/AMM/Mayhem structures.** Use the complete
   address ledgers rather than only high-similarity examples. Preserve ambiguity,
   opaque Mayhem rows, distinct source snapshots and each matcher’s scope.
5. **Close compiler/dependency/layout identity.** Finish Metaplex’s residuals,
   authenticate historical recipes, distinguish generic/canonical sysroots,
   account for source paths/coordinates and reproduce full sections/relocations.
   Do not call byte padding a raw compiler match.
6. **Complete security and external acceptance separately.** Finite differentials
   do not substitute for a security audit. SDK results need current build bindings;
   old overlay success cannot be transferred to a changed binary by description.

No defensible single “percent complete” or time estimate follows from these
counts. Tiny repeated compiler helpers, large business handlers, original source
provenance and successful privileged flows carry very different amounts of work.

## Reproduce the audit

```sh
python3 -B repro/reconstruction-audit-2026-10-26/audit.py --check
python3 -B research/fees-call-target-attribution/verify.py
python3 -B repro/donation-relay/distribution-worker-source-recovery/verify.py
python3 -B repro/consolidation/2026-10-26/guard.py verify_current.py \
  --repo . --metadata repro/layered-passes/pass-27/current-metadata
```

The first command rechecks every retained input hash, selected compilation-input
binding, body window and published audit table. The next two rederive the newer
research claims. These are saved-evidence checks, not fresh source builds or VM
execution. Historical [COMPLETION.md](COMPLETION.md) and
[BUILD_IDENTITY_AUDIT.md](BUILD_IDENTITY_AUDIT.md) remain checkpoint records;
this report is the current cross-check of selection and subsequent research.

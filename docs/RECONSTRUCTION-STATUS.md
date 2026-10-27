# Reconstruction status after unchecked-prefix recovery — 26 October 2026

Reviewed evidence revision: `e2d7855848a3411d665deb915077ef20672e7cdd`.
This review updates the research frontier while preserving the selected-checkpoint
[baseline audit](RECONSTRUCTION-AUDIT.md). The [recomputed inventory](../repro/reconstruction-status-2026-10-26/README.md)
contains every one of the **4,415 selected/research function-window rows**.

The [comprehensive review](../repro/reconstruction-status-2026-10-26/review.md)
reconciles all 150 named handlers and all 4,415 window rows, gives unresolved
text size for every build and lists the largest remaining bodies. Its
[machine-readable summary](../repro/reconstruction-status-2026-10-26/review.json)
is regenerated from the verified inventory. No new runtime coverage is claimed
by this documentation review.

## What is actually byte-identical?

**None of Pump, PumpSwap, Fees, Mayhem or Relay has a whole-file byte-identical
reconstruction. No public handler has an exhaustive semantic-equivalence proof.**

| Dependency | Exact result | Remaining qualification |
| --- | --- | --- |
| SPL Token | All 108,600 captured bytes reproduced | Preserve source/build provenance; byte equality is not a security audit |
| Token-2022 | All 611,056 meaningful ELF bytes reproduced | The full 1,382,016-byte capture is reproduced only by separately adding 770,960 zero bytes |
| Associated Token Account | All 105,032 bytes reproduced by two research recipes | Explicit linker ordering and an empty Cargo feature are non-historical recipes; authentic recipe and selected promotion remain unresolved |
| Metaplex Token Metadata | Not identical: 1,509 differing positions | 1,477 text bytes in Utilize, 30 source-coordinate bytes and two relocation bytes; allocation padding is a separate issue |

See the baseline audit's [dependency evidence](RECONSTRUCTION-AUDIT.md#1-whole-program-and-dependency-identity).
A generated allocation image is not an unchanged compiler output.

## Function status: exact, reconstructed but imperfect, and unresolved

A **raw local match** reproduces all bytes inside an inferred original function
window. It can still reference different data or call different destinations at
its new address. A **normalized match** reproduces the complete body only after
the owning study masks specified calls/relocated pointers. It is not byte identity.
**Unmatched** means no full counterpart under that matcher, not necessarily absent
Rust source. **Opaque** means the source ledger has not admitted it for normalized
analysis. Candidate symbol names are hypotheses about original identity.

| Program / build | Original windows | Exact local bytes | Normalized only | No complete match | Opaque without raw match |
| --- | ---: | ---: | ---: | ---: | ---: |
| Pump selected | 1,035 | 98 | 430 | 507 | 0 |
| PumpSwap selected | 785 | 93 | 395 | 297 | 0 |
| Fees selected | 585 | 102 | 363 | 120 | 0 |
| Mayhem selected | 441 | 58 | 131 | 7 | 245 |
| Relay selected source 15 | 492 | 33 | 89 | 370 | 0 |
| **Fees latest research** | **585** | **118** | **424** | **43** | **0** |
| **Relay latest research** | **492** | **130** | **352** | **10** | **0** |

Each row is a partition, not a score of semantic correctness. Mayhem's source
ledger has 257 opaque windows, 12 of which happen to match local raw bytes.
Selected Fees retains two call-conflicting rows; body existence does not resolve
those conflicts. Different programs and studies use different matching rules.

- [Every exact local body, with candidate names and original addresses](../repro/reconstruction-status-2026-10-26/raw-body-matches.md).
- [Every matched/unmatched/opaque window and candidate correspondence](../repro/reconstruction-status-2026-10-26/functions.tsv).
- [Every unmatched or opaque window](../repro/reconstruction-status-2026-10-26/remaining-windows.md).
- [All 150 named public-handler dispositions and known gaps](../repro/reconstruction-audit-2026-10-26/handlers.md).

Examples of exact local matches include standard formatting/string helpers in
Pump/AMM/Fees and numeric/runtime helpers in Mayhem. Recent Relay recovery also
reproduces the repeated `StringError` type-ID bodies. These are not grounds for
calling whole trade or donation handlers perfect.

## How much remains?

The strongest artifact-backed Relay research candidate matches **482/492 windows (98.0% by
window count)**. Its 10 unmatched windows span **52,616 of 752,488 original text
bytes (7.0%)**. Those bytes describe the sizes of unmatched original windows,
not the number of absent or incorrect bytes. The residual includes large business
functions; matching the other 482 still leaves their call/data identity to prove.

Fees research has **542/585 windows with a normalized counterpart**: 395 unique
structural pairs and 147 original windows in ambiguous duplicate groups. Its 43
unmatched windows span **248,904 of 799,648 original text bytes (31.1%)**, although
they are only 7.4% of the window count. Many remaining bodies are large. The
[current call ledger](../repro/reconstruction-status-2026-10-26/fees-call-attribution.json)
recomputes 65 additional duplicate-body correspondences on this candidate, for
460 attributed pairs. There are 82 still-unattributed duplicate windows and 18
call edges to different-body frontiers. This refinement adds no body coverage.

There is no defensible single source-completion percentage or ETA. Whole-program
identity additionally requires data, layout, relocations, indirect calls and
build-input recovery, and behavior needs broader successful/rejected execution.

### Source-only shared-worker proposal: separate evidence tier

The [shared-worker source proposal](../repro/donation-relay/shared-worker-source-proposal/README.md)
reports a local 483/492 result, gaining worker 112 with no loss. Its published
56-file source map, patch, static verifier and eight tests pass. It includes no
compiled artifact or replay receipt, and default verification reports
`runtime_verified=false`. The proposal also uses an isolated pre-metadata source
baseline; composition with later data work is not established.

The artifact-backed inventory above therefore remains pinned to 482/492. A fresh
independent build, complete window/callee comparison and bound replay are needed
before updating that inventory. Whole-file equality remains unachieved.

## Relay: the complete remaining body list

The labels below are working source attributions from the recovery studies,
not symbols authenticated from the stripped original. Every row remains
unmatched in the current burn/close-recovery candidate on both tested build recipes.

| Original ordinal | Address | Bytes | Working attribution / next comparison |
| --- | ---: | ---: | --- |
| 92 | 70,200 | 6,272 | Native donation body: transfers, bookkeeping and error paths |
| 93 | 76,472 | 6,272 | Native-pubkey donation variant |
| 94 | 82,744 | 2,568 | Regular donation body |
| 95 | 85,312 | 2,568 | Payer donation variant |
| 96 | 87,880 | 4,000 | Epoch close: state updates, checked increment and transfer |
| 97 | 91,880 | 5,216 | Distribution after swap |
| 98 | 97,096 | 5,696 | Distribution without swap |
| 99 | 102,792 | 4,448 | Swap-only body |
| 100 | 107,240 | 5,328 | Swap then distribute |
| 112 | 131,136 | 10,248 | Shared donation worker and its error/data paths |

The former 27-window frontier is obsolete. Subsequent studies recovered receipt
coordinates (one), Token-2022/framework versions (four), framework/sysroot and
share-error behavior (nine), the mint-fee predicate (one), the Jupiter optional-seed builder (one), and burn/close ownership (one),
without losing previous normalized matches. Source-location recovery separately resolves all
43 differences in a fixed audited cohort of 346 location references; it does not
add another matched function or establish all-data identity.

Both current burn/close-recovery candidates pass fresh **536 replay records / 534 unique fixtures**.
The Darwin-compiler/Linux-library candidate is 818,096 bytes, SHA-256
`1eaf3af16fdafdfa9d2ca47e88c07a7f15f13b88aa57df1f63c655c10a1616e2`.
The full Linux candidate is also 818,096 bytes, SHA-256
`c6ae09b906b3c6a88042e40b02e0a2f6598268061d7527b667c0e631655a3921`.
Their equal frontier does not imply equal ELF files or recovered historical tools.
The 184-byte length difference from the original's meaningful ELF is not an
estimate of remaining code. Privileged successes and allocation-failure paths
remain outside the claimed fresh replay coverage.

Evidence: [source-location recovery](../repro/donation-relay/source-location-recovery/README.md),
[Linux reproduction](../repro/donation-relay/linux-canonical-reproduction/README.md),
[framework recovery](../repro/donation-relay/framework-sysroot-recovery/README.md).

### Relay metadata now reproduced from source

The [security-metadata recovery](../repro/donation-relay/security-metadata-source-recovery/README.md)
uses ordinary `solana-security-txt` 1.1.3 source to reproduce the full 510-byte
payload and all 247 bytes of `.dynstr`, including the `SECURITY_TXT` export.
Its 818,664-byte Linux candidate is SHA-256
`af837c4491a267e144cfb0cb7e1fc6772f22ddd353ada93de2b1286489d4beea`.
The packet rederives 482/492 normalized matches, 130 raw-local matches, the same
348 equal source-location pairs and 536 fresh replay records / 534 unique
fixtures. There are no new or lost instruction-window matches. The complete
function inventory above remains pinned to its separately named burn/close
candidate; this metadata candidate is a further research variant.

The original meaningful ELF is 818,280 bytes; its captured allocation also has
12,168 trailing zero bytes. This candidate contains no added allocation padding
and still differs as a whole file. The string object and relocation are present,
but their addresses and other section contents still require recovery. These
results do not establish historical source authenticity or broader semantics.

### Jupiter is now a complete normalized match

The [optional-seed recovery](../repro/donation-relay/jupiter-option-source-recovery/README.md)
closes all four instructions left by the earlier iterator-clone trial. The
original tests the optional slice pointer, whereas the earlier source tested
slice length. `Option<&[&[&[u8]]]>` with a Rust `match` reproduces the entire
2,496-byte window on both compiler recipes. The caller passes `Some(seeds)`.
All 11 direct-call sites bind to complete matched callees. The location audit
retains its original 346 equal pairs and adds two, for 348/348 equal pairs.
This is normalized body recovery, not raw whole-file or exhaustive semantic
identity. Nineteen further metadata-construction trials and an `if let` variant
are retained as negative controls. The earlier 32 burn/close trials remain
negative; the subsequent ownership recovery below resolves window 109.

### Burn/close is now a complete normalized match

The [mint-ownership recovery](../repro/donation-relay/burn-mint-ownership-recovery/README.md)
resolves window 109 by consuming the mint in the nonzero burn and fully
destructuring the input context. This recovers the original conditional cleanup
and return layout. All 24 direct-call sites bind to matched callees; the same
348 source-location pairs remain equal. Both compiler recipes match the complete
2,856-byte body and pass fresh bounded replay. No whole-file or exhaustive
semantic identity is claimed. Thirty-six epoch-close trials remain negative;
epoch-close window 96 is still in the ten-row residual list.

### Donation controls: no new complete body match

The [59 source builds](../repro/donation-relay/donation-source-controls/README.md)
cover construction/argument variants in donation wrappers and ownership/result
variants in the shared worker. All 173 targeted window comparisons remain
unmatched. Some ownership variants also lose the previously matched context-drop
window 51. The control builds reproduce their respective 482-window parent
binaries exactly; experimental candidates are not promoted. This rules out the
tested source forms without claiming that all donation logic is understood.

### Shared-worker cleanup: verified graph, unresolved source

The [shared-worker flow audit](../repro/donation-relay/shared-worker-flow-audit/README.md)
shows that all paths in the conservative decoded graph to an explicit return
pass through the matched context-drop helper, in both original and current
workers. This also holds after the transfer call. The drop block is at different
linear offsets (3,152 versus 352); those positions do not establish a different
ownership boundary. Calls are assumed to return and branch feasibility is not
proved. Five further mint-key/whitelist source builds all retain 482 matches
without recovering the worker. Preserve the common cleanup while investigating
source expression and lifetimes; no experimental source is promoted.

### Donation wrapper argument-binding controls

The [complete 32-subset study](../repro/donation-relay/partial-argument-controls/README.md)
tests every subset of the five wire-argument fields as partial local bindings,
with the remaining fields read through `args`. All 128 comparisons of windows
92–95 remain unmatched. No subset gains or loses any full-window match. This
rules out partial argument binding alone under the tested compiler recipe; it
does not rule out different source layouts, ABI choices or compiler inputs.
The ten-window residual remains unchanged.

### Conditional wrapper value-flow diagnostic

The [caller diagnostic](../repro/donation-relay/wrapper-value-flow/README.md)
compares regular and payer wrappers on modeled success/error paths. Selected
context and argument fields match at the shared-worker boundary, and selected
return fields match given identical abstract worker results. This depends on
explicit clone/copy summaries, nonwrapping increments and the input-address
model; arbitrary aliases and real callee effects are not proved. The four
conditional traces add no body matches or accepted handlers. Both wrappers and
the shared worker remain in the residual list.

### Epoch-close source controls

The [fourteen epoch-close controls](../repro/donation-relay/epoch-source-controls/README.md)
test cached configuration/mint fields and checked-add error/Result forms. None
recovers original window 96, and all retain the 482-window frontier. Most error
forms compile to the same body; explicit eager conversion changes the body but
does not match. The observed post-conversion branch remains a diagnostic clue,
not proof of a particular source expression. A separate cached v1.50 compiler
substitution, retaining v1.48 libraries and linker, regresses to 226 normalized
matches (256 lost, none gained). That combination is rejected; it does not
establish the original compiler or evaluate every v1.50 recipe.

### Root-profile and Result-helper controls

The [twelve additional builds](../repro/donation-relay/profile-result-controls/README.md)
include an exact baseline control and four root compiler overrides. Opt-level 2,
s, z and codegen-units 2 retain 382, 316, 314 and 372 normalized windows,
respectively, with no new original match. Seven Result-helper source trials keep
482 matches. A unit-returning error helper reproduces the already-matched
504-byte window 115, illustrating that identical local shape does not uniquely
identify its original return type. Epoch close and the shared worker remain
unmatched; no candidate from this packet is promoted.

### Shared-worker arithmetic and ordering controls

The [six arithmetic/ordering builds](../repro/donation-relay/arithmetic-order-controls/README.md)
test in-place checked operations and a separately named tip division. None
recovers window 112 or changes the 482-window frontier. Both tip-only forms
reproduce the existing candidate exactly, so that source distinction is removed
by this compiler. The unit-result helpers do not recover their caller; no trial
is promoted or newly runtime-accepted.

### Swap caller constructor order and layout

The [swap-caller controls](../repro/donation-relay/swap-caller-controls/README.md)
retain compiler-generated layouts for the reconstructed account/context types;
the diagnostic build reproduces the current candidate exactly. Moving the
program field to the end of the `just_swap` burn-context initializer removes an
extra memcpy call, agreeing with the original call count. Its body is still
4,408 bytes versus the original 4,448 and remains unmatched. A fresh replay of
both original and this partial correction passes 536 records / 534 unique
fixtures with the existing exclusions. Four argument-wrapper variants remain
negative. No candidate is promoted and the frontier remains 482/492.

### Settlement direct-call inventory

The [direct-call audit](../repro/donation-relay/settlement-call-audit/README.md)
checks original windows 97–100 against the baseline and constructor-order
candidate. Every direct local callee has a normalized-body counterpart. Callee
body-group multiplicities agree for three baseline callers and all four after
the constructor change removes one memcpy. Linear call sequences and caller
bodies still differ. This narrows missing-call hypotheses without proving
arguments, inline checks, branch conditions, data or transitive behavior; no
additional function is considered recovered.

## Fees: new complete bodies, substantial residual business logic

The latest 861,000-byte candidate is SHA-256
`fe11df62162e27700890e5dcd07d5760a66f5528fd89de4b523975dbfc38f112`.
The newly merged studies recover:

| Complete original window | Evidence |
| --- | --- |
| 696-byte `update_buyback_authority` body at 96,896 | [Source path/guard recovery](../research/fees-buyback-update-origins/README.md) |
| 640-byte `update_buyback_claim_rate_limit` body at 97,592 | Same study; helper inlines into the public body |
| 336-byte Shareholder-vector clone at 58,520 | [`Copy` specialization](../research/fees-shareholder-copy-clone/README.md); both encoded callees independently bound to raw-equal helpers |
| 600-byte buyback initializer at 120,216 | [Unchanged helper relocated to its diagnostic source path](../research/fees-buyback-initializer-origin/README.md) |
| 3,320-byte authority-update body at 103,408 | [Preserved body tokens and diagnostic source coordinates](../research/fees-authority-body-origin/README.md) |
| 776-byte legacy account cleanup and 1,072-byte dispatcher | [Owned account/context recovery](../research/fees-sharing-owned-legacy/README.md); cleanup raw bytes equal |
| 192-byte fee-total predicate at 700568 | [Full Linux integration](../research/fees-total-predicate-integration/README.md); panic leaf, message and source coordinates checked |
| Two 624-byte setters at 260568 and 261192 | [Setter recovery](../research/fees-config-setter-recovery/README.md); error origins, field stores and ten direct callee bindings checked |
| V2 parser (352 bytes), cleanup (776 bytes), dispatcher (1,104 bytes) | [V2 ownership](../research/fees-sharing-owned-v2/README.md), integrated with the setters; cleanup raw bytes equal |
| Two 4,160-byte tier bodies, 368-byte reserve and 200-byte slice-length-mismatch panic bodies | [Tier replacement/upsert recovery](../research/fees-tier-splice-recovery/README.md); 57 direct callee-body bindings checked |
| Configuration/stable updates (2,608 / 2,568 bytes), normal/stable upserts (2,528 bytes each) | [Event and admin-source recovery](../research/fees-config-event-recovery/README.md); duplicate upserts distinguished by outgoing calls |

These are complete normalized windows, not merely matching diagnostic fragments.
There are 64 unique raw-equal structural pairs; counting all original windows
with any raw counterpart, including ambiguous duplicates, gives 118. Those
numbers answer different questions and must not be interchanged.

The candidate retains passing **17,331 cases across 18 suites** and **1,542 exact
outcome/log/compute comparisons**. The current context-origin candidate was replayed afresh;
its control reuses the verified buyback-context artifact. Existing unchecked-input
and finite-coverage limits remain. The 58 unresolved bodies, ambiguous attribution,
shareholder validation, transitive calls/data and final ELF layout remain open.

The fee-total helper, flat-fee setters, tier helpers and four configuration/upsert
public callers now have complete normalized counterparts. The upserts share a
body shape but are distinguished by their callee targets; both local outgoing
checks and the global incoming-call refinement agree. Other callers, referenced
data and full transitive behavior remain open. These matches do not establish
whole-program or exhaustive semantic equivalence.


The [exotic-fee growth study](../research/fees-exotic-growth-precedence/README.md)
adds 24 signed boundary cases crossing allocation size, account/admin funding,
invalid totals and overflow. The previous research candidate disagrees in four
cases; moving validation after growth and using the original false zero-init
flag removes all four. The corrected research candidate passes the existing
17,331-case suite and 1,542-case exact matrix too. Its 5,664-byte caller still
differs from the original's 5,520 bytes, so coverage remains unchanged. A
same-sized experimental body also fails full comparison and is not accepted.

### Optional account ownership: two recovered bodies

The [optional-account ownership study](../research/fees-optional-account-ownership/README.md)
changes only the optional AMM event authority from borrowed unchecked account
to owned `AccountInfo`. It recovers original 10,232 (528-byte normalized parser)
and 41,560 (160-byte raw-equal cleanup), with no lost matches. Both direct calls
in the optional parser bind to matched callee bodies. The enclosing account
parser remains unmatched. The new candidate passes fresh 17,331 suite cases,
1,542 exact comparisons, 24 retained growth-boundary cases and 32 new signed
optional-account cases. The 32-case matrix compares state, errors, lamports,
events and inner instructions; it makes no log/compute equality claim.

### Social-claim signing-seed vector

The [seed-vector recovery](../research/fees-social-seed-vector/README.md) copies
the stored user-ID bytes before constructing V2 token-claim signing seeds. It
recovers original 51,608 (296 bytes) with raw differences restricted to two call
immediates, both targeting complete matched bodies. No matches are lost. The
claim caller remains unmatched. Fresh suite, exact-matrix, growth and optional
replays pass; 20 extra cases cross native/token paths, token programs and user-ID
byte lengths including UTF-8. They compare state/errors/events/CPI/return data,
not all logs or compute.

### Extension no-resize messages

The [extension-size log study](../research/fees-extend-size-logs/README.md) restores
the original exact-size and oversized-account messages. Its eight signed cases
show program-log disagreement in the parent and agreement in the new candidate,
with other observed results unchanged. The change also recovers the complete
448-byte formatting helper at 52,568, with only three call-immediate differences
and matched callees. The larger resize handler remains unmatched. One previously
normalized 24-byte window also becomes raw-equal due to the new layout; that
adds no new body coverage. Fresh regression and all retained focused matrices pass.

### Crank boxed interface mint

The [crank mint recovery](../research/fees-crank-interface-mint/README.md) replaces
the research legacy mint account with a boxed interface mint. Original window
9,880 now matches completely; existing windows 640 and 693,080 become unique as
redundant candidate specializations disappear. That is one new body match and
two fewer structural ambiguities. All three parser callees match, and the
larger account parser remains unmatched. Thirty new signed owner/length cases
correct ten observed discrepancies in both the parent and boxed-legacy control.
All retained broad/focused regressions pass. This does not claim successful
Token-2022 transfers through the crank's downstream legacy token program.

### Shared zero-quote predicate

The [common-helper recovery](../research/fees-curve-zero-helper/README.md) emits
the 504-byte zero-quote predicate from ordinary Borsh pubkey deserialization.
Array conversion and `TryFrom` controls emit 432-byte bodies and do not match.
All four direct callee bodies and both referenced panic locations match. The
helper is wired into both existing fee-sharing callers; those full callers
remain unresolved. The change adds one normalized body with no lost coverage,
and passes fresh broad and retained focused regression suites.

### Tier-copy slice panic data

The [slice-origin contract study](../research/fees-slice-origin-contract/README.md)
corrects four location records on its reproduced PR #149 baseline. Only eight
ELF bytes change and the full instruction section remains raw-equal. It also
binds the real caller edges, three message pieces and numeric/panic callees,
identifying original 784,168 as a source/destination slice-length-mismatch
panic, rather than an ordinary index-bounds panic. It adds no body matches.
The [integration](../research/fees-slice-origin-integration/README.md) now carries
those four records into the latest research source. Its entire instruction
section remains raw-byte equal to the 376-pair parent, and exactly eight data
bytes change. All intervening gains and fresh regression suites are retained.
The older study's 368-pair counts do not replace the current frontier.

### Buyback initializer context

The [buyback context recovery](../research/fees-buyback-context-ownership/README.md)
boxes the vault and token account and owns the event/program account infos.
It recovers original windows 351,128 (7,184-byte parser), 364,568 (5,512-byte
initialization closure) and 370,080 (560-byte exit) without losing matches.
At this stage, 86 of 87 direct callee bodies matched; the remaining edge called
closure 358,312 (6,256 bytes), whose subsequent recovery is described below.
That adjoining body is excluded from the 7,184-byte parser size. The exit owner and error-field strings match,
and previous slice/common location contracts remain equal. Fresh broad and
focused regression suites pass. This is body/context recovery, not exhaustive
initializer semantics or a new selected-handler acceptance.

### Buyback context source origin

The [source-origin recovery](../research/fees-buyback-context-origin/README.md)
moves the unchanged context declaration to `instructions/buyback/mod.rs:12`,
while retaining the initializer function on line 94. It fixes the two unmasked
line/path-length constants and the actual error-origin path, recovering all
6,256 bytes of closure 358,312. All four parser/initialization/exit components
now have complete normalized bodies and all 104 direct callee bodies match.
This adds one body plus one duplicate call attribution; no previous match is
lost. Previous panic-location contracts and fresh regression suites pass.
Full data/indirect-call and whole-file identity remain open.

### Crank event-account layout and remaining caller gaps

The [owned event-account recovery](../research/fees-crank-event-ownership/README.md)
changes one context field from `UncheckedAccount` to `AccountInfo`, retaining its
seed constraint. This recovers the complete 952-byte crank exit and 840-byte
dispatch wrapper, without losing any match. Both original exit field offsets,
the owner bytes and three error labels agree; all 12 direct exit callees match.
The wrapper still calls the unmatched parser at 408,640 and business handler at
147,944. These two local gains do not close the public handler's full call tree.

The [root codegen controls](../research/fees-wrapper-codegen-controls/README.md)
reproduce the prior candidate exactly at one unit. Two, four, eight and sixteen
units recover no new bodies and lose 127, 133, 163 and 163 covered windows,
respectively. They retain a bump default store but do not recover the buyback
wrapper. Keep the one-unit recipe; the wrapper's original extra initialization
instruction still needs a source/build explanation.

### Sweep context: parser, exit and wrapper recovered

The [sweep context ownership study](../research/fees-sweep-context-ownership/README.md)
boxes the vault and both token accounts, and owns the event/program account
infos. The destination remains borrowed. This recovers the complete 9,280-byte
parser, 944-byte exit and 1,320-byte dispatch wrapper, without losing a match.
All 89 direct parser/exit callees match. The wrapper has five matching direct
callees and one remaining business-body frontier at original 120,816.

The three separate controls add no complete body match. Earlier crank and
initializer bodies, their explicit callee limitations, and retained panic-data
contracts remain unchanged. The new candidate passes fresh full and focused
regressions; source, build and data evidence are retained separately from the
local instruction matches. No selected artifact is promoted.

### Buyback update: shared parser and both wrappers recovered

The [buyback-update ownership study](../research/fees-buyback-update-ownership/README.md)
owns the event authority and program account infos in the shared update context.
It recovers the complete 5,856-byte parser, 1,744-byte authority-update wrapper
and 1,568-byte claim-rate wrapper. All 61 direct callee bodies match; single-field
ownership controls add no complete body. No prior match is lost.

Twenty-five selected message, seed, label and owner-ID ranges also match, with a
mutation test distinguishing their identity from instruction equality. Nested
panic/format metadata, wider transitive data and exhaustive behavior still need
separate proof. Fresh full and focused regression passes; earlier sweep, crank,
initializer and panic-location contracts remain verified.

### Isolated event-context integration

The [six ownership trials](../research/fees-event-context-ownership/README.md)
recover two bodies each for social claim, withdrawal and social-PDA creation.
Their combined source retains all six gains and every parent match. All 168
parser callees match; the three dispatch wrappers still call unmatched business
bodies. The original instruction-message bytes are checked separately.

The fee-sharing V2 trial loses two normalized bodies and one raw-local match;
its borrowed event field is retained. Admin-reset and fee-sharing-creation
trials add no complete body and are not integrated. Do not apply a blanket
conversion to every unchecked event account. Fresh combined-candidate full and
focused regressions pass, and earlier context/data contracts remain verified.

### FeeConfig unchecked prefix and initialization evidence

The [unchecked-prefix recovery](../research/fees-unchecked-prefix-recovery/README.md)
restores full-account input handling for the research decoder. It consumes the
eight-byte prefix, without checking its value in the unchecked path, and invokes
the existing payload decoder. The complete 1,144-byte helper now matches, all
11 direct callee bodies match, and the incoming initializer closure and payload
decoder remain matched. Owner constants and the decoder error-message record
are verified independently of instruction normalization.

The parent fails the added native prefix regression; the corrected source passes
35 host contract cases, including short buffers and format thresholds. The local
slice control restores the prefix but leaves 22 stack-operand differences and
does not consume the caller's descriptor. The consuming variant is retained.
The 17,331-case SBF regression passes but does not invoke `initialize_fee_config`.
These tests do not establish a successful authorized fixed-admin initializer
transaction. Older packets' discriminator-free unchecked-input limitation is
resolved for this current research candidate, not rewritten in those packets.

## Public behavior: reconstructed is not perfect

Across the four core selected programs, **140/150 handlers have bounded
implementations, five are partial, and five are unaccepted/unrecovered**. This
count excludes the separately tracked Relay. In particular:

| Program | Partial / unaccepted selected handlers | Other known gaps |
| --- | --- | --- |
| Pump | Partial: `buy_v3`, `sell_v3`, `buy_exact_quote_in_v3`, `create_v2`, `multi_hop_curve_swap`. Unaccepted: `admin_update_token_incentives`, `claim_token_incentives`, `set_mayhem_virtual_params` | `sell_v2` quote transfer-fee minimum-output/event discrepancy; full extension, account, error precedence and event coverage |
| PumpSwap | `create_config` successful fixed-admin initialization lacks accepted runtime validation | 297 unmatched windows, 160 ambiguous normalized rows, call/data and diagnostics |
| Fees | All 31 selected handlers have bounded coverage | Does not make remaining business bodies exact or establish all-state equivalence |
| Mayhem | `initialize_mayhem_state` unaccepted in selected build; corrected overlay has rejection and real Pump-CPI evidence | Seven admitted unmatched bodies, 257 opaque rows, diagnostic/error differences and five unknown GlobalParams field roles |

The overlay supplies implementations for previously absent selected entrypoints,
but cannot acquire selected status by documentation. Candidate rebuilding, bound
receipts, acceptance decisions and explicit guard changes are still required.

## Recommended execution order and completion criteria


The [Mayhem configuration-history packet](../research/mayhem-globalparams-field-history/README.md)
adds captured account values and a reported ten-update trajectory. Its offline
checker passes file hashes, account decoding and the derived version chain;
it does not independently re-decode the transaction instruction/event payloads.
Those payloads need a separate cross-check before the history is used to close
field-role claims. The five semantic roles remain unresolved; no field is renamed.

1. **Continue Relay body recovery:** isolate one ordinary Rust change per trial,
   starting with epoch close and the shared donation worker. Keep
   negative trials; require no lost normalized matches and fresh replay of any
   proposed candidate. Do not infer a match from equal sizes or fuzzy similarity.
2. **Close known behavior defects:** Pump `sell_v2` and the ten partial/unaccepted
   selected dispositions above, with bound success/rejection tests. Cover genuine
   CPI callers, ownership and extension/mode combinations before acceptance.
3. **Continue Fees business/source recovery:** work from all 43 residual addresses,
   preserve the refreshed duplicate-call attribution, and validate paths not
   exercised by the existing corpus. Normalize only declared relocations/calls.
4. **Recover Pump/AMM/Mayhem residuals:** preserve opaque and ambiguous states.
   Pump's separate workspace-member experiment reaches 538 normalized windows
   with 497 residuals, but is not the selected 528-window candidate.
5. **Close data and build identity:** recover constants, strings, layout,
   relocations, indirect targets and authentic tool/dependency inputs; complete
   Metaplex and resolve ATA selection/provenance independently.
6. **Promote only with evidence:** source snapshot, locked build inputs, actual
   fresh compiler invocation, exact candidate hashes, replayed behavior and
   reviewed selection/guard updates. Final byte acceptance requires unchanged
   compiler output equality, separately labeling any allocation padding.

Security and operational acceptance remain distinct from reproduction. All tests
here are local; no live network action is part of this review.

## Reproduce this review

```sh
python3 -B repro/reconstruction-audit-2026-10-26/audit.py --check
python3 -B research/fees-shareholder-copy-clone/verify.py
python3 -B research/fees-authority-body-origin/verify.py
python3 -B research/fees-refreshed-call-attribution/verify.py
python3 -B repro/donation-relay/burn-mint-ownership-recovery/verify.py
python3 -B research/fees-crank-event-ownership/verify.py
python3 -B research/fees-sweep-context-ownership/verify.py
python3 -B research/fees-buyback-update-ownership/verify.py
python3 -B research/fees-event-context-ownership/verify.py
python3 -B research/fees-unchecked-prefix-recovery/verify.py
python3 -B research/fees-wrapper-codegen-controls/verify.py
python3 -B repro/reconstruction-status-2026-10-26/refresh.py --check
```

These verify retained evidence and rederive byte/window inventories; they are not
new compiler builds or fresh VM executions. The owning packages record those
builds and replays. The new inventory preserves the old selected 3,338 rows and
recomputes the 1,077 current research rows directly from their artifacts.

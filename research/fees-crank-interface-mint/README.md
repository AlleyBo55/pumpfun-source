# Crank quote-mint interface and boxed parser

The original crank context uses a **boxed interface mint**, not the reconstructed
unboxed legacy-token mint. This source change recovers original window **9,880
(352 bytes)** and corrects the observed owner/length validation behavior.

| Variant | Unique structural pairs | Ambiguous original windows | Unmatched windows |
| --- | ---: | ---: | ---: |
| Parent | 372 | 149 | 64 |
| Boxed legacy mint control | 372 | 149 | 64 |
| Boxed interface mint | 375 | 147 | 63 |

Only window 9,880 gains a complete normalized counterpart. Windows 640 and
693,080 already had counterparts and now become unique after redundant candidate
specializations disappear. This is **one new body and two structural
ambiguities removed**, not three newly recovered bodies. There are no lost
normalized or raw matches. The full partition is 118 raw-local / 404
normalized-only / 63 unmatched.

The recovered boxed parser allocates/copies 128 bytes, agreeing with the original.
Boxing the legacy mint instead generates a 96-byte parser and does not match.
All three direct callee bodies of the recovered parser match; raw differences
are confined to their call immediates. The enclosing account parser remains
unmatched: 10,872 original bytes versus 10,376 candidate bytes.

## Actual behavior check

Thirty new normally signed synthetic crank cases cross native/other quote keys,
legacy-token / Token-2022 / incorrect program ownership, and mint data lengths
0, 81, 82, 83 and 165. The fixture overrides only the quote-mint account before
the transaction and retains its observed owner/data in each pre-state. The
parent and boxed-legacy control disagree with the original in ten Token-2022
owner cases; the boxed-interface candidate agrees in all 30.

Comparison covers errors, pre/post accounts, inner instructions and event logs.
Other logs are retained but not required equal; compute is not compared. These
results establish the tested parser behavior, not successful Token-2022 token
transfers: the crank still uses its declared legacy token program downstream.

Fresh regression on the interface candidate passes 17,331 cases across 18
suites, 1,542 exact outcome/log/compute cases, and the 24 growth, 32 optional,
20 user-ID and 8 extension-log cases from previous recoveries. Allocator-exhaustion
and exhaustive lifecycle equivalence remain outside these claims.

## Evidence

Only the quote-mint type in research `src/donation.rs` changes. The 35-file source
map, exact transform for both trials, fresh Linux v1.44 root compilations,
artifacts and comparisons are retained. The parent artifact is a reused control.
No selected sources or checkpoints are changed.

Interface candidate: 859,904 bytes, SHA-256
`16b13f46151ce47360f4d25eca740fe89a000b6ab83e9cdd2e2c3c12e87e400c`.
Current call refinement has 436 correspondences: 375 unique plus 61 additional
call-attributed pairs; 86 duplicate windows remain unattributed. The 63 unmatched
original windows span 318,520 / 799,648 text bytes (39.8%). Whole-file equality
remains false.

Run `python3 -B research/fees-crank-interface-mint/verify.py` to check retained
sources, builds, body/call comparisons and replay contents. This does not compile
or execute the target. `mint_cases.py` reruns the focused signed transactions.

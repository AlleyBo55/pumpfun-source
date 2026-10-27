# Crank event-account ownership recovery

Storing `CrankDonationFeePda.event_authority` as an owned `AccountInfo` recovers
two complete original instruction windows, with no lost normalized or raw
matches. Fees now has **382 unique structural pairs and 56 unmatched windows**.
The existing seed constraint remains unchanged.

| Original address | Bytes | Component | Matching direct callee bodies |
| --- | ---: | --- | ---: |
| 424,824 | 952 | `CrankDonationFeePda::exit` | 12/12 |
| 656,832 | 840 | `__global::crank_donation_fee_pda` | 2/4 |

The previous exit body differed only at two field loads: offsets 624 and 680
instead of the original 664 and 720. The owned field recovers both offsets.
The owner bytes and three referenced field labels also match separately:
`donation_fee_pda`, `donation_fee_pda_ata`, and `quote_mint`. The mutation test
shows that an unchanged instruction body can still refer to a wrong label.

The dispatch wrapper now matches as a complete normalized body, but its
account parser (original 408,640) and business handler (147,944) still differ.
Only its memcpy and exit callees match. Neither new local match proves a
complete crank reconstruction or whole-program identity.

## Evidence and validation

Only one source type changes in the 36-input map, relative to the
[buyback-origin parent](../fees-buyback-context-origin/README.md). The original
four buyback context bodies and their 104 direct-call matches remain intact,
as do the four tier-copy and two common-helper panic locations.

The fresh pinned Linux v1.44 candidate is 861,752 bytes, SHA-256
`7a0a6a0030050f6230e33d9fa2cf5f8e32bf6d43c2144145437047dd90c9c81f`.
Its full partition is **118 raw-local / 411 normalized-only / 56 unmatched**.
The remaining windows span 296,712 / 799,648 original text bytes (37.1%).
Call refinement yields 444 correspondences: 382 unique plus 62 additional
duplicate pairs, with 85 duplicate windows still unattributed. The current
call ledger has 2,768 bound-target edges and 21 different-body frontier edges.
These counts do not establish indirect-call or all-data identity.

Fresh regression passes 17,331 cases across 18 suites; 1,542 exact
outcome/log/compute comparisons; and the 24 growth, 32 optional-account,
20 user-ID, 8 extension-log and 30 crank-mint cases. Each harness retains its
own observation limits; only the dedicated flag matrix asserts exact logs and
compute. No selected checkpoint changes.

Run `python3 -B research/fees-crank-event-ownership/verify.py` and
`python3 -B research/fees-crank-event-ownership/test_scope.py` to recheck the
retained source/build/artifact bindings, local bodies, referenced data and
receipts. These verification commands do not compile or execute target code.
The separate [wrapper codegen controls](../fees-wrapper-codegen-controls/README.md)
reject four root compiler substitutions; none replaces this candidate.

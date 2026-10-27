# Event account ownership: isolated controls and integration

Owning the event authority and program account infos in three contexts recovers
six complete original windows, with no lost raw or normalized matches. Fees now
has **394 unique structural pairs and 44 unmatched windows**. The accepted
combination changes only `social.rs`, `withdrawal.rs` and
`instructions/fee_sharing/create_social_fee_pda.rs`.

| Original address | Bytes | Recovered component | Matching direct callee bodies |
| --- | ---: | --- | ---: |
| 389,488 | 6,168 | Social-claim account parser | 46/46 |
| 468,624 | 7,072 | Social-PDA creation account parser | 50/50 |
| 520,760 | 7,904 | Withdrawal account parser | 72/72 |
| 644,264 | 1,600 | Social-PDA creation dispatch | 7/8 |
| 645,864 | 2,104 | Social-claim dispatch | 12/13 |
| 657,672 | 1,104 | Withdrawal dispatch | 3/4 |

All 168 direct parser callees match. The three dispatchers still call unmatched
business bodies at 190,104, 132,744 and 249,264 respectively. Their recovered
instruction messages are checked separately from normalized body equality.
Full data/indirect-call identity and exhaustive semantics remain open.

## Six isolated source trials

Each trial starts from the same [buyback-update parent](../fees-buyback-update-ownership/README.md)
and changes only that context's event/program field types, leaving constraints
unchanged. No blanket conversion is accepted.

| Context | New complete bodies | Lost complete bodies | Result |
| --- | ---: | ---: | --- |
| Social claim | 2 | 0 | Integrated |
| Withdrawal | 2 | 0 | Integrated |
| Fee-sharing V2 update | 0 | 2 | Rejected; also loses one raw-local match |
| Admin sharing reset | 0 | 0 | Not integrated |
| Social-PDA creation | 2 | 0 | Integrated |
| Fee-sharing creation | 0 | 0 | Not integrated |

The V2 loss is at original 44,632 and 641,744. Keep its existing borrowed event
field; this result rules out that isolated conversion under this recipe, not
all future changes to the context. The combined three-context build preserves
the union of the six gains and all parent matches. All 36 input files are hash
bound for every trial and the combination; only three files differ in the final
candidate. Previous buyback, sweep, crank and panic-location contracts remain
verified. The preserved 25 literal ranges and three new instruction messages
are not a claim to cover all referenced data.

## Build and validation

Seven fresh pinned Linux v1.44 builds and a reused parent control are retained.
The combined candidate is 868,000 bytes, SHA-256
`d56316613f653ccb02b299bfed0ecfbea732dcca49758141f4750a793871acc7`.
Its full partition is **118 raw-local / 423 normalized-only / 44 unmatched**.
The residual spans 250,048 / 799,648 original text bytes (31.3%). Call refinement
finds 459 correspondences (394 unique + 65 additional duplicates), leaving 82
duplicate windows unattributed. There are 3,133 bound-target and 19
different-body frontier edges. Whole-file equality remains false.

Fresh combined-candidate regression passes 17,331 cases across 18 suites,
1,542 exact outcome/log/compute comparisons, and 24 growth, 32 optional-account,
20 user-ID, 8 extension-log and 30 crank-mint cases. Each harness retains its
existing observation limits. This does not promote selected source or artifacts.

Run `python3 -B research/fees-event-context-ownership/verify.py` and
`python3 -B research/fees-event-context-ownership/test_scope.py` to verify the
retained source/build/artifact bindings and comparisons. These commands do not
rebuild or execute target programs.

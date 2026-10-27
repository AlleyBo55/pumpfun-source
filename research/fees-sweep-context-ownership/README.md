# Sweep buyback context ownership recovery

Using boxed vault/token accounts and owned event/program `AccountInfo` fields
recovers three complete original windows, with no lost normalized or raw
matches. Fees advances to **385 unique structural pairs and 53 unmatched windows**.
Only five field types in `SweepBuyback` change; their constraints are unchanged.

| Original address | Bytes | Component | Matching direct callee bodies |
| --- | ---: | --- | ---: |
| 370,640 | 9,280 | `SweepBuyback::try_accounts` | 77/77 |
| 379,920 | 944 | `SweepBuyback::exit` | 12/12 |
| 651,272 | 1,320 | `__global::sweep_buyback` | 5/6 |

The dispatch wrapper still calls the unmatched sweep business body at 120,816.
The parser and exit matches do not close that handler, its full call tree, or
all referenced data. The exit's owner bytes and three field labels are checked
separately. A mutation test changes a label without changing any instruction
and confirms that the data contract rejects it.

## Controls and source evidence

The vault, vault ATA and destination ATA must use boxed storage. The destination
remains an `UncheckedAccount`; only event authority and program become owned
`AccountInfo` fields. The boxed-only exit has the correct 944-byte shape but
loads its three account pointers at 144/152/160 instead of 240/248/256.
Owning the event and program accounts recovers those offsets and both other
complete bodies.

| Source variant | Unique pairs | Unmatched | New complete bodies |
| --- | ---: | ---: | ---: |
| Parent control, reused | 382 | 56 | 0 |
| Three boxed accounts only | 382 | 56 | 0 |
| Three owned unchecked accounts only | 382 | 56 | 0 |
| Three boxes plus all three owned unchecked accounts | 382 | 56 | 0 |
| Three boxes plus owned event/program accounts | 385 | 53 | 3 |

All variants preserve earlier normalized and raw coverage. Only the final
variant is carried forward. The controls isolate the tested type choices;
they do not establish unique historical source text. The previous initializer,
crank, tier-copy and common-helper contracts remain verified.

## Build and regression evidence

The 36-input source map, four fresh pinned Linux v1.44 builds and their logs,
and the reused [crank parent](../fees-crank-event-ownership/README.md) are retained.
The accepted research candidate is 861,544 bytes, SHA-256
`658a81d0aa4210e0c4879280c5e970e26a6e97749145433d9e66fb6756747fc6`.

The full partition is **118 raw-local / 414 normalized-only / 53 unmatched**.
Residual windows span 285,168 / 799,648 original text bytes (35.7%). Call
refinement yields 449 correspondences (385 unique plus 64 additional duplicate
pairs), with 83 duplicate windows still unattributed. The call ledger has
2,875 bound-target and 21 different-body frontier edges. None of these counts
is a whole-file or exhaustive semantic-equivalence proof.

Fresh regression passes 17,331 cases across 18 suites; 1,542 exact
outcome/log/compute comparisons; and 24 growth, 32 optional-account, 20 user-ID,
8 extension-log and 30 crank-mint cases. Each harness retains its observation
limits; only the dedicated flag matrix asserts exact logs and compute.
Selected source and checkpoint artifacts are unchanged.

Run `python3 -B research/fees-sweep-context-ownership/verify.py` and
`python3 -B research/fees-sweep-context-ownership/test_scope.py` to verify the
retained evidence. These commands do not rebuild or execute target programs.

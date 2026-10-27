# Buyback update context ownership recovery

Owning the event authority and program `AccountInfo` fields in `UpdateBuyback`
recovers the complete shared account parser and both update dispatch wrappers.
No previous raw or normalized match is lost. Fees now has **388 unique
structural pairs and 50 unmatched windows**.

| Original address | Bytes | Component | Matching direct callee bodies |
| --- | ---: | --- | ---: |
| 331,936 | 5,856 | `UpdateBuyback::try_accounts` | 43/43 |
| 652,592 | 1,744 | `__global::update_buyback_authority` | 9/9 |
| 654,336 | 1,568 | `__global::update_buyback_claim_rate_limit` | 9/9 |

All 61 direct callee bodies match, including the previously recovered update
handlers. The new match does not prove all transitive data, indirect calls or
exhaustive behavior. Twenty-five selected literal ranges are separately checked:
account labels, PDA seed strings, instruction messages and owner IDs. Nested
panic/format metadata objects remain outside that data check. The mutation test
changes an instruction message while preserving `.text` and confirms that the
separate literal check rejects it.

## Source controls

Only two field types change in one source file; the constraints and both
handler bodies remain unchanged. All other 35 input files are identical to the
[sweep parent](../fees-sweep-context-ownership/README.md).

| Context variant | Unique pairs | Unmatched | New complete bodies |
| --- | ---: | ---: | ---: |
| Parent control, reused | 385 | 53 | 0 |
| Own event authority only | 385 | 53 | 0 |
| Own program only | 385 | 53 | 0 |
| Own both | 388 | 50 | 3 |

Both single-field controls preserve prior coverage but recover no complete
body. Only the two-field variant is carried forward. The previous initializer,
sweep and crank bodies and their explicit remaining call frontiers are retained,
as are the tier-copy and common-helper panic-location contracts.

## Build and validation

The fresh pinned Linux v1.44 candidate is 863,728 bytes, SHA-256
`f5d786a94c1469a498006934a7e124dd9291a7d91f62c653938800dc847c2795`.
All three builds, source maps, logs and artifacts are retained. The full
partition is **118 raw-local / 417 normalized-only / 50 unmatched**.
Remaining windows span 276,000 / 799,648 original text bytes (34.5%). Call
refinement yields 452 correspondences: 388 unique plus 64 additional duplicate
pairs, leaving 83 duplicates unattributed. The ledger has 2,938 bound-target
edges and 19 different-body frontier edges. Whole-file equality remains false.

Fresh regression passes 17,331 cases across 18 suites; 1,542 exact
outcome/log/compute comparisons; and 24 growth, 32 optional-account, 20 user-ID,
8 extension-log and 30 crank-mint cases. Each harness retains its observation
limits. Selected source and checkpoint artifacts are unchanged.

Run `python3 -B research/fees-buyback-update-ownership/verify.py` and
`python3 -B research/fees-buyback-update-ownership/test_scope.py` to recheck the
retained evidence. These commands do not rebuild or execute target programs.

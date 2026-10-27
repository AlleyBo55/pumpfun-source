# Fees: recover the reachable FeeTier reserve helper

Appending one real reserve call to the existing `upsert_tiers` capacity check instantiates the original 40-byte-element allocator helper at **54864**, a complete **368-byte relocation-normalized match**. The statement reserves only the positive difference between the requested final length and the current length. All other source bytes and source-line positions are preserved.

| Evidence | Control | Proposal |
| --- | ---: | ---: |
| Unique structural body pairs | 359 | 360 |
| Unmatched original windows | 79 | 78 |
| Candidate windows | 583 | 584 |
| Unique raw-equal local pairs | 59 | 59 |

There are no lost body pairs. The new reserve helper is **not raw-equal**: its two local CALL immediates differ. The standalone checker decodes those calls and proves that they reach the already matched `finish_grow` and `handle_error` bodies, checks the two 40-byte multiplication literals and allocation-bound literal, and independently finds the reachable candidate call from `upsert_tiers`. It also decodes the two original helper calls from 4160-byte state methods at 261816 and 265976. Those complete original callers remain unmatched; a recovered allocator body does not establish their behavior or historical source.

The complete proposal passes **17,331 differential cases across 18 suites** and **1,542 exact outcome/log/compute comparisons**. Identical control receipts are reused explicitly from [PR #143](https://github.com/lalalune/pumpfun-source/pull/143). Finite corpus agreement does not prove all behavior, particularly allocation failure and other untested input combinations.

```sh
python3 research/fees-tier-reserve/verify.py
python3 -I research/fees-tier-reserve/verify.py
```

All 34 source inputs per build, complete artifacts and symbols, actual build logs, launch/results, full receipts and fresh strip replays are retained. The checker verifies exact one-statement source delta, every source hash, all inferred candidate extents against symbol aliases and 187 unchanged harness hashes. Rebuild from the experiment source revision and complete source overrides with official Linux platform-tools v1.44, canonical `sbpf-solana-solana` and `RUSTFLAGS=-Zremap-cwd-prefix=`, using the retained launch commands; strip with the pinned v1.52 tool. Recorded logs and hashes are evidence, not authenticated process traces.

Structural signatures mask actual relocated LDDW addresses and local CALL immediates while retaining scalar/register/stack/branch bytes and import identities. Whole-capture and ELF-extent equality remain false, and whole-file identity for the four core programs remains **0/4**. This packet does not modify selected programs, pinned scripts, workflows, root attributes or checkpoint ledgers. Upstream PR #142 independently recovers a fee-total predicate on the earlier legacy-sharing source; its additional match has not been assumed in this packet. Combining that source is the next separate experiment.

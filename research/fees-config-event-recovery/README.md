# Configuration event ownership and admin source

Four public configuration caller windows now have complete normalized body
matches: `update_fee_config` (2608 bytes), `update_stable_fee_config` (2568 bytes),
`upsert_fee_tiers` and `upsert_stable_fee_tiers` (2528 bytes each). Only these four
handlers' event construction changes. The other 34 build inputs are unchanged.

The first experiment removes `event.clone()` from `emit!`, which borrows its
argument. This removes unnecessary vector allocation/cleanup but leaves each
body 16 bytes too long. The final experiment reads the event's admin value from
`fee_config.admin`, matching the inline field loads instead of following the
signer's two pointers. Each relevant account declaration has the unchanged
`has_one = admin` constraint, which already requires those values to agree on
the accepted instruction path. Final body sizes and instructions match.

| Build | Unique pairs | Ambiguous original windows | Unmatched |
| --- | ---: | ---: | ---: |
| Reused PR #146 parent | 366 | 147 | 72 |
| Borrow event for logging | 366 | 147 | 72 |
| Stored configuration admin | **368** | **149** | **68** |

The upsert bodies share a normalized shape, so they are not two new *unique*
structural pairs. Their outgoing calls disambiguate them: exactly one candidate
per original reaches matching callee bodies at all call offsets. The wrong
upsert counterpart conflicts at three call offsets. All **49 direct local
calls** across the four correct pairs have complete callee-body counterparts.
This packet records that outgoing-callee attribution separately; the global
incoming-call refinement independently identifies the same two upsert pairs.

## Evidence and limits

Both experiments were freshly compiled with the unchanged official Linux v1.44
compiler, canonical target, locked inputs and existing root path remaps. The
control binaries and build record are explicitly reused from PR #146. Each new
build records an actual root compiler invocation and unchanged before/after
source hashes. Exact source substitutions and all 35 input bindings are checked.

The final candidate passes fresh **17,331 comparisons in 18 suites** and the
**1,542-case exact outcome/log/compute matrix**. No separate runtime acceptance is
claimed for the intermediate borrow-only build. The broad suites retain their
own compared-field and finite-coverage limits. Neither normalized bodies nor
callee-body correspondence prove all referenced data or transitive semantics.

Whole-capture and meaningful-ELF equality remain false. Selected program sources,
checkpoint pins, matcher masks and the existing account constraints are unchanged.
The remaining 68 original windows and whole-program identity still need work.

```sh
python3 -B research/fees-config-event-recovery/verify.py
python3 -I -B research/fees-config-event-recovery/verify.py
python3 -B research/fees-config-event-recovery/test_scope.py
```

Rebuild by materializing the source maps in `experiment.json` and using the
recorded command/environment with local container paths. The scratch driver is
retained as workflow evidence, not a turnkey SDK installer. Keep source whitespace
and line positions intact.

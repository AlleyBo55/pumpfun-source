# Complete normal and stable tier-update bodies

The two **4,160-byte** bodies at original addresses **261816** and **265976**
now have complete normalized counterparts. They cover replacement and upsert:
check nonempty input and offset, construct a temporary tier vector, enforce the
50-tier limit, validate all fee totals and ordering, then replace the stored
vector. The source updates the real configuration and upsert entrypoints.

The same candidate recovers the **368-byte reserve helper at 54864** and the
**200-byte bounds-panic body at 784168**, with no prior match lost. The reserve
helper was independently recovered in [PR #145](../fees-tier-reserve/README.md);
it is counted only once in this combined candidate.

| Source experiment | Unique pairs | Unmatched | Normal / stable body bytes |
| --- | ---: | ---: | ---: |
| Reused PR #144 parent | 362 | 76 | No complete counterparts |
| Temporary vector, `Clone` tiers | 363 | 75 | 4544 / 4544 |
| `Copy` tiers | 364 | 74 | 4144 / 4144 |
| Explicit `usize` limit | 364 | 74 | 4152 / 4152 |
| Aggregate fee-validity predicate | 365 | 73 | 4160 / 4160; normal matches |
| Correct stable-vector receiver and origins | **366** | **72** | **Both match** |

The limit's type matters to the compared-value formatting code. Collecting fee
validity with `all(...)` reproduces the original loop and error placement. The
stable routine accesses the vector at `FeeConfig` offsets 24/32/40, rather than
receiving a vector at offsets 0/8/16. Its error source lines are 436, 438, 458,
464 and 471; the normal routine's are 383, 385, 405, 411 and 418. The checker
reads those literals and source strings from both binaries.

All **57 direct local CALLs** across the four recovered bodies reach complete
normalized callee-body counterparts. This is separately checked after body
normalization, which itself excludes local CALL immediates. It is not a proof
of all callee data, indirect calls, transitive semantics or original symbol
names. Final whole-capture and meaningful-ELF equality still fail.

## Build and behavioral evidence

All five experiments were freshly compiled with the unchanged official Linux
v1.44 compiler, canonical `sbpf-solana-solana`, locked inputs and the existing
root path mappings. Each retained build has an actual root rustc invocation and
unchanged before/after source hashes. The control artifacts and build records
are explicitly reused from PR #144; no fresh control compile is claimed.

The final candidate passes **17,331 original/candidate comparisons across 18
existing suites**, and **1,542 exact outcome/log/compute comparisons**. The first
`Clone` experiment additionally passed 625 configuration and 578 upsert cases.
No broader runtime claim is made for the other intermediate controls. The
broad suites retain their own compared-field and finite-coverage limitations.

The candidate has 35 bound source inputs; only the root module, state routines
and `FeeTier`'s `Copy` derivation differ from the parent. Sources, exact diffs,
compiler logs, artifacts and receipts are retained. No selected program source,
checkpoint pin, captured byte or matcher mask is changed.

```sh
python3 -B research/fees-tier-splice-recovery/verify.py
python3 -I -B research/fees-tier-splice-recovery/verify.py
python3 -B research/fees-tier-splice-recovery/test_scope.py
```

Materialize `experiment.json`'s source maps into separate workspaces to rebuild;
use the recorded commands and environment with local container paths.
`recorded-build-driver.py` preserves the final scratch workflow and is not an SDK
installer. Keep the exact whitespace/source coordinates. The remaining 72
windows, top-level caller shapes, referenced data and ELF layout still need work.

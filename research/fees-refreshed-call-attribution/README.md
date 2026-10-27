# Fees: eight more duplicate-body call attributions

Replaying the existing call-attribution algorithm against the [authority-origin candidate from PR #129](https://github.com/lalalune/pumpfun-source/pull/129) resolves **8 additional original duplicate-body windows**, with no prior duplicate attribution lost. The exact original and candidate CALL instructions supply the witnesses. Names annotate results; names and address order never select a pair.

| Measure | Earlier PR #93 build | Current build |
| --- | ---: | ---: |
| Body-unique structural pairs | 340 | 354 |
| Additional call-attributed duplicate pairs | 53 | 61 |
| Total call-attributed correspondences | 393 | 415 |
| Consistent bound local CALL edges | 2208 | 2485 |
| Different-body frontier edges | 26 | 22 |
| Still-unattributed duplicate windows | 94 | 86 |
| Original windows with no complete body match | 98 | 84 |

The 354 body pairs belong to the source reconstruction checkpoint. **The extra 61 attributions add no machine-code coverage**: their complete body signatures were already present but duplicated. Structural signatures retain scalar/register/stack/branch bytes and import identities, masking only local CALL immediates and actual relocated LDDW addresses. Calls provide correspondence hypotheses, not proof of all opaque data, transitive/indirect calls or program semantics.

The eight new original windows are:

| Address | Bytes | Candidate annotation |
| --- | ---: | --- |
| 12464 | 1024 | `Account<T>::try_from_unchecked` |
| 14480 | 960 | `Account<T>::try_from_unchecked` |
| 16400 | 960 | `Account<T>::try_from_unchecked` |
| 17360 | 1024 | `Account<T>::try_from_unchecked` |
| 27096 | 1024 | `Account<T>::try_from` |
| 33112 | 960 | `Account<T>::try_from` |
| 714624 | 912 | `system_program::allocate` |
| 715536 | 912 | `system_program::assign` |

Refinement converges in two rounds, adding **52 then 9** duplicate pairs. Each promotion has an incoming encoded call from an earlier paired caller, equal complete body signatures and mutually unambiguous forward/reverse proposals. Conflicts with an existing attribution abort the analysis. There are no encoded-call conflicts. Original boundaries remain inferred; all 580 current candidate boundaries and every symbol extent including aliases are independently checked.

## Verify

```sh
python3 research/fees-refreshed-call-attribution/verify.py
python3 -I research/fees-refreshed-call-attribution/verify.py
python3 research/fees-refreshed-call-attribution/test_attribute.py
```

Both complete historical and current binary inventories are recomputed. The earlier result must exactly reproduce PR #93's retained analysis, rather than importing its counts into the new build. Complete source overrides, all 26/34 input hashes, both build results and 187 unchanged harness hashes are retained. Source PR/commit references in `input-provenance.json` bind the current source checkpoint; its build and runtime receipts remain there. This packet performs no new source compilation or target-program execution. The eight unchanged adversarial tests check conflicting proposals, non-injective correspondence, multi-round discovery, names, imports and unreachable duplicates.

There are 57 unique raw-equal local pairs in the current build. Complete raw capture and ELF-extent comparisons remain false; core whole-file identity remains **0/4**. No selected source, pinned script, workflow or checkpoint ledger changes. The 415 total is a correspondence count and is not a completion percentage.

# Relay: residual CPI source trials

This packet banks **53 compiled source trials** against the two remaining CPI
helpers, plus a separate source-only confirmation build. It does **not** recover
another complete window: the accepted research frontier remains **480/492**, with
**12 unmatched** and no whole-file identity.

The useful result is a much narrower Jupiter builder mismatch. Replacing
`remaining.to_vec()` with `remaining.iter().cloned().collect::<Vec<_>>()` reproduces
**308 of the 312 normalized instruction slots** in original window 90, including
the observed vector-allocation code. Only these four 8-byte slots differ:

| Offset within original window | Residual |
| ---: | --- |
| 80 | Stack slot used to save an incoming value |
| 96 | Complementary stack-slot store |
| 1,680 | Stack load/store ordering |
| 1,688 | Complementary stack load/store ordering |

This is an instruction comparison, not a semantic or completion percentage.
The existing matcher masks only actual local CALL immediates and relocated LDDW
addresses; it does **not** mask these four stack instructions. They remain real
residuals. Exact raw bytes, normalized bytes, hashes and all original/candidate
window counts are rederived by `verify.py`.

## Controlled experiments

All trials start from the 56-input [combined source-location recovery](../source-location-recovery/README.md)
and change only `src/settlement_handlers.rs`. No trial is promoted to selected
source or replaces the combined source-location research checkpoint.

| Group | Builds | Result |
| --- | ---: | --- |
| Burn/close destructuring, CPI field order and tail return | 16 | No match for the 2,856-byte original window 109 |
| Burn/close ownership, borrowed mint and individual moves | 16 | No match; together the 32 trials emit 20 distinct normalized helper bodies, 2,760–2,960 bytes |
| Jupiter vector construction | 4 | Iterator clone and mapped clone emit the same near-matching body; `to_owned` and `Vec::from` retain the old body |
| Jupiter instruction-field order, branch spelling and return form | 14 | No complete match; direct return changes the body to 2,080 bytes; all other forms retain the same four-slot residual |
| Jupiter program/authority reference arguments | 3 | No complete match; same four-slot residual |

The body-size range is an observation, not evidence that a shorter body is more
correct. The 32 burn/close variants and other rejected variants have static/build
evidence only; no runtime validation is claimed for them.

## Best partial trial and bounded execution

The iterator-clone candidate is **818,176 bytes**, SHA-256
`007b200e784270f1b9dbe8cc1c15a1553e04b9bbf46344d96ce5d2c082fc0113`.
Its entire inventory retains the same 480 normalized matches, 130 raw local body
matches, 12 unmatched windows and 639 recursively call-shaped pairs. None of
those counts is semantic/data closure. Whole-file equality is false.

Fresh replay of this candidate passes all **536 records / 534 unique fixtures**.
Those are the existing bounded fixtures, not new privileged Jupiter or burn/close
success coverage. Passing them does not validate the changed allocation path,
allocation-failure behavior, or the four residual instructions end to end.

A separate source-only controller rebuilds the identical candidate from the same
56 inputs after the sweep. Its verbose log records the actual root-crate rustc
invocation. The sweep controllers load the original comparison target before
running their loop; this is comparison data, never a compiler input. The final
confirmation driver does not read the original binary. Compilation records and
hashes are retained evidence, not authenticated process traces or proof of the
historical source/recipe.

## Verification and rebuilding

```sh
python3 -B repro/donation-relay/residual-cpi-source-trials/verify.py
python3 -B repro/donation-relay/residual-cpi-source-trials/verify.py \
  --materialize /tmp/relay-jupiter-partial --variant jupiter-iter-cloned
```

Verification uses the parent's installed local-VM dependencies, including
`solders`; an isolated Python environment must install those dependencies too.
The verifier binds the parent packages, reconstructs every source input map,
checks all 53 build logs and artifacts, re-analyzes whole windows, preserves the
four explicit mismatches and checks the retained replay against its exact
candidate. Artifacts are stored by content hash to avoid duplicating identical
outputs. `metadata.json` indexes every variant, and `report.json` contains the
recomputed results.

Use the parent's Darwin v1.48 compiler/linker with official Linux v1.48 target
libraries, locked dependencies and the same canonical `sbpf-solana-solana` target.
The source-only confirmation controller and recorded launch command show the
exact flags. Adjust only output/source directory paths when rebuilding; original
binary bytes must not become compiler inputs. No full Linux compiler reproduction
of this partial trial is claimed.

Next work: resolve the four Jupiter stack-placement instructions under the strict
matcher, then revisit burn/close with ownership/data-flow evidence beyond these
rejected source spellings. Preserve all 12 outstanding windows until a complete
match is actually demonstrated.

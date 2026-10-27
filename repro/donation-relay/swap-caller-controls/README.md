# Swap caller layout and constructor-order controls

The regular `just_swap` body remains unmatched. These six builds retain
**482/492 normalized windows and 130 raw local bodies**, with no gained or lost
matched window. No candidate is promoted.

## What changed and what did not

The compiler's type-layout output is now retained for the reconstructed
`JustSwapV1` and `BurnCloseContext` types. The diagnostic build reproduces the
accepted candidate and symbol image exactly. In this recipe, `BurnCloseContext`
contains five 48-byte AccountInfo values, ordered token, mint, authority,
destination and program.

Mapping the original clone-call operand offsets against the reconstructed
account layout suggests the same construction order. The existing `just_swap`
source constructs program third, requiring an extra 48-byte copy into its
final slot. Moving program to the final initializer removes that extra memcpy
call. This mapping is an inference from the observed offsets; the original Rust
declarations and source text are not established by the diagnostic output.

| Candidate | `just_swap` bytes | Local memcpy calls | Complete normalized match |
| --- | ---: | ---: | --- |
| Layout/control build | 4,456 | 2 | No |
| Reordered burn-context constructor | 4,408 | 1 | No |
| Wire argument struct, early destructuring | 4,528 | 1 | No |
| Wire argument struct, direct field access | 4,408 | 1 | No |
| Wire argument struct, late destructuring | 4,536 | 1 | No |
| Wire argument struct, late field move | 4,536 | 1 | No |

The original body is 4,448 bytes and contains one local memcpy call. Removing
the extra copy is a partial code-generation correction, not recovery of the
whole body. The wire-argument variants test the remaining Vec ownership/copy
hypothesis and do not resolve it. Size proximity is not a matching criterion.

## Fresh bounded replay of the constructor change

Both the original and reordered candidate were executed afresh on the retained
corpus: **536 records / 534 unique fixtures**, with zero comparison differences
and all saved original observations reproduced. The verifier rechecks transaction
signatures, fixture binding, outcomes, account snapshots, inner instructions,
return data and logs using the existing comparison exclusions. Executable image
bytes and metering log numbers are excluded as documented by the parent harness.

This is finite offline evidence. It does not establish privileged success paths,
all alias/allocation behavior, security, whole-file identity or a unique source
recipe. The constructor candidate remains unpromoted because the body still
differs; no new runtime acceptance is asserted for the other source variants.

## Evidence and verification

`report.json` contains decoded direct-call sequences, current compiler layouts,
and full-inventory comparisons. Every build binds 56 source inputs, its actual
root invocation, exact source overrides and stripped/unstripped artifacts. The
layout data describes the reconstructed types, not recovered original debug
information. Four negative layout-parser tests cover offsets, missing types,
inconsistent totals and unsupported records.

```sh
python3 -B repro/donation-relay/swap-caller-controls/verify.py
python3 -B repro/donation-relay/swap-caller-controls/test_layouts.py
python3 -I -B repro/donation-relay/swap-caller-controls/verify.py --static
```

Full verification requires the existing `solders` runtime for signature and
receipt checks. `--static` requires only the standard library and explicitly
skips signed-receipt validation. Neither command compiles or executes the target
program. The saved replay runner records the actual fresh executions. All six
builds use the Darwin v1.48 compiler and Linux v1.48 target libraries; no new
Linux-compiler reproduction is claimed.

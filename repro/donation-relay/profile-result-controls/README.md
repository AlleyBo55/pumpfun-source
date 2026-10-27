# Root-profile and Result-helper controls

These twelve builds add no new original body match. The accepted Relay frontier
remains **482/492 normalized windows, 130 exact local bodies and ten unmatched**.
No experimental candidate is promoted.

## Root compiler settings

Source bytes and dependency settings are fixed. Each override applies only to
the root crate, after Cargo's normal flags; these are not complete-workspace
profile or LTO experiments.

| Root override | Normalized windows | Lost from 482 | Gained | Raw local windows |
| --- | ---: | ---: | ---: | ---: |
| Control: opt-level 3 | 482 | 0 | 0 | 130 |
| opt-level 2 | 382 | 100 | 0 | 128 |
| opt-level s | 316 | 166 | 0 | 89 |
| opt-level z | 314 | 168 | 0 | 88 |
| codegen-units 2 | 372 | 110 | 0 | 128 |

The control reproduces the preceding candidate and symbols exactly. Changing
these root settings does not recover any of the ten residual windows; it loses
previous matches. This excludes the tested settings with this source/library
recipe, not every compiler profile or historical build recipe.

## Error helper return-type controls

Seven source builds test out-of-line error helpers returning `Result<T>` or
`Result<()>`, including epoch increment assignment through a match, inline
function, map-or expression or if-let. The generic helper is applied to epoch
close, the shared donation worker, and then both. All seven retain the same 482
matched original windows. Neither business body is recovered.

A useful limit on attribution is reproduced: the `Result<()>` helper compiles
to the **same 504-byte normalized body as original window 115**, which already
has a counterpart from `From<ErrorCode> for Error`. Thus local normalized bytes
alone do not establish a unique original Rust return type. The generic
`Result<u64>` and `Result<u128>` helpers instead produce different 488- and
496-byte bodies. The explicit no-inline annotation retains the tested helper
boundary; its presence in historical Rust is not established.

This is additional interpretation of an already-matched helper, not an extra
recovered window or proof of transitive semantics. Caller instructions and
input/output contracts remain part of the evidence needed to identify a helper.

## Evidence and verification

Every build binds all 56 source inputs, its actual root compiler invocation,
source-unchanged check, and stripped/unstripped artifacts. Only three named
source files may differ in the helper trials; all other source inputs remain
bound to the burn/close checkpoint. Profile controls change no source file.
`report.json` records complete-inventory gains/losses and helper-body comparisons.

```sh
python3 -B repro/donation-relay/profile-result-controls/verify.py
python3 -I -B repro/donation-relay/profile-result-controls/verify.py
python3 -B repro/donation-relay/profile-result-controls/verify.py \
  --materialize /tmp/relay-result-control --variant unit-error-helper-epoch
```

The standard-library verifier reanalyzes the binaries; it does not compile or
execute them. The tested recipe uses the Darwin v1.48 compiler and Linux v1.48
target libraries. No fresh Linux-compiler or target-runtime acceptance is claimed
for these rejected variants. Saved controllers retain the build procedure;
adjust workspace paths before rebuilding.

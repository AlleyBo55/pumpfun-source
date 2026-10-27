# Epoch-close field and error-result controls

These **14 compiled source experiments** do not recover the 4,000-byte original
epoch-close body (ordinal 96). All retain **482/492 normalized matches, 130 raw
local bodies and the same ten unmatched windows**, with no match gained or lost.
No candidate is promoted.

| Source family | Builds | Question tested |
| --- | ---: | --- |
| Cached configuration/mint fields | 6 | Retain either/both fields by reference or by copied value across distribution initialization and signer-seed construction |
| Error conversion type | 3 | Convert the checked-add error eagerly/lazily to Anchor Error, or lazily retain the code enum |
| Intermediate Result shape | 5 | Map the error, construct a default Result, bind a typed Result, or call an automatic/forced-inline Result helper |

The field-cache hypothesis came from the original reusing a configuration-field
address after initialization. The error hypothesis came from the original's
branch after its overflow-error conversion. Most attempted error-source changes
compile to the same candidate body; the eager conversion changes code without
matching the original. These observations exclude the tested source forms under
this recipe, not every equivalent Rust expression or compiler input.

The packet retains the exact source snapshots, all 56-input maps, actual root
compiler invocations, source-unchanged checks, and stripped/unstripped artifacts.
Identical artifacts are stored once. Only the epoch-close prefix of
`src/settlement_handlers.rs` is changed; the remaining source is checked against
the existing burn/close checkpoint.

```sh
python3 -B repro/donation-relay/epoch-source-controls/verify.py
python3 -I -B repro/donation-relay/epoch-source-controls/verify.py
python3 -B repro/donation-relay/epoch-source-controls/verify.py \
  --materialize /tmp/relay-epoch-control --variant epoch-error-type-lazy-anchor-error
```

The standard-library verifier rechecks all source/artifact hashes and recomputes
the complete function inventory and target body comparisons. It does not compile
or execute a target program. These experiments use the existing Darwin compiler
and Linux target-library recipe; no new runtime acceptance is claimed for
rejected variants. The accepted checkpoint's bounded runtime evidence remains
in its owning package.

## Separate compiler-substitution control

An additional build keeps the same 56 source inputs, v1.48 Cargo and linker, and
Linux v1.48 target libraries, but substitutes the cached Darwin v1.50 Rust
compiler. Its launcher and compiler-driver hashes differ from v1.48 even though
both report Rust 1.84.1-dev / LLVM 19.1.7.

The output has **226/492 normalized matches and 108 raw local matches**: it
loses **256** previous normalized matches and gains **none**. Epoch close is
still unmatched. The 800,608-byte stripped output has SHA-256
`8adb66cdae050753a73b21fbe75689ebdaba6aa51976d7388ea1ad165d6ac526`.
It is rejected. The accepted frontier remains 482/492.

`compiler-control/` retains the invocation, complete compiler log, source-map
check, version output, tool/driver fingerprints and independently recomputed
frontier change. Its two binaries are in the content-addressed artifact store.
This is a controlled substitution using old target libraries, not a claim about
all v1.50 build recipes or the historical compiler. No runtime validation is
claimed for this rejected output.

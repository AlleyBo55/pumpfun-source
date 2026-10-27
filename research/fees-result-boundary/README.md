# Fees buffer consumption and Anchor result boundary

Consuming the checked buffer in place recovers the complete first-account parser
instruction body after masking only encoded CALL immediates and two verified
constant addresses. Returning Anchor results from the legacy layout parsers also
recovers the downstream decoder's 2,648-byte extent and improves its instruction
alignment. Both remain source experiments, with no selected-source promotion.

## Complete bounded parser comparison

The captured first-account helper is the inferred window `[36072, 37320)`. The
candidate symbol is 1,248 bytes and contains 143 decoded instructions, counting
LDDW as one instruction. Its entire instruction stream equals that original
window after masking precisely these differing operands:

- 12 encoded CALL immediate words;
- two LDDW addresses, each referring to an equal 32-byte constant in both images.

Every opcode, register, branch displacement, stack offset and other literal
matches. The discriminator and invalid-data values remain significant. No stack
or register normalization is applied to obtain this result. The raw window still
differs at the enumerated operands; resolved CALL behavior and whole-program
identity do not follow from this bounded comparison.

The candidate query parser's first encoded CALL reaches a 200-byte wrapper whose
last encoded CALL reaches this helper. That wrapper also matches the original
after CALL-immediate masking. The checker binds this incoming chain to candidate
symbols and the captured query → wrapper → account-parser chain, rather than
attributing the match from a similar generic helper alone.

The decisive checked-deserializer change is:

```rust
*buf = &buf[8..];
Self::try_deserialize_unchecked(buf)
```

The preceding experiment passed a new local body slice. Updating the passed slice
instead reproduces the original allocation and lifetime of its descriptor in
the enclosing Account parser. The checker establishes emitted-byte equality
under the stated masks; exact historical Rust text is not recovered.

## Downstream result-boundary reconstruction

The original decoder window `[257264, 259912)` contains 325 reachable instructions
with no non-call successor outside the window. Its three allocation layouts use
body thresholds 2,504, 4,065 and 4,089.

Giving the legacy parser methods an `anchor_lang::Result` return type preserves
their error conversion boundary before upgrading their decoded state to the
current FeeConfig. It increases call-masked sequence matches from 112 to 236
instructions and reproduces the original 2,648-byte extent and 325-instruction
count. It also has 13 encoded calls, including six candidate-symbol-bound I/O
error conversions. Original names remain inferred.

| v1.44 decoder form | Bytes | Instructions | Call-masked sequence matches |
| --- | ---: | ---: | ---: |
| Derived layout result, then conversion | 2,488 | 305 | 112 |
| Field-by-field reads in one function | 2,472 | 304 | 104 |
| Legacy parser returns Anchor result | 2,648 | 325 | 236 |
| Upgrade with Result::map | 2,648 | 325 | 210 |

The fixed Anchor-result source emits the same 2,648-byte extent and 236 matching
sequence instructions with v1.44, v1.45, v1.46 and the supported-target v1.46.1
experiment. `analysis.json` enumerates non-call operand differences between those
compiler outputs. These controls do not resolve the remaining decoder gap or
identify the historical compiler.

The v1.46.1 supported-target account helper is 1,384 bytes and has a different
instruction shape. The two-address normalization is marked inapplicable for that
probe; the complete normalized parser match above is the v1.44 consuming-buffer
candidate. The supported-target adaptation is an additional recipe variable.

The score uses `difflib.SequenceMatcher` after zeroing only encoded CALL immediate
words. It is an alignment measurement, not a function-match or equivalence
criterion. The decoder retains block-placement, register, stack and literal
differences. In particular, equal extent and instruction count are insufficient
for byte identity. The packet retains the alternatives and compiler comparisons
rather than selecting a new checkpoint from these scores.

## Validation and limits

The Anchor-result candidate and the consuming-checked-buffer candidate each pass
all 17,331 cases across the existing 18 Fees suites with zero reported mismatches.
Compiler and mapping probes carry only the behavioral receipts explicitly bound
to them in `experiment.json`. Each report preserves its own scope. No behavioral
acceptance is claimed for a static-only probe.

Each stripped ELF is bound to its symbol ELF by equality of the entire `.text`.
All 26 source input hashes and 187 harness hashes are retained. The 252 locked
registry archives were verified, and all 7,936 regular files in them were compared
against the extracted source used for compilation with zero differences. The
source-file-map digests and counts are retained in the dependency receipt.

These deserializers accept and consume a discriminator-free body at the unchecked
boundary. Public unchecked calls using the selected full-buffer convention are
not claimed equivalent. Tests exercise bounded on-chain entrypoints in local
LiteSVM instances, not every possible Rust API call or program input.

All candidate complete files still differ from both the captured allocation and
its ELF extent. Core raw identity remains 0/4. CALL destinations, global data
layout, remaining decoder instructions and other program windows still require
reconstruction. No captured bytes enter compilation, linking or stripping.

## Verify and rebuild

```sh
python3 research/fees-result-boundary/verify.py
```

The checker uses Python's standard library and the unchanged ELF reader. It
recomputes the complete normalized parser comparison, the closed original CFG,
decoder measurements, source/artifact bindings and receipt bindings. Verification
does not rerun compilation or transactions.

Source overrides and zero-context review patches are retained under `sources/`.
`consuming-selected.patch` compares the complete proposal to the frozen selected
`types.rs`; `anchor-result.patch` shows the earlier result-boundary step.
The common recipe is recorded in `experiment.json`: one isolated workspace path,
locked/offline Cargo, release profile, platform-tools compile bundle, and v1.52
strip tool. Target source files are unchanged between compiler controls. Build
logs and any alternate launch/result records describe their actual pipeline
differences. Paths, host tools and target spelling are part of provenance.

The v1.46.1 compatibility diagnostics are retained under `attempts/`. Its bundle
advertises the legacy `sbf-solana-solana` target but omits that sysroot directory;
it supplies `sbpf-solana-solana`. Both printed target specifications are equal.
A minimal legacy-target build cannot find core, and the supplied target builds
the same minimal crate. An isolated directory alias still fails because Rust
checks the crate's recorded target triple. These observations do not exclude
v1.46.1 as the historical compiler.

The retained v1.46.1 experiment therefore invokes the bundle's Cargo and rustc
directly with `sbpf-solana-solana`, the same release profile and path-remapping
flag, then strips with v1.52. Its driver and target spelling are explicit recipe
variables. It builds successfully, emits ELF machine 263 / flags 0, and passes
10,838 query cases. Its launch/result records and target diagnostics preserve the
adaptation separately from the legacy-driver attempts. The official compiler
and bundled libraries remain unchanged.

Logs and hashes are ordinary build provenance, not an OS-level process trace.
Program sources, selected binaries, pinned scripts, workflows and historical
acceptance ledgers remain unchanged.

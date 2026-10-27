# Fees account-parser guard and decoder experiments

These controlled source builds recover the captured parser's two error entries
and its discriminator-free decoder call boundary. They do **not** reproduce the
whole deployed binary or establish the original source text. Active program
sources and selected checkpoints are unchanged.

The original window is `[36072, 37320)`, inferred to be 1,248 bytes. Candidate
extents below come from retained symbol ELFs whose complete `.text` equals the
corresponding stripped output used for execution.

| Build | Helper bytes | Separate invalid-data entries | Identical instructions in call-masked sequence alignment |
| --- | ---: | ---: | ---: |
| Unchanged selected source, rebuilt on Linux | 1,144 | 1 | 97 |
| Split the length and discriminator guards | 1,232 | 2 | 128 |
| Split guards plus an inherent body-decoder helper | 1,216 | 2 | 90 |
| Split guards; unchecked decoder accepts the body | 1,248 | 2 | 116 |
| Same body decoder, with a named local slice | 1,248 | 2 | 116 |

The original contains 143 decoded instructions, counting LDDW as one instruction.
The alignment column is a `difflib.SequenceMatcher` measurement with only encoded
CALL immediate words zeroed. It is not a whole-function match count or an
acceptance metric. In particular, the 1,248-byte variants have more stack-operand
differences than the guard-only variant despite recovering the branch layout.

## What the bytes establish

Splitting the combined source guard preserves separate error conversions in the
emitted helper. Both original entries and the split entries load
`0x8000000000000003`; the complete query differential passes for both builds.

The original caller subtracts eight from the length and advances the data pointer
by eight before its decoder call. The decoder at 257,264 checks lengths 2,504,
4,065 and 4,089. The selected unchecked decoder receives the full account and
checks 2,512, 4,073 and 4,097. This supports the additional experiment that moves
discriminator removal into the checked caller and lowers those thresholds by
eight.

That experiment produces the same 1,248-byte helper extent and identical opcode,
register and branch fields at corresponding instruction positions. Every changed
operand is enumerated in `analysis.json`:

- 12 encoded CALL immediates;
- two addresses whose referenced 32-byte constants are equal in both images;
- seven stack-address addends and 18 stack displacements.

The checker verifies these actual fields rather than broadly masking all LDDW
values, branch offsets or immediate operands. The FeeConfig discriminator and
error literals remain significant. Classifying stack offsets does not prove
equivalent stack lifetimes or runtime relocation behavior. Raw helper bytes still
differ, and core whole-file identity remains 0/4.

The inherent-helper probe is retained as a negative result: its compiler-selected
argument passing and stack layout diverge further. Giving the body slice a local
name changes four bytes elsewhere in the symbol ELF and leaves this helper
unchanged. Neither probe is selected.

## Execution and source limits

`receipts/` retains the existing unmodified query/full-suite reports bound to the
actual stripped ELF hashes. Each report preserves its own behavioral limits.
These tests compare original and candidate execution in separate local LiteSVM
instances. They are bounded synthetic cases, not proof of complete equivalence.

The unchanged Linux baseline passes 10,838 query cases. The guard-only and
body-direct variants each pass 17,331 cases across the 18 existing Fees suites,
with zero reported mismatches. The body-named and inherent-helper probes have no
new behavioral acceptance claim.

**The body-direct experiment changes the unchecked decoder's input convention.**
It accepts a body without the discriminator. This matches the observed checked
caller/decoder boundary, but public unchecked calls with full account data are
not claimed equivalent. Passing the handler suites does not authorize promoting
this implementation into the selected source. The files under `sources/` are
isolated experiment inputs and unapplied review patches.

## Reproduce the evidence check

```sh
python3 research/fees-guard-experiment/verify.py
```

This requires only Python's standard library, the unchanged `scripts/analyze.py`
ELF reader, and the 26 repository source files listed in `experiment.json`. It
checks packet hashes, ELF hashes and `.text` binding, candidate symbol extents,
all classified operands, source hashes, and differential receipt bindings. It
does not rerun compilation or transaction execution.

## Build provenance and replay

`experiment.json` records the complete 26-file source maps, executable hashes,
release-archive hashes/URLs, recorded SDK hash, common compiler command and
workspace/environment paths. All 252 registry crate archives were checked
against the locked checksums; the individual results are retained. Cargo used
`--locked --offline` for every build.

Compilation uses Linux platform-tools v1.44 and the retained Agave 2.1.21 driver.
The unchanged recorded SDK's strip script installs and uses platform-tools v1.52.
This deliberately follows the retained two-phase pipeline rather than treating
the strip tool as the compiler. The SDK archive is already retained at
`repro/pump_fees/linux-recorded-pipeline-correction/recorded-sdk.tar.gz`.

To replay, materialize the 26 baseline files from the recorded source revision in
one isolated workspace. Configure Cargo/Rustup and the official tool caches using
the recorded binaries; extract the retained SDK. Run the common recipe with the
listed environment. For each variant, replace only
`programs/pump-fees/src/types.rs` with its retained override, preserving the same
workspace path and Cargo target directory. Save the stripped output and the
unstripped target ELF before the next build. Compare both complete files to the
hashes in the descriptor. Paths and host tools are part of the recorded local
recipe; a different environment needs an independent comparison, not an assumed
raw-output match.

The first successful baseline used a fresh target directory. After all four
variants, restoring the exact original source reproduced **both** baseline ELF
files byte for byte (`cmp`, exit 0). The retained baseline log is this successful
replay; subsequent variant builds reuse the same locked dependency artifacts.

Earlier attempts failed before a usable baseline: process tracing was denied;
one compilation exited without a retained diagnostic; a later attempt found
unresolved generic symbols in cached Anchor proc macros. A fresh target directory
built successfully. The root cause of those cached artifacts is unproven. No
OS-level process trace is claimed. The retained logs and executable hashes are
ordinary build provenance, not an authenticated syscall trace.

# Fees allocation-layout decoder reconstruction

This source experiment recovers the downstream decoder's early allocation-size
branches and caller-slice consumption. It retains compiler and local-variable
probes that did not resolve the preceding account parser's stack layout. No
active source, selected candidate, script pin or historical checkpoint changes.

## Decoder evidence

The checked account parser calls encoded target 257,264. The next greater encoded
CALL entry in the captured `.text` is 259,912. That 2,648-byte window contains 325
decoded instructions: all are reachable from its entry, and every non-call
successor stays on an instruction boundary inside the window. This supports a
bounded decoder extent; it does not recover a historical symbol or prove the
runtime meaning of every encoded call.

The captured decoder first rejects body lengths below 2,504. It chooses among
the legacy, stable-fee and full layouts at lengths 4,065 and 4,089, before parsing
their fields. In its first layout path it updates the incoming slice descriptor's
length and pointer before the first decoder call. The prior reconstruction reads
through a local slice copy and checks extension sizes during a shared parse.

`sources/versioned.patch` replaces that shared parse with three derived layout
decoders and their conversions to the current FeeConfig. It preserves the
previous experiment's checked-caller discriminator removal. The private legacy
type names are reconstruction choices, not names recovered from the original.

| Decoder build | Bytes | Decoded instructions | Matching instructions in call-masked sequence alignment |
| --- | ---: | ---: | ---: |
| Original inferred window | 2,648 | 325 | — |
| Prior body decoder, v1.44 control | 1,552 | 185 | 19 |
| Same source, v1.45 control | 1,552 | 185 | 19 |
| Early local-slice probe, v1.44 | 1,552 | 185 | 19 |
| Three layout decoders, v1.44 | 2,488 | 305 | 112 |
| Three layouts, field-by-field conversion, v1.44 | 2,472 | 304 | 104 |

The new decoder also emits the two incoming-slice stores at relative offsets 240
and 256, as in the captured prefix. `analysis.json` records their actual
instructions. The prefix check tracks unchanged copies of the incoming r2
pointer only until the first CALL; it does not claim a complete memory analysis.

The alignment measurement masks only encoded CALL immediate words. Registers,
branch offsets, stack operands and literal values remain significant. The score
is not a count of matching functions or a proof of equivalence. The new decoder
still differs in size, instruction scheduling, register use and stack layout.
No decoder or whole ELF is byte-identical; core identity remains 0/4.

The field-by-field probe converts each fallible read into an Anchor error rather
than converting the aggregate result of a derived layout decoder. It reproduces
the original window's 13 encoded calls; the derived-layout variant has ten.
Candidate target symbols identify six I/O-error conversions in the field-by-field
probe versus three in the derived-layout probe. Original target names remain
inferred, and these call-count similarities do not establish equivalence. The
field-by-field result is retained because it improves one structural observation
while worsening the byte-alignment measurement.

## Negative controls and remaining account-parser gap

The v1.45 build uses the exact same 26 source-file hashes as the v1.44 control and
a fresh Cargo target directory. Its 1,248-byte account parser is equal to the
v1.44 parser after masking CALL immediates and the two verified addresses of equal
32-byte constants. Its stack offsets therefore preserve the same mismatch with
the original. This does not exclude v1.45 as the historical compiler; it only
shows that this source/recipe change does not fix the local gap.

Moving the local slice declaration earlier also changes stack allocation without
reproducing the original. That static probe is retained with no new behavioral
acceptance claim. The three-layout decoder does not resolve the preceding account
parser's stack differences either. These are explicit remaining differences,
not newly accepted normalized function matches.

## Execution scope

The retained v1.44 control and versioned-decoder outputs each pass all 17,331 cases
in the existing 18 Fees suites with zero reported mismatches. The v1.45 control
and field-by-field probe each pass the 10,838-case query suite. Each receipt is
bound to the retained stripped
ELF's SHA-256, and each stripped ELF's entire `.text` equals its symbol ELF.
Reports preserve the test suites' own limits. Synthetic differential cases do not
establish complete program identity or a security audit.

As in the [preceding study](https://github.com/lalalune/pumpfun-source/pull/75),
the unchecked decoder in these variants accepts a discriminator-free body.
The new versioned decoder additionally consumes the passed slice. Public calls
to the selected unchecked implementation are not claimed equivalent. These
experiment sources require review before any selection change.

## Verification and replay

```sh
python3 research/fees-layout-decoder/verify.py
```

The checker uses Python's standard library and the unchanged pinned ELF reader.
It recomputes artifact bindings, source/harness hashes, original CFG reachability,
decoder measurements, cursor stores, compiler-control comparison and receipt
bindings. It does not rerun compilation or transaction execution.

`experiment.json` records the source maps, shared v1.44 build recipe and tool
hashes. The v1.45 official release URL, archive hash and launch/result records are
retained separately. Both compilers are Linux x86_64 platform-tools releases.
Compilation uses the named v1.44/v1.45 bundle; the unchanged recorded SDK strips
with v1.52, following the earlier study's retained two-phase recipe. The v1.44
builds reuse its locked dependency artifacts. The v1.45 build uses a fresh target
directory and `--locked --offline`; its launch/result record binds unchanged
source input hashes before and after compilation.

For a replay, materialize the 26 files from the recorded source revision in one
isolated workspace, replace only `types.rs` with a retained variant, and run the
recorded compiler/SDK recipe. Preserve the same workspace path within each
controlled comparison. Retained logs and hashes are ordinary provenance, not an
OS-level process trace. Paths, compiler release and host environment must be
accounted for before assuming raw-output reproducibility.

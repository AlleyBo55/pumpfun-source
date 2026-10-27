# Raw-gated Metaplex Utilize compiler traces

The [final selection-input follow-up](isel-boundary/README.md) adds a second
raw-identical run: CodeGen Prepare's output equals the exact final input to
selection, and the combined predicate expands into separate branches during
SBF selection before finalization. The six-stage evidence below is retained.

The candidate 11 remaining-use guard already branches to the error path in
machine IR immediately before `finalize-isel`. Its direction is also present
after finalization, branch folding, block placement and the SBF pre-emission
peephole. This supplies actual compiler observations for the earlier
[static branch-selection audit](../../repro/metaplex/branch-selection-audit/README.md).

The trace is attributable to candidate 11 because the fresh traced build's
**raw output is exactly 707,448 bytes**, SHA256
`3bbaf27ff0c10ff68d8a195a82f39eadee266f324067bd0a66081710be30b4ec`.
There is no output padding, rewriting or normalization. This is the same raw
gate established by [PR 60](https://github.com/lalalune/pumpfun-source/pull/60).
This package is self-contained and does not require that PR's files.

## Observed stages

The function is
`_ZN14token_metadata9processor4uses7utilize15process_utilize17h9789c7990f4c0b83E`.
The [analysis](analysis.json) records byte offsets and one-based line numbers
into the complete 51,216,417-byte stderr log. The six linked snapshots are
unmodified, complete function dumps extracted from that log, not new compiler
inputs.

| Snapshot | Guard and taken edge | Other edge |
| --- | --- | --- |
| [Before CodeGen Prepare](snapshots/before-codegenprepare.txt) | `%233 = icmp ult i64 %232, %4`; the combined guard branches to error block 239 | Block 243 subtracts requested `%4` from remaining `%232` |
| [Before Finalize ISel](snapshots/before-finalize-isel.txt) | Block 83: `JUGT_rr %47:gpr, %22:gpr, %bb.36` | Explicit jump to success block 38 |
| [After Finalize ISel](snapshots/after-finalize-isel.txt) | Same virtual-register guard and error block | Explicit jump to success block 38 |
| [After branch folding](snapshots/after-branch-folder.txt) | Block 32: `JUGT_rr $r9, $r7, %bb.34` | Explicit jump to success block 37 |
| [After block placement](snapshots/after-block-placement.txt) | Block 35: `JUGT_rr $r9, $r7, %bb.39` | Success block 36 is the fallthrough |
| [After SBF pre-emission peephole](snapshots/after-preemit-peephole.txt) | Same physical-register guard and error block | Same success fallthrough |

The requested-use value is the fifth physical argument: `%47` is copied from
`r5`, later held in `r9`. The remaining value is loaded through IR pointer `%231`:
virtual `%22` from stack object 26 at offset 8, later physical `r7` from
`[r10 - 184]`. The successful successor subtracts requested from remaining;
the error successor stores error 86 (`0x5600000000` in the packed return).
The verifier checks those bindings as well as the branch mnemonic, so a nearby
total-use or approved-authority guard cannot substitute for this one.

The final raw instruction at file offset **238832** is
`2d79120000000000`: unsigned `r9 > r7`, taken to error offset **238984**,
with success at **238840**. The static audit records the deployed instruction
at the same offset as `3d97070000000000`: unsigned `r7 >= r9`, taken to success
at 238896 with the error path as fallthrough. These complementary conditions
do not by themselves establish a behavioral difference.

The optimized IR already expresses remaining < requested as part of the
error predicate. The first captured **machine** snapshot shows requested >
remaining before finalization. The snapshot after block placement shows the
success path moved to fallthrough while preserving that condition. The
observations rule out a direction introduced only by the final SBF peephole
for this invocation. They **do not identify the first pass that introduced
the direction**, observe every intervening pass, or show the deployed build's
IR. CodeGen Prepare and instruction selection still lie between the first
two captured snapshots.

## Build and compiler provenance

[Run 40343712336](https://github.com/startrack3r/pumpfun-source/actions/runs/40343712336)
completed successfully at controller revision
`6125ce9e1d2c801d5e9c6f911eae4df5e5e4c837`.
The exact 53-member artifact ZIP is retained as `40343712336.zip`, SHA256
`c5eeca041127129b539bf094e19add33f71045c8bc797bc2e56412c51cfe8030`.
`receipt.json.gz` retains provider metadata and executed-source Git blob bindings;
`hosted-job.log.gz` retains the successful three-test wrapper run.

The source remains Metaplex revision
`17e99434af5ead3e989c08f32af33609821d0bc0` plus the exact candidate 11 patch.
All 812 baseline and 812 patched source files match the historical manifests.
The full source archive, including its upstream LICENSE, is retained. The
source, lockfile, image, tools archive and driver pins are in [trace.py](trace.py).
The build uses the pinned verifiable-build image, SDK 1.16.25 and authenticated
platform-tools v1.37. Both before/after driver hashes are
`e7d221509c0d5f5430175547b6d972e300892258bfa6e1b0cf1c4058a73ad9f2`.

The wrapper only adds these observations to the `token_metadata` link-producing
rustc invocation, preserving dependencies and metadata probes unchanged:

```text
-Cllvm-args=-print-before=codegenprepare,finalize-isel
-Cllvm-args=-print-after=finalize-isel,branch-folder,block-placement,sbf-mi-pemit-peephole
```

The actual compiler's hidden-option help is retained. The full NUL-delimited
invocation is `rustc-4272.argv` inside the artifact, also rendered verbatim as
[compiler-argv.json](compiler-argv.json). It includes `opt-level=z`,
`codegen-units=1`, `overflow-checks=on`, `strip=symbols` and
`-Zremap-cwd-prefix=`. It specifies no `target-cpu` or `target-feature` override;
this does not identify a historical deployment CPU selection.

The pass names follow the pinned LLVM gitlink
`7b8db05b564faffb522434b73b7082662171f94a`, including
[FinalizeISel](https://github.com/solana-labs/llvm-project/blob/7b8db05b564faffb522434b73b7082662171f94a/llvm/lib/CodeGen/FinalizeISel.cpp)
and [SBF pre-emission registration](https://github.com/solana-labs/llvm-project/blob/7b8db05b564faffb522434b73b7082662171f94a/llvm/lib/Target/SBF/SBFMIPeephole.cpp).
`finalize-isel` expands pseudos produced by selection; the captured snapshot
before it already contains SBF machine instructions.

Dependency acquisition authenticates 537 registry archives against Cargo.lock
and the sole Git dependency's exact revision. Compilation is then separate,
with container networking disabled, `CARGO_NET_OFFLINE=true`, and both build
offline flags. No captured executable is mounted and no program is replayed.
The executed fork-only workflow is inside the ZIP as evidence, not installed
as an upstream workflow.

**Retained SDK failure:** after successful compilation, the SDK's optional
Criterion v2.3.3 acquisition fails DNS resolution in the offline container.
The build wrapper returns zero and the raw identity gate passes. Complete
stderr and the verifier preserve this limitation; not every SDK subprocess
succeeded. Earlier pre-compiler acquisition/setup failures remain in PR 60.

## Offline verification and reproduction

From the repository root, with Python 3.11+ (Git is needed for patch replay):

```sh
python -B research/metaplex-utilize-trace/verify.py --replay-patch
python -B research/metaplex-utilize-trace/test_verify.py
python -B research/metaplex-utilize-trace/test_wrapper.py
```

The wrapper tests execute only on Linux. They passed on the recorded hosted
runner; Windows reports skips for these three tests. The portable verifier
checks artifact/run/source bindings, all complete source manifests, lockfile
archive checksums, offline container settings, raw binary identity, exact
compiler arguments, extracted snapshots and derived guard edges. Its analyzer
is deliberately specific to this evidence, not a general IR interpreter.

To repeat the source experiment on an isolated Linux x86_64 Docker runner:

```sh
python -B research/metaplex-utilize-trace/trace.py --output /fresh/experiment/path
```

The output path must not exist. Public input acquisition needs network access;
program compilation runs offline. Any future trace whose raw output fails
the candidate 11 gate must be retained as a different experiment and cannot
inherit these conclusions.

This is a provenance and attribution increment. The 1,509 differing positions
in the existing padded allocation-image comparison remain (1,477 text bytes,
30 coordinate bytes and two relocation bytes). There is no deployed raw
identity, historical compiler/source identification or security claim here.
The final selection-input follow-up narrows the remaining interval. Historical
source/compiler evidence or internal DAG decisions are still needed to explain
the deployed layout. These observations do not justify a flag or source-layout
sweep.

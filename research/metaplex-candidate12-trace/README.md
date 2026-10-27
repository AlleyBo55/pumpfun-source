# Why the retained candidate12 keeps an extra Utilize jump

A fresh diagnostic build reproduces the previously rejected candidate12 exactly:
**707,448 raw bytes**, SHA256
`4f039033a3cde9d47aa8ee0f68c13c2c4d55a9d6ee0ab50df9d4ef93a4a02edf`.
This captures a contrast with the candidate11 traces in
[PR62](https://github.com/lalalune/pumpfun-source/pull/62). It does not introduce
a source variant or improve the deployed-byte match.

Both historical patches replay to all 812 source hashes. Exactly one source
file differs: `programs/token-metadata/program/src/processor/uses/utilize.rs`.
Candidate12 removes the explicit remaining-use condition from the unified
zero/total/remaining guard and retains checked subtraction. The complete
non-diagnostic rustc argument vectors are identical between the new run and
the retained candidate11 boundary run. Compiler/image/dependency pins follow
the earlier isolated reproduction, including 537 checksum-verified registry
archives and the exact rooster Git revision.

## Observed difference

Candidate11's final LLVM input combines all three checks into one predicate
leading to one error block. Candidate12 instead reaches selection with a
separate remaining-use branch and a second error block. Its complete function
text after CodeGen Prepare exactly equals its final selection input:
61,906 bytes, SHA256
`8df3a10b7bbc3f6260a01c0e83358d20da0729f931e670def85ceb939e82e202`.
The candidate11 function at that point is 61,589 bytes, SHA256
`53c696eb06a494644b27443547e74a0675bc1ae84eff069be0ffb4f0bcfea538`.
These are exact text comparisons with banners excluded, without normalization.

| Candidate12 observation | Remaining-use branch | Other edge and layout |
| --- | --- | --- |
| Final LLVM input | Block235 compares remaining `%237` < requested `%4`; error248, success243 | Zero/total checks separately reach error239. Both error blocks store86. |
| Before and after Finalize ISel | Block36: `JUGT_rr %47:gpr, %22:gpr, %bb.40` | Explicit jump to success39. Next layout block37 is the separate zero/total error; remaining-use error40 is elsewhere. |
| After branch-folder | Block33: `JUGT_rr $r9, $r7, %bb.34` | Explicit jump to success37. All three guards now reach error34, also the next layout block. |
| After block placement and pre-emit peephole | Block35: `JUGT_rr $r9, $r7, %bb.36` | Explicit jump to success39 remains; error36 is next in layout. |

The error destinations converge somewhere between the captured post-finalize
and post-branch-folder points. Several passes run in that interval; this packet
does **not** identify the particular merging pass or capture an internal DAG
decision. The snapshots do establish that the complementary error-taken
condition and explicit success jump survive the later observed stages.

The final raw bytes confirm the same two instructions:

| File offset | Exact bytes | Destination |
| --- | --- | --- |
|238832|`2d79010000000000`|Unsigned r9 > r7 to error238848|
|238840|`0500070000000000`|Unconditional jump to success238904|

The earlier [candidate12 review](../../repro/pump/metaplex-candidate-build-12-review/REPORT.md)
already measured the additional instruction and the resulting address shifts.
This packet adds actual compiler-stage evidence for that rejected output.
It does not repeat its whole-program instruction mapping or turn that mapping
into raw identity. Candidate13's equivalent output and candidate14's equality
with candidate11 remain existing negative experiments, not new source leads.

## Retained evidence and replay

[Run40352331268](https://github.com/startrack3r/pumpfun-source/actions/runs/40352331268)
executed controller commit `9a33ea96c86731faac31d352dacda1545cdf29a5`.
The exact 505,927-byte provider ZIP has SHA256
`eeafc83d3b85a85ce10906c0f34be9149040927732628f66867b9250dac06049` and
contains all 53 members. Complete compiler stderr is 531,662 bytes, SHA256
`a8cb0bd2897e61382e2b348ed1e07f35335b718ca10c229f40b9baeecd2aea3d`.
Eight complete function snapshots are extracted as contiguous log bytes.
Actual NUL-delimited compiler arguments, commands/exits, source manifests,
raw output, workflow, provider metadata and executed-source bindings remain.

`reference/` retains the exact candidate11 boundary artifact and provider
receipt from run40347761346. This lets the comparison validate the previous
raw hash, source delta, actual arguments and final IR without requiring PR62's
files in the checkout. PR62 remains the report for the full previous analysis.
The source archive includes the upstream license. Recipe and build-evidence
checks are adapted from PR62 at `9b861f53e4181d1ee95046d2be5b38dbeaf167b3`.

```sh
python -B research/metaplex-candidate12-trace/verify.py --replay-patch
python -B research/metaplex-candidate12-trace/test_verify.py
python -B research/metaplex-candidate12-trace/test_wrapper.py
```

All 15 portable tests pass on Windows Python3.13.7; all three wrapper tests
pass on the hosted Linux runner and skip on Windows. Mutations cover altered
or padded raw output, branch direction/targets, missing success jump/stage,
wrong remaining-use load, changed final IR, network-enabled compilation,
false deployed-identity claims, changed reference output, extra source changes,
compiler arguments, provider ZIP bytes and relocated saved snapshots.

For an independent Linux x86_64 Docker reproduction, run `trace.py --output
/fresh/experiment/path`. It acquires pinned public inputs before starting
compilation with container networking disabled and Cargo offline. The original
target executable is never mounted or executed. The executed fork-only workflow
is retained inside the artifact, not installed as an upstream workflow.

The SDK again attempts its optional Criterion v2.3.3 download after compilation;
DNS fails in the offline container. The full failure remains in stderr and is
explicitly checked, despite the wrapper's zero exit and passing raw gate.
There is no padding, binary rewrite, output normalization, program replay,
candidate promotion, historical deployed-source attribution or security claim.
Further progress requires evidence that distinguishes authentic historical
inputs or more specific compiler events; this observation alone does not
justify another ordinary source rewrite.

# Final LLVM input to SBF instruction selection

This follow-up closes the gap between the earlier optimized-IR snapshot and
initial selected machine code. A second fresh source build still produces
exactly **707,448 raw bytes**, SHA256
`3bbaf27ff0c10ff68d8a195a82f39eadee266f324067bd0a66081710be30b4ec`.
No compiler optimization, source, dependency or path argument changes were
introduced. The verifier compares all non-diagnostic rustc arguments with the
first run's actual NUL-delimited invocation.

## What changed in the evidence

| Captured point | Observation |
| --- | --- |
| [Before CodeGen Prepare](before-codegenprepare.ll) | Complete function body equals the earlier run's body byte for byte. |
| [After CodeGen Prepare](after-codegenprepare.ll) | 61,589-byte function body; SHA256 `53c696eb06a494644b27443547e74a0675bc1ae84eff069be0ffb4f0bcfea538`. |
| [Final LLVM input to selection](final-isel-input.ll) | Exactly the same 61,589 bytes as the preceding row. Stage banners are excluded; text is not normalized. |
| [Before Finalize ISel](before-finalize-isel.txt) | Complete machine dump equals the earlier run's dump byte for byte. Separate zero, total and remaining guard blocks exist. |

CodeGen Prepare changes other parts of this function, including SSA numbering;
the whole function before and after that pass is not identical. The specific
zero/total/remaining guard text remains identical at all three IR points:

```llvm
  %226 = icmp eq i64 %4, 0
  %227 = getelementptr inbounds %135, ptr %32, i64 0, i32 3
  %228 = load i64, ptr %227, align 8
  %229 = icmp ult i64 %228, %4
  %230 = select i1 %226, i1 true, i1 %229
  %231 = getelementptr inbounds %135, ptr %32, i64 0, i32 2
  %232 = load i64, ptr %231, align 8
  %233 = icmp ult i64 %232, %4
  %234 = select i1 %230, i1 true, i1 %233
  br i1 %234, label %239, label %243
```

At final input this is in IR block 220. Error block 239 stores error 86;
success block 243 subtracts requested `%4` from remaining `%232`.
The machine snapshot has blocks 33, 84 and 83 for the zero, total and remaining
checks respectively, all annotated with IR block 220. The remaining guard is
`JUGT_rr %47:gpr, %22:gpr, %bb.36`, followed by a jump to success block 38.

Thus the observed expansion from the combined IR predicate into separate
guard branches occurs during the **SBF DAG-selection interval before
Finalize ISel**. The conditional direction is already represented in the IR;
this is not evidence of a changed logical predicate. The internal DAG
events and the deployed compiler's input remain unobserved.

## Why these points bound selection

The actual legacy pass-structure log names the SBF DAG selector, followed by
the inserted machine-function printer and then Finalize ISel. The pinned
LLVM source corroborates the meaning of the diagnostic boundaries:

- `TargetPassConfig.cpp:1014–1021` installs `print-isel-input` after IR
  transformations, before the verifier and instruction selection.
- `TargetPassConfig.cpp:1097–1105` installs selection, then Finalize ISel,
  then the printer for `print-after-isel`. That last option would duplicate
  a later point; it is deliberately not used here.
- `SelectionDAGBuilder.cpp:2201–2325` describes logical OR/AND expansion
  into guard blocks; `visitSwitchCase` at lines 2527–2543 conditionally
  complements the branch when the true target is the next layout block.

The observed remaining guard's next layout block is 34 (IR block 235), while
its error target is 36 (IR block 239). The error target is not the next block.
This is consistent with the source's non-complementing case; it is a source
inference, not a captured execution of that C++ conditional. It does not
explain which historical input produced the deployed success-taken layout.

All six consulted source files, including LLVM's complete license, are
retained in `compiler-source.tar.gz` with exact URL/size/hash receipts in
[compiler-source-receipts.json](compiler-source-receipts.json). Their revision
is the declared LLVM gitlink `7b8db05b564faffb522434b73b7082662171f94a`.
The source describes the pipeline; the observed compiler driver and raw
output supply the runtime provenance, as in the parent report.

## Reproduce and verify

[Run 40347761346](https://github.com/startrack3r/pumpfun-source/actions/runs/40347761346)
at `c75ac9c5397ddf53c1ed7516c3ccc77611a02bbc` retains all 53 artifact members.
The exact 475,827-byte ZIP has SHA256
`dbc3e9edd72bf3bb5cf7b3f9d6e8d51a1b87266853e36683e828bf12d906a699`.
The full compiler stderr is 281,503 bytes; the exact function-name filter
reduces unrelated output. It retains the actual pass structure, all four
snapshots, compiler warnings and the SDK's optional Criterion DNS failure.
The wrapper returns zero and the raw gate passes despite that auxiliary
download failure. No program was executed.

```sh
python -B research/metaplex-utilize-trace/verify_boundary.py
python -B research/metaplex-utilize-trace/test_boundary.py
python -B research/metaplex-utilize-trace/test_isel_wrapper.py
```

The boundary verifier first verifies the complete parent evidence package,
then this run's provider/source bindings, all 812 source hashes, dependency
pins, container networking, raw identity, arguments, compiler source files
and exact extracted snapshots. The three new wrapper tests passed in the
hosted Linux run; they skip on Windows. Eight portable boundary tests reject
raw changes, IR changes, a complemented predicate, a missing stage banner,
changed machine output, non-diagnostic compiler arguments and source tampering.

To repeat acquisition followed by offline compilation on a Linux x86_64
Docker runner, use `boundary.py --output /fresh/experiment/path`. Its source
is bound to the executed controller commit. The fork-only workflow remains
inside the artifact as evidence and is not installed upstream. The `.ll`
files are exact function-text dumps with external type/metadata references;
they are not standalone LLVM modules or compiler inputs.

No deployed-byte gap is reduced by this observation. The next useful evidence
would distinguish the final IR layout or selection inputs of an authenticated
historical candidate, or expose the internal DAG decisions while preserving
the raw gate. Repeating the already-observed later machine passes is unnecessary.

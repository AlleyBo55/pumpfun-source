# Fees initializer: reproduce the two-load scheduling order

The complete original initializer window `[82696, 85560)` differs from the coordinate-control build at only two instruction positions after the explicit call/pointer masks. The original loads the bump before the decoded account pointer; the candidate loads them in the opposite order.

A local bump binding alone retains the candidate's machine order. Adding `core::sync::atomic::compiler_fence(Ordering::SeqCst)` after that binding reproduces the original's complete **2,864-byte initializer signature**. Under those masks all 337 instructions agree; in raw bytes 326 are identical and 11 differ only at masked operands (9 local CALL immediates and 2 relocated LDDW values). The compiler barrier emits no additional SBF instruction: the retained machine-body comparison shows only those two loads exchanging positions. This is a reconstruction technique, not evidence that the historical source used a compiler barrier.

| Build | Unique structural pairs | Initializer body matches |
| --- | ---: | --- |
| Coordinate control | 334 | No |
| Early binding control | 334 | No |
| Early binding plus compiler barrier | 335 | Yes |

No prior unique pair is lost. All function names, addresses and sizes remain identical between the control and barrier build. Their complete `.text` differs at exactly 15 instructions across nine functions: the two exchanged loads and 13 immediate 32-bit source-coordinate stores. Every difference is retained and checked; all other instruction bytes remain intact. Outside `.text`, the stripped ELFs also differ in five `.data.rel.ro` panic-location line fields, each shifted by the two inserted source lines.

The final map has 335 unique structural pairs, 43 ambiguous groups containing 144 original windows, and 106 unmatched original windows. Only 54 unique pairs have equal raw bytes. Neither the complete ELF nor the captured allocation is byte identical; core raw identity remains **0/4**.

## Verification

```sh
python3 research/fees-initializer-scheduling/verify.py
python3 -I research/fees-initializer-scheduling/verify.py
python3 research/fees-initializer-scheduling/map_windows.py
```

The packet retains three compiled variants, all needed source overrides and patches, stripped/unstripped ELF artifacts, build logs, tool/input hashes, successful strip replays, complete mappings and full behavioral receipts for the control and barrier builds. Each of those two builds passes all 17,331 existing cases across 18 independent original/candidate SBF suites. No suite invokes `initialize_fee_config` (the initialization suite covers `initialize_fee_program_global` only), so these receipts are a no-regression check of the other handlers; the initializer result rests on the static signature comparison. The binding variant is a static negative control. The checker validates 26 build inputs, 187 unchanged harness files, full `.text` binding, exact candidate boundary agreement with the symbol tables, the source edits, the complete initializer signature and every changed instruction.

Structural signatures mask local CALL immediate words and actual relocated LDDW addresses, retaining import names and relocation positions. Scalar literals, opcodes, registers, branches and stack offsets remain intact. Opaque pointed-to data and callee bodies are not proven equivalent by those masks. Candidate symbol names are annotations, not recovered historical names. Behavioral suites do not assert identical logs, compute or exhaustive semantics.

## Rebuild

Start at the source revision in `experiment.json` in a separate workspace and apply the chosen overrides. Use its offline locked recipe with official platform tools v1.44 and the recorded SDK; preserve the unstripped output and strip using the recorded v1.52 tool. The target directory reuses locked dependencies from the prior clean baseline. Logs and tool hashes are retained without claiming an authenticated process trace. The unchecked parser retains the discriminator-free-slice compatibility limit from PR #83.

Selected sources/candidates, checkpoint ledgers, pinned scripts and workflows are unchanged. This packet includes the preceding parser/dispatch/coordinate overrides and can be checked independently of their merge status.

# Fees: recover the dispatcher order and map all function windows

The candidate declares its 31 program handlers alphabetically. The original's 5,016-byte dispatcher tests their discriminators in a different order. Reordering the unchanged source methods to that observed order reproduces the complete dispatcher instruction structure, including every discriminator and branch displacement, under the explicit relocation masks below. Raw bytes still differ at 26 local CALL immediates and one relocated LDDW pointer word in that window.

The proposed build includes the parser reconstruction from PR #83 as a control input. This packet retains all required source overrides and artifacts, so it can be verified independently of that PR's merge status. The selected project sources and candidate remain unchanged.

| Build | Candidate windows | Unique structural pairs | Unmatched original windows | Unique pair bytes |
| --- | ---: | ---: | ---: | ---: |
| Selected-source Linux baseline replay | 582 | 320 | 121 | 343,928 |
| Reconstructed parser control | 582 | 322 | 119 | 347,824 |
| Reordered dispatcher | 582 | 323 | 118 | 352,840 |
| Aligned declaration lines | 582 | 326 | 115 | 355,024 |

The baseline row is a Linux rebuild of the unchanged selected sources. Its stripped output is the Linux current-source candidate `6c44d9f2…` already retained in `repro/pump_fees/linux-current-source-build`, **not** the selected macOS candidate `2387f813…` (`repro/pump_fees/sharing-authorize-main-v144/main/candidate.so`). The two have equal `.text` length but differ at 19,484 `.text` bytes. They do not share an identical window map: each has 582 inferred windows, but only 525 share (address, size), 57 are placed differently, and their masked-signature multisets differ. Under the masks below they give the same original-side classification: the same 320 uniquely paired original windows (343,928 bytes, 54 raw-equal), the same 43 ambiguous groups (144 original windows) and the same 121 unmatched original windows. The candidate-side pairings differ; for example, original window 824 pairs with macOS window 824 but with Linux window 640.

The dispatcher adds original window `[598128, 603144)` without losing any prior unique structural pair. Under the same masks, three imported account decoders then differ only in one embedded source-line integer each (a 32-bit immediate store, 27→29, 27→29 and 28→30): the candidate's `declare_program!` calls are at lines 29/30, versus the original's observed 27/28. Removing the two leading documentation lines aligns these emitted integers and adds the three 728-byte BondingCurve, Global, and Pool decoder windows at 537312, 539488 and 575408 as unique structural pairs under those masks. None of the three is raw-identical: each pair still differs at 6 local CALL immediates and 8 relocated LDDW pointer words, and the raw-equal pair count stays 54 in all four builds. No prior pair is lost. This controlled result does not establish the unique historical source layout.

There are also 43 ambiguous signature groups, containing 144 original windows. Those are retained as groups and excluded from the unique-pair count. Only 54 of the unique pairs have identical raw bytes. Neither whole ELF nor the captured allocation is byte identical; core raw identity remains **0/4**.

## Mapping method and limits

The mapper infers starts from the `.text` start, ELF entry point, defined dynamic function symbols, local encoded CALL targets, and code pointers referenced by relocation type 8. It excludes external CALL relocation type 10 from local target inference. Consecutive starts partition the entire `.text`. On each retained unstripped candidate this independently inferred partition matches **every function symbol address and size**, with no extra/missing boundaries. Applying the same inference to the original yields 585 windows; the original's historical local symbols are unavailable.

Structural signatures preserve every opcode, register, branch displacement, stack offset and scalar literal. They mask local CALL immediate words and actual relocated LDDW pointer values. External CALLs carry their dynamic import names and relative offsets in the signature, so different imported functions cannot silently collapse into a match. Pointer relocation positions are also included. Candidate symbol names annotate candidates only; they are not recovered historical names.

Opaque pointers and local CALL destinations are not proven equivalent by these signatures. These are navigation and comparison results, not semantic equivalence, transitive callee proof, source uniqueness, or verified equality of all referenced data. The more narrowly verified constant/message records for the two parser windows remain documented in PR #83.

For the final build, `nearest_same_extent_diagnostics` also lists the closest comparisons among unmatched windows with the same extent and instruction boundaries. It keeps every tied alternative and all differing instructions. These hints never accept a match or resolve an ambiguous group; windows of different extents are outside that diagnostic search.

## Verification and reproduction

```sh
python3 research/fees-dispatch-order/verify.py
python3 -I research/fees-dispatch-order/verify.py
python3 research/fees-dispatch-order/map_windows.py
```

The checker re-derives all mappings from the retained ELFs, checks exact candidate boundary agreement with the symbol tables, binds each stripped `.text` to its unstripped ELF, validates 26 source input hashes and 187 unchanged harness hashes, and verifies that all 31 method bodies and surrounding source are unchanged by reordering. It separately checks that declaration alignment removes only the two leading documentation lines. Both proposed builds pass all 17,331 existing behavioral cases across 18 independent original/candidate SBF suites. These bounded tests do not assert identical logs, compute, or exhaustive semantics.

`experiment.json` records the upstream source revision, source overrides, offline locked compiler command, tool and output hashes, and successful v1.52 strip replays of the official v1.44 compiler outputs. The four variants reuse the locked dependencies from the prior clean baseline target directory. Build logs and executable hashes are retained without claiming an authenticated process trace. Rebuild at the recorded revision, apply the selected overrides to a separate workspace, and use the command and environment in that file. The parser overrides retain the discriminator-free unchecked-input compatibility limit described in PR #83.

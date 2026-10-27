# Fees: align eight source-coordinate windows

Blank-line insertion at source coordinates observed in the original recovers eight more complete instruction-window signatures. All nonblank source lines are unchanged. This experiment starts with the reconstructed parser and dispatcher/declaration control from PRs #83 and #84, retaining every needed override and artifact for independent verification.

| Attribute | Reconstructed source line | Added original windows |
| --- | ---: | --- |
| `#[account]` BuybackVault | 50 | `[529488, 530216)` |
| `#[account]` SocialFeePda | 113 | `[531232, 531976)` |
| `#[account]` DonationFeePda | 135 | `[532872, 533600)` |
| `#[account]` FeeProgramGlobal | 154 | `[535376, 536104)` |
| `#[account]` SharingConfig | 37 | `[442944, 443688)` |
| `#[program]` | 38 | IDL write `[614624, 616000)`, set-buffer `[616120, 617360)`, account decoder `[678032, 678760)` |

The candidate remains at 582 inferred windows, exactly matching all retained function symbols and extents. Unique structural pairs increase from **326 to 334**, with none lost. There are 43 ambiguous groups containing 144 original windows, and 107 original windows remain unmatched. Only 54 unique pairs have identical raw bytes. Neither the unmodified ELF nor the captured allocation is byte identical; core raw identity remains **0/4**.

The controlled code difference is unusually narrow: all function names, addresses and sizes remain identical, and exactly 21 instructions across 16 functions change. Every changed instruction is an immediate 32-bit store (opcode `0x62`), with only its immediate value changing. Every other `.text` byte remains intact. The retained analysis enumerates every change; this also exposes coordinate changes in windows that still do not match the original.

## Verify

```sh
python3 research/fees-source-coordinates/verify.py
python3 -I research/fees-source-coordinates/verify.py
python3 research/fees-source-coordinates/map_windows.py
```

The checker verifies the packet manifest, 26 build inputs and 187 unchanged harness files, both full ELF artifacts, complete stripped/unstripped `.text` binding, all inferred candidate boundaries against the symbol tables, the eight gained comparisons, and the exact set of 21 changed instructions. It checks that the source changes only insert blank lines and that the attributes occupy the recorded lines. Both builds pass 17,331 existing behavioral cases across 18 independent original/candidate SBF suites. These bounded tests do not assert identical logs, compute, or exhaustive semantics.

The mapping uses the same explicit limits as PR #84: local CALL immediate words and actual relocated LDDW pointer values are masked, while external import names and relocation offsets are retained in signatures. All opcodes, registers, branch/stack offsets and scalar literals are preserved. Opaque pointed-to data and callee bodies are not proven equivalent by these signatures. Candidate names are annotations, not recovered historical names. Matching these source-line outputs does not identify unique historical source contents or formatting.

## Build provenance

`experiment.json` records the upstream source revision, source overrides, offline locked compiler command, input/output and tool hashes, and successful strip replays. Official platform tools v1.44 compile both builds; the recorded SDK's v1.52 tool strips them. The common target directory reuses locked dependencies from the prior clean baseline. Logs and executable hashes are retained without claiming an authenticated process trace.

Rebuild at the recorded revision in a separate workspace using the selected overrides and recipe. The unchecked parser accepts a discriminator-free slice, with the same compatibility limit as PR #83. This packet changes no selected source, selected candidate, checkpoint ledger, pinned script or workflow.

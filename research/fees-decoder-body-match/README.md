# Fees decoder: complete instruction-body match under address masks

Returning the current `FeeConfig` from each legacy/stable/full reader in `anchor_lang::Result<Self>` makes the complete 2,648-byte unchecked decoder match the original instruction stream under the explicit address masks below. Returning smaller legacy structures and converting them in the dispatcher produces the same extent but only 236 matching instructions in sequence. Both variants retain the consuming checked parser that matches the first account helper.

| Window | Original extent | Full-results comparison |
| --- | --- | --- |
| FeeConfig first-account helper | `[36072, 37320)` | All 1,248 bytes match after masking 12 CALL immediates and two verified constant addresses (raw bytes differ at those 14 instructions) |
| FeeConfig unchecked decoder | `[257264, 259912)` | All 2,648 bytes / 325 decoded instructions match after masking 13 CALL immediates and one verified message-record address (raw bytes differ at those 14 instructions) |

The decoder differs at precisely one non-CALL instruction: the LDDW at relative offset 2264. Its 24-byte record has the same length (27), opaque trailing integer (37), relocation type (8), and `failed to fill whole buffer` string bytes. The stored relocated string pointer is checked separately in each ELF. Only the instruction's pointer value is masked. Every opcode, register, branch displacement, stack offset, scalar literal and other instruction byte remains intact. The account helper's two pointers resolve to the same 32 zero bytes and Fees program ID bytes in both images.

These are bounded instruction comparisons. CALL target bodies are not proven equivalent by masking their addresses. Neither retained candidate equals the original allocation or its ELF extent. The project remains at **0/4 raw byte-identical core binaries**; this packet does not change the selected source or candidate.

## Reproduce the retained checks

```sh
python3 research/fees-decoder-body-match/verify.py
python3 -I research/fees-decoder-body-match/verify.py
python3 research/fees-decoder-body-match/analyze.py
```

The standard-library checker re-derives both instruction comparisons, verifies the message record and its relocation, binds the complete `.text` of each unstripped ELF to its stripped output, checks all 26 build input hashes and 187 unchanged harness hashes, and checks both full behavioral receipts. Each variant passes 17,331 cases across 18 independent original/candidate SBF suites. These bounded tests compare the outputs recorded by their existing harnesses; they do not establish exhaustive semantic equivalence or matching logs/compute.

## Build inputs and artifacts

`sources/` retains complete source overrides and a zero-context control-to-proposal patch. `experiment.json` records the common offline locked build command, workspace environment, tool hashes, source hashes, output hashes, and successful strip replays. The compiler uses official platform tools v1.44; the recorded SDK installs the v1.52 strip tool. Dependencies are reused from the prior clean baseline target directory. `extracted-source-verification.json` retains the check of all 252 locked archives and 7,936 extracted files. Build logs and executable hashes provide provenance without claiming an authenticated process trace.

To rebuild, start at the recorded `source_revision`, replace only `programs/pump-fees/src/types.rs` with the chosen override, provide the recorded SDK and offline locked dependencies, and run the command in `experiment.json`. Preserve the unstripped `target/sbf-solana-solana/release/pump_fees_candidate.so` and strip with the recorded v1.52 `llvm-objcopy --strip-all`. Do not apply these research overrides to the selected source as part of verification.

The unchecked parser accepts and consumes a discriminator-free slice. Passing full account data directly to that API is outside the claimed compatibility scope. Original function names are inferred from the caller path and candidate symbols; the original extents are checked using closed reachable control flow.

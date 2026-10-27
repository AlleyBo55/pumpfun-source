# Fees: recover both deprecated-handler source origins

The two deprecated handlers already match the original instruction structure except for their source-line integers. Aligning their error macros to the observed lines 183 and 188 adds the complete original revoke window `[659640, 660160)` and transfer window `[660160, 660680)`. These are structural-signature matches: in each 58-instruction window 47 instructions are raw-identical and 11 differ only at masked operands (4 local CALL immediates and 7 relocated LDDW values).

The transformation removes 17 blank lines before the first error and folds 32 line breaks in five earlier methods. It retains every Rust token. `align_source.py` exactly replays the transformation and verifies that the folded bodies contain no quoted tokens or comments. This recovers the emitted coordinates without identifying unique historical source formatting.

Unique structural pairs increase from **335 to 337**, with none lost. All function names, addresses and sizes remain identical between the retained builds. Their `.text` differs only at 13 immediate 32-bit stores across eight functions; every other instruction byte remains unchanged. Outside `.text`, five `lib.rs` panic-location line fields in `.data.rel.ro` also change (164→136, 314→265, 404→355, 405→356, 421→372). The full report enumerates every change, including source-coordinate changes in other windows that remain unmatched.

There are 43 ambiguous groups containing 144 original windows and 104 unmatched original windows. Only 54 unique pairs have identical raw bytes. Neither complete ELF nor captured allocation is byte identical; core raw identity remains **0/4**.

## Verify and rebuild

```sh
python3 research/fees-deprecated-origins/verify.py
python3 -I research/fees-deprecated-origins/verify.py
python3 research/fees-deprecated-origins/map_windows.py
```

Both builds pass all 17,331 existing behavioral cases across 18 independent original/candidate SBF suites. The standalone checker verifies the full receipts, 26 build inputs, 187 unchanged harness files, retained ELF hashes, complete stripped/unstripped `.text` binding, candidate boundaries against every symbol-table address/extent, source transformation, two added windows, and all changed instructions. Tests do not assert identical logs, compute or exhaustive semantics.

The mapper preserves opcodes, registers, branch/stack offsets and scalar literals. It masks local CALL immediate words and actual relocated LDDW addresses, retaining external import identity and relocation offsets. Opaque data and callee bodies remain outside these structural comparisons. Candidate names are annotations rather than recovered historical symbols.

At the source revision in `experiment.json`, apply the chosen overrides in a separate workspace and use the recorded offline locked recipe. Official platform tools v1.44 compile both builds; the recorded v1.52 tool strips them. Source/tool hashes, build logs and successful strip replays are retained. Dependencies reuse the prior clean baseline target directory. Logs and executable hashes are not an authenticated process trace.

This packet includes the preceding parser, dispatcher, coordinate and initializer-barrier overrides independently of their merge status. It retains the discriminator-free unchecked-input compatibility limit. No selected source/candidate, checkpoint ledger, pinned script or workflow changes.

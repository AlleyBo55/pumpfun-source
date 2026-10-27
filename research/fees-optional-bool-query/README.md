# Fees: recover the complete plain-query wrapper

The original `get_fees` wrapper is `[636160, 637720)`, **1,560 bytes**. The reconstructed optional boolean preserves EOF as false, formats invalid byte values with the original Borsh-style message, and uses `InvalidData` for that optional byte. The leading pool boolean still uses ordinary Borsh's `InvalidInput`. A literal-byte match in the decoder and a single final `Ok(fees)` in the handler recover the original control flow and result layout.

The **complete wrapper structural signature now matches**. Unique structural pairs increase from **343 to 344**, with none lost; **94 original windows remain unmatched**. All **580 candidate boundaries/extents** equal its full function symbol table. The public argument types and boolean wire encoding remain unchanged. Only the retained `lib.rs` and `types.rs` overrides change from PR #96.

The proposal passes **17,331 independent original/candidate cases across 18 suites**. A separate focused matrix exercises every optional-byte value plus absence, both valid pool flags and three market caps: **1,542 cases**. The proposal matches outcomes, **raw logs and exact compute units in all 1,542**. The control preserves outcomes but differs in raw logs (the compute-use lines) and compute in 1,539 cases; its known differences are retained as a sensitivity control. These finite cases do not prove exhaustive program equivalence.

## Verify

```sh
python3 research/fees-optional-bool-query/verify.py
python3 -I research/fees-optional-bool-query/verify.py
```

`exhaustive_flags.py` re-executes the focused matrix with the pinned LiteSVM environment and a supplied uncompressed candidate ELF. The proposal uses the default zero-difference expectation. Reproducing the known control uses `--expected-differences 1539`; it is not treated as a zero-difference result.

The standalone checker re-derives the complete window signature, the two different encoded error-kind values, direct calls to the paired account parser and tier selector, the 29-byte format prefix through its actual relocated string record, and both formatting callback body signatures. It binds all 26 source inputs, 187 unchanged harness files, stripped/unstripped outputs, build results/logs, strip replays and both kinds of execution receipt. Control suite receipts are reused from the identical PR #96 artifact; all proposal executions and both focused matrices are fresh.

Body signatures preserve scalar literals, opcodes, registers, stack/branch offsets and external import identities while masking local CALL immediates and actual relocated LDDW addresses. The explicit callee/format bindings strengthen this wrapper's evidence. Other opaque data, indirect-call behavior outside the finite cases and whole-file layout remain unproved. Raw whole-file and ELF-extent comparisons remain false; core byte identity is still **0/4**.

Rebuild with the complete retained source overrides at the recorded revision using official platform-tools v1.44, the canonical `sbpf-solana-solana` target, `RUSTFLAGS=-Zremap-cwd-prefix=`, and the pinned v1.52 strip tool, following `builds/*-launch.json`. Logs/hashes are retained evidence rather than an authenticated process trace. Previous unchecked-input compatibility limits remain. No selected source/candidate, checkpoint ledger, pinned script or workflow changes.

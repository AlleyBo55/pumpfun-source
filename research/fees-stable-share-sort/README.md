# Fees: recover stable sorting in both shareholder validators

The original `sol_memmove_` import belongs to a 32-byte wrapper at `[796392, 796424)`. Its merge-sort caller is `[45488, 50760)` (5,272 bytes). The original legacy and V2 shareholder helpers, `[205768, 211408)` and `[225920, 231576)`, both call that sorter at relative offset 2200.

Changing the two reconstructed `keys.sort_unstable()` calls to `keys.sort()` recovers the **complete merge-sort and memmove-wrapper structural signatures**. It also restores the missing `sol_memmove_` import. The 32-byte wrapper is raw-identical, including its import relocation. The merge-sort window is a structural match: 601 of 636 instructions are raw-identical and 35 differ only at masked operands (21 local CALL immediates and 14 relocated LDDW values). Unique structural pairs increase from **338 to 340**, with none lost. The candidate has 579 inferred windows, exactly matching all retained function symbol addresses/extents; 98 original windows remain unmatched. The surrounding shareholder helpers still differ and are not claimed reconstructed by this change.

Both the exact control and stable-sort builds pass **17,331 cases across 18 independent original/candidate SBF suites**. The test scope is bounded and excludes matching raw logs, compute and exhaustive semantics. Whole compiler-file/allocation identity remains false; core raw identity remains **0/4**.

## Verify and rebuild

```sh
python3 research/fees-stable-share-sort/verify.py
python3 -I research/fees-stable-share-sort/verify.py
python3 research/fees-stable-share-sort/map_windows.py
```

The standalone checker re-derives both original caller edges, the merge-sort-to-wrapper edge, and the wrapper's actual external relocation/import identity. It verifies the complete new signatures, all source and artifact hashes, stripped/unstripped `.text` binding, exact candidate boundary inference, strip replays, and both full behavioral receipts. All 26 source inputs and 187 unchanged harness files are bound. The source patch changes exactly the two sorting statements; all other source overrides are identical between control and proposal.

Signatures preserve scalar literals, opcodes, registers, stack offsets and branch displacements. They mask local CALL immediates and actual relocated LDDW addresses, retaining import names and relocation positions. Opaque data and callee bodies are not proven equivalent by those masks. Candidate symbols annotate candidates only; original function roles are inferred from their call/relocation evidence.

The saved `builds/` commands invoke the official platform tools v1.44 Cargo/rustc directly with `--target sbpf-solana-solana` and `RUSTFLAGS=-Zremap-cwd-prefix=`. This is the controlled canonical-target build route from [`research/fees-canonical-target`](../fees-canonical-target/README.md) (PR #90), not the recorded `cargo-build-sbf` driver recipe, which requests the legacy `sbf-solana-solana` target. Among the tested profiles that route matches more original windows, but it is not established as the historical build route. The control build here is byte-identical to that packet's `latest-canonical` build (candidate SHA-256 `43a6748a…`), which supplies the 338-pair baseline. Apply the selected complete overrides at the recorded source revision in a separate workspace, preserve the unstripped output, and strip with the pinned v1.52 tool. Both builds use the same locked crate set offline and reuse PR #90's canonical-target directory, so only the program crate is recompiled. Logs and hashes are not an authenticated process trace.

This includes the preceding parser, dispatcher, source-coordinate, initializer-scheduling and deprecated-handler line-alignment reconstruction overrides (through PR #88), independently of their merge status, and retains their unchecked-input compatibility limit. No selected source/candidate, checkpoint ledger, pinned script or workflow changes.

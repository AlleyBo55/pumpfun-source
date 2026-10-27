# Fees: recover the complete buyback initializer body

Moving the unchanged private initializer helper to `programs/pump-fees/src/instructions/buyback/mod.rs`, with its guard on line **94**, recovers the complete **600-byte original window at 120216**. The helper inlines into the public program initializer body identified by the candidate symbol. The public program source and account declarations are unchanged.

The checker reads the actual original/candidate diagnostic pointers, all **50 path bytes**, and the line/length stores. It proves the helper text is identical and reconstructs the old containing file using only the required re-export. Real source coordinates supply the values; executable bytes are never patched. The source is reconstructed and is not authenticated historical source.

Unique structural pairs increase from **352 to 353**, with none lost; **85 original windows remain unmatched**. Both candidates have 580 inferred windows, independently equal to every candidate function-symbol extent including aliases, and 57 unique raw-equal local pairs. Complete raw capture and ELF-extent equality remain false; core whole-file identity remains **0/4**.

## Verify and rebuild

```sh
python3 research/fees-buyback-initializer-origin/verify.py
python3 -I research/fees-buyback-initializer-origin/verify.py
```

Both candidates retain passing **17,331-case** differential suites across 18 local suites, plus **1,542** exact outcome/log/compute comparisons each. The proposal was executed afresh; the identical Shareholder-Copy control receipt is explicitly reused. The focused matrix covers every optional byte plus absence, both pool flags and three caps in one fixed valid configuration. These finite checks do not establish exhaustive program semantics.

The packet retains complete overlays, all **32/33 input hashes**, 187 unchanged harness hashes, stripped/unstripped artifacts, build logs and fresh strip replays. Build from the recorded source revision with its overrides, official platform-tools v1.44 and canonical `sbpf-solana-solana`, using `RUSTFLAGS=-Zremap-cwd-prefix=` and the recorded `builds/*-launch.json` command. Strip with the pinned v1.52 tool. Logs and hashes are retained evidence rather than authenticated process traces.

Signatures mask local CALL immediates and actual relocated LDDW addresses while preserving scalar values, registers, stack/branch offsets and external import identities. The source-location checks do not establish other opaque data or transitive/indirect callee identity. Existing unchecked-input limits remain. Selected programs, pinned scripts, workflows and checkpoint ledgers are unchanged.

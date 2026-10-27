# Fees: recover both buyback update body windows

Moving two unchanged private helper bodies to the diagnostic file and guard lines observed in the original binary recovers complete **696-byte** and **640-byte** structural windows. These helpers inline into the public program bodies named by the candidate symbols. The account declarations and public program source functions are unchanged.

| Original address | Bytes | Helper | Guard line |
| --- | ---: | --- | ---: |
| 96896 | 696 | `update_buyback_authority` | 36 |
| 97592 | 640 | `update_buyback_claim_rate_limit` | 47 |

Both guards live in `programs/pump-fees/src/instructions/admin/update_buyback_authority.rs`. The checker independently reads the actual original/candidate path pointers, all 69 pointed-to bytes, and the line/length stores. The full helper text is identical; the old containing file changes only by replacing the two lines with re-exports. Real source files supply the locations; no executable bytes are edited.

Unique structural pairs increase from **349 to 351**, with none lost; **87 original windows remain unmatched**. Both candidates have **580 inferred windows**, equal to every candidate function-symbol extent including aliases, and 57 unique pairs have equal raw local body bytes. Core whole-file identity remains **0/4**. Raw whole-capture and ELF-extent comparisons still fail.

## Verify and rebuild

```sh
python3 research/fees-buyback-update-origins/verify.py
python3 -I research/fees-buyback-update-origins/verify.py
```

The self-contained packet retains complete source overlays and all 31/32 input hashes, 187 unchanged harness hashes, stripped/unstripped artifacts, build logs and fresh strip replays. Use the bound source revision with the recorded overrides, official platform-tools v1.44, the canonical `sbpf-solana-solana` target and `RUSTFLAGS=-Zremap-cwd-prefix=`, following `builds/*-launch.json`. Strip with the pinned v1.52 tool. The functions are reconstructed source, not authenticated historical source; logs and hashes are retained evidence rather than authenticated process traces.

Both candidates retain **17,331 original/candidate comparisons across 18 local suites**, with no mismatches. The proposal was executed afresh; the identical creation-parser control receipt is explicitly reused from PR #117. Each candidate also passes 1,542 exact outcome/log/compute comparisons covering every optional byte plus absence, both pool flags and three caps in one fixed valid configuration. A separate fresh 1,249-case buyback execution is retained. These finite checks do not establish exhaustive semantic equivalence. An initial full-suite attempt stopped when a sparse checkout removed an initialization fixture; its failed log is retained, and the complete suite was rerun after restoring the fixture.

Signatures preserve scalar literals, registers, stack/branch offsets and external import identities while masking local CALL immediates and actual relocated LDDW addresses. The source-location checks do not prove other opaque data or transitive/indirect callees equal. Existing unchecked-input compatibility limits remain. Selected programs, pinned scripts, workflows and checkpoint ledgers are unchanged.

# Fees: restore legacy sharing-account ownership

The legacy `UpdateFeeShares` declaration needs six owned `AccountInfo` fields and an unboxed `Account<Global>`. Replacing only those field types recovers a **776-byte cleanup body with exactly equal raw bytes**, plus the complete **1,072-byte structural dispatch wrapper**. Account attributes, business code, the public program namespace and all other inputs are unchanged.

| Evidence | Control | Proposal / original |
| --- | ---: | ---: |
| Unique structural pairs | 354 | 356 |
| Original windows unmatched | 84 | 82 |
| Unique raw-equal local pairs | 57 | 58 |
| Candidate windows | 580 | 581 |
| Dispatch copy length | 536 | 1512 |

The new original windows are **43856** (776 bytes) and **640672** (1072 bytes), with none lost. The cleanup drops six owned handles at the observed offsets, starting with reference-counted pointers at 368/376 and a 48-byte stride. It contains no calls or relocated pointers: its equality is raw, not normalized. The checker independently decodes both success/error cleanup CALLs in the dispatch wrapper and proves they target this exact raw-equal body. It also checks the actual instruction-log strings, the 1,512-byte copy literal and the raw-equal `memcpy` callee.

## Verify and rebuild

```sh
python3 research/fees-sharing-owned-legacy/verify.py
python3 -I research/fees-sharing-owned-legacy/verify.py
```

Both retained candidates pass **17,331 original/candidate comparisons across 18 local suites** and **1,542 exact outcome/log/compute comparisons** each. The proposal was executed afresh; identical control receipts are reused from PR #129. The focused matrix covers every optional byte plus absence, both pool flags and three caps in one fixed valid configuration. Finite results do not establish exhaustive semantics.

The standalone checker proves the precise type substitutions and byte-for-byte preservation of all other source, validates all **34 inputs per build**, 187 unchanged harness hashes, every inferred candidate boundary and symbol extent including aliases, complete artifacts and fresh strip replays. Rebuild from the bound source revision and full overrides using official Linux platform-tools v1.44, canonical `sbpf-solana-solana`, and `RUSTFLAGS=-Zremap-cwd-prefix=` as recorded in `builds/*-launch.json`; strip with the pinned v1.52 tool. Captured source whitespace is preserved by packet-local attributes. Logs and hashes are retained evidence, not authenticated process traces or historical-source proof.

The wrapper match masks local CALL immediates and actual relocated LDDW addresses while preserving scalar/register/stack/branch bytes and import identities. The explicitly checked callees do not establish all other transitive calls or opaque data. Whole-capture and ELF-extent comparisons remain false; core whole-file identity remains **0/4**. Selected programs, pinned scripts, root attributes, workflows and checkpoint ledgers are unchanged.

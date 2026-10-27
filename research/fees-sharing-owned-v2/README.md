# Fees: restore V2 sharing-account ownership and boxing

The V2 declaration retains a borrowed event authority, owns the other six formerly unchecked handles as `AccountInfo`, and boxes its sharing-config and bonding-curve accounts. These field-type changes recover a **776-byte cleanup body with exactly equal raw bytes**, the complete **1,104-byte structural dispatcher**, and a **352-byte boxed-account parser**.

| Evidence | Control | Proposal |
| --- | ---: | ---: |
| Unique structural pairs | 356 | 359 |
| Original windows unmatched | 82 | 79 |
| Unique raw-equal local pairs | 58 | 59 |
| Candidate windows | 581 | 583 |
| Dispatch copy length | 544 | 608 |

The new original windows are **9528**, **44632** and **641744**, with none lost. The cleanup contains no calls or relocated pointers, so its complete equality is raw. The checker independently decodes both success/error cleanup CALLs in the dispatcher, proves they target this exact body, and checks the instruction-log bytes, six 48-byte-stride handle slots starting at 264/272, the 608-byte copy literal and its actual raw-equal `memcpy` callee. The boxed parser is a structural match, with no additional historical type-name assertion.

Six separately built negative controls borrow each other unchecked field instead of the event authority, keeping six owned handles and the same boxes. Every one loses the dispatcher at **641744**, yielding 358 unique pairs and 80 unmatched windows. All their sources, builds, artifacts and strip replays are retained. They are excluded from the proposed source and have no claimed runtime-suite validation. The exact dispatch match distinguishes the selected field arrangement within this tested seven-choice family; it is not exhaustive historical-source proof.

## Verify and rebuild

```sh
python3 research/fees-sharing-owned-v2/verify.py
python3 -I research/fees-sharing-owned-v2/verify.py
```

The control and proposal each retain passing **17,331-case** differential suites across 18 local suites, plus **1,542** exact outcome/log/compute comparisons. The proposal was executed afresh; identical control receipts are reused from PR #140. The focused matrix covers every optional byte plus absence, both pool flags and three caps in one fixed valid configuration. Finite results do not establish exhaustive semantics.

The checker proves the exact type substitutions, unchanged account attributes/business code and all **34 inputs per build**. It binds 187 unchanged harness hashes, every candidate boundary and symbol extent including aliases, complete artifacts and fresh strip replays. Rebuild from the bound source revision and full overrides with official Linux platform-tools v1.44, canonical `sbpf-solana-solana` and `RUSTFLAGS=-Zremap-cwd-prefix=`, using the commands in `builds/*-launch.json`; strip with the pinned v1.52 tool. Packet-local attributes preserve captured source whitespace. Logs/hashes are retained evidence, not authenticated process traces.

Structural signatures mask actual relocated LDDW addresses and local CALL immediates while retaining scalar/register/stack/branch bytes and import identities. The explicitly checked callees do not prove all other calls or opaque data equal. Whole-capture and ELF-extent comparisons remain false; core whole-file identity remains **0/4**. Selected programs, pinned scripts, root attributes, workflows and checkpoint ledgers are unchanged.

# Fees: recover tier selection and quote-query instruction windows

The original plain query calls a 376-byte tier selector at `[700760, 701136)`. The quote query calls a 656-byte helper at `[259912, 260568)`, which performs four Pubkey comparisons and calls that same tier selector. Recovering these boundaries and copy semantics produces **three complete structural window matches**:

| Original window | Bytes | Recovered role |
| --- | ---: | --- |
| `[700760, 701136)` | 376 | Tier selector |
| `[259912, 260568)` | 656 | Quote-mint selector |
| `[637720, 639104)` | 1,384 | Generated quote-query wrapper |

The source changes affect two inputs: `Fees` derives `Copy`; the existing tier selector is kept out of line; and quote selection moves into a non-fallible helper using Pubkey equality. Its USDC comparison preserves the original operand order. The public instruction signature and arguments remain unchanged. No decoder/error-format experiment is included in the proposal.

Unique structural pairs increase from **340 to 343**, with none lost; **95 original windows remain unmatched**. The candidate has **580 inferred windows**, exactly reproducing its function symbol addresses/extents. This includes the preceding stable-sort and canonical-target research overrides independently of their merge status. The ordinary query wrapper and unrelated private helpers remain unresolved. Whole compiler-file/allocation identity remains false; core raw identity remains **0/4**.

## Verify and rebuild

```sh
python3 research/fees-query-selectors/verify.py
python3 -I research/fees-query-selectors/verify.py
python3 research/fees-query-selectors/analyze.py
```

The standalone checker verifies all artifact/source hashes, all 26 build inputs and 187 unchanged harness files, stripped/unstripped `.text` binding, candidate boundary inference, retained strip replays, complete new signatures, and both full differential receipts. It also verifies six actual encoded call edges: the quote wrapper to its helper, that helper to the tier selector, and four calls to the paired comparison wrapper. At each of the three relocated quote-constant pointers it checks all 32 pointed-to bytes against both the original and the Rust constant. Scalar literals, registers, stack/branch offsets and external import identities remain part of body signatures.

Signatures mask local-CALL immediates and actual relocated LDDW addresses. The three verified quote constants and six callee bindings strengthen these particular pairs; other opaque data, the tier-selector panic location and dynamic calls are not proven identical by masking. Candidate symbols annotate candidates only. This remains bounded reconstruction evidence rather than a proof of complete semantic or byte identity.

The proposal passes **17,331 independent original/candidate SBF cases across 18 suites**. The unchanged control's previously recorded 17,331-case receipt is reused from [PR #91](https://github.com/lalalune/pumpfun-source/pull/91), bound to the identical candidate hash. Test scope excludes matching raw logs, compute and exhaustive semantics. Source/build hashes and logs are retained evidence, not an authenticated process trace.

Rebuild using the exact source overrides at the recorded source revision and the retained `builds/*-launch.json` commands: official platform-tools v1.44, canonical `sbpf-solana-solana`, `RUSTFLAGS=-Zremap-cwd-prefix=`, and the pinned v1.52 strip tool. The complete proposal retains the previous unchecked-input compatibility limit. Selected sources/candidates, checkpoint ledgers, pinned scripts and workflows are unchanged.

# Relay: framework, sysroot and share-error recovery

The best retained research build now matches **479/492 complete original windows
under the existing normalization**, including **127 raw local body matches**.
**13 windows remain unmatched.** None of the prior 470 matches is lost. The
818,072-byte output is still different from the captured 830,448-byte allocation;
no selected source or artifact is promoted by this packet.

## Controlled progression

| Build | Normalized windows | Unmatched | What changes |
| --- | ---: | ---: | --- |
| [Parent](../token-extension-version-recovery/README.md) | 470 | 22 | Anchor 0.31 with local Anchor SPL manifest using Token-2022 v8 |
| `native-pinned` | 474 | 18 | Official Anchor Lang/SPL 0.32.1, resolved macros 0.32.2; retain compatible older lock entries |
| `native-current` | 475 | 17 | Coherent newer transitive resolution, including Pubkey 2.4.0 |
| `linux-libs-pinned` | 477 | 15 | Pinned dependency variant plus official Linux v1.48 target libraries |
| `linux-libs-current` | 478 | 14 | Current dependency variant plus the same Linux target libraries |
| `share-values` | **479** | **13** | Add missing share-total comparison values to the error |

All five full-program builds in this table use the **Darwin v1.48 Rust compiler**.
The last three explicitly select the **official Linux v1.48 target sysroot** with
`--sysroot`, and the Darwin `ld.lld` for linking. They are cross-host recipes,
not claims that these full programs were compiled on Linux. The small type-ID
probes were separately compiled by the actual Linux compilers in an isolated
Ubuntu image. No captured instructions or data are passed to the Rust compiler.

The native-current and share-values candidates each pass a fresh replay of all
**536 records / 534 unique fixtures**, reproducing the saved original observations.
These are repeated runs of the same finite corpus, not additional unique cases.
The unchanged comparator excludes executable-image fields and compute metering.

## Recovered windows and meaning

- **172, 282, 300, 332:** the official 0.32 framework/API family recovers IDL
  resize, account close, the signed CPI adapter, and account resizing. The earlier
  family emits three-argument `realloc` calls; the newer family uses `resize`.
- **344:** the full dependency variant recovers the 7,392-byte Pubkey base58
  writer. The minimal older-lock variant does not. A trial to update only Pubkey
  fails resolution because its older ZK dependency pins Pubkey 2.2.1; that failure
  is retained. This is evidence about the coherent tested dependency resolution,
  not proof that a single crate bump independently produces every difference.
- **56, 267, 351:** all three 56-byte type-ID bodies now match **raw bytes**.
  Actual Linux v1.48 canonical-target and Darwin-with-Linux-sysroot probes return
  the captured constants. Linux v1.48 legacy-target and both tested v1.49 target
  aliases do not. This refines the earlier [local-host matrix](../../../research/relay-string-error-provenance/README.md).
- **4:** the original 1,352-byte `with_values` specialization stores a 32-bit
  value and the constant `10000`; callers are the share-total rejection paths
  in original windows 97, 98 and 100. The old reconstructed `admit_shares!` error
  omitted these values. Adding `.with_values((sum,10000))` recovers the complete
  helper. This fixes a diagnostic omission, not just a compiler-layout choice.

`gain-map.json` records original addresses/extents and candidate symbols. The
anonymous original labels remain inferred. Full-window normalization still masks
only the same actual call/relocation immediates as the parent analyzer; it does not
mask scalar literals, register choices, stack offsets or branches.

The existing corpus does **not** establish successful privileged settlement or
exercise the fixed-relayer-protected share-total rejection end to end. The new
error-value evidence is the full captured helper and its caller references plus
the compiled match. That limitation remains even though all saved replays pass.

## Negative controls

Three mint-expression trials preserve the prior 470 matches but recover no new
window: reverse the two fee fields in the bitwise expression, or use either order
of the equivalent boolean tests. Their complete outputs and source changes are
retained. The original mint-policy window still differs at three register-use
instructions; equivalent source expressions alone did not resolve it.

The first offline Anchor 0.32 build fails because a resolved macro archive was not
cached. The subsequent explicit locked fetch and successful offline builds are
retained separately. Logs/hashes are evidence records, not authenticated traces.

## Remaining original windows

| Ordinals | Work still needed |
| --- | --- |
| 90 | Jupiter CPI construction |
| 92–95 | Native, pubkey, regular and payer donation handlers |
| 96 | Epoch close |
| 97–100 | After-swap, non-swap, just-swap and swap-then-distribute handlers |
| 106 | Mint-safety policy |
| 109 | Residual burn/close helper |
| 112 | Shared donation worker |

Even matched windows still require transitive data/call validation, complete ELF
layout and exhaustive behavior. Neither 479/492 nor 127 raw bodies is a percentage
of semantic correctness, original source recovered, or effort remaining.

## Recheck and rebuild

```sh
python3 -B repro/donation-relay/framework-sysroot-recovery/verify.py
# Also check every retained Linux SDK file against this machine's cache:
python3 -B repro/donation-relay/framework-sysroot-recovery/verify.py --check-sdk
# Reconstruct exact source inputs without changing selected programs:
python3 -B repro/donation-relay/framework-sysroot-recovery/verify.py \
  --materialize share-values --output /tmp/relay-share-values-source
```

The verifier reconstructs each input set from the sealed ancestor plus the saved
Cargo/source overrides, re-analyzes complete stripped/unstripped outputs, checks
all gains/losses, rechecks signed fixture bindings and checks the retained registry
receipt: **177 packages / 4,006 files** against official archive checksums. SDK
archive/member hashes and actual compiler probe outputs are retained under `sdk/`
and `probes/`. The Linux v1.48 archive hash is a checked content hash; its retained
release metadata does not supply an independent publisher digest.

For rebuilding, use the recorded driver/environment per variant and materialized
source. The tested target is `sbpf-solana-solana`, release profile, `--locked
--offline`, `-Zremap-cwd-prefix=`, and the root-crate remap
`src/=programs/contracts/src/`. Cross-host variants additionally use the exact
Linux sysroot and Darwin linker paths recorded in their drivers. The registry
cache must first contain the locked public crates. The drivers record the local
scratch layout and reuse dependency caches; their paths may need adapting.

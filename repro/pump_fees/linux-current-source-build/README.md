# Linux x86_64 Fees v1.44 builds (contributor-reported)

Builds on the upstream packages `repro/pump_fees/linux-v144-sysroot-provenance`,
`repro/pump_fees/linux-v144-hosted-comparison` and
`repro/pump_fees/linux-darwin-v144-attribution`.

The contributor reports two offline `cargo build-sbf --tools-version v1.44`
builds with the official Linux platform-tools v1.44 archive
(SHA-256 `6719b889d60677a8a2fcf4c82f68441a1afe0ab093edd2efe9f84a67a808b3e9`)
and CLI 2.1.21 on a Linux x86_64 host. This package retains only the two output
binaries and their raw comparisons. It includes no build log, host record,
toolchain receipt or source-input manifest for either build, so build provenance
is contributor-reported, not independently verified here.

| Source snapshot | Candidate | SHA-256 |
| --- | --- | --- |
| Frozen Fees revision `4ffe8bd88761059693e481ae972443c10204f7af` | `fees-frozen-linux-v144.so` | `7e823e605097cdba7a3d782a2f20edaee9980d7d5a29822ac7d1a43400620133` |
| Current main `804df5c8` (sharing-authorize source 26) | `fees-current-linux-v144.so` | `6c44d9f2ffe9b18c79a6344b256d8acd7a34c10e77b894c51f46512a447b8ce6` |

## Findings

1. `fees-frozen-linux-v144.so` is byte-identical to the hosted run 40166255149
   candidate (`7e823e60…`). It is the same Git blob as
   `repro/pump_fees/linux-v144-hosted-comparison/artifact/pump_fees_candidate.so`.
   The contributor reports it as a fresh build on a second Linux host. If so,
   it confirms that build's determinism, but without a build record the
   committed file cannot be told apart from a copy of the hosted artifact.
2. Comparison with the retained macOS main candidate `2387f8139a13918a…`
   (`repro/pump_fees/sharing-authorize-main-v144/main/candidate.so`, 863,808
   bytes; measured during maintainer review, not recorded in
   `raw-byte-comparison.json`):
   - Both files have the same ELF section set. `.dynsym`, `.dynstr` and
     `.shstrtab` are byte-identical.
   - `.rodata` is 8 bytes shorter in the Linux build. Its three sysroot path
     strings start with `/home/runner/` where the macOS build has `/Users/runner/`.
     Printable strings of six or more characters across the whole file are
     identical after normalizing that prefix.
   - `.text` has the same size (789,416 bytes) but 6,423 of its 98,677
     instruction slots differ. 2,071 are `lddw` immediates consistent with
     shifted rodata addresses, 247 are call immediates, and 309 are memory
     offsets only. The rest (3,418 opcode and 279 register differences, plus
     99 others) point to code-generation differences beyond address shifts,
     such as instruction selection, register allocation or ordering.
   - This package does not establish the cause of these code differences. The
     contributor reports, without a retained receipt, that both builds used the
     same 26 source inputs.
3. The raw comparison of the current-source Linux build `6c44d9f2…` against the
   frozen hosted-candidate build `7e823e60…` and the captured original
   `4f2955d0…` is recorded in `raw-byte-comparison.json`: 420,129 differing
   shared positions (first at 24, length delta +94,816) versus the frozen
   candidate; 460,758 differing shared positions (first at 24, length delta
   −85,144) versus the original. The upstream
   `linux-v144-sysroot-provenance` package already establishes that the
   original embeds `/home/runner/work/platform-tools` sysroot paths from the
   official Linux v1.44 archive.
4. Whole-file equality remains false for every local candidate versus the
   captured original. No padding or normalization was applied to any
   comparison. The contributor reports that no source or binary patch was
   applied and that the builds were clean and offline after an initial locked
   fetch.

## Verify

Run `python3 -B verify.py` for portable manifest/candidate/raw-comparison
checks. Add `--repo /path/to/pumpfun-source` to re-read the captured original
`evidence/original/pump_fees/deployed.so` and repeat all raw comparisons from
disk. Neither mode builds, executes the target or contacts a network.

## Reproduce

```sh
cargo build-sbf --manifest-path programs/pump-fees/Cargo.toml \
  --tools-version v1.44 --sbf-sdk <platform-tools>/sdk/sbf \
  --sbf-out-dir <out> -- --locked
```

with platform-tools v1.44 extracted so that `<platform-tools>/sdk/sbf/bin`
holds the shipped rustc/cargo.

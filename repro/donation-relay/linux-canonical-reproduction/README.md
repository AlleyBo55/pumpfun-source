# Fully Linux reproduction of the 480-window Relay recipe

The same recovered source now builds with the **official Linux x86_64 v1.48
SDK** in a dedicated Ubuntu 22.04 container. It reproduces **480/492 normalized
original windows**, **127 raw local body matches**, and the same **12 unmatched
windows** as the earlier Darwin-compiler/Linux-library recipe. No earlier match
is lost. The 818,072-byte output remains different from the 830,448-byte capture.
Selected program sources and artifacts are unchanged.

## Measured builds

| Variant | Exact source reference | Normalized matches | Unmatched |
| --- | --- | ---: | ---: |
| `control` | [Token-extension recipe](../token-extension-version-recovery/README.md) | 473 | 19 |
| `framework` | [Framework/sysroot/share-error recipe](../framework-sysroot-recovery/README.md) | 479 | 13 |
| `final` | [Mint-pair recipe](../mint-fee-pair-recovery/README.md) | **480** | **12** |

Every launch input map is compared to its sealed source reference. Only public
source, a read-only public registry cache and the read-only official SDK were
mounted for compilation. The captured program was read by the host analyzer only
after compilation; it was not mounted as a build input.

The framework and final Linux candidates each pass **536 fresh signed replay
records / 534 unique fixtures**, reproducing the saved original observations.
These are repeat executions of the existing finite corpus, not new unique
coverage. Compute metering and executable-image fields retain the original
comparator's exclusions. Protected settlement success and exhaustive behavior
remain unproved.

The final Linux and Darwin/Linux-library images have the same size and match set,
but are **not identical files**: 9,469 positions differ. This does not establish
host-independent whole-ELF output, a unique historical compiler recipe, or original
function names. Complete normalized windows still mask only the established
actual call/relocation immediates; data and indirect-call obligations remain.

## Cache control and the mint delta

An initial mint-source copy returned the previous ELF while Cargo reported the
root crate `Fresh`. That is **not evidence that the tuple predicate has no effect
on Linux**. Two such cache-reuse attempts and their source/output hashes are
retained but excluded from the measured-build table.

The package-scoped `cargo clean` attempt removed zero files. We then removed only
the 11 cached root-crate artifact/fingerprint paths in this task's isolated
`/work/target` directory; the precise paths are retained. The successful final
build log contains the actual SDK `rustc` invocation for the updated source.
No dependency, selected artifact or original capture was deleted or modified.

After that real compilation, exactly three stripped-output bytes differ from the
Linux framework control, at offsets 66185, 66193 and 66201—the same mint register
operand changes observed in the Darwin build. The original mint-policy window
then matches completely under normalization. Prefer a fresh `CARGO_TARGET_DIR`
when reproducing copied source trees, and check that the intended crate actually
compiles; source hashes alone cannot rule out stale build outputs.

## Recheck and reproduce

```sh
python3 -B repro/donation-relay/linux-canonical-reproduction/verify.py
```

The verifier checks source maps, sealed parents, stripped/unstripped outputs,
complete-window analysis, the unchanged residual set, three-byte mint delta, the
actual final compiler invocation, and signed replay evidence. It performs no new
compilation or target execution. `setup/` retains the container image/mounts,
installed package inventory, setup logs, registry checks and SDK archive check.
The [parent SDK inventory](../framework-sysroot-recovery/sdk/sdk-files.json)
contains the 2,873 checked SDK files, and its release metadata/observed archive
hash bind the official input. The archive's retained release metadata provides
no independent publisher digest.

The recorded drivers use the original local scratch paths. Reconstruct the exact
source from the corresponding parent package, adapt the public source/registry/SDK
mounts to a fresh directory, and use the pinned Ubuntu image and Linux SDK. The
build is `cargo rustc --release --target sbpf-solana-solana --locked --offline`,
with `-Zremap-cwd-prefix=` for the target and
`--remap-path-prefix=src/=programs/contracts/src/` for the root crate. All three
builds use the documented release profile; the final build adds verbose logging.

# Relay's repeated error type-ID frontier

This is a negative compiler-provenance experiment and an improved attribution,
not a recovered machine window. The latest full Relay research build remains
**470/492 normalized windows, 88 raw local matches, 22 unmatched**. Whole-file
identity remains false. Selected sources and artifacts are unchanged.

## What the three bodies represent

Original windows **56, 267 and 351** have the same 56-byte body. Their only
immediates return these halves of a type ID:

- stored at result +8: `0x77694f7f95096e5`
- stored at result +0: `0xf26e267850bd6732`

The latest candidate has three corresponding identical `core::error::Error::type_id`
symbols. Its vtables connect each to the `Debug`, `Display` and `description`
methods for **`alloc`'s internal `StringError`**, used by conversion from `String`
to `Box<dyn Error + Send + Sync>`. These are not the type ID of `std::io::Error`.
The original's anonymous bodies have the same instruction shape and different
128-bit constants. Associating them with the same method is an inference from
that structure and the candidate; it does not recover original symbol names.

`elf-evidence.json` retains full original/candidate bodies, hashes, addresses and
candidate vtable references. The verifier derives them again from the pinned
capture and retained unstripped candidate. No binary is patched.

## Local compiler matrix

`probe.rs` includes both a direct `TypeId::of::<std::io::Error>()` control and an
ordinary boxed-string conversion that emits the internal error's type-ID method.
The matrix tried every advertised `sbf-solana-solana` / `sbpf-solana-solana` alias
on ten installed macOS-host toolchains: v1.43, v1.44, v1.45, v1.46, v1.48, v1.50,
v1.51, v1.52, v1.53 and v1.54. It uses optimization level 3, panic abort, overflow
checks and the empty working-directory remap used by the reconstruction.

- **19 attempts; 17 successful compilations.** The two older-target attempts on
  v1.53/v1.54 fail because their `std` target libraries are absent. They are not
  counted as successful mismatches.
- **Zero successful probes return the captured type ID.** All emitted assembly,
  compiler versions, exact commands and compiler/core/alloc/std hashes are kept.
- The **v1.48 canonical `sbpf` probe reproduces the latest candidate's constants**:
  `0xcd7cc2605a5a778b`, `0x38559c1419c640e8`.
- Six further v1.48 controls retain the assembly for crate-name, directory-remap,
  crate-metadata, panic, overflow and target-alias choices. The first five keep
  the candidate's `sbpf` constants; changing the target alias gives different
  `sbf` constants.

The standalone probe and full dependency-linked program are different build
contexts. In particular, the existing full-program target-only trial retained
the same three unmatched window ordinals. Changing the target also changes
the candidate fingerprints, but neither fingerprint equals the capture.
This study therefore **does not establish that changing the application target
recovers the captured bodies**, nor that the original necessarily used a
particular SDK, host or released compiler. Linux-host sysroot provenance and
precompiled versus downstream-instantiated methods remain to be investigated.

## Recheck

```sh
python3 -B research/relay-string-error-provenance/verify.py
```

This verifies the complete package inventory, parent manifests, binary bindings,
body/vtable evidence, recorded assembly constants, 17 successes, two failures and
six controls. It does not rerun compilers or claim runtime coverage. No new
behavioral comparisons are added; the parent build's 536 records / 534 unique
fixtures remain its separately recorded finite suite.

`recorded-matrix.py` and `recorded-controls.py` are the exact local drivers used;
their paths name the original ignored scratch directory. The package retains
results independently of that directory. There is no new buildable Relay
candidate or promotion in this experiment.

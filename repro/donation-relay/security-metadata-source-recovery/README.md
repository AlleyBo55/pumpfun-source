# Relay: recover the missing security declaration from ordinary source

Adding the official `solana-security-txt` macro and the saved declaration's eight
semantic fields recovers the original **510-byte security payload**, its exported
`SECURITY_TXT` object, and the **entire 247-byte `.dynstr` section byte-for-byte**.
This is source compilation, not an embedded captured byte array or ELF rewrite.

The proposal retains **482/492 normalized instruction windows, 130 raw local
window matches, and all 348 equal source-location pairs**, with no lost window.
A fresh offline replay passes **536 records / 534 distinct fixtures** under the
existing comparison rules. **Whole-file byte identity remains false.**

## What was missing

The captured Relay exports `SECURITY_TXT`, a 16-byte Rust string reference in
`.data.rel.ro`. Its `R_BPF_64_RELATIVE` relocation points to the NUL-delimited
security declaration. The previous 482-window candidate had neither the export
nor that declaration. The saved human-readable declaration already exists in
`localnet/relay/embedded-security.txt`.

`source/embedded_security.rs` reconstructs the ordinary `security_txt!` fields:
name, project URL, contacts, policy, preferred languages, source-code URL,
auditors, and acknowledgements. The dependency is pinned to official registry
`solana-security-txt = "=1.1.3"`, already present transitively in the parent lock.
Its unchanged macro and checksum-bound package provenance are retained. This
macro emits a normal Rust string static. No original instructions, raw data
arrays, captured ELF, or address-specific linker script enter the source inputs.

The only source changes are that declarative module, an append-only module
reference in `src/lib.rs`, and the direct dependency in `Cargo.toml`/`Cargo.lock`.
Appending the module preserves every existing source line and column. The exact
57 compiled source inputs are retained in `source-snapshot.json.gz`; the verifier
inverts those four changes and checks all 56 parent hashes against the pinned
482-window upstream launch. `source-changes.diff` is the readable patch.

This recovers metadata from the original artifact and its saved declaration;
it does **not** establish that the historical project's repository or precise
source text has been recovered. Names and contact fields are informational,
not an instruction to contact anyone or use a live service.

## Measured ELF changes

| Section | Original | Parent | With declaration |
| --- | ---: | ---: | ---: |
| `.text` | 752,488 | 752,888 | 752,888 |
| `.rodata` | 19,863 | 19,343 | 19,847 |
| `.data.rel.ro` | 6,928 | 6,912 | 6,928 |
| `.dynsym` | 408 | 384 | 408 |
| `.dynstr` | 247 | 234 | **247, exact bytes** |
| `.rel.dyn` | 37,232 | 37,216 | 37,232 |

Sizes alone do not establish section identity. Except for `.dynstr` and the
already-equal `.shstrtab`, complete sections remain unequal. The string-reference
pointer and relocation addresses differ; only its complete 510-byte payload is
raw-byte-identical. The remaining 16-byte `.rodata` deficit is unresolved, not
an invitation to manufacture padding. Function ordering, addresses and ten
unmatched business bodies remain unresolved.

The actual original ELF extent is **818,280 bytes**, followed by **12,168 zero
bytes** in the **830,448-byte captured program allocation**. The parent compiler
ELF is 818,096 bytes; the recovered compiler ELF is **818,664 bytes**, 384 bytes
larger than the original ELF extent. Neither compiler output has a trailing
allocation region. These are distinct comparisons; no allocation padding is
added to the compiler result.

Full shared-position differences against the capture change from 415,605 to
403,421, while the capture-only length tail changes from 12,352 to 11,784 bytes.
These position-sensitive counts are retained diagnostics, **not** an identity
percentage or proof that layout is recovered.

## Build and verification evidence

The official Anza platform-tools v1.48 native-Linux baseline was independently
rebuilt and exactly reproduces parent SHA
`c6ae09b906b3c6a88042e40b02e0a2f6598268061d7527b667c0e631655a3921`.
The proposal SHA is
`af837c4491a267e144cfb0cb7e1fc6772f22ddd353ada93de2b1286489d4beea`.

The trial copied the baseline dependency cache into a separate target directory,
explicitly cleaned the root package and required one actual root-crate `rustc`
invocation. The copied seed, registry sources and source inputs remained
unchanged. Both builds completed without recorded SBF backend errors. Ordinary
`llvm-objcopy --strip-all` is the only post-compilation transformation. Logs,
tool/archive hashes, source maps, commands and the reviewed controller snapshot
are retained under `builds/`; snapshots describe the original workspace and are
not installed tools or standalone portable launchers. Recorded logs and input
manifests are not authenticated process traces or filesystem isolation proofs.

The verifier reparses both binaries, checks the dynamic-symbol object's type,
section, relocation, exact payload extent and contents, recomputes every window
and section comparison, and rechecks all 348 source-location pairs. It also
revalidates the fresh replay receipt against the unchanged saved fixture corpus,
including transaction signatures. Replay remains bounded; existing exclusions
for compute-meter logs and executable-account binary storage remain unchanged.
No live transaction, deployment, wallet or RPC service is involved.

```sh
# Uses the repository's existing pinned solders runtime for receipt checks.
python -B repro/donation-relay/security-metadata-source-recovery/verify.py
python -B repro/donation-relay/security-metadata-source-recovery/test_verify.py
python -B repro/donation-relay/security-metadata-source-recovery/verify.py \
  --materialize work/relay-security-source
```

To rebuild, use the exact official v1.48 SDK, registry checksums and native-Linux
recipe in `builds/recovered/launch.json`: target `sbpf-solana-solana`, root
`--remap-path-prefix=src/=programs/contracts/src/`, and target Rust flags
`-Zremap-cwd-prefix=`, with Cargo `--locked --offline`. Dependency source caches
must retain the SDK Cargo's recorded registry source paths. The manifest uses
one codegen unit, release optimization, overflow checks and abort panics.
Rebuild in a fresh target or explicitly remove root artifacts; do not count a
cached artifact as a compilation. Materializing source does not install tools,
compile code, or run the target. The retained replay runner can independently
rerun the same local corpus against a newly produced candidate.

Selected production source/checkpoint artifacts are unchanged. This is a
research milestone toward full byte identity, not completion.

# Shipped sysroot helpers and direct Pump / AMM / Fees fingerprints

The official Darwin arm64 platform-tools **v1.46.1** archive ships the exact
1,160-byte `core::fmt::write` body found in the retained v1.46.1 Fees build.
The same body occurs in the retained v1.46 build. It does not occur anywhere
in the captured Fees `.text`; the prior audit's corresponding captured window
is 1,056 bytes and equals the v1.44 build's body.

Direct inspection of **all three captured programs** also finds that v1.44
formatting body and its 352-byte `__multi3` body, each exactly once per program.
All six raw matches occupy complete windows between independently decoded direct
call targets, with no loader relocations inside them. The shipped v1.46.1
formatting body occurs in none of the three captured `.text` sections. This
provides direct Pump/AMM byte evidence, instead of inferring their compiler
family solely from the Fees measurement and common ELF header/source paths.

A fresh static check of the official **v1.44** archive also finds both positive
helper bodies unchanged in its `sbf` and generic `sbpf` sysroots. The archive's
six corresponding `sbpfv1`/`sbpfv2`/`sbpfv3` bodies differ and have no exact
occurrences in these three captures. Ten complete objects are retained for this
comparison. The equal generic helper bytes do **not** distinguish the `sbf` and
`sbpf` aliases, nor identify a unique historical compiler.

This adds a direct **release archive → rlib → ELF object symbol → linked
function** byte comparison to the existing
[controlled compiler audit](../../repro/identity-audit/2026-10-25/compiler-v1461/REPORT.md).
That audit already measured v1.46.1; this is not a new compiler build or a newly
discovered v1.46.1 exclusion. The narrower finding is that this negative helper
fingerprint is present in the shipped generic-v0 sysroot object before application
linking. Changing application source order alone cannot explain a difference
already present in that object, if the object body is linked unchanged.

## Exact observations

| Bytes | File offset | Length | SHA-256 |
| --- | ---: | ---: | --- |
| Shipped `core.rcgu.o` symbol | 670,992 | 1,160 | `c95bc90f012059c7644fb399e1344707a09e5fb7ef9f0ada292a5b22e734ebd6` |
| Retained v1.46.1 Fees build | 322,864 | 1,160 | same |
| Retained v1.46 Fees build | 320,240 | 1,160 | same |
| Retained v1.44 Fees build | 319,272 | 1,056 | `7a5339492369c3813ea033c29cf8313288cf8efa07b2da552321cebc9c9f13c1` |
| Captured Fees window | 775,776 | 1,056 | same as v1.44 |

The shipped symbol is `_ZN4core3fmt5write17h1292dd406f3af67fE`, in section 525,
`.text._ZN4core3fmt5write17h1292dd406f3af67fE`, of an ELF64-LE relocatable object
with `(e_machine, e_flags) = (263, 0)`. Its section-relative offset is zero.
The symbol's complete body has no object relocations and no SBF relative-call
immediates. Indirect-call instructions remain intact. All comparisons above use
unmodified bytes; **no instruction masking, relocation rewriting, zero padding,
or normalized match** is involved.

The verifier derives body bounds from the unstripped ELF symbol tables, checks
stripped/unstripped `.text` equality and the raw stripped body at the recorded
offset, and cross-checks the prior helper record. The captured binary is stripped:
its function identification/bounds come from the linked prior audit, not an
original named symbol. The new check reads that exact captured window and also
searches all of captured `.text` for the complete shipped 1,160-byte body; there
are zero occurrences. It makes no behavioral claim about the two implementations.

## Direct cross-program check

`cross-program-analysis.json` retains every matched range, exact caller instruction
and signed displacement, target address, next direct-call target, and referring
caller at the end boundary. Addresses are converted through the ELF `.text`
mapping; the reader does not assume that virtual addresses equal file offsets.
Relocated external calls are excluded and LDDW continuation words are skipped.

| Captured program | v1.44 formatting body `[start,end)` | v1.44 `__multi3` body `[start,end)` | Shipped v1.46.1 formatting body occurrences |
| --- | --- | --- | ---: |
| Pump | `[1762144,1763200)` | `[1791432,1791784)` | 0 |
| PumpSwap | `[1131744,1132800)` | `[1161264,1161616)` | 0 |
| Fees | `[775776,776832)` | `[799040,799392)` | 0 |

The multiplication body's SHA-256 is
`face056642083fcc15c6737f1910030a4b59b6a78a4fa523f142dc0f28635762`.
The two positive reference bodies are read from the retained **v1.44 linked Fees
build**, cross-checked against its unstripped symbols, stripped bytes and prior
helper records. The additional `v144/` packet independently compares those
complete bodies with shipped object symbols as described below. The negative
1,160-byte reference is read from the retained **v1.46.1
shipped libcore object**, whose archive association is checked as described below.

Each positive match starts at an actual relative-call target; the next such
target is exactly its end. This is stronger than an unbounded byte-substring
match, but these stripped captures have no debug symbols proving every possible
function boundary. Indirect-only entries or undiscovered internal boundaries
are outside this ledger. The raw occurrences do not prove behavioral equivalence,
full dependency identity, or a unique compiler release. The captures are read
unmodified, including their allocation tails, but only `.text` is searched.

## Archive binding

Input repository revision: `b05ed7f023fcd2935564441ccf239a477790c741`.
The hash-bound repository inputs are listed in `provenance.json`.

- [Official release](https://github.com/anza-xyz/platform-tools/releases/tag/v1.46.1),
  asset ID `564703966`, `platform-tools-osx-aarch64.tar.bz2`, 372,707,817 bytes.
- Archive SHA-256:
  `b8764fbd1cd2c7e99011f7b1ac645e1a6eb9313d3356c44ec7a2d46c4b340f5a`.
  It matches the retained release API's publisher digest. The acquisition command
  was a direct HTTPS download; no release executable was run.
- Archive member:
  `rust/lib/rustlib/sbpf-solana-solana/lib/libcore-d7515fd2b390385b.rlib`,
  32,617,896 bytes, SHA-256
  `508892859174d93bfeec246a85d77283e83ecfc481e2ee2225f3bd01c46ffe0d`.
- Its ar member `core-d7515fd2b390385b.core.e8f91360fcb7dc2d-cgu.0.rcgu.o`
  starts at rlib byte 31,413,080, is 1,204,816 bytes, and has SHA-256
  `bd8b5c5964af0dd1ac566932938fc44d814c1aaa2bdee95ac4fb0242d18c4476`.
  This complete object is retained as `core.rcgu.o` so symbol and relocation
  checks can run without the large release archive.
- `version.md` records Rust source commit
  `71e82b8fbf1c50edc2cb1bf711b1d5b15a2c7278`. This is a distribution's recorded
  source identity, not a source-to-toolchain reproducible-build attestation.
- A fresh stream check verified **all 30 files** in the prior selected distribution
  manifest against the official archive, plus `version.md`, and compared the
  retained object with its ar member. The 30 entries cover five tool paths and 25
  generic SBPF target rlibs, not the entire distribution. `ld.lld` is shipped as
  `llvm/bin/ld.lld -> lld`; the checker validates that exact link and hashes
  `llvm/bin/lld` in memory. It creates/follows no filesystem links. The initial
  failed check, which expected every selected entry to be regular, is retained in
  `audit-attempts.json`.

`archive-validation.json` is the successful run receipt. The large tarball and
rlib remain outside this packet. Default verification checks retained object and
repository bytes and explicitly reports that it has **not rechecked** the
archive-to-object association. To independently recheck that association, supply
the publisher-digest-verified archive with `--archive`; the checker hashes it
before reading members and never extracts or executes tools. Saved JSON receipts
alone do not authenticate omitted archive bytes or establish historic execution.

## Positive v1.44 archive binding

The [official v1.44 release](https://github.com/anza-xyz/platform-tools/releases/tag/v1.44)
asset `234589328`, `platform-tools-osx-aarch64.tar.bz2`, is 400,794,156 bytes.
Fresh acquisition gives SHA-256
`66e20d135fddd70ff519baf7ff320d762957f9aedf93a50e23756db23ad79351`, exactly matching
the earlier repository toolchain acquisition receipt. This release's API digest
is absent: the hash is an observed-content pin, **not a publisher checksum**.
The distribution records Rust revision `08b7341888ab480dfaaa0698300cbbbbb2d75b53`.

| Shipped target | Formatting bytes / equals linked reference | `__multi3` bytes / equals linked reference |
| --- | --- | --- |
| `sbf-solana-solana` | 1,056 / yes | 352 / yes |
| `sbpf-solana-solana` | 1,056 / yes | 352 / yes |
| `sbpfv1-solana-solana` | 1,072 / no | 368 / no |
| `sbpfv2-solana-solana` | 1,072 / no | 384 / no |
| `sbpfv3-solana-solana` | 1,072 / no | 384 / no |

All ten objects are ELF64-LE `ET_REL`, machine263, with flags0/0/1/2/3 for the
listed targets. Each selected function is complete according to its object's
symbol table and has no object relocations or relative-call immediates. The
generic formatting symbols differ (`hc096270015428e07` versus `hf318c977a49e4ec1`)
while their body bytes are equal. Matching symbols by name alone would therefore
lose this alias ambiguity. No bytes are masked, padded or rewritten.

`v144/provenance.json` records all ten rlib hashes, exact ar member names/offsets,
complete object hashes and symbol records. `v144/objects.tar.gz` retains those
complete objects; `v144/analysis.json` records their direct comparisons with the
linked reference and raw occurrence offsets in each capture. The four positive
object bodies refer to the same six call-bounded capture windows above, not
twelve distinct functions. The six extended-target bodies have no raw hits.

The optional `--v144-archive` check hashes the whole archive before parsing,
then verifies all ten selected rlibs, each retained object and `version.md`.
`v144/archive-validation.json` retains the successful check. This does not cover
every distribution file or establish which sysroot a historical build loaded.
Default verification explicitly leaves this omitted-archive check false.
Rust's pinned license/copyright files and its `Cargo.lock` accompany the objects;
the lock identifies compiler-builtins revision `5380e204aab5be48c798679cc52b1f871c8ad4bc`,
whose complete license is also retained. These source notices are not a
source-to-toolchain reproducible-build attestation.

## Third-party notices and receipt redaction

The binary objects in this packet are unmodified third-party build outputs, not
contributions under the repository license. `core.rcgu.o` (v1.46.1 libcore) and
the five libcore objects in `v144/objects.tar.gz` are Rust standard-library code;
`COPYRIGHT`, `LICENSE-APACHE` and `LICENSE-MIT` (and their identical copies under
`v144/`) are Rust's upstream notices for them and for `v144/rust-Cargo.lock.gz`.
The five `compiler_builtins` objects in `v144/objects.tar.gz` are covered by
`v144/compiler-builtins-LICENSE.txt`. `license-sources.json` records each root
notice's upstream URL (anza-xyz/rust `71e82b8f…`) and SHA-256;
`v144/license-sources.json` records each `v144/` notice's upstream URL, Git blob
SHA-1 and SHA-256. At maintainer review every notice's `git hash-object` also equaled
the corresponding upstream tree blob (`COPYRIGHT` `05993830…`, `LICENSE-APACHE`
`1b5ec8b7…`, `LICENSE-MIT` `31aa7938…` at both Rust revisions, compiler-builtins
`LICENSE.txt` `92bbe113…` at `5380e204…`). These notices do
not relicense the packet's own scripts, tests, JSON analyses or this README, which
fall under the repository's root `LICENSE`.

Maintainer review replaced one contributor-local absolute Windows path (the curl
`--output` argument in `v144/download-receipt.json`) with a placeholder and added
an `output_path_redaction` note. No URL, size, digest, asset ID or exit field
changed; the verifier does not read the redacted argument.

## Reproduce

From the repository root, using Python 3.11 or later, standard library only:

```sh
python -B research/fees-sysroot-object-provenance/verify.py
python -B -m unittest discover -s research/fees-sysroot-object-provenance -p 'test_*.py'
python -B research/fees-sysroot-object-provenance/verify.py \
  --archive /path/to/platform-tools-osx-aarch64.tar.bz2
python -B research/fees-sysroot-object-provenance/verify.py \
  --v144-archive /path/to/v1.44/platform-tools-osx-aarch64.tar.bz2
```

The default checks are offline and read-only. The optional archive command is
also offline; acquire the linked release separately. Tests mutate instruction
bytes, archive payloads, symbol/section data, relocation references, duplicate
members, symlink destinations and external input identities. Rust's pinned
MIT/Apache license and copyright notices accompany the object; their source URLs
and hashes are in `license-sources.json`.

## Limits and next step

This packet attributes both positive reference routines to shipped v1.44
objects, and the negative formatting reference to a shipped v1.46.1 object.
It checks those bytes directly in three captured programs. It does not prove
which files a historical compiler loaded:
the v1.46 body is byte-identical despite a different mangled symbol. It does not
identify the deployed compiler, recover missing application source, or improve
whole-file identity. Raw output, captured allocation size, and behavioral
equivalence are separate questions.

The useful constraint is on a **stock generic-v0 sysroot with unchanged linkage
of this body**. LTO/recompilation, custom sysroots, changed standard-library build
profiles, and mixed compiler/linker pipelines remain possible. v1.44 remains
the prior audit's strongest measured stock candidate. Future compiler trials
should record and compare the supplied sysroot object's body as well as the
frontend version; repeating the already measured v1.46.1 application build is
not needed to establish this particular mismatch.

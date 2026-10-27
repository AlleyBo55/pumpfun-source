# Pinned v1.37 branch-layout discriminator

Two small LLVM inputs with identical named blocks, instructions and CFG edges
produce complementary remaining-use branches under the same pinned v1.37 `llc`.
Only textual basic-block order differs. Moving the underflow error block next to
the guard changes `requested > remaining` into `remaining >= requested` during
selection, before Finalize ISel. Block contents, predicates, compiler and flags
are identical in the two measurements.

This narrows an input-layout mechanism relevant to the
[candidate12 trace](../metaplex-candidate12-trace/README.md). It is a synthetic
compiler experiment, **not a new Metaplex source candidate or program build**.
Both tiny outputs have 88 text bytes / 11 instructions and no unconditional jump.
The experiment therefore **does not reproduce candidate12's extra jump**, repair
its whole-program bytes, or identify the historical source. Its useful result is
that the pinned backend can already generate the desired complementary condition
from the unchanged predicate when its selection-time layout permits it.

## Observed stages

Both inputs first test zero and over-total requests, then test the same
`icmp ult i64 %remaining, %n`. Both error blocks store 86 and call the same opaque
external `sink`; the success block subtracts and stores the remainder. They are
standalone LLVM inputs authored for this experiment. No captured executable or
Metaplex source is supplied to the compiler.

| Observation | `far-error.ll` | `near-error.ll` |
| --- | --- | --- |
| Layout after remaining-check block | initial-error, success, underflow-error | underflow-error, initial-error, success |
| Final LLVM selection input | Original block order and every named block's instructions preserved | Same |
| Before Finalize ISel | `JUGT_rr %1, %3` to error; explicit jump to success | `JUGE_rr %3, %1` to success; explicit jump to error |
| Before branch-folder | `JUGT_rr $r2, $r4`; explicit success jump | `JUGE_rr $r4, $r2`; explicit error jump |
| After branch-folder | Condition retained; success is fallthrough, jump removed | Condition retained; error is fallthrough, jump removed |
| After block-placement and pre-emit | Same direction, no unconditional jump | Same direction, no unconditional jump |
| Final branch bytes, `.text` offset 16 | `2d42040000000000` | `3d24040000000000` |

The two error blocks are identical (store 86, call `sink`, return), so
branch-folder also tail-merges them in both variants. In the near input
`underflow_error` disappears into `initial_error`, whose predecessors become
blocks 0, 1 and 2; the far input merges the same way. That merge is why each
output has 11 instructions. "Error is fallthrough" in the near column therefore
means the merged error block. The condition direction is already fixed in the
dump before Finalize ISel, which runs before this merge, so the merge does not
explain the direction change.

`analysis.json` records full emitted instruction bytes, section/file offsets,
signed branch targets, exact stage hashes, complete remaining-check blocks and
their next layout blocks. Complete logs, IR inputs, ELF objects and disassembly
are retained inside the provider ZIP. The verifier reads object bytes directly;
disassembler labels are not the basis of the branch comparison.

The far object is 912 bytes, SHA-256
`d87cbb3844874e1829053d153c75925b7f337916e3f0d6b42bff2877427c4e50`;
the near object is 944 bytes, SHA-256
`61e40392ead0d6a46ff847ea61492a7fb1758ee2f929f241526f8660b6c61bab`.
Both are relocatable ELF64 objects with `(e_machine,e_flags)=(247,0)`, not linked
program images. Equal text lengths do not imply equal instructions or object bytes.

## Source explanation, separated from runtime observations

The archive's `version.md` declares Rust revision
`764ce69bd00903f5c59f44b6aa72649b173f568c`. Saved primary GitHub tree responses bind
its `src/llvm-project` gitlink to
`7b8db05b564faffb522434b73b7082662171f94a`. Seven complete source/license files at
that LLVM revision are retained in `compiler-source.tar.gz`, with source URLs,
SHA-256 and Git blob identifiers in `compiler-source-receipts.json`.

- `SelectionDAGBuilder.cpp`, `visitSwitchCase`, complements a condition when its
  true target is the next layout block. In the near input that target is the
  underflow-error block. The observed switch to `JUGE` is already present before
  Finalize ISel; the experiment does not instrument the internal C++ decision.
- `SBFISelLowering.cpp`, `NegateCC` / `LowerBR_CC`, swaps operands for unsupported
  less-than/less-or-equal conditions when extended jumps are unavailable.
- `SBFInstrInfo.cpp`, `analyzeBranch`, handles unconditional `JMP` but returns
  analysis failure for conditional branches. Its `insertBranch` handles an empty
  condition only, and `removeBranch` removes `JMP` only.
- `SBFInstrInfo.h` supplies no `reverseBranchCondition` override; the generic
  `TargetInstrInfo.h` implementation returns unsupported. `BranchFolding.cpp`'s
  conditional-inversion paths depend on successful branch analysis and reversal.

These source constraints explain why expecting generic late conditional
inversion is not a reliable repair strategy for this backend. They do **not**
mean later passes cannot remove jumps: both synthetic runs remove their explicit
fallthrough jumps, as the saved before/after branch-folder observations show.
The source explanation is an inference corroborated by the stages, not a trace
of calls to `analyzeBranch` or `reverseBranchCondition` in the Metaplex build.

The static
[branch-selection audit](../../repro/metaplex/branch-selection-audit/README.md)
reached the same `visitSwitchCase` / `NegateCC` / `analyzeBranch` inference from
source alone, at the same LLVM gitlink. This packet adds a measured `llc`
observation of that mechanism. The audit also records the original Metaplex bytes
at file offset 238832, `3d97070000000000` (unsigned `r7 >= r9` jumps to success,
error is fallthrough). That is the same orientation as the near variant's `JGE`.

The seven files in `compiler-source.tar.gz` are unmodified LLVM Project files
from the anza-xyz fork. They are licensed under the Apache License v2.0 with LLVM
Exceptions; the six source files carry that SPDX header, and the complete license
is retained as `llvm/LICENSE.TXT` in the same tarball. That license covers those
retained files only. It does not change the license of this packet's own
scripts, analyses or README.

## Execution provenance and retained failures

Successful fork run [40366528602](https://github.com/startrack3r/pumpfun-source/actions/runs/40366528602)
used controller `40c72c1c209a3d67cb667ab58578263a3168c3ea`. The exact 48-member
provider ZIP has SHA-256
`3aeec015a49f8d8341bdbb457e51499a6b95f10eb7ea9e315894587c7aff820c`.
All commands succeeded, including container cleanup.

The 362,756,282-byte platform-tools archive matches the previously pinned SHA-256
`8d5153589dbe19635affe937663cf4555a7e69a62d91ab4a1df064aaa8d5f066`.
The installed 63,765,552-byte `llc` matches its archive member, SHA-256
`2affdc891b942c66d57e5a7329661a440f197bc7b39b1a76c533ca8fe932e65b`.
The pinned Solana build-image digest and actual image ID are checked before use.
Compilation uses `-mtriple=sbf -mcpu=generic -mattr=+solana -O3 -filetype=obj` in a
network-disabled container with a read-only root filesystem and temporary tool
and output storage. The full 2026 acquisition/command receipts are retained.
This is a fresh `llc` execution, not an invocation of the Rust frontend or an
attestation of the historical deployed compiler. The old release has no
independent publisher digest in the previously retained metadata; the archive
hash is a fixed observed-content pin. The large archive is omitted here.

Two failed runs remain byte-for-byte alongside the successful artifact:

| Run | Preserved result |
| --- | --- |
| [40365560810](https://github.com/startrack3r/pumpfun-source/actions/runs/40365560810) | Archive digest passed, then member lookup failed on `./`-prefixed paths; no compiler or container execution occurred. |
| [40365964291](https://github.com/startrack3r/pumpfun-source/actions/runs/40365964291) | Far input compiled and disassembled, then `docker cp` could not retrieve its tmpfs object; near input was not compiled. |

The final controller normalizes archive lookup names while retaining exact tar
member names for extraction, reads object bytes through the running container,
and adds a before-branch-folder snapshot. It changes neither input's block
contents. The fork-only workflow is retained inside each artifact as execution
evidence; this contribution does not install a workflow upstream.

## Reproduce and next constraint

```sh
python -B research/metaplex-branch-layout/verify.py
python -B -m unittest discover -s research/metaplex-branch-layout -p 'test_*.py'
```

Default verification is offline, read-only and standard-library-only. It checks
all three provider/source/command bindings, source hashes and LLVM gitlink,
unchanged named IR blocks, stage directions and complete raw object bodies. The
packet also verifies after relocation outside the checkout. No normalized ELF,
patched object or allocation image is generated.

On a separate Linux x86_64 Docker runner, `probe.py --output /fresh/path` reacquires
the pinned inputs and repeats the two offline compilations. It needs no Solana
accounts, program cache or captured binaries and sends no blockchain transaction.

For actual reconstruction, the unresolved input is a justified Rust/source or
compiler history that produces the relevant selection-time layout in the full
Utilize function. The measured tiny CFG is not a substitute for that evidence.
Candidate12's 8-byte shift and candidate11's source-coordinate residuals remain;
neither candidate is promoted and no whole-program or security claim is made.

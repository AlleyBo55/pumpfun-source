# Fees: bind slice-copy panic data and four original source locations

Whitespace moves two real tier-copy statements to the original lines and columns,
correcting four referenced source-location records. The rebuilt ELF changes at **exactly eight
bytes**, each in `.data.rel.ro`; its entire `.text` section remains raw-byte
equal to its freshly built control. No captured artifact is patched or used as
a compiler input. Both statements' tokens, subsequent guard lines and the other
34 inputs remain unchanged.

| Original caller | Actual call | Resolved original location |
| --- | --- | --- |
| 261816 | Slice range failure at +1264 | `programs/pump-fees/src/state.rs:398:19` |
| 261816 | Slice length failure at +2096 | `programs/pump-fees/src/state.rs:398:33` |
| 265976 | Slice range failure at +1264 | `programs/pump-fees/src/state.rs:451:19` |
| 265976 | Slice length failure at +2096 | `programs/pump-fees/src/state.rs:451:33` |

The checker decodes the actual LDDWs, their relocation-backed file strings and
location records, and both encoded caller edges to the complete 200-byte body
at original **784168**. It separately reads that body's three literal message
pieces, two numeric arguments, shared numeric formatter and encoded panic call.
The message reports a **source/destination slice-length mismatch**. The matched
Linux symbol identifies `core::slice::copy_from_slice::len_mismatch_fail`.
`clone_from_slice` on the upstream `Copy` tier type reaches this specialization
as well. Describing this body as an ordinary index bounds check confuses two
different panic contracts.

This explains the three-piece versus two-piece observation retained by the
earlier target-library negative trial: the earlier comparison did not identify
the same panic kind. This packet does not repeat that toolchain experiment or
alter its frozen sources, logs or receipts. It supplies a new, independently
decoded caller/data attribution.

## Validation and scope

The fresh control reproduces **both PR #149 ELFs raw-byte exactly**, including its
**368 unique structural body pairs**. It retains **68 unmatched original
windows**, **587 candidate windows** and **63 unique raw-equal local pairs**.
The proposal preserves all of those counts. Four location contracts are improved;
there is **zero additional instruction-body coverage** and no whole-file identity.

The control and proposal retain their source-hash-bound builds, complete
artifacts, symbol extents, actual compiler logs and strip replays. The control's
identical **17,331-case / 18-suite** and **1,542-case** runtime receipts are
explicitly reused from PR #149; the proposal has fresh executions of both,
plus the **24-case exotic-fee growth/rejection-precedence matrix**. These cases
compare the seven fields listed in the receipt; their retained logs are not part
of that matrix's match predicate. The current event-borrow and exotic-fee
precedence recoveries are carried forward without discarding their gains.
Current-state, preserved-metadata and portable saved-signature guards passed on
the recorded primary checkout after its missing historical assets were restored.
Their exact scope and outputs are retained in `checks/`; they do not claim a
guard pass for a different later branch head or originating runtime-byte identity.
The standalone checker enforces the exact eight-byte ELF delta and
complete raw text equality. Three adversarial tests distinguish an opaque
source-column mutation, an opaque message mutation and a masked CALL retargeting.
Their failures require the separate data/target checks, even when the body or
entire text still matches.

Both builds preserve the parent's three root rustc path mappings for the math
source, as recorded in their actual root compiler invocations. The fresh
control's entire 860,464-byte candidate and 1,236,624-byte symbol ELF reproduce
the upstream artifacts exactly. This compiler reproduction is separate from
comparison against the deployed original. No build receipt is retagged to a
different artifact.

```sh
python3 research/fees-slice-origin-contract/verify.py
python3 -I research/fees-slice-origin-contract/verify.py
python3 -B research/fees-slice-origin-contract/test_scope.py
```

Rebuild from the bound revision and complete source overrides using official
Linux platform-tools v1.44, canonical `sbpf-solana-solana` and the retained
commands with `RUSTFLAGS=-Zremap-cwd-prefix=`. The selected programs, pinned
scripts, workflows, root attributes and checkpoint ledgers are unchanged.
Recorded hashes/logs are retained evidence, not authenticated process traces.
The recorded driver is a workflow capture, not an SDK installer. Original
function boundaries remain inferred; every candidate boundary is separately
checked against all symbol extents, including aliases. Structural signatures
mask local CALL immediates and actual relocated LDDW addresses, retaining scalar,
register, stack, branch and external import identities.
Finite runtime comparisons do not establish exhaustive semantics. This verifies
the explicitly decoded data/call contracts; other referenced data, transitive
semantics, 68 unmatched bodies and final ELF layout remain open. Four-core whole
raw binary identity remains **0/4**.

The raw comparison report is replayed independently for all four selected
binaries without padding or normalization. It also compares this final research
Fees artifact. These are comparisons of actual stored artifacts; this check
does not claim fresh compilation of the other three programs.

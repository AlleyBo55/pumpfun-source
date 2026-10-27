# Relay: location-data gaps behind matched instruction bodies

The pinned **480/492 normalized-window** candidate still contains **43 uses of
six distinct source-location value-pairs** in 23 uniquely matched windows. The
referenced strings and line/column fields differ from the capture even though
those function bodies match after the existing call/relocation masking.

This packet adds a static data audit and four **uncompiled source-coordinate
proposals**, not another normalized or raw-byte recovery claim. No executable is
rewritten. Selected sources, compiler outputs and runtime receipts are unchanged.

## Measured differences

Paths below are relative to the common `programs/contracts/src/` prefix.

| Original source location | Candidate source location | Uses |
| --- | --- | ---: |
| `lib.rs:36:1` | `lib.rs:36:5` | 33 |
| `tools/fair_distribution.rs:46:20` | `tools/fair_distribution.rs:33:35` | 1 |
| `tools/checks.rs:96:31` | `mint_policy.rs:116:21` | 1 |
| `events/v1/donation_epoch_processed.rs:5:1` | `anchor_donate.rs:44:1` | 6 |
| `events/v1/donation_epoch_just_swapped.rs:5:1` | `anchor_donate.rs:36:1` | 1 |
| `events/v1/donation_epoch_closed.rs:5:1` | `anchor_donate.rs:31:1` | 1 |

The affected original windows are 69, 106, 171, 172, 175, 177–187, 200–204,
209 and 218. The complete addresses, bytes, hashes, matching candidate symbols,
reference-instruction offsets and nearby direct-call targets are recorded in
`location-audit.json`.

Each value-pair can represent more than one physical record. Every use retains
its actual original/candidate target address and full 24-byte object bytes; each
group also carries the first decoded record and exact bounded path.

These are actual bounded field differences, not comparisons of arbitrary bytes
after an object. For example, window 106's record is used next to
`core::cell::panic_already_mutably_borrowed`; its captured diagnostic names
`tools/checks.rs:96:31`, whereas the candidate names `mint_policy.rs:116:21`.
Generated IDL methods reference the `lib.rs` record near unwrap, bounds and
overflow panic handlers. The event-related records occur near allocation-error
handlers. Static proximity supports the source attribution but is not a complete
reachability/dataflow proof or a claim those paths were exercised by a fixture.

## Exact scope and method

Inputs are the pinned capture (`367f07a6…`) and the
[mint-fee-pair candidate](../../repro/donation-relay/mint-fee-pair-recovery/README.md)
(`da61931f…`, 818,072 bytes), plus its unstripped symbols (`dbf90f77…`). The
capture is 830,448 bytes; whole-file equality remains false.

The verifier checks the existing ELF parser's SHA-256 before import, independently
recomputes function normalization, and scans only the **336 original windows
having exactly one normalized candidate match**. It recognizes **346 paired
location-shaped records**: 303 agree in path/line/column and 43 do not.
Ambiguous and unmatched windows are intentionally excluded, so this is not an
all-program diagnostic inventory or complete data-identity proof.

Each recognized object is bounded to 24 bytes: a relocated pointer, an explicit
64-bit string length and two 32-bit fields. The pointed-to string is read for
exactly that length, must lie in `.rodata`, and must be an ASCII `.rs` path.
The record must lie in `.data.rel.ro` and have an actual
`R_BPF_64_RELATIVE` relocation. In these pinned SBF files the non-text relocation
addend occupies the high 32-bit word; the decoder requires the low word to be
zero. The allocation/relocation representation and exact bytes are observations;
identifying the resulting fields as Rust `Location { file, line, col }` is an
inference supported by source anchors and the consuming panic/allocation calls.
No generic rule is asserted for other ELF formats or SDK versions.

The source anchors are hash-bound to the pinned 480-window candidate's recorded compile
input map. No earlier build's source or address mapping is silently reused.

## Source-only proposals

Four independent diffs under `patches/` address the six observed records:

1. **Program attribute:** remove the four leading spaces before `#[program]`
   at `src/lib.rs:36`, preserving the line number.
2. **Event locations:** move the three unchanged event declarations into
   `src/events/v1/` files with `#[event]` at line 5, column 1. Replace the old
   declarations with `include!` calls, preserving their inclusion namespace and
   the number of lines in `anchor_donate.rs`.
3. **Mint borrow:** move the unchanged typed mint helper into an `include!` file
   at `src/tools/checks.rs`, locating its `borrow` token at line 96, column 31.
4. **Remainder push:** place the existing `remainders.push` call's `push` token
   at line 46, column 20. Consume existing blank lines so the previously
   reconstructed indexed amount update remains on line 63.

`proposals.py` reconstructs every diff from the pinned source anchors and checks
the exact target tokens/coordinates. Tests check that whitespace-normalized,
textually expanded source is otherwise unchanged. This is a source-structure
check, **not** proof of identical macro expansion, machine instructions, full
panic behavior or byte improvements. `include!` can affect compiler source
provenance and code generation; fresh builds and original/candidate replay are
required before promoting any change. These coordinates reproduce observations,
not the unknown original comments, whitespace or source text.

The patches apply to fresh materialized candidate sources, never to the sealed
checkpoint packages or the current selected `programs/` tree. The four diffs were checked and applied in order to a temporary copy of the
exact 52-input candidate source tree, then compared byte-for-byte with their
proposed sources. No proposed build
has been performed and no output-byte gain is claimed.

## Recheck

```sh
python3 -B research/relay-location-data-audit/audit.py
python3 -B research/relay-location-data-audit/test_audit.py
```

Both commands are offline and standard-library-only. They read ELF data but
execute no compiler, target program, VM or transaction. Negative tests reject
unrelocated/wrong-type pointers, truncated records, invalid bounds, non-source strings and pointer-format
changes, and ensure changing a column is not hidden by address normalization.
`audit.py --write` regenerates only this packet's JSON/manifest;
`proposals.py --write-patches` regenerates only its reviewable source diffs.
Neither command changes a selected input or emits a candidate executable.

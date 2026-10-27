# Pump: classifying the remaining unmatched windows (layout vs logic)

Reframes the recovery frontier by measuring *why* each unmatched `.text` window
is unmatched. Scored against the workspace-member build from
[`../file-path-prefix-recovery`](../file-path-prefix-recovery/REPORT.md)
(538/1035 normalized). Of the 497 still unmatched:

| Category | Count | Body bytes | Meaning |
| --- | ---: | ---: | --- |
| `metadata_only` | **72** | 96,720 | Body logic byte-identical; differs only in `file!()`/`line!()` error-origin metadata. |
| `body_diff` | 233 | — | Same size, genuinely different body — real logic/codegen recovery. |
| `no_same_size_candidate` | 192 | — | No candidate function of that size — missing or substantially different. |

## Method

For each unmatched original window, find the best same-size candidate function
(from the unstripped symbols build) and compare normalized bytes (ELF
relocations and direct-call immediates already masked). A window is
`metadata_only` iff **every** differing byte lies in the immediate field of a
`stw` (0x62) / `stdw` (0x7a) store-immediate instruction — the instructions that
write an Anchor error's `Source { filename, line }` (`line!()` as a `u32`, the
`file!()` `&str` length as a `u64`; the string pointer itself is relocation-
masked). See [`classify_frontier.py`](classify_frontier.py).

Validation: all 72 `metadata_only` windows have Hamming distance ≤ 3
(11 at 1, 9 at 2, 52 at 3) — exactly the shape of a `line!()` difference
(1–2 bytes) plus an optional filename-length byte. Two were disassembled to
confirm:

- `toggle_create_v2` (ham 1): `stw [r10-0xf8], 114` vs `144` — `line!()` only.
- `set_params::execute::{closure}` (ham 3): `stw` line `465` vs `22`
  (2 bytes) + `stdw` filename length `27` vs `31`.

## What this means for recovery effort

- **72 windows (≈96 KB of already-correct logic)** need no logic work — only the
  source *layout* that the original compiler saw: each error site on its
  original file path **and** original line number. Filenames are known (the
  module layout recovered in the file-prefix packet); line numbers require the
  source to be structured line-for-line like the original. Partial credit is
  real but a full flip needs both.
- **233 `body_diff`** are the true logic/codegen frontier — same function size,
  different body.
- **192 `no_same_size_candidate`** are the largest gaps — functions missing from
  the reconstruction or compiled to a different size.

So of the 497, only ~14 % are "logic already correct, layout wrong"; the
remaining ~86 % (425 windows) need genuine function recovery. This bounds how
far source-layout fixes alone can go and points the hard work at the 425.

## Scope

Read-only analysis; heuristic classification (a `body_diff` whose only diffs
happened to fall in store-immediate fields could be mislabeled, but the ≤3
Hamming bound and the two confirmed disassemblies make that unlikely for this
set). No bytes written, no source changed, no byte-identity claim.

# Pump: classifying the remaining unmatched windows (layout vs logic)

Reframes the recovery frontier by measuring *why* each unmatched `.text` window
is unmatched. The committed counts are the author's measurement against the
Linux (WSL) workspace-member build from
[`../file-path-prefix-recovery`](../file-path-prefix-recovery/REPORT.md)
(538/1035 normalized). Of the 497 still unmatched:

| Category | Count | Body bytes | Meaning |
| --- | ---: | ---: | --- |
| `metadata_only` (historical heuristic label) | **72** | 96,720 | Store-immediate-only differences: 71 reported origin-only windows, plus `0x60260` with a program error-code difference (6025 vs 6109). The aggregate is not 72 metadata-only semantic matches. |
| `body_diff` | 233 | — | Same size, genuinely different body — real logic/codegen recovery. |
| `no_same_size_candidate` | 192 | — | No reconstruction function of that size — missing, or compiled to a different size. |

## Method

For each unmatched original window, find the closest same-size function in the
unstripped reconstruction build (minimum normalized Hamming distance) and
compare normalized bytes (ELF relocations and direct-call immediates already
masked). A window is `metadata_only` iff **every** differing byte lies in the
immediate field of a `stw` (0x62) / `stdw` (0x7a) store-immediate instruction.
Anchor writes an error's `Source { filename, line }` with exactly those
instructions: `line!()` as a `u32`, and the `file!()` `&str` length as a `u64`
(the string pointer itself is relocation-masked). See
[`classify_frontier.py`](classify_frontier.py).

The opcode test alone is a heuristic, because any program constant can sit in
those immediate fields. Review therefore checked the 72 windows slot by slot.
For the 71 reported origin-only windows, differing `stw` values were identified
as `line!()` slots paired with `file!()`-length stores (same base register,
length slot + 8), and differing `stdw` values as file-length stores. The
remaining window, `0x60260`, additionally differs in its program error code
(6025 vs 6109). That is an error-behavior divergence, not source metadata.
These are normalized local-body observations, not proof of transitive logic
equivalence; per-window detail is in
[`../metadata-callsite-map`](../metadata-callsite-map/REPORT.md).

All 72 have Hamming distance <= 3 (11 at 1, 9 at 2, 52 at 3), the shape of a
`line!()` difference (1–2 bytes) plus an optional filename-length byte. Two
were disassembled (and re-checked in review):

- `toggle_create_v2` (ham 1): `stw [r10-0xf8], 114` vs `144` — `line!()` only.
- `set_params::execute::{closure}` (ham 3): `stw` line `465` vs `22`
  (2 bytes) + `stdw` filename length `27` vs `31`.

## What this means for recovery effort

- **71 reported origin-only windows** are candidates for source-layout recovery.
  Their normalized differences were attributed to original file/line metadata;
  this does not establish transitive semantics or authorize forced coordinates.
- **One additional window, `0x60260`,** differs in program error code 6025 versus
  6109. It needs error-behavior recovery as well as any origin recovery. The
  retained 96,720-byte aggregate includes this window and must not be described
  as entirely matching logic.
- **233 `body_diff`** windows have a same-size candidate with other body
  differences.
- **192 `no_same_size_candidate`** windows lack a same-size function. A missing
  size alone does not prove a missing source function; codegen can alter size.

Thus the reported split is 71 origin-only candidates and 426 remaining windows
(1 error-code divergence + 233 body differences + 192 missing/mis-sized).
The retained JSON and script keep the historical heuristic label/count of72;
this report qualifies its interpretation without rewriting the measurements.

## Reproduce

```sh
python3 -B classify_frontier.py \
  --elf-reader repro/function-inventory/2026-10-24-374fcf0/work/pump-amm-current-body-inventory/elf_reader.py \
  --original evidence/original/pump/deployed.so \
  --symbols <build>/target/sbf-solana-solana/release/pump_recovered.so \
  --catalog <score-dir>/pump-bodies.json --output <fresh>.json
```

`pump-bodies.json` comes from
[`../independent-head-reproduction/score_pump.py`](../independent-head-reproduction/score_pump.py)
run on the build from
[`../file-path-prefix-recovery/build_prefix.sh`](../file-path-prefix-recovery/build_prefix.sh).
The script refuses missing inputs or an existing output before it imports the
reader (`test_cli_inputs.py`). The reader is executable Python: use the
repository's copy shown above.

Review check: a macOS rebuild of the same source (canonical pipeline,
`cargo-build-sbf` 2.1.21, v1.44) scores 533/1035. This script classifies its
502 unmatched windows as 72 `metadata_only` (the identical list, offsets and
Hamming distances as the committed JSON), 192 `no_same_size_candidate`, and 238
`body_diff`. The 238 are the same 233 plus five 56-byte
`core::error::Error::type_id` windows whose 16-byte `TypeId` constants depend
on the build host (see the head-reproduction packet). The committed JSON is
unchanged.

## Scope

Read-only analysis. No bytes written, no source changed, no byte-identity
claim; normalized matching does not establish transitive behavior or final
link layout. The original report and script are preserved unchanged in
`history/`. These observations do not by themselves authorize forcing source
paths or lines, or promoting any source or artifact.

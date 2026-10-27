# Pump: the metadata-only windows need call-site layout, not a module rename

A negative result with an actionable map. Building on
[`../frontier-classification`](../frontier-classification/REPORT.md), this
resolves what each of the 72 `metadata_only` windows actually needs, and shows
that relocating source files flips **none** of them.

## The windows are per-call-site, not per-function

For each `metadata_only` window the differing bytes are the immediates of the
Anchor error-origin stores: `line!()` (`stw`, 0x62) and the `file!()` `&str`
length (`stdw`, 0x7a). Subdividing by which store differs from the closest
same-size reconstruction function:

| subset | count |
| --- | ---: |
| `file+line` (file length **and** line differ) | 56 |
| `line` (file length matches, line differs) | 16 |
| `file` (only the file length differs) | **0** |

One of the 72 (`0x60260`, a `file+line` window) also differs in its program
error code (6025 vs 6109), so for that window the logic is not quite identical
either; the other 71 differ only in `Source { filename, line }`.

**55 of 72 are 520-byte error-constructing closures** (the shape of an
`ok_or_else(|| error!(..))`-style closure). Each one captures the `file!()` and
`line!()` of the place it was written, so the original contains one copy per
call site. Their closest reconstruction functions are only four closures
(`create_v2::nested_create::overflow` x32,
`set_params::execute::{closure}` x16, `minimum::execute::{closure}` x5,
`create_v2::nested_create::walk::{closure}` x2): the reconstruction has far
fewer copies, in different files and at different lines. Matching these
windows means writing the same error sites in the same files at the same
lines. That is call-site layout, and a rename does not provide it.

## Why relocating files flips zero

`file` is empty: every `metadata_only` window also carries a `line!()`
difference. Therefore:

- Moving or renaming source files can correct the `file!()` length on the 56
  `file+line` windows but leaves their `line!()` wrong, so **0 flip**.
- For the 16 `line` windows the file length already agrees; a move to a path
  of different length would add a second difference.

This is not limited to the closest candidate. A stronger check over **every**
same-size reconstruction function, for **every** one of the 502 unmatched
windows in a macOS rebuild of the workspace-member build, found **no** pair
that differs only in `file!()` length immediates. So with the current function
bodies, a pure path relocation (such as main's later
[`pump-restructured`](../../parallel-work/2026-10-25/independent-reconstruction-review/restructure/pump-restructured/README.md)
`#[path]` tree, which targets the embedded path strings) is not expected to
flip any remaining window. The recovered module layout is necessary context
but is not, by itself, a lever on any window. Every remaining `metadata_only`
flip is gated on matching the original's exact source **line**, and for 56 the
call-site file too.

## The call-site map (original files these error sites are written in)

First error-origin site of each window (`orig_file`), from the original binary:

| original file | windows | `file+line` | `line` |
| --- | ---: | ---: | ---: |
| `programs/pump/src/lib.rs` | 23 | 17 | 6 |
| `programs/pump/src/trade_v3.rs` | 13 | 13 | 0 |
| `programs/pump/src/buy_v2.rs` | 10 | 9 | 1 |
| `programs/pump/src/multi_hop_curve_swap.rs` | 8 | 8 | 0 |
| `programs/pump/src/sell_v2.rs` | 5 | 1 | 4 |
| `programs/pump/src/migrate_v2.rs` | 3 | 3 | 0 |
| `programs/pump/src/create_v2.rs` | 2 | 1 | 1 |
| `programs/pump/src/migrate.rs` | 2 | 0 | 2 |
| `programs/pump/src/pump_quote.rs` | 2 | 2 | 0 |
| `programs/pump/src/token_incentives/volume_accumulator.rs` | 2 | 2 | 0 |
| `programs/pump/src/quote_control/initialize_quote_control.rs` | 1 | 0 | 1 |
| (no attributable `Source` site) | 1 | 0 | 1 |

Per-window offsets, original file and line (`orig_file`/`orig_line`, plus all
sites in `source_sites`), which stores differ, and the closest reconstruction
function are in [`metadata-callsite-map.json`](metadata-callsite-map.json)
(produced by [`meta_map.py`](meta_map.py), read-only). Symbol names have the
build-specific `17h...E` hash suffix removed.

Correction history: the author's first revision (preserved unchanged in
`history/`, including its JSON) attributed the windows
to the wrong files (for example 29 to `src/idl.rs`), because `meta_map.py`
passed the window's end address where its size was expected, so it scanned
from `start` to `start + end` rather than `start + size`
and kept the last `.rs` string it met far outside the window. It also read
Anchor framework error codes (4101, 3002, 2501, 2506) as line numbers for 13
windows. Both are fixed: `line!()` is now taken from the `Source` slot paired
with the file-length store. The corrected attributions agree with
[`../frontier-spec`](../frontier-spec/REPORT.md), and several lines cross-check
against main's decoded panic-`Location` oracle
(`create_v2.rs:27`, `volume_accumulator.rs:8/19`, `lib.rs:90/1815`).

## Reproduce

```sh
python3 -B meta_map.py \
  --elf-reader repro/function-inventory/2026-10-24-374fcf0/work/pump-amm-current-body-inventory/elf_reader.py \
  --original evidence/original/pump/deployed.so \
  --symbols <build>/target/sbf-solana-solana/release/pump_recovered.so \
  --catalog <score-dir>/pump-bodies.json --output <fresh>.json
```

The script refuses missing inputs or an existing output before it imports the
reader (`test_cli_inputs.py`). The reader is executable Python: use the
repository's copy shown above. `pump-bodies.json` comes from
[`../independent-head-reproduction/score_pump.py`](../independent-head-reproduction/score_pump.py)
run on the workspace-member build
([`../file-path-prefix-recovery/build_prefix.sh`](../file-path-prefix-recovery/build_prefix.sh)).
The committed JSON was regenerated from a macOS rebuild of that build. Its 72
`metadata_only` windows, their closest candidates and Hamming distances are
identical to the Linux (WSL) build the packet was first measured on (see the
frontier-classification packet), so the map is the same for either build.

The earlier review noted that the saved rows could not verify the 56/16/0
split. Each row now records `differs` (and `error_code_also_differs`), and the
script prints the split and the every-candidate check, so both are reproducible.

## Takeaway

The `metadata_only` set is not a cheap mechanical win. It is a precise statement
of where the original writes these error sites. Closing it means
reconstructing that call structure: which functions raise them, in which
files, at which lines. This map is the spec for that work. No source changed
here, no bytes written, no byte-identity claim.

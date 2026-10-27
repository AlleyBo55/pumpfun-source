# Pump: the metadata-only windows need call-site layout, not a module rename

A negative result with an actionable map. Building on
[`../frontier-classification`](../frontier-classification/REPORT.md), this
resolves what each of the 72 `metadata_only` windows actually needs, and shows
that a module reorganization flips **none** of them.

## The windows are per-call-site, not per-function

For each `metadata_only` window the differing bytes are the immediates of the
Anchor error-origin stores: `line!()` (`stw`, 0x62) and the `file!()` `&str`
length (`stdw`, 0x7a). Subdividing by which store differs:

| subset | count |
| --- | ---: |
| `both` (file **and** line differ) | 56 |
| `line_only` (file matches, line differs) | 16 |
| `filename_only` | **0** |

**55 of 72 are one ~520-byte helper**, inlined/monomorphized per call site; its
`file!()`/`line!()` capture the *call site's* location, not a function
definition. The original contains that helper many times, once per call site,
across the files below; the reconstruction has far fewer copies, in different
files. So "matching" these windows means calling the same helper from the same
files at the same lines — call-site layout, not a rename.

## Why a module reorg flips zero

`filename_only` is empty: every `metadata_only` window also carries a `line!()`
difference. Therefore:

- Renaming/moving source files corrects the `file!()` byte on the 56 `both`
  windows but leaves their `line!()` wrong — **0 flip**.
- It would *break* the 16 `line_only` windows, whose `file!()` already matches.

So the module layout recovered earlier is necessary context but not, by itself,
a lever on any window. Every remaining `metadata_only` flip is gated on matching
the original's exact source **line** (and, for 56, the call-site file too).

## The call-site map (original files these helpers are invoked from)

| original file | windows |
| --- | ---: |
| `src/idl.rs` (Anchor IDL machinery) | 29 |
| `programs/pump/src/create_v2.rs` | 13 |
| `programs/pump/src/lib.rs` | 11 |
| `programs/pump/src/creator/distribute_creator_fee_v2.rs` | 7 |
| `programs/pump/src/util/transfer_fee.rs` | 3 |
| `programs/pump/src/admin_set_idl_authority.rs` | 3 |
| `programs/pump/src/trade_v3.rs` | 2 |
| `programs/pump/src/token_incentives/volume_accumulator.rs` | 2 |
| `programs/pump/src/creator/distribute_creator_fees.rs` | 1 |
| `programs/pump/src/buy_v2.rs` | 1 |

Per-window offsets, original file and extracted line are in
[`metadata-callsite-map.json`](metadata-callsite-map.json) (produced by
[`meta_map.py`](meta_map.py), read-only).

## Takeaway

The `metadata_only` set is not a cheap mechanical win. It is a precise statement
of where the original invokes these error-bearing helpers; closing it requires
reconstructing that call structure (which functions call them, in which files,
at which lines). This map is the spec for that work. No source changed here, no
bytes written, no byte-identity claim.

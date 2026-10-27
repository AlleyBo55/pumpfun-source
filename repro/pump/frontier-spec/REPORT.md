# Pump: full audit spec for the 497 unmatched windows

A measurement-only spec covering every unmatched `.text` window in the
author's Linux (WSL) workspace-member build (538/1035 normalized). For each window it records the
signals a reconstructor needs to find and prioritize targets, and reproduces no
program logic. Per-window data in [`frontier-spec.json`](frontier-spec.json)
(from [`frontier_spec.py`](frontier_spec.py), read-only).

Signals per window: size, category, closest same-size reconstruction function
(symbol) and its normalized Hamming distance, the original `file!()`/`line!()`
of its first Anchor error-origin site (`orig_file`/`orig_line`) and of every
site (`source_sites`, `"file:line"`), referenced program error codes
(6000–6999), direct/indirect call and data-ref counts, and external call
symbols.

`line!()` is read from the `Source` slot paired with the `file!()` length store
(same base register, length slot + 8). An earlier revision took the first small
`stw` immediate in the window, which misread Anchor framework error codes
(e.g. 4101 `TryingToInitPayerAsProgramAccount`, 3002
`AccountDiscriminatorMismatch`, 2006 `ConstraintSeeds`) as line numbers in 33
windows; those rows are corrected here. 67 windows carry more than one site.

## Categories

| category | count | what it means |
| --- | ---: | --- |
| `body_diff` | 233 | a same-size reconstruction function exists but the body differs |
| `no_same_size_candidate` | 192 | no reconstruction function of that size — missing or mis-sized |
| `metadata_only` | 72 | only store immediates differ: `file!()`/`line!()` for all 72, plus a program error code in one (`0x60260`); see the call-site map packet |

## Prioritization of `body_diff` by distance

Normalized Hamming to the closest same-size reconstruction function:

| band | count | reading |
| --- | ---: | --- |
| near (≤16) | 23 | a few instructions off — smallest source corrections |
| mid (17–128) | 40 | partial divergence |
| far (>128) | 170 | substantially different body |

### Closest-candidate clusters (the reconstruction function nearest each unmatched original)

Near clusters (small corrections): `alloc::raw_vec::RawVec::grow_one`
(min ham 3), `BuyV2 as AccountsExit::exit` (4), `QuoteControl as
AccountDeserialize` (11), `drop_in_place<[AccountInfo;5]>` (16).

Far clusters (real recovery): `Vec as BorshDeserialize::deserialize` (6 windows),
`spl_token::instruction::transfer_checked` (5), `__private::__idl::*`
(`__idl_resize_account`, `IdlAccount as AccountSerialize`),
`__private::__global::distribute_creator_fees_v2`,
`anchor_lang::error::*`. These point at dependency/codegen version mismatches
(borsh, spl-token, anchor IDL machinery) as much as program logic.

## `no_same_size_candidate` (192) attributed to original source files

From the error-origin `file!()` where recoverable — i.e. which original modules
contain functions the reconstruction is missing or has at the wrong size:

| original file | windows |
| --- | ---: |
| `lib.rs` | 10 |
| `trade_v3.rs` | 6 |
| `create_v2.rs` | 5 |
| `pump_quote.rs` | 5 |
| `buy_v2.rs` | 4 |
| `creator/distribute_creator_fee_v2.rs` | 3 |
| `creator/distribute_creator_fees.rs` | 3 |
| `multi_hop_curve_swap.rs` | 3 |
| `sell.rs` | 3 |
| `creator/collect_creator_fee.rs`, `extend_account.rs`, `migrate_v2.rs`, `set_reserved_fee_recipients.rs`, `token_incentives/volume_accumulator.rs` | 2 each |

(Many windows have no recoverable `file!()` — they carry no error macro — and
are identified by size + call/data fingerprint in the JSON.)

## External-call fingerprint

Across all unmatched windows the dominant external calls are `abort` (135 — the
`overflow-checks` panic paths) and `sol_log_` (56 — `msg!` logging). Per-window
external-symbol lists in the JSON help identify a function by what it calls
(syscalls, SPL/Anchor entry points) without reading its body.

## How to use this

1. Start with the 23 near `body_diff` windows — closest existing function named,
   a few instructions off.
2. The far clusters concentrate in dependency surfaces (borsh, spl-token, anchor
   IDL) — likely resolved by matching dependency/codegen versions rather than
   per-function edits.
3. The `no_same_size_candidate` table says which original modules still need
   functions written; the call-site map packet gives their invocation sites.

## Reproduce

```sh
python3 -B frontier_spec.py \
  --elf-reader repro/function-inventory/2026-10-24-374fcf0/work/pump-amm-current-body-inventory/elf_reader.py \
  --original evidence/original/pump/deployed.so \
  --symbols <build>/target/sbf-solana-solana/release/pump_recovered.so \
  --catalog <score-dir>/pump-bodies.json --output <fresh>.json
```

The script refuses missing inputs or an existing output before it imports the
reader (`test_cli_inputs.py`); the metadata test requires every difference to
fall in bytes 4–7 of a store, as in the classification packet. The reader is
executable Python: use the repository's copy shown above. `pump-bodies.json` comes from
[`../independent-head-reproduction/score_pump.py`](../independent-head-reproduction/score_pump.py)
run on the workspace-member build from
[`../file-path-prefix-recovery/build_prefix.sh`](../file-path-prefix-recovery/build_prefix.sh);
`--symbols` is that build's unstripped
`target/sbf-solana-solana/release/pump_recovered.so`. Neither is committed.

The committed JSON describes the Linux (WSL) workspace-member build (538/1035).
Review check: a macOS rebuild of the same source (canonical pipeline,
`cargo-build-sbf` 2.1.21, v1.44) reproduces every candidate-side field of all
497 rows exactly; it has 5 additional unmatched windows, all 56-byte
`core::error::Error::type_id` bodies whose 16-byte `TypeId` constants are
host-dependent (see the head-reproduction packet), which are not in this spec.
The committed JSON is that regenerated output restricted to the 497 Linux
windows. The author's original report and script are preserved unchanged in
`history/`; the author's JSON is in git history (commit `3bf0002e`).

Measurement only. No source changed, no bytes written, no byte-identity claim;
external symbol names, error codes, sizes and file paths are facts read from the
binaries, not program logic.

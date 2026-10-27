# Pump: full audit spec for the 497 unmatched windows

A measurement-only spec covering every unmatched `.text` window in the
workspace-member build (538/1035 normalized). For each window it records the
signals a reconstructor needs to find and prioritize targets, and reproduces no
program logic. Per-window data in [`frontier-spec.json`](frontier-spec.json)
(from [`frontier_spec.py`](frontier_spec.py), read-only).

Signals per window: size, category, closest same-size reconstruction function
(symbol) and its normalized Hamming distance, the original `file!()`/`line!()`,
referenced Anchor error codes (6000–6999), direct/indirect call and data-ref
counts, and external call symbols.

## Categories

| category | count | what it means |
| --- | ---: | --- |
| `body_diff` | 233 | a same-size reconstruction function exists but the body differs |
| `no_same_size_candidate` | 192 | no reconstruction function of that size — missing or mis-sized |
| `metadata_only` | 72 | body byte-identical; only `file!()`/`line!()` differ (see the call-site map packet) |

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
| `creator/collect_creator_fee.rs`, `extend_account.rs`, `migrate_v2.rs` | 2 each |

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

Measurement only. No source changed, no bytes written, no byte-identity claim;
external symbol names, error codes, sizes and file paths are facts read from the
binaries, not program logic.

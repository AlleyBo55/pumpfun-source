# Relay: recover the SwapReceipt decoder source coordinate

The reconstructed `SwapReceiptV1` checked decoder now matches the complete
1,120-byte original window 167 under the existing CALL/relocation normalization.
The source change places its `#[account]` attribute on the observed line 5 rather
than line 2. No Rust token changes. The historical three preceding lines remain
unknown; this reconstructs the measured coordinate, not the original preamble.

**466/492 normalized windows, 88 raw local matches, 26 unmatched.** No prior
normalized match is lost. Whole captured-file equality remains false.

## Controlled builds

| Variant | Source | Target | Raw windows | Normalized windows | Remaining |
| --- | --- | --- | ---: | ---: | ---: |
| legacy | Retained distribution-worker source | `sbf-solana-solana` | 86 | 465 | 27 |
| canonical | Identical source | `sbpf-solana-solana` | 88 | 465 | 27 |
| recovered | Three blank lines before one attribute | `sbpf-solana-solana` | 88 | 466 | 26 |

The fresh legacy build exactly reproduces the previous stripped and unstripped
outputs (`fb4fcb3a…`, `2402f38e…`). Switching the target alone improves two local raw
matches (windows 482 and 486) but recovers none of the 27 normalized residuals.
The three repeated `Error::type_id` bodies remain unmatched. That negative result
is retained rather than promoted as a source-recovery gain.

The recovered stripped output is **813,968 bytes**, SHA-256
`03b725918aca825b316254311ea6ebe83da708bc3775df72c5d04be3b63fe978`.
Its unstripped output is SHA-256
`998c05f61b35e364362e0e851974603cf7e7c22bdb28ba2935803a588b1413d3`.

Against the canonical control, exactly two file bytes change from 2 to 5:
469212 (the decoder's source-line store) and 769096 (a metadata location).
The decoder's remaining instruction bytes match under the unchanged masks.
Original window 167 is `[513680,514800)`; its candidate counterpart starts at
468816. Both point to the same 47 filename bytes,
`programs/contracts/src/state/v1/swap_receipt.rs`.

The actual build logs, launch/source-hash records, output hashes, full source
snapshots, compressed stripped/unstripped outputs and original window inventory
are retained. `recorded_build_driver.py` is the driver actually executed; its
paths describe this run, not a portable tool installer. Builds used the installed
official platform-tools v1.48, locked dependencies and offline Cargo. No original
executable was a compiler input. Logs/hashes are not an authenticated process
trace or proof of a unique historical toolchain.

## Fresh runtime validation

All **536 named records / 534 unique saved fixtures** were replayed against both
the captured original and the recovered candidate. Every fresh original result
reproduced its saved observation, and every candidate comparison matched.
Transactions retain signature, blockhash and history checks. No transaction was
re-signed or changed; Token-2022 uses the captured executable where required.

`fresh-runtime.json.gz` retains both fresh results, fixtures, transaction bytes,
input-report hashes and comparator differences. The original comparator omits
compute-metering lines and executable image bytes; those exclusions are unchanged.
No privileged fixed-relayer/Jupiter success or exhaustive input equivalence is
claimed. Matching finite rejections does not close those obligations.

## Verify and continue

```sh
python3 -B repro/donation-relay/swap-receipt-coordinate-recovery/verify.py
```

Requires the repository's pinned solders package. The verifier performs no build
or VM execution: it rederives all 492-window comparisons, the exact two-byte
delta, the source-only change, original/candidate filename and line evidence,
saved signatures, fixture identity, original replay equality and candidate
effects. `remaining-windows.json` preserves the other 26 residuals.

Next leads include the three repeated type-ID bodies, the TLV extension-bound
comparison, complete donation/settlement handlers, mint policy and close/CPI/resize
helpers. Selected source 15, active `programs/donation-relay`, selected status and
all historical evidence remain unchanged by this additive research package.

# Mayhem overlay: corrected CPI fixture on the corrected initializer

PR #79 corrected the overlay's `initialize_mayhem_state` and validated it with the
17-case Pump-to-Mayhem CPI harness. PR #80 then fixed that harness's creator input
(the old `zero-creator-is-rejected` case serialized the payer) and grew it to 20
cases, but validated only the earlier pair (Pump `5392c9a9…`, Mayhem `cbe8c8e7…`).
This package runs the corrected 20-case harness against the **corrected** overlay
Mayhem from #79 (`research/mayhem-initializer-validation/build/vault.so`,
`8e6a5f8c…`) and records a review rebuild of that overlay source.

## CPI receipts

| Receipt | Caller (candidate side) | Candidate Mayhem | Result |
| --- | --- | --- | --- |
| `overlay-pump-caller.json.gz` | overlay Pump `5392c9a9…` | `8e6a5f8c…` | 20 cases, 0 mismatches |
| `captured-pump-caller.json.gz` | captured Pump `7a19affa…` | `8e6a5f8c…` | 20 cases, 0 mismatches |

The original side is always captured Pump + captured Mayhem. Both zero-creator
cases reject with Pump's `CreatorShouldNotBeZero` (6030) on both sides; both
distinct-creator cases succeed and store the supplied creator. Zero-creator
rejection happens in Pump before the Mayhem CPI, so those two cases do not exercise
the initializer. The receipts are local LiteSVM runs on synthetic fixtures; they do
not establish exhaustive or historical behavior.

## Review rebuild

`scripts/build_partial_candidate.py` (macOS arm64 host, `cargo-build-sbf` 2.1.21,
platform-tools v1.52, offline, clean target) was run on two materialized trees:

- pre-correction overlay source (#79's retained `baseline-source`): output
  691,128 bytes, SHA-256 `cbe8c8e7…`, **identical** to the committed
  `repro/mayhem/recovered-dispatch-25-from-main-v152/main/candidate.so`;
- current overlay source (`apply.py` on main, identical to #79's `vault-source`):
  output 695,456 bytes, SHA-256
  `b088163ae28a3e03649f2da8de03ca7b053a1397275b0fa61716a9f720180d76`.

This host recipe does **not** reproduce #79's Linux Docker output `8e6a5f8c…`
(695,448 bytes; direct `cargo build` + `llvm-objcopy`). The two outputs have the
same allocated-section sizes except `.rodata` (16,652 vs 16,644 bytes), and
`.text` (632,656 bytes in both) differs at 18,348 byte positions. The pre-correction
pair (`cbe8c8e7…` vs #79's Linux baseline `77b8e81c…`) has the same structure:
an 8-byte longer `.rodata` and 18,376 differing `.text` positions. This is a raw
positional comparison of two builds, not a claim that the differences are only
paths or addresses. The rebuilt binary is not retained; its `build-comparison.json`
records (source hashes, command, toolchain, raw comparison against the original)
are under `rebuild/`. Against the rebuilt `b088163a…`, the standalone five-case
harness, #79's 53-case rejection matrix and both 20-case CPI runs above also gave
0 mismatches. Neither build is byte-identical to the deployed original.

## Verify

```sh
python -B research/mayhem-overlay-cpi-recheck/verify.py --repo .
```

The checker validates receipt and binary hashes, the harness hash, and reuses
`research/mayhem-creator-fixture/verify.py`'s `check_report` (signatures, decoded
Borsh inputs, expected rejections, persisted creators, recomputed comparisons).
It also checks the rebuild records' bindings to the overlay sources. It does not
replay programs or compile. To replay, run the harness with a fresh output path:

```sh
python -B repro/behavioral-recovery/scripts/pump_create_mayhem_differential.py \
  --candidate-pump repro/pump/recovered-dispatch-56-from-main-v144/main/candidate.so \
  --candidate-mayhem research/mayhem-initializer-validation/build/vault.so \
  --output work/recheck-overlay-pump-caller.json.gz
```

# Behavioral recovery overlay

Recovered Pump and Mayhem handlers that are validated against the captured
originals but are **not** in active `programs/` source. Use this overlay when you
need a dispatch-complete build for local SDK testing.

## What it adds

| Handler | Program | Differential result vs. captured original (local re-run 2026-10-26) |
| --- | --- | --- |
| `admin_update_token_incentives` | pump | 299 cases, 0 mismatches |
| `claim_token_incentives` | pump | recovered; its differential is bound to an older build record and was not re-run |
| `create_v2` Mayhem mode + `initialize_mayhem_state` (pump→Mayhem CPI) | pump, mayhem | 20 cases, 0 mismatches (17 before commit `73cfb605` added three creator cases) |
| v3 Token-2022 transfer-fee quotes (`buy_v3`, `sell_v3`, `buy_exact_quote_in_v3`) | pump | 126 cases, 0 mismatches |
| `set_mayhem_virtual_params` (dormant, CPI-only) | pump | 84 cases, 0 mismatches (signer-stub driver) |

The initializer now declares `mint_authority` as an `UncheckedAccount` with an
explicit `signer` constraint, preserving the Pump PDA check while matching mint
deserialization before signature validation. Its token vault uses `init_if_needed`,
matching the original's handling of existing vaults and their owner/mint/address
constraints. The [controlled reconstruction](../../research/mayhem-initializer-validation/README.md)
reduces 35/53 standalone validation mismatches to zero; the original five-case
harness also has zero mismatches. The 17 CPI cases of the pre-`73cfb605` harness pass with the captured
original Pump as caller on both sides. The current 20-case harness gives 0
mismatches for this corrected build with the committed `5392c9a9` Pump candidate as
caller, and for the committed `5392c9a9`/`cbe8c8e7` pair (local runs, 2026-10-26).
These are bounded local comparisons, not whole-program equivalence or byte identity.

Commit `73cfb605` (the [creator-fixture correction](../../research/mayhem-creator-fixture/README.md))
made the harness serialize each case's requested creator: the old
`zero-creator-is-rejected` case had serialized the payer, so it repeated an ordinary
creation. It also added zero/distinct-creator controls; the zero-creator cases
reject in Pump (6030) before the Mayhem CPI. That package retains the 20-case
receipt for the `5392c9a9`/`cbe8c8e7` pair. The [corrected-fixture recheck](../../research/mayhem-overlay-cpi-recheck/README.md)
retains the 20-case receipts for this corrected build with the `5392c9a9` Pump
and with the captured Pump as caller (0 mismatches each).

The current Mayhem overlay's pinned Linux v1.52 build is 695,448 bytes, SHA-256
`8e6a5f8c34a12303096902e50848f556bc7a9d9ce0dc0d9030e632b85b88e166`;
its source, raw output, symbols, logs and receipts are retained in that package.
A macOS `scripts/build_partial_candidate.py` (`cargo build-sbf`, v1.52) rebuild
does not reproduce that Linux output: on the same source it gives 695,456 bytes, SHA-256
`b088163ae28a3e03649f2da8de03ca7b053a1397275b0fa61716a9f720180d76`, while on the
pre-correction source it reproduces `cbe8c8e7…` exactly (recorded in the recheck
package; the rebuilt binary is not retained).

With the overlay applied, pump dispatches 56/56 IDL instructions and Mayhem 25/25.
Earlier builds on 2026-10-26, before the initializer correction above
(`scripts/build_partial_candidate.py`; preserved historical outputs):

- Mayhem (v1.52) reproduces the committed candidate byte-for-byte:
  `repro/mayhem/recovered-dispatch-25-from-main-v152/main/candidate.so`
  (sha256 `cbe8c8e71f0c256326cf639f303b3d939244320637531d79041585c9358020e2`).
- Pump (v1.44) builds to sha256
  `df61557a0bed2450d32b277df56a68d3e58ecd87e41486b9ea4c2071e9a67155`. It differs
  from the older committed candidate
  `repro/pump/recovered-dispatch-56-from-main-v144/main/candidate.so`
  (`5392c9a9…`, built from `14ec9b5c`) because the overlay sits on main's newer
  `admin_cto.rs` and its `lib.rs` orders module declarations and
  `UpdateMayhemVirtualParamsEvent` differently; the effect of each change was not
  measured separately. The differentials in the table above were re-run locally
  against both builds with identical results. Those receipts and the `df61557a`
  build record were not retained; the committed `5392c9a9`/`cbe8c8e7` candidates
  reproduce the same counts.

The `@pump-fun/pump-sdk` harness in
`repro/parallel-work/2026-10-25/independent-reconstruction-review/sdk-integration-test/`
ran create/buy/sell, v3, incentives, Mayhem create and AMM flows against the older
committed candidates (`5392c9a9…`, `cbe8c8e7…`), not the current overlay builds.

## Why it is not active source

`scripts/verify_recovered_builds.py` hash-binds all 37 Pump compile inputs to the
selected checkpoint, the pass-27 guard pins Mayhem's 14 compile inputs (including
the `lib.rs` this overlay replaces), and the reconciliation policy only admits
source with matching byte-level evidence. None
of these builds is byte-identical to the deployed original, so promoting them
means selecting a new checkpoint and re-running the bound differential suites.
Main's checkpoint notes also flag an AccountInfo ownership question on the
virtual-params proposal that review has not closed.

## Files

`programs/` mirrors the repository layout. Each file replaces its counterpart in
active source; `lib.rs`, `create_v2.rs`, `trade.rs` and `volume_sync.rs` are full
replacements, the rest are new modules. `admin_cto.rs` and the Fees sources are
intentionally absent: main's versions are newer and already include the typed
CTO errors.

`scripts/` holds the recovery differentials and `fixtures/signer_stub` their
signer-forwarder program. They live here rather than in the top-level `scripts/`
and `programs/` because the pass-27 CI guard pins the top-level script set and
lists these exact active paths as must-not-exist.

## Use

```sh
python3 repro/behavioral-recovery/apply.py --target work/behavioral-recovery
cd work/behavioral-recovery
cargo build-sbf --manifest-path programs/pump/Cargo.toml --tools-version v1.44 -- --locked
cargo build-sbf --manifest-path programs/mayhem/Cargo.toml --tools-version v1.52 -- --locked
```

Validate a build against the captured originals (from the repository root):

```sh
python3 repro/behavioral-recovery/scripts/pump_incentives_admin_differential.py --candidate <pump.so> --output work/incentives.json.gz
python3 repro/behavioral-recovery/scripts/pump_set_mayhem_virtual_params_differential.py --candidate <pump.so> --output work/virtual-params.json.gz
python3 repro/behavioral-recovery/scripts/pump_v3_token_extensions_differential.py --candidate <pump.so> --output work/v3.json
python3 repro/behavioral-recovery/scripts/pump_create_mayhem_differential.py --candidate-pump <pump.so> --candidate-mayhem <mayhem.so> --output work/create-mayhem.json.gz
python3 repro/behavioral-recovery/scripts/mayhem_initialize_state_differential.py --candidate <mayhem.so> --output work/mayhem-init.json
```

`fixtures/signer_stub` is the forwarder used to invoke the CPI-only
virtual-params handler with a genuine `invoke_signed` PDA signature.

## Provenance

Recovered in commits `294c9186` (incentives), `14ec9b5c` (validated 56/56 +
25/25 state) and `5f38701c` (virtual-params wiring); the primary checkout's
uncommitted deltas were snapshotted in `1bec3365` and rebased onto main here.

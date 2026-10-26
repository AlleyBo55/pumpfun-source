# mayhem — restructured to the recovered original module tree (compiling)

_2026-10-26. Companion to `pump-fees-restructured/`. Reference artifact under `repro/` — NOT active
main source (the upstream-reconciliation policy admits only byte-equal-to-original active source)._

## What this is
The mayhem program (crate dir **`mayhem-program`**, lib `mayhem_recovered`) reorganized from the
reconstruction's operation-grouped layout into the **original module tree recovered from the deployed
binary's embedded panic-`Location` paths**. It compiles with platform-tools **v1.52** (Rust 1.89) as a
**workspace member** and reproduces the original's embedded source-path strings exactly.

### Move map (current reconstruction → recovered original file)
| recovered file | merged from |
|---|---|
| `instructions/pump_interface.rs` | `buy.rs` + `sell.rs` (handler→`buy`/`sell`) |
| `instructions/pump_interface_v2.rs` | `buy_v2.rs` + `sell_v2.rs` |
| `instructions/pump_amm_interface.rs` | `buy_pump_swap.rs` + `sell_pump_swap.rs` |
| `instructions/burn.rs` | `burn.rs` (kept) |
| `instructions/extend_account.rs` | lib.rs inline `extend_account` |
| `instructions/fee_recipients.rs` | lib.rs inline `initialize_fee_recipient`, `sweep_fees`, `sweep_fees_admin`, `withdraw_quote_admin`, `withdraw_admin` |
| `instructions/admin.rs` | lib.rs inline `initialize_global_params`, `update_global_params`, `update_admin`, `update_trader`, `update_max_sol_per_sweep`, `update_max_stable_per_sweep`, `reset_sol_deployed`, `reset_stable_deployed`, `reset_state`, `stop_trading`, `resume_trading` |

Interface merges dedup shared consts (`WSOL`, `SPL_TOKEN_ID`) and the `math()` error helper, and rewire
`super::buy`/`super::sell` cross-refs to the merged modules. Inline admin/fee handlers were relocated as
module fns and delegated from the `#[program]` dispatcher; lib.rs top-level helpers (`sweep_remaining`)
made `pub(crate)`. Merging collides on the shared `handler` fn name — resolved by renaming per operation.
Grouping is **partly inferred** (operation→interface regroup is not 1:1), unlike pump_fees' near-1:1 map.

## KEY FINDING — the embedded source-path strings are RECOVERABLE (not lost metadata)
Prior analysis attributed the whole panic-`Location` residual in `.data.rel.ro` to unrecoverable
file-layout metadata. That is only half true. The residual splits cleanly:

1. **PATH strings — RECOVERABLE.** The `file!()` path recorded at each panic/`require!`/`unwrap` site is
   determined entirely by (a) the crate **directory name** and (b) whether the crate is built as a
   **workspace member** (path = `programs/<dir>/src/...`) vs standalone (path = bare `src/...`). It does
   NOT depend on the lost source content.
2. **(line, col) positions — source-bound.** The exact statement line/column inside each file still needs
   the authentic source; the restructured files place statements at different lines.

### Empirical proof (this crate)
| build | embedded path form | exact original path strings present | oracle files matched |
|---|---|---|---|
| standalone (`--manifest-path programs/mayhem/Cargo.toml`, dir `mayhem`) | `src/instructions/pump_interface.rs` … | **0 / 9** | 0 files / 0 sites |
| **workspace member** (dir `mayhem-program`, built from workspace root) | `programs/mayhem-program/src/instructions/pump_interface.rs` … | **9 / 9** | 7 files present / 87 sites |

`(file,line,col)` sites still 0/64 (line positions are source-bound). See `oracle.txt`.

### Implication for byte-identity
The committed candidates are built **standalone**, so every one of the 4 core programs is currently
leaving the embedded-path bytes mismatched for free. Building the reconstruction as a **workspace with all
programs as members** (repo root `Cargo.toml members = [...]`) — and renaming mayhem's dir `mayhem` →
`mayhem-program` to match the original — recovers those `.data.rel.ro` path-string bytes with zero source
changes. This narrows (does not close) the whole-binary gap: the `(line,col)` immediates and the code-body
instruction scheduling/ordering remain bounded by the lost original source.

## Build
From the workspace root (`workspace-Cargo.toml` → `Cargo.toml`, member `programs/mayhem-program`):
`cargo build-sbf --manifest-path programs/mayhem-program/Cargo.toml --tools-version v1.52 --offline
--sbf-sdk <sdk> --sbf-out-dir OUT -- --locked --offline` → `mayhem_recovered.so` (rc=0). See `build.log`.

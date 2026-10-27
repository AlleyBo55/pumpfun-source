# Independent reconstruction review — 2026-10-25

Independent status review + fresh verification of the four-program reconstruction,
produced by a separate review session. Start with `FINAL_REPORT.md`.

- `FINAL_REPORT.md` — consolidated findings, remaining-work ledger, SDK-testing path.
- `STATUS_REPORT.md` — initial detailed status.
- `SECTION_DIVERGENCE.md` — ELF section breakdown (gap is 84–98% in .text).
- `CONCURRENCY-NOTE.md` — shared-checkout reconciliation (pump_amm "stale" resolved).
- `A-reproduction/` — all 4 candidates rebuild deterministically from current source (comparison + build-provenance JSON).
- `B-differential/` — full differential regression: 86/90 runners pass, 39,098 cases; 4 real divergences enumerated.
- `C-dependencies/` — Metaplex `Utilize` (single-branch root cause + proposed patch) and ATA (custom_panic toolchain-snapshot) byte-closure analysis.
- `D-sdk-localnet/` — verified runnable localnet SDK-testing setup + safe-flow matrix.

All claims herein were adversarially re-verified (see FINAL_REPORT §8). No captured
original was used as a build input; no brute-force recipe search or binary patching.
Whole-binary byte-identicality of the 4 core programs remains 0/4.

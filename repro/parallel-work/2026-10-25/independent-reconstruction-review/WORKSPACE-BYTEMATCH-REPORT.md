# Single-workspace conversion vs byte-identicality — measured result

_2026-10-26. Question posed: "convert the repo to a single workspace with all programs as members
(rename mayhem's dir to mayhem-program), rebuild the committed candidates, and quantify the whole-binary
byte-match delta vs the originals." This reports what the conversion actually does, measured against
`evidence/original/<p>/deployed.so`._

## TL;DR
**Do not convert to a single multi-member workspace.** It does not improve byte-identicality and makes two
things worse. The embedded `programs/<dir>/src/…` source-path strings — the only thing the conversion was
meant to recover — can be recovered cleanly and risk-free with `--remap-path-prefix`, but doing so moves
whole-binary byte-match by **~0.0–0.03 percentage points** (it is a few hundred bytes in a ~1.9 MB binary).
The dominant byte gaps (function ordering that matches neither build nor the original, plus source-bound
codegen) are untouched by any build-mode change.

## What was built (controlled, same committed origin/main source, deterministic)
Builds are deterministic: two standalone builds of the same source from the same path are byte-identical
(sha match, `.text` 0 diff bytes). So before/after differences below are real build-mode effects, not noise.
Three build modes, each from pristine `origin/main` source with each program's own `Cargo.lock`:
- **standalone** — program built as its own workspace root (= how the committed candidates are built). Embeds bare `src/…` paths.
- **workspace** — program built as a member of a `[workspace]` root (mayhem dir renamed `mayhem-program`). Embeds `programs/<dir>/src/…`.
- **remap** — standalone + `RUSTFLAGS=--remap-path-prefix=src/=programs/<dir>/src/`. Embeds `programs/<dir>/src/…`.

## Measured byte-match vs the deployed original
| program | mode | whole-ELF % vs orig | .text % vs orig | original path strings matched | `.text` reordered vs standalone |
|---|---|---|---|---|---|
| pump | standalone | 36.232 | 36.471 | 0/33 | — |
| pump | workspace | 36.267 | 36.510 | 9/33 | **yes** (6371 slots, 3.48%) |
| pump | remap | 36.231 | 36.471 | 9/33 | **no** (0 opcode/branch slots) |
| pump_amm | standalone | 41.561 | — | 0/33 | — |
| pump_amm | remap | 41.586 | — | 4/33 | no (0) |
| mayhem | standalone | 39.482 | — | 0/9 | — |
| mayhem | remap | 39.488 | — | 3/9 | no (0) |

Path-string recovery is real (0 → 9/4/3 of the original's Location-bearing files) but whole-binary match is
essentially flat because (a) the strings are a tiny fraction of the binary and (b) lengthening `src/…` →
`programs/<dir>/src/…` grows `.rodata`, shifting everything after it and washing out the gain in an
offset-aligned comparison.

## Why the workspace conversion is worse, not better
1. **Function reordering (no benefit).** Building a program as a workspace member instead of its own root
   changes the crate's build context, which **reorders functions in `.text`**: before vs after share a
   **100% masked-instruction multiset** (identical instructions) but differ in **3.48% of slots by opcode/
   branch** — i.e. the same code laid out in a different order. The new order matches neither the standalone
   build nor the original, so it churns the binary for no byte-match gain (pump `.text` 36.47→36.51%, noise).
2. **Dependency-version drift (real code change).** The programs' own locks disagree: pump/pump-amm/pump-fees
   pin **spl-token-2022 6.0.0** and solana-program **2.3.0**; pump-fees/donation-relay use solana-program
   **2.2.1**; donation-relay pulls **spl-token-2022 7.0.0**; mayhem uses **anchor 1.0.0** vs 0.31.1 elsewhere.
   A single shared `Cargo.lock` must unify these — it resolved **spl-token-2022 → 7.0.0** (not cached, so the
   offline build failed). That changes real dependency code in pump/pump-amm/pump-fees → a byte **regression**.
   pump-amm's `[patch.crates-io] solana-pubkey = vendor/…` would also apply workspace-wide.

## The clean alternative
`--remap-path-prefix=src/=programs/<dir>/src/` on each standalone build recovers the exact same path strings
with **zero function reordering** (0 opcode/branch-position differences vs the standalone build, for all three
programs) and **zero dependency drift**. It is *not* byte-identical to the standalone candidate: lengthening
`src/…` → `programs/<dir>/src/…` grows `.rodata`, which shifts `.rodata` addresses and therefore the `.text`
`lddw` immediates that load them (~2.4% of `.text` slots change in their immediate field only — no opcode,
register, or branch-target changes). So the delta vs the current candidate is exactly: the path strings + the
addressing immediates they shift — no logic, no layout churn. For mayhem it yields the original's
`programs/mayhem-program/src/` prefix **without renaming the crate directory**. This is the least-disruptive
way to make the candidates carry the path bytes, if that fidelity is wanted for its own sake. It does not
materially improve whole-binary byte-match.

## Independent verification
Four independent agents (each with its own ELF parser, no shared script) re-derived the claims and confirmed:
before/after/remap share a **100.000% masked opcode+register multiset** (same instructions — nothing added,
removed, or logic-altered); the **workspace build reorders `.text`** (before↔after differ by reordering +
path strings only); **remap is not byte-identical** to standalone (the immediate ripple above) but introduces
no reordering or logic change; path recovery is **9/33 (pump), 4/33 (pump_amm), 3/9 (mayhem)** of the
original's set. They also confirmed the committed candidates reproduce only ~27% of the original's source-file
layout (e.g. pump: 20 of the candidate's own paths don't exist in the original, 24 of the original's are
absent — the `creator/`, `token_incentives/`, `util/` subtrees were flattened), so full path recovery needs
the recovered module trees, not a build-mode change.

## Recommendation
- **Keep per-program workspaces (status quo).** Do not merge programs into one workspace.
- If path-string fidelity is desired, add `--remap-path-prefix=src/=programs/<dir>/src/` to each program's
  build recipe (e.g. `.cargo/config.toml` `[build] rustflags`, or the candidate build script) — clean, no drift.
- Full path recovery (all 33/33 files) still requires the recovered module trees (banked under
  `restructure/`), and whole-binary byte-identity remains bounded by function ordering + lost source.

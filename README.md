# pumpfun-source

Reconstructed Rust source for the Pump.fun Solana programs, plus the captured
on-chain binaries and the evidence used to check the reconstruction against them.

**None of the four core programs or the selected Relay is byte-identical to its
deployed binary yet.**
Behavior is reconstructed handler by handler and checked with differential tests
that run the captured original and the rebuilt candidate side by side in a local VM.

For subsequent gains and the latest research frontier, see the
[byte-identity progress log](docs/BYTE-IDENTITY-PROGRESS.md).

Latest artifact-backed Relay research: **482/492 normalized windows, 10 unmatched**, including
[the Jupiter optional-seed builder](repro/donation-relay/jupiter-option-source-recovery/README.md)
and [the complete burn/close helper](repro/donation-relay/burn-mint-ownership-recovery/README.md).
Both compiler recipes retain **130 raw local body matches**, agree on all 348
recognized source-location pairs, and each pass 536 fresh replay records.
Artifact-backed follow-up [reconstruction studies](docs/BYTE-IDENTITY-PROGRESS.md)
have not added whole-body matches. Conditional value-flow agreement and locally
matching helpers do not establish full function or program identity.
The [Relay security-metadata recovery](repro/donation-relay/security-metadata-source-recovery/README.md)
now reproduces the complete 510-byte security declaration and 247-byte dynamic
string table from ordinary Rust source. Its Linux candidate retains the same
482-window frontier and 348 source-location matches; whole-file equality remains
unachieved. The function inventory keeps its explicitly hashed burn/close inputs. The
[source-only shared-worker proposal](repro/donation-relay/shared-worker-source-proposal/README.md)
reports 483/492 in local builds. Its source checks pass, but it publishes no
compiled artifact or replay receipt; that result is separate from this inventory.

Latest Fees research: **395 unique structural pairs, 43 unmatched windows**.
The [configuration-event recovery](research/fees-config-event-recovery/README.md)
adds four complete caller-body matches; the two upsert bodies share a structural
shape and are distinguished by their callees. The [current call ledger](repro/reconstruction-status-2026-10-26/fees-call-attribution.json)
also attributes 65 duplicate-body pairs, giving 460 correspondences.
Whole-file identity remains unachieved. The [exotic-fee growth study](research/fees-exotic-growth-precedence/README.md)
corrects rejection precedence and the realloc flag in new boundary cases;
that caller still has no complete body match. The [optional-account ownership recovery](research/fees-optional-account-ownership/README.md)
adds a complete optional parser and a raw-byte-equal cleanup helper; its enclosing
account parser still differs. The [social-claim seed-vector recovery](research/fees-social-seed-vector/README.md)
adds the complete 296-byte user-ID copy helper; its claim caller still differs.
The [extension-size log recovery](research/fees-extend-size-logs/README.md) restores
the original no-resize messages and a complete 448-byte formatting helper.
The [crank interface-mint recovery](research/fees-crank-interface-mint/README.md)
adds one boxed parser match, removes two structural ambiguities, and corrects
the tested mint owner/length validation. The [shared zero-quote predicate](research/fees-curve-zero-helper/README.md)
now has a complete 504-byte match, including both referenced panic locations.
The [slice-panic location integration](research/fees-slice-origin-integration/README.md)
now carries all four tier-copy records into the latest candidate, changing only
eight data bytes and preserving its entire instruction section. The [buyback context recovery](research/fees-buyback-context-ownership/README.md)
adds the initializer parser, one initialization closure and the exit routine.
The [context-origin recovery](research/fees-buyback-context-origin/README.md)
now closes the second closure and its direct-call mismatch as well. The
[crank event-account recovery](research/fees-crank-event-ownership/README.md)
adds the complete exit routine and dispatch wrapper; the account parser and
business handler remain unmatched. Four [root codegen controls](research/fees-wrapper-codegen-controls/README.md)
add no matches and are retained as rejected experiments. The
[sweep context recovery](research/fees-sweep-context-ownership/README.md)
adds its complete account parser, exit and dispatch wrapper; the sweep business
body remains unmatched. The [buyback-update context recovery](research/fees-buyback-update-ownership/README.md)
now closes the shared update parser and both update dispatch wrappers, with
all 61 direct callee bodies matching. The [event-context integration](research/fees-event-context-ownership/README.md)
adds six parser/dispatch bodies across social claim, social-PDA creation and
withdrawal; their three business bodies remain unmatched. The
[unchecked-prefix recovery](research/fees-unchecked-prefix-recovery/README.md)
restores the full-account input convention and closes the 1,144-byte initializer
helper. Its host contract tests and SBF regression evidence have separate scopes.

The [current reconstruction review](docs/RECONSTRUCTION-STATUS.md) lists exact,
normalized, unmatched and opaque function status, all 10 remaining Relay bodies,
and prioritized behavior/build work. The [refreshed 4,415-row inventory](repro/reconstruction-status-2026-10-26/README.md)
includes every exact local body match and every unresolved window.

The [26 October reconstruction audit](docs/RECONSTRUCTION-AUDIT.md) separates
selected builds from newer research and lists [all 150 handlers](repro/reconstruction-audit-2026-10-26/handlers.md),
[every exact local body-byte match](repro/reconstruction-audit-2026-10-26/raw-body-matches.md)
and [all selected/research function windows](repro/reconstruction-audit-2026-10-26/functions.tsv).

## Current review

The [comprehensive review](repro/reconstruction-status-2026-10-26/review.md)
classifies **all 150 public handlers and all 4,415 selected/research window rows**.
No handler is certified perfectly recreated. The selected core builds contain
140 bounded implementations, five partial handlers and five unaccepted handlers;
“unaccepted” can include existing overlay or static-only source.

| Current build | Exact local bodies | Normalized only | Unmatched | Opaque | Unresolved original text |
| --- | ---: | ---: | ---: | ---: | ---: |
| Pump selected | 98 | 430 | 507 | 0 | 1,391,456 / 1,792,208 bytes (77.6%) |
| PumpSwap selected | 93 | 395 | 297 | 0 | 734,392 / 1,162,040 bytes (63.2%) |
| Fees research | 118 | 424 | 43 | 0 | 248,904 / 799,648 bytes (31.1%) |
| Mayhem selected | 58 | 131 | 7 | 245 | 636,128 / 706,744 bytes (90.0%) |
| Relay research | 130 | 352 | 10 | 0 | 52,616 / 752,488 bytes (7.0%) |

Unresolved text includes whole unmatched and opaque windows. These are not
differing-byte counts or estimates of effort. Calls, data, layout,
relocations, build provenance and broader behavior remain to be verified even
where a local body matches. Research rows do not replace selected checkpoints.

The public-handler gaps are concrete:

- **Partial:** Pump `buy_exact_quote_in_v3`, `buy_v3`, `sell_v3`, `create_v2`
  and `multi_hop_curve_swap`.
- **Unaccepted in selected builds:** Pump `admin_update_token_incentives`,
  `claim_token_incentives` and `set_mayhem_virtual_params`; PumpSwap
  `create_config`; Mayhem `initialize_mayhem_state`. Some have overlay or
  static-only source, so this category does not mean no implementation exists.
- **Implemented with bounded evidence:** the other 140 handlers. This includes
  known discrepancies such as Pump `sell_v2` quote transfer-fee behavior;
  passing finite cases does not establish perfect reconstruction.

The [handler ledger](repro/reconstruction-audit-2026-10-26/handlers.md) records
the evidence and missing coverage for each name. The [complete window ledger](repro/reconstruction-status-2026-10-26/functions.tsv)
separately records every raw, normalized, unmatched and opaque machine body.

## Selected checkpoint and historical audit

Handler counts are bounded reconstructions with saved differential comparisons;
they are not counts of exhaustively perfect functions. The unaccepted
[behavioral recovery overlay](repro/behavioral-recovery/README.md) dispatches all
56 Pump and 25 Mayhem instructions for local testing.

| Program | Selected bounded handlers | Saved comparisons | Whole captured file equal |
| --- | ---: | ---: | --- |
| Pump | 48 / 56; 5 partial, 3 unaccepted | 9,269 + 1,024 Surfpool | No |
| PumpSwap (AMM) | 37 / 38 | 17,462 | No |
| Fees | 31 / 31 | 17,461 | No |
| Mayhem | 24 / 25 | 9,595 | No |
| Donation Relay | selected source 15; newer generated-framework source in `repro/donation-relay/` | 12 ordinary | No |

Selected original-window inventories contain **384 windows with equal local
body bytes**, **1,408 additional normalized-only matches**, **1,301 without a
complete body match**, and **245 remaining opaque windows**. These partition
3,338 original windows; matching bytes or normalized instructions does not prove
call/data identity or all behavior. Original boundaries remain inferred.

At the earlier immutable audit snapshot (not the current research frontier), research was separate: Fees had 340 unique structural pairs, 53 additional
call-attributed duplicate pairs, 94 still-unattributed duplicate windows and 98
unmatched windows. Relay's distribution-worker research reached 465/492 normalized
windows (86 raw local matches), leaving 27 unmatched; selected Relay remains at
122/492. These are not source-completion percentages or promoted checkpoints.

Known behavior gaps remain even among bounded handlers, including Pump `sell_v2`
quote transfer fees. See the [remaining-work list](docs/REMAINING-WORK.md).

Dependencies captured alongside the core programs:

| Dependency | Rebuilt from public source |
| --- | --- |
| SPL Token | Byte-identical |
| Token-2022 | Raw ELF matches the captured prefix; generated zero padding reproduces the full allocation ([report](repro/pump/verified-token-2022/README.md)) |
| Associated Token Account | Raw bytes reproduced (105,032 bytes, `6804554e…`) only through two non-historical recipes: a linker symbol order ([report](repro/ata/reconstructed-order/README.md)) and one empty Cargo feature ([report](repro/ata/synthetic-ordering-exact-build/REPORT.md)). The authentic recipe is unknown; `repro/dependency-status.json` still says unresolved |
| Metaplex Token Metadata | 1,509 differing positions in the allocation comparison: 1,477 text bytes in Utilize, 30 source-coordinate bytes and 2 relocation bytes ([report](repro/pump/metaplex-candidate-build-11/README.md)) |

The Token-2022 and Metaplex raw ELFs are shorter than their captured allocations
by 770,960 and 86,543 zero bytes respectively. Allocation-image comparisons are
separate from equality of the unmodified compiler output.

Selections live in [`repro/status.json`](repro/status.json) (the four core
programs), [`repro/donation-relay/current.json`](repro/donation-relay/current.json)
(Relay) and [`repro/dependency-status.json`](repro/dependency-status.json)
(dependencies). [`docs/REMAINING-WORK.md`](docs/REMAINING-WORK.md) lists what is left.

## Quick start

Python 3.12. Evidence checks need only the standard library; local VM execution
needs the pinned packages. Clone with line-ending conversion off, or converted
receipts break the evidence hashes
([checkout integrity](repro/checkout-integrity/README.md)).

```sh
git clone --config core.autocrlf=false https://github.com/lalalune/pumpfun-source.git
cd pumpfun-source
python3 scripts/verify_evidence.py      # captured bytes and manifests
python3 scripts/test_tooling.py         # tooling self-tests
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/local_validation.py
```

Build a program and compare it with the deployed original:

```sh
cargo build-sbf --manifest-path programs/pump/Cargo.toml --tools-version v1.44 \
  --sbf-out-dir work/pump-build -- --locked
python3 scripts/compare.py pump work/pump-build/pump_recovered.so --output work/comparison-pump
```

Toolchains: Pump, PumpSwap and Fees use platform-tools v1.44 through
`scripts/build_partial_candidate.py`, which wraps `cargo build-sbf` with an
isolated SDK and records a provenance report. Mayhem's selected v1.54 build came
from a one-shot direct Cargo/rustc controller (`repro/mayhem/compiler-v154-main/`);
the repository adapter (`scripts/build_reconstruction_candidate.py --tools-version v1.54`)
reproduces the same bytes (`repro/build-tooling/supported-sbpf-integration/`).

For local SDK testing with every handler present, apply the
[behavioral recovery overlay](repro/behavioral-recovery/README.md) and use the
`@pump-fun/pump-sdk` harness in
`repro/parallel-work/2026-10-25/independent-reconstruction-review/sdk-integration-test/`.

## Layout

| Path | Contents |
| --- | --- |
| `programs/` | Reconstructed Rust crates. CI hash-binds these to the selected checkpoints. |
| `evidence/` | Captured deployed binaries, account payloads and upstream IDLs. Comparison inputs only, never compiler inputs. |
| `repro/` | One evidence package per checkpoint or study: builds, comparison reports, differential receipts, verifiers. |
| `scripts/` | Capture, build, compare and differential tooling ([index](scripts/README.md)). |
| `localnet/` | Surfpool fixtures and transaction tests. |
| `research/` | Imported research lab and provenance studies. |
| `binaries/` | Standalone compiler-experiment objects; never selected candidates. |
| `audit/`, `docs/`, `outputs/` | Validation scope, design notes and per-pass reports. |

## Rules the evidence follows

- Behavioral equivalence and byte identity are reported separately and never combined into one score.
- Raw compiler-byte identity never uses padding or rewriting; allocation-image matches are labeled separately.
- Original binaries are read only after compilation finishes.
- Changing a CI-bound source file means selecting a new checkpoint with fresh build and differential evidence.
- Tests run only against local VMs and simulators; nothing is sent to a live network.

## More detail

- [Current reconstruction review](docs/RECONSTRUCTION-STATUS.md), [selected baseline audit](docs/RECONSTRUCTION-AUDIT.md) and [remaining work](docs/REMAINING-WORK.md)
- [Historical selected-checkpoint completion ledger](docs/COMPLETION.md) and [scope](docs/SCOPE.md)
- [Tooling](docs/TOOLING.md) and [historical build-identity audit](docs/BUILD_IDENTITY_AUDIT.md)
- Per-pass ledgers in `repro/layered-passes/`; historical packages are immutable.
- [Security policy](SECURITY.md) and [audit scope](audit/AUDIT.md)

## License

This repository's own code and documentation are released under the
[MIT License](LICENSE). Third-party and vendored materials (for example the
Apache-2.0 Solana SDK files under `programs/pump-amm/vendor`, imported research
and retained crate archives) keep their original licenses, and upstream Pump IDLs
and binaries remain with their original authors.

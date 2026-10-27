# Current function-window inventory

Evidence snapshot: `e2d7855848a3411d665deb915077ef20672e7cdd`. Selected inputs retain their verified `1463bd22fb7811825c5e7acf1cb963eb39ab68d9` checkpoint bindings. Research rows replace the older Fees/Relay research inventory; they do not replace selections.

| Program / build | Windows | Exact local bytes | Normalized only | No complete match | Opaque |
| --- | ---: | ---: | ---: | ---: | ---: |
| pump | 1035 | 98 | 430 | 507 | 0 |
| pump_amm | 785 | 93 | 395 | 297 | 0 |
| pump_fees | 585 | 102 | 363 | 120 | 0 |
| mayhem | 441 | 58 | 131 | 7 | 245 |
| donation_relay | 492 | 33 | 89 | 370 | 0 |
| pump_fees_research | 585 | 118 | 424 | 43 | 0 |
| donation_relay_research | 492 | 130 | 352 | 10 | 0 |

Fees has 380 body-unique pairs plus 62 additional call-attributed duplicate pairs (442 correspondences); 85 duplicate windows remain unattributed. These are not 62 additional body matches. Rows count inferred original windows, not unique source functions or effort. Raw matches may be duplicate/ambiguous and do not establish referenced data or transitive callees. The Fees matcher and Relay matcher use separately documented masks; do not add their counts into a source-completion score.

- [Comprehensive review: all handlers, unresolved text size and closure criteria](review.md)
- [Every window, symbol candidate, match address and evidence path](functions.tsv)
- [Every exact local body match](raw-body-matches.md)
- [Every unmatched or opaque window](remaining-windows.md)
- [All 150 public-handler dispositions](../reconstruction-audit-2026-10-26/handlers.md)
- [Counts, candidate hashes and input hashes](status.json)

Verify: `python3 -B repro/reconstruction-status-2026-10-26/refresh.py --check`. This re-reads binaries and checks the declared masks; it does not compile or execute target programs. Also run the parent audit and both owning research verifiers to check source bindings, retained runtime receipts and selected artifacts.

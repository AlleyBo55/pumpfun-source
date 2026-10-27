# Function-window audit summary

Snapshot: `1463bd22fb7811825c5e7acf1cb963eb39ab68d9`. Raw bodies were rehashed from actual binary bytes; normalized relations use each pinned source ledger’s own rules. Counts are original windows, never candidate-pair counts.

| Program / build | Windows | Exact local bytes | Normalized only | No complete match | Opaque, no byte match |
| --- | ---: | ---: | ---: | ---: | ---: |
| pump | 1035 | 98 | 430 | 507 | 0 |
| pump_amm | 785 | 93 | 395 | 297 | 0 |
| pump_fees | 585 | 102 | 363 | 120 | 0 |
| mayhem | 441 | 58 | 131 | 7 | 245 |
| donation_relay | 492 | 33 | 89 | 370 | 0 |
| pump_fees_research | 585 | 107 | 380 | 98 | 0 |
| donation_relay_research | 492 | 86 | 379 | 27 | 0 |

These columns partition the rows. Mayhem has 257 source-ledger opaque windows; 12 happen to have equal local byte bodies and are counted in the exact-byte column, leaving 245 in the last column. Its 177 admitted normalized matches remain a separate count.

The selected Fees ledger also retains two call-conflicting rows. A raw or normalized body match does not erase that conflict. Pump’s 617 historical raw **pairs** represent 98 distinct original windows in this audit, not 617 reconstructed functions.

- [All 150 handlers](handlers.md)
- [Every exact local body match](raw-body-matches.md)
- [All 4,415 selected/research window rows](functions.tsv)
- [Machine-readable evidence and input hashes](audit.json)

Rebuild these tables with `python3 -B repro/reconstruction-audit-2026-10-26/audit.py`; check them with the same command plus `--check`. No target programs are executed.

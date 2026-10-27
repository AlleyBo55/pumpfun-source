# Fees: compare compiler controls across every function window

The fixed-source compiler controls from PR #81 reproduce similar bounded decoder bodies, but their complete function maps differ substantially. Re-deriving the entire map gives this comparison against the original's 585 inferred windows:

| Retained profile | Candidate windows | Unique structural pairs | Unmatched original windows |
| --- | ---: | ---: | ---: |
| v1.44, legacy target/driver | 582 | 320 | 121 |
| v1.45, legacy target/driver | 604 | 282 | 162 |
| v1.46, legacy target/driver | 604 | 266 | 180 |
| v1.46.1, canonical target/direct Cargo | 604 | 219 | 239 |

All 26 source input hashes are identical across these builds. Their ELF hashes exactly match the previously retained PR #81 artifacts. These are the earlier fixed decoder-source controls, **not** the later parser/dispatcher/coordinate source that reaches 334 pairs in PR #85.

This supports prioritizing v1.44 for this source profile; it does **not** identify the historical compiler or exclude another compiler with different historical source/build inputs. The v1.46.1 row also changes the target spelling and driver: its bundle provides `sbpf-solana-solana` standard libraries, while the legacy driver requests `sbf-solana-solana`. That row is not a compiler-only comparison. Its retained launch/result records describe the direct Cargo invocation.

The mapper independently recovers every candidate function address and size exactly against each retained symbol table. It preserves all scalar literals, stack/branch displacements, opcodes and registers; masks only local CALL immediate words and actual relocated LDDW addresses; and retains external import names and relocation offsets in signatures. Ambiguous groups remain separate. Opaque pointed-to data and callee bodies are outside these structural comparisons.

Candidate functions whose symbols name `type_id` are also compared by their **complete unmasked raw bytes** against every inferred original window. None matches under any retained profile. The report retains every such body and hash; candidate names do not identify the historical types. This remaining difference prevents claiming exact compiler recovery from matching normalized parser bodies alone.

## Verify

```sh
python3 research/fees-compiler-frontier/verify.py
python3 -I research/fees-compiler-frontier/verify.py
python3 research/fees-compiler-frontier/map_windows.py
```

The standard-library checker validates the packet manifest, 26 fixed source inputs, 187 unchanged harness files, prior artifact bindings, complete stripped/unstripped `.text` equality, successful v1.52 strip replays, inferred boundaries and full comparison reports. Build logs, tool/archive hashes, canonical launch/result records, and the shared source override are retained. Runtime receipts for these unchanged builds are in PR #81; this packet adds the broader static comparison.

None of these outputs matches either the captured allocation or the original ELF extent. Core raw identity remains **0/4**. Selected sources/candidates, checkpoint ledgers, scripts and workflows remain unchanged. Logs and executable hashes are not an authenticated process trace.

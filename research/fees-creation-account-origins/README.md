# Fees: recover creation parser source locations

Moving the unchanged account declarations to the source paths recorded in the original binary, with their `#[derive(Accounts)]` attributes on the observed lines, recovers **3 complete structural windows**. The checker reads the actual path pointers, full pointed-to strings, path-length stores and line stores from both binaries.

| Original address | Bytes | Path below `src/instructions/` | Derive line |
| --- | ---: | --- | ---: |
| 434760 | 8184 | `fee_sharing/create_donation_fee_pda.rs` | 21 |
| 456176 | 7992 | `fee_sharing/create_fee_sharing_config.rs` | 54 |
| 475696 | 7984 | `fee_sharing/create_social_fee_pda.rs` | 11 |

Unique structural pairs increase from **346 to 349**, with none lost; **89 original windows remain unmatched**. Both candidates have **580 inferred windows**, exactly reproducing every function-symbol address and extent, including aliases. This is new research evidence; selected sources/candidates are unchanged, and core whole-file byte identity remains **0/4**.

## Verify and rebuild

```sh
python3 research/fees-creation-account-origins/verify.py
python3 -I research/fees-creation-account-origins/verify.py
```

The complete moved declarations, including attributes, remain byte-for-byte identical as source text. These are reconstructed declarations, not recovered historical source text. The checker reconstructs each old containing file using only the preserved declaration, the required re-export and blank lines, proving that the business-handler text in those files is unchanged. The program declaration, `lib.rs`, argument types, state file and sharing-update source are unchanged between these builds. Real source files and whitespace supply the locations; no generated executable bytes are edited.

The standalone checker re-derives complete signatures and bindings from the ELF bytes and binds all **29/31 source inputs**, the complete overrides, 187 unchanged harness files, unstripped/stripped `.text`, successful build records, and fresh strip replays. Symbols annotate candidate windows only; original roles are inferred from the captured paths, encoded code and comparison evidence.

Both retained builds pass **17,331 independent original/candidate comparisons across 18 local suites**. The control receipt is reused from its identical earlier artifact; the proposal was executed afresh. Each also retains a **1,542-case** matrix covering every optional byte plus absence, both pool flags and three caps in one fixed valid configuration, with identical outcomes, raw logs and compute units. `exhaustive_flags.py` reproduces that focused check with the pinned LiteSVM environment and an uncompressed candidate. These finite results do not prove exhaustive program semantics.

Signatures preserve scalar literals, registers, stack/branch offsets and external import identities while masking local CALL immediates and actual relocated LDDW addresses. The 3 source-location-specific checks do not prove other opaque data or transitive/indirect callees equal. Raw whole-file and ELF-extent comparisons remain false.

Use the complete recorded source overlays at the bound source revision, official platform-tools v1.44 with the canonical `sbpf-solana-solana` target and `RUSTFLAGS=-Zremap-cwd-prefix=`, following `builds/*-launch.json`; strip with the pinned v1.52 tool. Logs/hashes are retained evidence rather than an authenticated process trace. Previous unchecked-input compatibility limits remain. No pinned script, workflow, checkpoint ledger or selected program changes.

# Fees: recover the complete Shareholder vector clone

Adding `Copy` to the existing `Shareholder` derive selects the compiler's byte-copy vector-clone specialization and recovers the **336-byte original window at 58520**. Both encoded calls, at offsets 280 and 328, resolve to complete callees with equal raw body bytes: `memcpy` and `alloc::raw_vec::handle_error`. This attributes two existing callee matches; it adds only one original body window.

The standalone checker proves that the `Shareholder` derive is the only source change between control and proposal, across all 32 inputs. An independently compiled negative control adds `Copy` to `FeeTier` instead. It adds and loses no unique structural pairs and is excluded from the proposed source. All three complete source overlays, artifacts, build records and strip replays are retained.

Unique structural pairs increase from **351 to 352**, with none lost; **86 original windows remain unmatched**. There are 580 inferred candidate windows, independently equal to all function-symbol extents including aliases. The candidate retains 57 unique pairs with equal raw local bytes. Its complete capture and ELF-extent comparisons remain false; core whole-file identity remains **0/4**.

## Verify and rebuild

```sh
python3 research/fees-shareholder-copy-clone/verify.py
python3 -I research/fees-shareholder-copy-clone/verify.py
```

The control and proposal each pass 17,331 original/candidate comparisons across 18 local suites and 1,542 exact outcome/log/compute comparisons covering every optional byte plus absence, both pool flags and three caps in one fixed valid configuration. The proposal was executed afresh; identical control receipts are explicitly reused. The negative control is retained as static/build evidence and has no claimed runtime-suite validation. Finite comparisons do not establish exhaustive semantic equivalence.

Build from the recorded source revision with the complete overrides and official platform-tools v1.44, using canonical `sbpf-solana-solana` and `RUSTFLAGS=-Zremap-cwd-prefix=` as recorded in `builds/*-launch.json`. Strip with the pinned v1.52 tool. The checker binds 187 unchanged harness hashes, all build inputs and stripped/unstripped text. Logs/hashes are retained evidence, not authenticated process traces or proof of historical source authenticity.

Structural signatures mask local CALL immediates and actual relocated LDDW addresses, retaining scalar values, registers, stack/branch offsets and external import identities. The two callee bindings are checked independently from actual encoded calls; other transitive or opaque data identity is not established. Existing unchecked-input limitations remain. Selected programs, pinned scripts, workflows and checkpoint ledgers are unchanged.

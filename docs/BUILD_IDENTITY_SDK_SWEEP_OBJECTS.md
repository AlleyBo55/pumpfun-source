# SDK sweep and creator-update object coverage

The [authenticated source expansion](../repro/sdk/sweep-setcreator-source-20261026/REPORT.md) binds eight more of the original dynamic account-object sites: four AMM fee sweeps supply all 12 IDL fields, two Pump curve sweeps supply nine of 13, and two conditional AMM creator-update sites supply one or three of five. The exact earlier eight site IDs and new eight are disjoint; nine of the original 25 were left for the separate source review below. This counts symbolic object bindings within the existing builder inventory, not instructions or runtime compatibility.

The [independent source and portability review](../repro/sdk/sweep-setcreator-source-independent-review-20261026/REPORT.md) confirms helper argument substitutions, complete object expressions, IDL ordering/flags/omissions and the conditional creator branches. Fresh relocation passed with exact-case paths and no stale workspace reads. Source seal: `ee143e26fcf33efee56fb421e6a2e604baa029ae4e51b07c7b170d1c74f19052`. Review seal: `d3a2cddb74cb5d1d3a2a86c77fe175e1a6d093d367b737486f992bdccc847e9c`.

Pump curve sweeps leave global, associatedTokenProgram, systemProgram and bondingCurve to resolution; their IDL recipes are retained. Creator updates without baseMint leave mint-derived accounts dependent on pool data. The online wrapper reads/decodes the pool, prepends extension below 300 bytes, then supplies baseMint explicitly. Client decoding padding and account extension are separate steps. The omitted program field has no IDL address/PDA recipe in the source packet. The subsequent compiled-wrapper observation below measures the supplied-baseMint branch and retains both omitted-baseMint failures.

The source packet itself ran no SDK JavaScript or Anchor method. Its static findings remain distinct from the later runtime experiment.

## Actual compiled-wrapper observation

The [saved runtime audit](../repro/sdk/sweep-setcreator-runtime-20261026/REPORT.md) binds one actual offline run of the public compiled SDK exports. Four AMM sweeps, two Pump curve sweeps and two creator updates with supplied baseMint constructed eight instructions; their program IDs, discriminators and all 84 ordered account metas match independent expectations. Numeric PDA/ATA checks cover sixteen derivation records and thirteen unique addresses. Both calls that omitted baseMint failed with unresolved metadata and bondingCurve accounts; they are preserved as resolver errors, not successful construction.

All 4,749 graph files remained unchanged. The observer recorded 316 loaded modules and one genuine bufferutil native addon load. Thirteen missing bigint native resolution candidates produced the recorded pure-JavaScript fallback; they were not native dlopen failures. No guarded RPC, transport or signing calls were observed. This is a Node-level observation, not an operating-system isolation claim.

Runtime review seal: `cec59238fb6f08abd74358642b771544da59d9e6e2a393220bec4e5d552c2ebb`. The [separate relocation receipts](../repro/sdk/sweep-setcreator-runtime-portability-20261026/observation.json) retain zero exact-case/workspace violations, seal `ce92f8b75de5612069178f9ab1398c0e2ed43e902a4e8968cb151f16a8277535`. Replay only saved data with:

```sh
python3 -B repro/sdk/sweep-setcreator-runtime-20261026/verify.py --expected-seal cec59238fb6f08abd74358642b771544da59d9e6e2a393220bec4e5d552c2ebb
```

The portable checker executes standard-library Python on bundled observations and reads compiled JavaScript as inert evidence. It does not rerun SDKs, import native crypto utilities, sign transactions or contact RPC. The synthetic client inputs do not establish valid real pool/mint/token/metadata state, recipient membership, account extension, target execution or arbitrary resolver compatibility. The separate source review below symbolically maps the remaining nine; it adds no runtime acceptance. Source/compiler/dependency identity and whole-byte identity remain open; core whole-file identity is still 0/4. Active program source, selected artifacts, status, workflows and historical packets are unchanged.


## Remaining nine trade objects: source-only mapping

The [authenticated source packet](../repro/sdk/trade-v2-v3-nine-source-20261026/REPORT.md) maps the nine remaining sites: six AMM tradeV2 objects provide all 17 IDL fields through accountsStrict; three Pump tradeV3 objects provide 10 of 17 through accountsPartial. Seven omitted fields retain their exact IDL address/PDA/relations recipes; Anchor resolution was not executed. This completes symbolic coverage of the original 25-site inventory only.

The packet retains two authenticated published SDK archives, 21 exact source/IDL members, complete ordered account flags and source expressions, raw numeric argument mapping, quote/fee rounding, slippage quantization and unresolved authentic state inputs. The [independent source review](../repro/sdk/trade-v2-v3-nine-independent-review-20261026/FINDINGS.md) checks all nine objects and 132 supplied fields, plus the critical arithmetic and recipient branches.

Source seal: `4bcd0ca9d8cb69a219d48d4098cab37556c7899c5ce447df8e55312db019de9e`. Independent review seal: `ea98378c78954bf86c9640030cdde9d8867181311f5c1a2a32b60856a1f78382`. Replay with `python3 -B repro/sdk/trade-v2-v3-nine-source-20261026/verify.py`.

No JavaScript, BN arithmetic, Anchor resolver, provider, signing, compiler or VM ran. Earlier runtime observations do not transfer to these nine sites. Authentic account state, transaction effects, transfer-fee/extension behavior, partial fills, arbitrary resolver compatibility and historical program source remain unproved. No stopped runtime lane is resumed; selected artifacts and whole-byte identity remain unchanged.

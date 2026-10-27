# Unselected source-path remap recipe

The exact helper proposed in commit `d9dc52b540816c1599af6aa8c8f4f746461a4680` is retained as `build_partial_candidate.py.txt` for review only. SHA-256: `94dbc8a5231cafd24bcb46ac2b1f610c51bf33357ade1f1f4d972ab53aaab00b`. It is not an active build entrypoint.

That commit changed the default helper and broke hosted evidence job 121652891000 in run 40345773231: the current helper no longer matched the historical promotion-control input. The default helper is restored byte-for-byte to SHA-256 `bb683621ffc4297c58f030cb03da54484b7370b786fd8eda965a37f4b3198ee9`. Frozen checkpoint code and receipts are unchanged.

The proposal appends a source-path remap to RUSTFLAGS. Matching embedded paths does not establish the historical build context, source structure, line coordinates, runtime equivalence, or whole-binary identity. Its retained comments describe the contributor's experiment; they are not independent certification. Existing workspace/remap research remains in its original packet.

Any future execution needs a separate explicit experimental entrypoint, complete input/tool bindings, fresh outputs and independent validation before a default recipe or artifact can change. No native build, original disassembly or VM was run for this preservation repair.

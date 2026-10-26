# Saved author sBPF cross-check and reproduction source

This package preserves the author's original ata_order_report.json and
inventory.json byte-for-byte. Their conclusions and counts are historical raw
receipts, not rewritten acceptance statements. The corrected source and this
report qualify their scope. No new decoder/Ghidra/original-image run was made
while preparing this correction.

## What is retained

The author supplied a dependency-free ELF reader/linear sBPF disassembler, a
preset ATA-window checker, a nine-input linear inventory and a Ghidra listing
export script. These are research tools, not an admitted decoder, full CFG
recovery, ABI verifier or complete identity proof. The report's prior claim that
REA rejects the images and its Ghidra import observations remain author-reported;
no REA/Ghidra executable/version or raw admission receipt is bundled.

The saved ATA report records the following two preset intervals of the named
associated-token image (reported full SHA2566804554e69fd3a58caa191dc4a58f4c67223d30ca28ab8987f39fc18d2f7374d):

| attribution | file offsets | bytes | linear instructions | raw SHA256 |
|---|---|---|---|---|
| AccountMeta |28592–29032|440|55|8e46c99eac4736d2fcff3fc0f8133cd49a19b8a7d67a36b26e1804f21fcba7c9|
| u8 |29032–29384|352|44|37b37fdcf5a13862220b07be1c9fb9d9c90870cfe198748cc96f2aa1052a0a9b|

Its raw/call-immediate-masked hashes agree with the vendored witness constants.
The first interval has two34 immediates; the second has none. That supports the
reported width/type attribution, but does not uniquely prove a Rust element type
or semantic equivalence. The offset-order check compares these already chosen
witness offsets. It is not a search recovering all function boundaries or an
independent comparison of the closest candidate. The checker records a full
image hash but only the two window hashes are pinned as acceptance conditions.

## Oracle and historical-identity limits

The author reported Ghidra12.1.4 eBPF decoding55/44 instructions with zero address-
stream mismatches and matching operands. That cross-check is UNREVERIFIED here:
no oracle dump, comparison method/output, command/exit logs, tool/runtime version
receipt or exact oracle-input binding is bundled. DumpText.java is source for a
listing export, not the missing oracle evidence. Counts/address streams alone
would not establish every operand or instruction semantic. No new oracle run or
original-image acquisition is required or implied by this correction.

The prior repository attributed an ATA residual307 differing positions to
monomorphization order and discussed Cargo-unit metadata. This tool does not read
the closest candidate or historical build graph, so its observations do not
independently establish that causal history, a unique required recipe, or that
whole-byte identity is unreachable. The stronger old prose in the unchanged raw
JSON remains a historical author assertion. Finite negative builds and a
window-order observation do not prove impossibility. Other programs' source,
compiler, ABI and whole-byte closure remain separate open obligations.

inventory.json retains the author's nine-image observations and labels function
counts heuristic. Inventory uses linear decoding and local-call targets/entry;
it is not complete function or reachable-CFG proof. Missing files are skipped,
so a successful command can be an incomplete inventory. The saved entries contain
both machine247 and263, including263 SPL-token entries; no all-dependencies247
generalization is made. Claimed Ghidra reachable counts/importability are not
repeated as verified results. No new decoder conformance proof is supplied.

## Reproduction interfaces and writes

From repository root, enter repro/ata/independent-ebpf-crosscheck. Both Python
entry points now require an explicit --output path. For example:

```bash
mkdir reproduced
python3 verify_ata_order.py --output reproduced/ata_order_report.json
python3 inventory.py --output reproduced/inventory.json
# Or: bash run.sh /chosen/report-directory
```

These commands read local binary inputs and write regenerated reports; they are
not globally read-only. The runner defaults to a separate reproduced/ directory and creates it with one
atomic mkdir without -p. The directory must not exist, and its parent must already
exist. An existing directory, a symlink or a choice such as . fails before either
Python tool starts. Both Python CLIs reject an existing/symlink output path before
reading original inputs, require an existing output parent, and write the new
report in exclusive x mode. If another process creates the path after the initial
check, exclusive creation fails without overwriting it. The two saved JSON
receipts remain protected. No original binary is modified, fetched or installed by
these tools. Whether executing an original decoder is authorized is a separate
operator decision; this preserved research package grants no new scope.

run.sh prints an optional Ghidra example with explicit fresh project/listing
paths. Ghidra writes its project and DumpText writes its output file (its legacy
fallback is /tmp/ghidra_text_dump.tsv if REA_DUMP_OUT is unset). The example sets
REA_DUMP_OUT explicitly. No Ghidra invocation is automatically performed by the
runner. The manifest hashes the corrected source/manual docs and the unchanged
saved receipts; it authenticates file bytes, not absent execution evidence.

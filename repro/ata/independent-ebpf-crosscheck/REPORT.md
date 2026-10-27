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

## Independent byte-distance: the 307 residual, re-derived

`byte_distance.py` re-measures the ATA residual directly from the two program
images using only `hashlib`: no disassembler, no symbols, and no dependency on
any other script in this package. It diffs `original.so` against the closest
candidate `candidate2.so` and localizes every differing offset. The candidate
pair lives under `repro/ata/monomorph-order-proof/`, which is sparse-excluded by
default; materialize it with `git sparse-checkout add
repro/ata/monomorph-order-proof` before running.

The tool asserts the recorded values below and exits non-zero on any drift, so
it also serves as a regression guard for the residual:

```
ATA original  6804554e69fd3a58  105032 B
ATA candidate ba8dd8a42ca7bff4  105032 B
total differing bytes: 307 (common-extent 307, length delta 0)
contiguous diff runs:  126, first at offset 28601
inside windows [28592, 29384]: 282  (AccountMeta 181, u8 101)
outside windows (call/reloc fixups): 25
```

Scope and limits. The byte counts, the 282/25 split across the two preset
windows already named by `verify_ata_order.py`, and the first differing offset
(28601) are reproducible facts about these specific `original.so` and
`candidate2.so` files. The attribution of the in-window bytes to swapped
`RawVec::reserve_for_push` monomorphizations is carried in the tool's
`interpretation` field as the author's reading; this measurement does not
independently establish it. The tool compares only this one candidate pair. It
does not search other candidates, recover function boundaries, prove the
element-type attribution, or prove that whole-byte identity is unreachable.

Review note (2026-10-26): an earlier version of the `interpretation` field also
read the residual as "not closable without the historical Cargo unit-graph
inputs". Later packages contradict that reading:
[`../reconstructed-order/`](../reconstructed-order/README.md) (a linker
symbol-ordering file that swaps only this pair) and
[`../synthetic-ordering-exact-build/`](../synthetic-ordering-exact-build/REPORT.md)
(an empty, code-free Cargo feature that changes `-C metadata`) both build
f5ce86 to the exact raw deployed bytes. Both use a non-historical ordering input,
so the historical recipe is still unknown. The `interpretation` field and
`byte_distance_report.json` were updated to match; the measured values did not
change.

Usage:

```bash
python3 byte_distance.py            # assert the recorded ATA pair (read-only)
python3 byte_distance.py --json     # same result, machine-readable to stdout
python3 byte_distance.py A.so B.so  # measure an arbitrary pair (descriptive only)
```

The committed `byte_distance_report.json` is the saved receipt of the asserting
run (`python3 byte_distance.py --json`, byte-for-byte); the tools in this package
do not overwrite it.

## Controlled experiment: Darwin build host (negative result)

Every retained ATA candidate was compiled on an `x86_64-unknown-linux-gnu` host.
Cargo at the commit shipped in bpf-tools v1.27 (`49d8809d`,
`compilation_files.rs::hash_rustc_version`) hashes the `rustc -vV` host triple
into every unit's `-C metadata` for a `-dev` compiler, and the release asset was
uploaded twelve minutes before its source tree was committed, consistent with a
local maintainer build. One pre-registered, single-input experiment was therefore
run: the same source revision, lockfile, SDK release and compiler commits, with
only the host changed to `x86_64-apple-darwin`. Hypothesis, inputs, build log,
toolchain identity, output binary and an offline verifier are retained in
[darwin-host-experiment/](darwin-host-experiment/REPORT.md).

```
candidate2 (Linux host)   differing positions vs deployed:  307
darwin build              differing positions vs deployed: 3288  (vs candidate2: 2981)
darwin diffs by section: .text 3267, .rel.dyn 21; .rodata and section layout identical
pair order: deployed AccountMeta->u8 | candidate2 u8->AccountMeta | darwin u8->AccountMeta
```

The hypothesis is rejected. Changing the host re-hashed every crate's metadata
and re-ordered dozens of functions (1,314 of 1,438 call-masked 64-byte `.text`
chunks stay at the same offset; the instruction multiset differs by nine
address-bearing instructions per side), while the deployed program differs from
the Linux candidate by a single function pair. This rejects the tested pinned Darwin recipe as an exact reproduction, but one
negative build cannot exclude all Darwin contexts or all global metadata inputs.
Hash-based ordering can preserve relative order. The historical host and missing
metadata inputs remain unresolved; a single-crate perturbation is a hypothesis,
not a uniquely established explanation.

Reading the v1.10.33 `cargo-test-bpf` source additionally excludes the upstream
CI invocation as that input without a build: it passes `--features test-bpf`
only to the subsequent host `cargo test`, never to the `cargo-build-bpf` step,
so its `.so` output is identical to a plain `cargo build-bpf`.

Scope and limits. This is one build on one host with every other input pinned;
it does not reduce the 307-position residual, recover the historical recipe, or
authorize a flag, version or path sweep. The lockfile hash was unchanged by the
build. The `bpf` rustup link and `~/.cache/solana` directory created by
`cargo-build-bpf` were removed afterwards; no global toolchain was modified.
`darwin-host-experiment/verify.py` is standard-library only, offline, and
asserts every number above from the retained binaries.

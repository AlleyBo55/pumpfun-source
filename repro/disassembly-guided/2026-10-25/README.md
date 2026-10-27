# Disassembly-guided reconstruction, 2026-10-25

**Disassembly is usable for exact instruction reconstruction. Lost original Rust source is not an impossibility proof.** This packet establishes a concrete tooling result, not completed contract reconstruction.

Blueshift `sbpf` commit `a161bf149e2265b2db79a443afc5c42fcfacc0a0`, version 0.3.2, was built with its committed lockfile. It decoded every executable byte in the nine retained program captures without diagnostics. The inventory contains 788,302 instructions covering 6,567,472 `.text` bytes. Each instruction has its original file offset, raw encoding, decoded fields and assembly mnemonic. Loader-relocated external calls are distinguished from relative internal calls, including external placeholder calls with `src=1, immediate=-1`.

The raw disassembler prints numeric relative calls that this assembler does not accept directly. The round-trip generator replaces those call operands with labels at the decoded target offsets. It preserves instruction order, branch displacements, constants and syscall names. For this encoding test only, an external call's placeholder is also preserved as a symbolic self-call; original loader relocations are not linked into the generated ELF. No raw `.byte`, `.quad` or `incbin` directives supply executable bytes.

All nine assembled `.text` sections are raw-identical to their targets, including Pump, AMM, Fees, Mayhem, ATA, Donation Relay, Token, Token-2022 and Metaplex. The actual generated ELF files are retained in `roundtrip-elfs/` and independently compared by `verify.py`. Their full ELF bytes differ from the originals. They are explicitly **reference-derived tool-validation outputs**, not independently reconstructed Rust builds, accepted contract candidates or original-source provenance.

## What this resolves and leaves open

This demonstrates that the remaining executable instructions can be represented and assembled exactly. It does not recover original variable names, Rust generics, macros, ownership structure, Cargo graph or diagnostic source formatting. Different high-level programs can compile to the same instructions. An exact assembly representation therefore does not uniquely identify historical Rust source.

For the independent Rust-build goal, the useful loop remains: select a measured original/candidate CFG discrepancy, recover its operands/callees/data, express a justified Rust hypothesis, compile under the pinned recipe, and compare the complete output. Source-location records are also evidence for reconstructing formatting, but any inferred comments/whitespace must be disclosed as reconstruction rather than authenticated historical text. Full ELF layout, relocation, data and allocation bytes remain part of final acceptance.

The Metaplex target branch at file offset 238832 is independently decoded as `jge r7, r9, +0x7`; `r7` holds remaining uses and `r9` requested uses. Its success path subtracts at 238936. Candidate11 instead places the shared error block later; candidate12 inserts an extra unconditional jump. The reviewed positive-guard Rust expression was tested separately in [hosted run 40233083060](https://github.com/lalalune/pumpfun-source/actions/runs/40233083060), on the frozen local checkpoint `5bb3dec06cccecc8cea529fc17815aa1bf78d17a`. Compilation succeeded, but the raw output exactly reproduced rejected candidate12 (`4f039033…`), with 196,601 differing payload positions. The reviewed guard is rejected as a byte-identity repair; the formatting-only follow-on was not dispatched. The earlier run 40191551052 used a different unified-guard patch and reproduced candidate11; its workflow input name does not establish that the currently reviewed patch was tested.

## Reproduction

Build the pinned upstream tool in a fresh checkout:

```sh
git clone https://github.com/blueshift-gg/sbpf.git /tmp/sbpf-research
git -C /tmp/sbpf-research checkout a161bf149e2265b2db79a443afc5c42fcfacc0a0
cargo build --locked --release --manifest-path /tmp/sbpf-research/Cargo.toml -p sbpf
python3 scripts/sbpf_disassembly_inventory.py \
  --tool-source /tmp/sbpf-research --output work/fresh-disassembly-inventory
python3 scripts/sbpf_disassembly_roundtrip.py \
  --tool-source /tmp/sbpf-research --inventory work/fresh-disassembly-inventory \
  --output work/fresh-disassembly-roundtrip
```

Verify retained artifacts offline, without a compiler or VM:

```sh
python3 repro/disassembly-guided/2026-10-25/verify.py
```

Tool sources: [Blueshift](https://github.com/blueshift-gg/sbpf) provides assembly, disassembly and debugging. [sol-azy](https://github.com/FuzzingLabs/sol-azy) provides disassembly, control-flow graphs and static analysis; it was reviewed but not executed for this packet. [REA issue 2003](https://github.com/morluto/rea/issues/2003) is an open interface-recovery proposal whose initial scope explicitly excludes decompilation; it is not evidence of a completed Rust decompiler.

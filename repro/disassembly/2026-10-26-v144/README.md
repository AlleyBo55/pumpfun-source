# Byte-checked original disassembly, Linux v1.44

The four captured core programs were disassembled with the official Linux
platform-tools v1.44 `llvm-objdump` (LLVM 18.1.7-rust-dev). Every executable
file-section byte was checked against its listing. The independent checker
accepted all 4,460,640 executable bytes, with no missing, repeated, mutated,
unparsed, or `<unknown>` instruction rows. These are original-derived analytical
listings, not candidate compiler output or reconstructed programs.

| Program | Executable bytes | Instruction rows | Eight-byte slots | LDDW rows |
| --- | ---: | ---: | ---: | ---: |
| Pump | 1,792,208 | 215,873 | 224,026 | 8,153 |
| PumpSwap | 1,162,040 | 139,524 | 145,255 | 5,731 |
| Fees | 799,648 | 96,083 | 99,956 | 3,873 |
| Mayhem | 706,744 | 83,947 | 88,343 | 4,396 |

LLVM prints decimal SBF instruction-slot addresses. A sixteen-byte LDDW occupies
two slots but one listing row. The verifier checks those widths and addresses,
compares all raw bytes, and requires complete coverage of every executable file
section. It does not infer control-flow reachability or function boundaries and
does not independently validate LLVM's mnemonic/operand semantics.

`manifest.json` pins the official archive URL, length and SHA-256, the actual
decoder executable hash/version, the generator/checker source hashes, and every
original/listing hash. Its `script_sha256` entries record the contributor's
capture-time files at PR commit `38da1ab9`, when they lived at
`scripts/disassemble.py` and `scripts/verify_disassembly.py`. Before merge they
were moved, unchanged apart from import/root-path lines, to
`research/disassembly-coverage/disassemble_checked.py` and
`research/disassembly-coverage/verify_disassembly.py`. The original
`scripts/disassemble.py` stays byte-identical because saved checkpoints and
the P27 guard pin its SHA-256 and the exact `scripts/*.py` inventory. Original hashes agree with the existing
`evidence/disassembly-manifest.json`. Before/after hashes of the originals and
tool agree for the successful capture. Historical disassembly evidence is untouched.

To reproduce from a checkout, extract the pinned official archive into a separate
tool directory without changing its bytes, then choose a fresh output directory:

```sh
python3 research/disassembly-coverage/disassemble_checked.py \
  --objdump /path/to/v1.44/llvm/bin/llvm-objdump --output work/disassembly-v144-new
python3 research/disassembly-coverage/verify_disassembly.py \
  evidence/original/pump/deployed.so work/disassembly-v144-new/pump.asm
python3 research/disassembly-coverage/test_disassembly.py
```

The generator uses repository-relative binary arguments, so checkout root paths
do not enter the listings. Regenerated output hashes can be compared with the
manifest. The large listings are reproducible and are not duplicated in this
packet. No source reconstruction, candidate binary, accepted handler count,
runtime coverage, historical compiler attribution, or whole-file identity status
is changed by this checkpoint. Core binary identity remains 0/4.

## Second-host recapture (maintainer merge review)

`review-recapture-darwin.json` records a recapture made with the relocated
generator and the darwin arm64 platform-tools v1.44 `llvm-objdump`. That decoder
is also LLVM 18.1.7-rust-dev, but its executable hash differs (`24f83fd4…` vs
`e2a1dc7f…`). All four listing SHA-256 values and all per-section coverage
counts equal the Linux checkpoint. `llvm-readelf -S` independently gives the
same single `.text` executable section sizes, which sum to 4,460,640 bytes.
The 20 regression tests are not run by CI, because adding them to `verify.yml`
would change a pinned workflow. Run them manually as above.

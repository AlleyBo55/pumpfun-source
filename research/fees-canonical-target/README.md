# Fees: recover raw type-ID bodies with the canonical v1.44 target

The v1.44 bundle includes separate standard libraries for the legacy `sbf-solana-solana` and canonical `sbpf-solana-solana` target names. Building the fixed source control with the canonical target reproduces **all four candidate `type_id` instruction bodies exactly in the original**, including every scalar constant. The legacy target matches none. Three identical bodies correspond to three original windows, so their address attribution remains ambiguous; the fourth adds a unique raw match at original 767336. Candidate symbols do not recover historical Rust type names.

| Source/build profile | Candidate windows | Unique structural pairs | Unmatched original windows | Raw type-ID bodies with original matches |
| --- | ---: | ---: | ---: | ---: |
| Fixed control, v1.44 legacy | 582 | 320 | 121 | 0/4 |
| Same control, v1.44 canonical | 582 | 321 | 117 | 4/4 |
| Same control, v1.52 legacy | 573 | 38 | 475 | 0/2 |
| Latest source, v1.44 legacy | 582 | 337 | 104 | 0/4 |
| Same latest source, v1.44 canonical | 582 | 338 | 100 | 4/4 |

Each control family fixes all 26 source input hashes. The v1.44 compiler executable is unchanged between target profiles. Legacy profiles use the recorded driver; canonical profiles use direct Cargo with explicit compiler, target and remapping flags. The v1.52 build emits only two `type_id` functions, hence 0/2. Every source override and every profile's build log is retained. Launch and result records under `builds/` exist for the canonical and v1.52 profiles. The latest-legacy record keeps only its command and exit code, and control-legacy, the earlier v1.44 legacy build of the same control source, has its log but no `builds/` record. The two target-spec JSON objects are identical; selecting a target name still selects a distinct prebuilt sysroot. This identifies a matching compiler/sysroot context among the tested profiles, not a unique historical build or source.

All five outputs share the original's `e_machine=263` and `e_flags=0`. Thus those fields alone do not impose an upper bound at v1.46.1: the tested v1.52 profile has the same header fields while differing extensively in its code. Its 10,838 query cases pass, illustrating why behavior, headers and raw identity must be assessed separately.

The latest canonical build passes **17,331 cases across 18 suites**, as does its exact-source legacy control. It preserves all earlier unique structural pairs and adds the one unique type-ID body plus the three ambiguous raw bodies. The canonical sysroot also makes one existing structural pair raw-identical: compiler_builtins `__muldf3` at original 797048. Raw-equal unique pairs therefore rise from 54 to 56 (767336 and 797048), with none lost. The latest map has 338 unique pairs, 44 ambiguous groups containing 147 original windows, and 100 unmatched originals. Only 56 unique pairs are raw-byte identical. Neither the whole compiler ELF nor the captured allocation matches; core raw identity remains **0/4**.

## Verify and rebuild

```sh
python3 research/fees-canonical-target/verify.py
python3 -I research/fees-canonical-target/verify.py
python3 research/fees-canonical-target/map_windows.py
```

The checker binds every retained ELF and complete stripped/unstripped `.text`, recovers candidate boundaries exactly against each symbol table, checks all 26 source inputs and 187 unchanged harness files, recomputes the full comparisons and unmasked type-ID bodies, and validates all three behavioral receipts. Structural signatures retain opcodes, registers, branch/stack offsets and scalar literals, masking only local CALL immediate words and actual relocated LDDW values. Import names and relocation offsets remain in signatures; opaque data and callee bodies are not proven equivalent by them. Runtime suites do not assert identical logs, compute or exhaustive semantics.

At the source revision in `experiment.json`, apply the selected overrides in a separate workspace. Follow the retained `builds/` commands for the canonical profiles; use `--target sbpf-solana-solana`, the pinned v1.44 Cargo/rustc, and `RUSTFLAGS=-Zremap-cwd-prefix=`. Preserve the unstripped output and use the pinned v1.52 `llvm-objcopy --strip-all`. Every profile builds the same locked crate set offline. The legacy profiles reuse the prior clean baseline target directory. control-canonical compiled all 176 crates in a fresh canonical-target directory, which latest-canonical then reused. The v1.52 profile compiled in its own fresh target directory.

The newer probe initially encountered a truncated installed compiler library and Cargo's changed offline-cache namespace. The tool bundle's 3,198 regular files were checked against its SHA-pinned archive and three installed files repaired before the successful build. Offline index/cache/source aliases point to the same previously verified locked crate contents. Repair and alias receipts are retained. These installation repairs do not alter the pinned strip executable. Logs and hashes are not an authenticated process trace.

Selected sources/candidates, checkpoint ledgers, pinned scripts and workflows are unchanged. The latest source includes the preceding research overrides, with their discriminator-free unchecked-input compatibility limit, independently of their merge status.

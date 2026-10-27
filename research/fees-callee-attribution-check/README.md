# Fees first-account callee-identity check (reconciling #42 layout with #74 callee)

This packet independently re-derives, from the pinned ELF bytes alone, the callee
claim of [PR #74](https://github.com/lalalune/pumpfun-source/pull/74)
(`research/fees-account-parser`, by shawkkkkk) and reconciles it with the merged
first-account-boundary report (#42). The two reports do not conflict: #74 reads
the selected candidate (`2387f813…`), while every candidate byte receipt in #42
was read from a different binary, the Linux current-source build
(`6c44d9f2…`), at addresses that mark the selected candidate's wrappers but not
that build's wrappers. See the review correction below.

## What #42 and #74 each examined

- **#42 (layout, historical report):** the report named its candidate sites
  A/B/C by the selected-candidate wrapper addresses retained by pass 36
  (83,152 / 83,352 / 83,552; pass 36's retained candidate window
  `[127336, 129120)` has raw SHA-256 `492ae4b3…`, which matches the selected
  candidate and not the Linux build), but read the bytes at and after those sites from
  `repro/pump_fees/linux-current-source-build/fees-current-linux-v144.so`. The
  merged #42 README (maintainer review) already withdrew its `7a`
  returned-value reading and leaves its niche/type conclusions and site
  attribution unverified. At the Linux-build bytes it read, two stores decode
  as follows (superseding the historical `stxdw [r6+0],r0` /
  `stw [r6+0x104],r2` wording, which misread two store-immediate opcodes):
  - **83,480 in the Linux build: `stdw [r6+0],0`** — opcode `0x7a`, a
    compile-time **immediate** dword zero, not the constructor's returned `r0`.
  - **83,664 in the Linux build: `stb [r6+260],2`** — opcode `0x72`, a
    store-immediate **byte** 2 at offset `0x104` (260), not a 4-byte register
    store.

  These are correct readings of those Linux-build bytes. They are not stores
  inside the selected candidate's wrappers B and C (see below).
- **#74 (callee identity):** in the selected candidate, after masking CALL
  immediates all three candidate wrappers equal the original wrapper; their
  **encoded callees** distinguish them. Only the wrapper the candidate query's
  first CALL reaches (site 83,552, helper CALL target 26,680) has a callee
  carrying the `FeeConfig` account discriminator `8f3492bbdb7b4c9b` (lddw
  immediate at 27,320), as the original helper (CALL target 36,072, literal at
  36,696) does. Candidate A (35,856) and B (30,752) helpers lack the literal.

## Reconciliation (corrected in review)

| | Selected candidate `2387f813…` (#74) | Linux build `6c44d9f2…` (#42 receipts) |
| --- | --- | --- |
| Query first CALL at 127,384 reaches | 83,552 | 82,232 |
| 200-byte windows equal to original wrapper 71,256 after masking only CALL immediates | 83,152; 83,352; 83,552 | 82,232; 82,800; 83,184 |
| Wrapper whose helper carries the FeeConfig discriminator | 83,552 → 26,680 (lddw at 27,320) | 82,232 → 28,728 (lddw at 29,368) |

In the Linux build, #42's sites A/B/C are CALL instructions at 83,168, 83,368
and 83,552, each followed by `exit`. Their fallthroughs are, respectively, the
200-byte wrapper at 83,184 (helper 33,840, no FeeConfig discriminator) and the
starts of two other functions at 83,384 and 83,568. Neither of those two windows
equals the original wrapper after CALL masking, and both store sites above
(83,480 and 83,664) lie outside all three Linux-build wrappers. The reviewer
also read the identical Linux build's symbol ELF
(`research/fees-guard-experiment/artifacts/baseline-symbols.so.gz`, whose
`.text` equals the stripped build): the functions at 83,384 and 83,568 are
184-byte `Account<T>::try_accounts` instances, not 200-byte wrappers.
`verify.py` checks everything in this paragraph except those symbol extents.

So #42's "A matches the original layout" reflects that A's fallthrough happens
to be a 200-byte wrapper in the Linux build, and "B and C differ" reflects that
their fallthroughs are different functions. Within the selected candidate all
three wrappers are identical to each other and to the original after CALL
masking, so #74's wrappers B and C have **no** Err-construction difference. An
earlier version of this README equated the two label sets and wrote "Layout
(#42) points at A; callee identity (#74) points at C" and that the B/C
differences "describe which wrapper each candidate pairs with its layout story".
That comparison crossed binaries and is withdrawn.

**Attribution follows the callee in both builds.** Read with the corrected
local-CALL arithmetic (`target = call + 8 + 8·imm32`, per Anza `sbpf`
`elf.rs`/`ebpf.rs`, the same fix #42's review applies), the query's first CALL
reaches the only wrapper whose helper carries the original's FeeConfig
discriminator: 83,552 → 26,680 in the selected candidate and 82,232 → 28,728 in
the Linux build. Encoded CALL targets remain static evidence, not a
loader/runtime proof, and no parser equivalence is claimed here.

## Verification

```sh
python3 -B verify.py
```

Recomputes every claim from the three pinned inputs (hashes below), using only
the standard library and the repo's pinned `scripts/analyze.py` ELF layout
reader: query first-CALL targets, wrapper helper CALL targets, lddw
discriminator sites, and the corrected store opcodes. For both candidate builds
it also locates every 200-byte window equal to the original wrapper after
masking only CALL immediates, confirms which one the query's first CALL reaches
and which helper carries the discriminator, and checks that #42's Linux-build
sites are CALL/`exit` pairs whose store sites lie outside those wrappers. It also re-checks
every saved REA receipt: each names a provider, a pinned subject digest, an
address and a length, and the bytes must match what that binary holds there.
Passes with `python3 -I` from another cwd. No execution, and no new claim
about parser equivalence; attribution evidence only.

## REA evidence

All binary bytes below were read through REA MCP (Ghidra 12.1.4 headless,
raw-binary import, `architecture=x86_64`, `entry_point=0x0`), one session per
binary, each read against the binary that owns the site.

| evidence_id | binary | read | shows |
| --- | --- | --- | --- |
| `ev_2e9537ce…` | original | `0x7eb70` 8B | query first CALL, imm −55972 |
| `ev_d3f0afd3…` | original | `0x11710` 8B | wrapper helper CALL → 36,072 |
| `ev_fbd3391a…` | original | `0x8ce8` 16B | original helper entry |
| `ev_7287fd7b…` | original | `0x8f58` 16B | FeeConfig discriminator lddw at 36,696 |
| `ev_d7278a47…` | original | `0x11648` 32B | original boundary CALL/`exit` + start of wrapper 71,256 |
| `ev_8a53568f…` | candidate | `0x1f198` 8B | query first CALL, imm −5480 |
| `ev_411683f8…` | candidate | `0x144d0` 208B | wrapper A whole region |
| `ev_65d40552…` | candidate | `0x14508` 8B | wrapper A error-path CALL |
| `ev_0733f6d8…` | candidate | `0x14588` 8B | wrapper A helper CALL → 35,856 |
| `ev_01db52bf…` | candidate | `0x145d0` 8B | wrapper B error-path CALL |
| `ev_b3852530…` | candidate | `0x14650` 8B | wrapper B helper CALL → 30,752 |
| `ev_dfc7cd50…` | candidate | `0x14698` 8B | wrapper C error-path CALL |
| `ev_058da4b5…` | candidate | `0x14718` 8B | wrapper C helper CALL → 26,680 |
| `ev_29133724…` | candidate | `0x8c10` 32B | helper A entry, no discriminator lddw |
| `ev_8c2de45e…` | candidate | `0x7820` 32B | helper B entry, no discriminator lddw |
| `ev_0d28b400…` | candidate | `0x6838` 32B | helper C entry |
| `ev_259a5be2…` | candidate | `0x6ab8` 16B | FeeConfig discriminator lddw at 27,320 |
| `ev_3f60b3c4…` | linux-v144 | `0x14618` 8B | `7a06000000000000` = `stdw [r6+0],0`, after #42 site B; not in a wrapper |
| `ev_3863850f…` | linux-v144 | `0x146d0` 8B | `7206040102000000` = `stb [r6+260],2`, after #42 site C; not in a wrapper |

Full receipts, with parameters and subject digests, are in `rea-evidence/`.
Raw instruction decoding at these sites is unavailable in this provider build
(`inspect_native_instruction` reports `undecodable`/`data` for raw-binary
imports), so `verify.py` derives the encodings from the same bytes; the
opcode/mnemonic reading is asserted in the checker, not taken on trust.


Pins (sha256):

| Input | sha256 |
| --- | --- |
| `evidence/original/pump_fees/deployed.so` | `4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e` |
| `repro/pump_fees/sharing-authorize-main-v144/main/candidate.so` | `2387f8139a13918a5c9c523f140ecdd72db7243c8e2ed9cd7e1ff9d42ad6c8af` |
| `repro/pump_fees/linux-current-source-build/fees-current-linux-v144.so` | `6c44d9f2ffe9b18c79a6344b256d8acd7a34c10e77b894c51f46512a447b8ce6` |

`saved-raw-reads.json` records the raw bytes at each proof site (CALL immediates,
lddw discriminator loads, the two Linux-build store instructions) with the input hashes; the
checker re-derives every value from the binaries, so the JSON is a receipt, not
an input.

Credit: callee-identity observation and candidate-numbering scheme are from
PR #74 (shawkkkkk). The corrected CALL encoding and the `0x7a` store reading
follow the maintainer's review corrections on the merged boundary packet.

## Review correction (2026-10-26)

The submitted reconciliation treated #42's sites A/B/C as the same three
functions as #74's selected-candidate wrappers. They are not: #42's candidate
receipts come from the Linux build, where the selected candidate's wrapper
addresses fall at CALL/`exit` pairs before other functions. The reconciliation
section above, the evidence-table labels, the wrapper A/B call-site labels in
`saved-raw-reads.json` (83,336 and 83,536 are helper CALLs; the error-path
CALLs are 83,208 and 83,408), and the `verify.py` checks were corrected in
review. The callee-identity reproduction of #74 is unchanged.

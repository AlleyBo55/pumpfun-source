# First-account boundary: retained observations and corrected verifier scope

This additive packet retains the author's REA receipts and initial report for
Fees first-account admission. It changes no program source, fixture, selected
artifact or identity status. The original report/verifier/manifest are retained
byte-for-byte under `history/`; their call targets and layout interpretation are
historical claims, not current verified conclusions. `history/verify.py` is kept
unchanged and does not pass from its new location: its manifest expects
`rea-evidence/` beside it, and its repo mode reads a fork remote.

## Review corrections

The original `resolve_call` added a signed instruction immediate directly to a
byte offset. On-disk local CALL targets instead use the next instruction plus
an immediate measured in eight-byte instruction units:

`target_file_offset = call_file_offset + 8 + 8 * signed_imm32`

This follows the primary Anza implementation: [elf.rs PC-relative CALL fixup](https://github.com/anza-xyz/sbpf/blob/main/src/elf.rs)
uses instruction index `i + 1 + imm`, and [ebpf.rs](https://github.com/anza-xyz/sbpf/blob/main/src/ebpf.rs)
defines the instruction size as 8 bytes. The historical numeric call-target lists are
withdrawn. No original body was inspected to replace them during this review.
Only explicit future binary-input invocation computes local targets. Syscall
hashes, relocated runtime calls and original-to-candidate attribution remain
outside that calculation.

The prior report also described bytes beginning `7a` as a register store of
returned `r0`. In the retained instruction set, `0x7a` is a store-immediate;
`0x7b` is a store-register. The literal `7a06000000000000` in the historical
verifier therefore cannot support its returned-value interpretation. That
interpretation is withdrawn. The reported Vec/String niche/type conclusions
and site attribution remain unverified; this packet does not infer a source
layout or repair the program from those claims.

## Verification

`python3 -B verify.py` checks the package inventory only. It performs no binary
reads, shape validation, signature check, native import or target execution.
It prints `PASS_PACKAGE_INVENTORY_ONLY`, not a body/call equivalence claim.
`python3 -B test_synthetic.py` tests local CALL arithmetic using invented bytes,
including signed backward offsets, next-PC scaling and external-call rejection.
These synthetic checks were run during review; no original decoding occurred.

Optional deliberate saved-byte verification requires both exact input files:

```sh
python3 -B verify.py --original /path/to/original-fees.so \
  --candidate /path/to/unrelocated-current-source-fees.so
```

This mode checks the original/candidate SHA256 pins retained in `verify.py`,
compares existing `read_bytes` receipt ranges, and computes local call targets.
It is not the default. It was run once during the maintainer merge review
(below). It does not discover new original bodies or follow call targets. Both explicit files are required; no
mutable fork remote/ref is assumed. Read/search receipts and mistaken earlier
observations remain unchanged in `rea-evidence/`.

The byte-range receipts alone do not prove parser ownership, Err layout, call
mapping, transitive behavior, source reconstruction or whole byte identity.
The original source function extent and first-account attribution remain open.

## Maintainer merge review run (2026-10-26)

The explicit mode was run with `evidence/original/pump_fees/deployed.so`
(`4f2955d0…`) and the candidate retained in the merged package
`repro/pump_fees/linux-current-source-build/fees-current-linux-v144.so`
(`6c44d9f2…`):

```sh
# from the repository root
python3 -B repro/pump_fees/first-account-boundary-admission/verify.py \
  --original evidence/original/pump_fees/deployed.so \
  --candidate repro/pump_fees/linux-current-source-build/fees-current-linux-v144.so
```

All seven saved `read_bytes` receipts matched the pinned inputs. The
local-CALL formula gives these file-offset targets:

| Site | CALL at | imm32 | Target |
| --- | --- | --- | --- |
| original | 71240 (`0x11648`) | -5015 | 31128 (`0x7998`) |
| candidate A | `0x144e0` | -6543 | 30832 (`0x7870`) |
| candidate B | `0x145a8` | -6192 | 33840 (`0x8430`) |
| candidate C | `0x14660` | -6087 | 34864 (`0x8830`) |

No callee body was read, so these targets do not attribute the original site
to any candidate. Receipt `ev_fc1cce98…` reads the original at `0x144e0`, which
is a candidate-site offset. Its bytes are unrelated original code and support
no site claim.

## Later cross-check (PR #82 review, 2026-10-26)

The candidate sites in the table above (`0x144d0` / `0x14598` / `0x14660`) are
the selected candidate's (`2387f813…`) wrapper addresses retained by pass 36,
but every candidate byte here was read from the Linux build (`6c44d9f2…`). In
that build the CALLs at `0x144e0` / `0x145a8` / `0x14660` are each followed by
`exit`; the three windows equal to original wrapper 71,256 after masking only
CALL immediates are 82,232 / 82,800 / 83,184, and the query's first CALL
reaches 82,232 (helper 28,728). These receipts therefore describe neither the
selected candidate's wrappers nor that build's first-account wrapper. See
`research/fees-callee-attribution-check/README.md` for the per-build table.

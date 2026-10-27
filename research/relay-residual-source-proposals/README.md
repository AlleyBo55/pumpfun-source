# Relay: historical independent source-hypothesis evidence

**These independently derived proposals are superseded by measured upstream
research.** [PR #112](https://github.com/lalalune/pumpfun-source/pull/112)
compiled the share-total compared-value correction and recovered window 4. It
also tested the proposed OR-operand reversal with **no recovered window**.
[PR #114](https://github.com/lalalune/pumpfun-source/pull/114) subsequently recovered
mint window 106 using a tuple zero predicate, not the OR-reversal proposal.

This packet preserves an independent static derivation against the historical
**470/492 normalized-window, 22-unmatched, 88-raw-local-match** input snapshot.
Its verifier deliberately checks that frozen snapshot; those numbers are **not
the current frontier**. The proposals were not built by this packet, but are no
longer untested globally. See the [current progress log](../../docs/BYTE-IDENTITY-PROGRESS.md)
for measured results. No selected source or original binary is changed here;
whole-binary identity remains false.

The inputs are the captured Relay, the retained unstripped **Token-2022 v8
research candidate** (`f4691718…`), and its immutable source predecessor plus
manifest overrides. `evidence.json` binds every input by SHA-256 and retains full
original/candidate bodies, exact mask locations, instruction differences, call
sites, and source-patch hashes. `verify.py` independently reads the ELF structures
and derives those observations using only Python's standard library.

## 1. Mint policy: reverse the transfer-fee OR operands

Original window **106**, at `115456`, and candidate `typed_mint_safe`, at `63472`,
now both occupy **3,440 bytes**. The v8 dependency change has removed the older
size mismatch. Only **three instructions / three bytes** differ after the existing
narrow direct-call and relocated-LDDW masks:

| Function-relative offset | Captured original | Retained candidate |
| --- | --- | --- |
| 1360 | `r1 \|= r2` | `r2 \|= r1` |
| 1368 | `r1 &= 65535` | `r2 &= 65535` |
| 1376 | branch if `r1 == 0` | branch if `r2 == 0` |

The preceding loads are identical: `r1` receives the older fee basis points
(offset 88), and `r2` the newer fee basis points (offset 106). The source currently
computes `older | newer`. The proposed `newer | older` retains the same ordinary
Rust value semantics and may alter the compiler's destructive-operand register
choice. The later framework/sysroot study tested this exact operand-reversal idea and
recorded no recovered window. This historical hypothesis is not a recovered
function or historical-source claim.

`proposals/mint-or-order.patch` is retained as the historical proposed negative
control, not a recommended next recovery step. Do not modify the sealed predecessor.

## 2. Share-sum error: restore compared values

Original window **4**, at `2184`, is a **1,352-byte** helper. Its instruction body
closely corresponds to candidate Anchor `Error::with_values` (eight differing
instructions), but stores a 32-bit first operand and the constant **10,000** in
adjacent 32-bit stack slots. The retained candidate helper takes two 64-bit
operands instead. This supports a missing `(u32, u32)` specialization with a
constant second operand; it does not recover an original symbol name.

All direct callers to original window 4 are the three share-distribution bodies:

| Original ordinal | Body start | Call offset |
| --- | ---: | ---: |
| 97, distribute after swap | 91880 | 2416 |
| 98, distribute without swap | 97096 | 3296 |
| 100, swap then distribute | 107240 | 1344 |

The reconstructed `admit_shares!` macro is used by exactly these handlers. It sums
basis points as `u32` and returns `BpsSumDoesNotEqualTenThousand` at
`programs/contracts/src/tools/checks.rs:204`, but currently omits compared values.
`proposals/shares-compared-values.patch` adds `.with_values((sum, 10_000u32))` to
that error without changing its condition, name, number, source location, or
successful path. This is a source-level diagnostic correction hypothesis with
strong static support. The later framework/sysroot study recovered window 4 with
`.with_values((sum,10000))`. Its unsuffixed literal differs from this packet's
explicit `u32` proposal, which is not claimed to have been compiled. The measured
source/build evidence supersedes the earlier hypothesis. Privileged-body runtime validation
is not established by this packet or the parent's rejection-oriented fixtures.

## Reproduce the static checks

From the repository root:

```sh
python3 -B research/relay-residual-source-proposals/verify.py
python3 -B research/relay-residual-source-proposals/test_verify.py
```

The tests check parser bounds, retain register/branch/constant differences, refuse
truncated instructions, distinguish external calls from masked direct calls,
check both patches, and rederive all saved evidence. They do not launch a compiler,
VM, network operation, or target-program instruction.

## Follow the measured frontier

Use the [framework/sysroot/share-error study](../../repro/donation-relay/framework-sysroot-recovery/README.md)
and [mint tuple-predicate recovery](../../repro/donation-relay/mint-fee-pair-recovery/README.md)
for source inputs, positive and negative builds, gains/losses, and finite replay
coverage. This packet adds an independent static cross-check, **not** an additional
reconstruction gain. Further experiments must begin from the current research
candidate and retain complete source-build provenance and raw whole-file comparison.

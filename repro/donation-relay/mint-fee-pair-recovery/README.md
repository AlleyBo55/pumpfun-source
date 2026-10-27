# Relay mint-fee predicate: 479 → 480 matched windows

The complete 3,440-byte original mint-policy window **106** now matches under the
existing call/relocation normalization. The candidate has **480/492 normalized
windows**, **127 raw local matches**, and **12 unmatched windows**, with no prior
match lost. All 536 records / 534 unique fixtures pass fresh signed replay and
reproduce the saved original observations. Whole-file byte identity remains false.

The source change is restricted to the transfer-fee zero test:

```rust
// Before
let fee_basis_points = older | newer;
if fee_basis_points != 0 { return Ok(false); }
// After
if (older, newer) != (0, 0) { return Ok(false); }
```

Both values are `u16`; both predicates reject exactly when either fee rate is
nonzero. The tuple form makes the compiler emit the captured register choices.
Only **three bytes** of the complete stripped output change: offsets 66185,
66193 and 66201. They are operand bytes for the OR, mask and conditional jump,
not modified binaries or masked discrepancies. Both outputs come from Rust
source builds. The exact change and the complete mint window are rederived by
the verifier.

The build retains the parent's explicit cross-host recipe: Darwin v1.48 Rust
compiler/linker with official Linux v1.48 target libraries and Anchor 0.32.
The [framework/sysroot parent](../framework-sysroot-recovery/README.md) retains
those tool/library inputs, dependency resolution and earlier negative controls.
A further serial-two-`if` control is retained here: it emits a 3,432-byte mint
function, so it cannot match this original window. No runtime claim is made for
that rejected control. The searched tuple variant was the first new matrix entry
and matched; no later planned variants were run.

Remaining windows are **90, 92–100, 109 and 112**: Jupiter construction, donation
and settlement handlers, residual burn/close, and the shared donation worker.
They still need complete source/codegen recovery. Matched windows do not settle
transitive data, indirect calls, privileged success paths or complete semantics.
Selected production sources and artifacts remain unchanged.

```sh
python3 -B repro/donation-relay/mint-fee-pair-recovery/verify.py
```

The checker reconstructs all 52 source-input hashes from the sealed parent plus
this single source override, rechecks both full ELF bodies, proves the exact
three-byte delta and single-window gain, and validates all retained replay
signatures, fixture bindings and observations. It does not execute the target
again. Build and search drivers retain the original scratch paths; use the
parent's source materializer and this `mint_policy.rs` override when rebuilding.

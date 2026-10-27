# Fees total predicate: isolated source-shape probe

The 192-byte original window at decimal address **700568** reads three u64s at
byte offsets 0, 8 and 16, aborts on either addition overflow, and returns whether
the sum is at most 10,000. An ordinary Rust predicate with overflow checks enabled
reproduces every instruction byte except two address-bearing operands: the panic
source-location pointer and the out-of-object panic call target. The verifier
checks the relocation records before excluding those operands.

This is an isolated compiler object, **not a new full-candidate match**. The
compiler is native Darwin platform-tools v1.44 (`rustc 1.79.0-dev`), not the
canonical Linux build. The probe does not establish the identity of the original
panic callee or source-location data. It proves neither whole-program behavior nor
authentic original Rust names. Its struct field names are a working interpretation.

Four encoded original calls reach this body, at 260600, 261224, 264056 and 268216.
The first two occur in currently unmatched 624-byte callers. The current source's
`validate_fees` instead combines checked-add/unwrap and the Anchor error result.
A useful next experiment is to split out this boolean predicate, call it from the
real validator, then build with the canonical Linux toolchain and replay the full
Fees corpus. Do not add an uncalled helper just to increase a match count.

Reproduction (substitute the local pinned v1.44 compiler path):

```sh
rustc research/fees-total-predicate-probe/fee_total.rs --crate-type lib \
  --target sbpf-solana-solana -C opt-level=3 -C overflow-checks=yes \
  -C panic=abort --emit=obj -o /tmp/fee_total.o
python3 -I -B research/fees-total-predicate-probe/verify.py
```

The retained compiler hash, command and object identify this actual probe.
Three in-memory mutations check that the verifier rejects changes to a field
load, overflow branch and comparison threshold. They do not modify captured data.

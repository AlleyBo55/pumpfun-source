# Shared donation arithmetic and evaluation-order controls

Six further compiled source variants leave Relay at **482/492 normalized
matches, 130 exact local bodies and ten unmatched windows**. None recovers the
original 10,248-byte shared donation worker. No source is promoted.

| Variant | Shared-worker bytes | Full normalized match |
| --- | ---: | --- |
| In-place checked addition | 10,336 | No |
| In-place subtraction and multiplication | 10,376 | No |
| All three operations in place | 10,376 | No |
| Named tip after state update | 10,328 | No |
| Named tip before state update | 10,328 | No |
| In-place addition plus named tip | 10,336 | No |

The in-place helpers return `Result<()>` and use the previously tested unit
error helper. They test the error/result representation while preserving checked
arithmetic behavior in ordinary Rust. The explicit inline annotations control
the experiment; historical source text is not claimed. The tip variants test
whether naming the division separately from the return struct changes the
observed evaluation order. Both tip-only variants reproduce the preceding
candidate and symbols exactly: the compiler removes that source distinction.

The complete binary inventory gains or loses no matched window in any variant.
The result is bounded to these source forms and the tested compiler/library
recipe. It does not establish that all arithmetic implementations or source
orders are equivalent, nor does it prove semantic perfection.

Each build retains its 56-input map, exact modified sources, root compiler log,
source-unchanged check and content-addressed binaries. `report.json` records the
worker hashes/sizes, helper comparisons and full-inventory results.

```sh
python3 -B repro/donation-relay/arithmetic-order-controls/verify.py
python3 -I -B repro/donation-relay/arithmetic-order-controls/verify.py
python3 -B repro/donation-relay/arithmetic-order-controls/verify.py \
  --materialize /tmp/relay-arithmetic --variant checked-assign-add
```

The verifier uses only the standard library and does not compile or run the
program. These rejected variants have no new runtime acceptance. The existing
checkpoint retains its independently recorded bounded replay evidence. All
builds here use the Darwin v1.48 compiler and Linux v1.48 target libraries.

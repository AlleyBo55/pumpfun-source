# Relay: recover the complete burn/close helper

Moving the mint account into the nonzero burn, and fully destructuring the input
context, recovers **all 2,856 bytes of original window 109 after the existing
CALL/relocation normalization**. Both compiler recipes reach **482/492 normalized
windows**, **130 raw local matches**, and **10 unmatched windows**, with no lost
match. Whole-file identity remains false.

## Ownership was the missing distinction

The previous helper cloned the mint before burning. That left an extra owned
mint reference to drop after the CPI. The captured code instead consumes it in
the nonzero branch; the zero-amount branch retains it for cleanup. The recovered
source expresses this ownership directly:

```rust
let BurnCloseContext { token, mint, authority, destination, program } = ctx;
if amount != 0 {
    // Burn receives `mint`, not `mint.clone()`.
    // Token, authority and program are cloned because close still needs them.
}
// Close consumes token, authority, destination and program.
```

Merely removing the mint clone gets the helper to the correct size but leaves
15 normalized instruction slots unequal. Fully destructuring the context also
recovers the cleanup/return layout. No register, instruction, binary or returned
artifact is patched. This is reconstructed Rust source, not proof of unique
historical source text.

The verifier checks the complete body and independently binds all **24 direct
call sites** to complete normalized-matched callees. Referenced data, indirect
behavior, historical provenance and exhaustive semantics remain separate from
this body-level result.

## Builds and execution

| Build | Normalized matches | Unmatched | Raw local matches | Fresh replay |
| --- | ---: | ---: | ---: | ---: |
| Darwin compiler with Linux target libraries | 482 | 10 | 130 | 536 records / 534 unique fixtures |
| Full Linux compiler | 482 | 10 | 130 | 536 records / 534 unique fixtures |

The recovered candidates are each **818,096 bytes**:

- Darwin/Linux libraries: `1eaf3af16fdafdfa9d2ca47e88c07a7f15f13b88aa57df1f63c655c10a1616e2`.
- Full Linux: `c6ae09b906b3c6a88042e40b02e0a2f6598268061d7527b667c0e631655a3921`.

All **348** previously audited source-location pairs remain equal. The source
inputs are identical across the recovered builds. Both build logs record an
actual root-crate rustc invocation with the established official v1.48 SDK
recipe. Logs/hashes are retained evidence, not authenticated process traces.

The fresh replay uses the unchanged bounded corpus. It does not claim new
privileged burn/close success coverage, all allocation failures or exhaustive
account-lifecycle equivalence. The negative variants have static/build evidence
only and are not proposed checkpoints.

## Negative controls and remaining work

The packet retains **46 builds**: 36 unsuccessful epoch-close experiments,
eight unsuccessful mint-move variants, and two recovered builds. Epoch-close
controls vary validated epoch value sources, initialization form, overflow
handling, seed-array types and CPI construction. They add no accepted epoch-close
match. Their sizes and full inventories are retained rather than substituting
size or fuzzy similarity for a match.

The source-only change from the 481-window parent is confined to the burn/close
helper in `src/settlement_handlers.rs`. Full input hashes, all source snapshots,
content-addressed artifacts and negative controls are in `metadata.json`, with
recomputed inventories in `report.json`. Whitespace-bearing source snapshots
are compressed to preserve their exact compiled bytes.

Remaining original ordinals: **92–100 and 112**. These are donation/settlement
business bodies, including epoch close, and the shared donation worker. Selected
program sources and selected artifacts remain unchanged.

## Verify or materialize

```sh
python3 -B repro/donation-relay/burn-mint-ownership-recovery/verify.py
python3 -B repro/donation-relay/burn-mint-ownership-recovery/verify.py \
  --materialize /tmp/relay-burn-owned --variant recovered
```

Verification requires the parent's local-VM dependencies, including `solders`.
It rechecks package/parent hashes, exact source transformations, all build inputs,
full instruction windows, call targets, location pairs and retained runtime
bindings. It does not run new compilations or transactions. The controllers and
launch records retain the two build recipes; adjust source/output paths when
rebuilding. Original executable bytes remain comparison inputs only.

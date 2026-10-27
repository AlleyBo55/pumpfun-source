# Relay: recover the complete Jupiter optional-seed builder

The complete **2,496-byte original window 90** at address **64,824** now matches
under the unchanged CALL/relocation normalization. Both the Darwin compiler with
Linux target libraries and the full Linux compiler build reach **481/492 matched
windows**, **130 raw local matches**, and **11 unmatched**. No prior normalized
window is lost. Whole-file identity remains false.

## What the remaining four instructions meant

The [previous near-match](../residual-cpi-source-trials/README.md) recovered the
account-vector allocation by changing `remaining.to_vec()` to iterator cloning.
Four stack load/store instruction slots still differed. They were not merely
interchangeable spills: the original tests the incoming optional slice's
**pointer**, while the reconstruction's `is_empty()` tests its **length**.

The recovered ordinary Rust source uses:

```rust
seeds: Option<&[&[&[u8]]]>
// ...
match seeds {
    Some(seeds) => invoke_signed(&ix, &infos, seeds)?,
    None => invoke(&ix, &infos)?,
}
```

The existing caller passes `Some(seeds)`. `None` and `Some(&[])` are distinct:
the former selects unsigned invocation, while the latter selects the signed
wrapper with an empty seed slice. This source type and branch structure reproduce
the original code; no executable is patched. Historical comments, identifiers
and the unique original source text are not established.

The verifier decodes the actual incoming-pointer load, stack stores and branch
at offsets 80, 88, 96, 1,400 and 1,408. It checks the **entire** window, not just
these instructions, and resolves all **11 direct-call sites** to complete matched
callees. All 346 previously audited source-location pairs remain equal; the newly matched
Jupiter body adds two equal pairs, giving **348/348**. This bounded cohort is not
all-data identity. Raw call destinations, other referenced data, indirect behavior and
exhaustive semantics remain separate obligations.

## Controlled builds

| Source / build | Normalized windows | Window 90 | Fresh replay |
| --- | ---: | --- | --- |
| Prior iterator-clone control, full Linux | 480 | Four instruction slots differ | 536 records |
| Optional seeds expressed with `if let`, Darwin/Linux libraries | 480 | Different control-flow layout | Not claimed |
| **Optional seeds expressed with `match`, Darwin/Linux libraries** | **481** | **Complete normalized match** | **536 records** |
| **Same 56 source inputs, full Linux build** | **481** | **Complete normalized match** | **536 records** |

The two recovered candidates are each **818,176 bytes**:

- Darwin compiler / Linux libraries: `ad97298ee51c3f585f6cc4012826be33a8d6fa835d9483aa8f67ce041382b6e2`.
- Full Linux compiler: `1bef9843beac4c9c8dd2158d014840a1b65a4fdd1d726ac7ee1f1e975a9b6587`.

Each differs from its corresponding iterator-clone control at exactly **ten
positions** in the stripped file. Those ten bytes are the four previously
unmatched instruction slots. Equal frontier counts do not imply equal files
across build hosts.

Nineteen additional account-metadata construction trials are retained as
negative evidence. Field-order permutations retain the near-match; moving the
closure capture or using key-copy methods changes code generation without
recovering the body. All retain 480 matches. They have no claimed fresh runtime
validation in this packet.

## Runtime and source/build scope

The Linux iterator control and both recovered candidates each pass fresh
**536-record / 534-unique-fixture** replay with the unchanged comparator. These
are existing bounded fixtures, not new privileged Jupiter success coverage.
The `None` versus `Some(empty)` reconstruction is supported by source/operand
and full-window evidence; this packet does not claim a new end-to-end privileged
transaction exercising both paths.

All 56 source inputs are bound by SHA-256. The only changed source file relative
to the combined location-recovery source is `src/settlement_handlers.rs`. Build
logs include an actual root-crate compiler invocation and unchanged-source
checks. The full Linux SDK is the previously verified official v1.48 archive;
this packet retains the current compiler/tool hashes and container image.
Logs and hashes are retained evidence, not authenticated process traces.

## Verify and materialize

```sh
python3 -B repro/donation-relay/jupiter-option-source-recovery/verify.py
python3 -B repro/donation-relay/jupiter-option-source-recovery/verify.py \
  --materialize /tmp/relay-jupiter-option --variant option-match
```

The verifier requires the parent's installed local-VM dependencies, including
`solders`. It rechecks parent/package hashes, exact source transformations,
23 build variants, all original window correspondences, the branch operands,
direct callees and retained replay bindings. It does not compile or run new VM
transactions. The controllers and recorded launch commands retain the build
recipes; adjust source/output paths for a fresh build. Original executable bytes
are comparison inputs only.

The remaining original ordinals are **92–100, 109 and 112**: donation and
settlement business bodies, burn/close and the shared donation worker. Selected
program sources and selected artifacts are unchanged.

# Fees total predicate: full Linux integration

Connecting the three-field fee-total predicate to the real validator recovers
original window **700568 (192 bytes)**. Both source forms gain exactly this
complete normalized body, with no previous body lost: **357 unique structural
pairs, 81 unmatched original windows, 58 unique raw-equal pairs**. The original
still has 585 inferred windows. This is a research checkpoint, not a selected
program or whole-ELF identity claim.

| Build | Unique pairs | Unmatched | Candidate bytes |
| --- | ---: | ---: | ---: |
| Rebuilt PR #140 control | 356 | 82 | 854,672 |
| Predicate in existing root module | 357 | 81 | 854,640 |
| Predicate with recovered source location | 357 | 81 | 854,672 |

The control reproduces the published stripped and symbol-bearing binaries
byte for byte. All three use the unchanged official Linux platform-tools v1.44
compiler, canonical `sbpf-solana-solana`, the frozen Cargo lock and v1.52 strip.
The compiler archive SHA-256 is checked and 30 compiler/linker/target-library
inputs are recorded. Each accepted build log contains the actual root compiler
invocation, and each source snapshot is checked before/after compilation.

The first attempted control lacked the host `cc` linker. After installing host
build dependencies, the control succeeded. A first predicate attempt reused the
shared Cargo cache without invoking rustc; it is explicitly excluded. Touching
the changed root source forced the successful invocation. Both diagnostic logs
are retained; no result is inferred from the cached attempt.

## What the source-location recovery establishes

The original overflow location encodes `pump-fees-math/src/lib.rs:28:9`, and its
reachable 88-byte panic leaf constructs `attempt to add with overflow`. The
preferred `origins` variant puts an ordinary `Fees::is_valid` method at that
source location and applies root-crate path remaps. The existing validator calls
it. The helper's normalized body, reachable panic leaf's normalized body,
filename, line, column and panic message agree with the original. The first
root-module variant matches the helper body but not its source coordinates.

The method name is a reconstruction choice; the embedded file/line/column are
binary evidence. This does not reconstruct the original crate boundary. The
original helper has four incoming calls, while this candidate has one through
`validate_fees`. Its surrounding callers still differ. A matched helper and
panic leaf do not prove all transitive runtime, data or indirect-call identity.

## Runtime checks and remaining work

Both proposals were freshly replayed against the original across **17,331 cases
in 18 existing suites**, plus **1,542 exact outcome/log/compute comparisons**.
The broad suites retain their own compared-field and coverage limits; a pass
does not mean every log or compute count agrees. `diagnostic-cases.json` separately
records every replayed case with the original math-overflow diagnostic and checks
its exact recovery by the source-location variant. Full receipts are retained.

No selected sources, checkpoint pins or captured bytes change. Continue with
the original callers at 260568, 261192, 261816 and 265976, and the remaining
configuration/ownership bodies. The first two callers copy fields into offsets
80/88/96 and 104/112/120 after validation; their error origins point to
`programs/pump-fees/src/state.rs` at lines 365 and 372. Those observations guide
future source work but do not establish recovered callers.

```sh
python3 -B research/fees-total-predicate-integration/verify.py
python3 -I -B research/fees-total-predicate-integration/verify.py
python3 -B research/fees-total-predicate-integration/test_scope.py
```

`experiment.json` maps every input to its retained source or immutable parent
path. To rebuild, materialize each map into a separate workspace and use its
recorded `builds/*-launch.json` command/environment with local container paths.
`recorded-build-driver.py` is the executed scratch driver, not a turnkey installer.
No compiler is required to verify the retained packet.

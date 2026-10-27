# Common zero-quote predicate recovery

A reconstructed shared Rust helper now reproduces the **complete 504-byte
original window at 75,880**, without losing a normalized or raw match. Fees
advances to **376 unique structural pairs / 62 unmatched original windows**.

The helper returns true for account data shorter than 115 bytes, otherwise
compares the 32 bytes at offsets 83–114 with a default pubkey. It preserves the
infallible `RefCell::borrow()` behavior, including the borrow-conflict panic.
The recovered form uses `Pubkey::try_from_slice`, the Borsh deserialization API.
This identifies a reproducing source expression; it does not authenticate the
original historical Rust spelling.

## Source controls and complete comparison

The prior helper was inlined from `sharing_update.rs`. All three new source
controls move it to `common/mod.rs`, call it from the existing legacy/V2
fee-sharing paths, and use `#[inline(never)]` to retain the separately compared
body. The original helper's two recorded panic references identify this path.
Existing source line counts are preserved, with the recovered expression at
line 21, column 48 for the borrow and column 56 for bounds checking.

| Expression | Compiled helper bytes | Complete original match |
| --- | ---: | --- |
| Array conversion + `Pubkey::new_from_array` | 432 | No |
| `Pubkey::try_from` | 432 | No; same compiled candidate as array form |
| `Pubkey::try_from_slice` | 504 | Yes, normalized |

All four direct local callee bodies match. Both referenced source-location
records match path, line and column, beyond simply masking their pointers.
The two real candidate callers are retained in `analysis.json.gz`; their full
caller bodies remain unresolved. No unused synthetic helper or binary patch
is introduced.

## Build and runtime scope

The parent is `research/fees-crank-interface-mint`. Its 35 source inputs are
hash-checked. The new variants each have 36 inputs: the root module declaration,
helper extraction/call-site updates, and new common module are the only changes.
Each control has a fresh pinned Linux v1.44 root compilation and retained log.
The parent binary is explicitly reused rather than called a new build.

Recovered candidate: 860,008 bytes, SHA-256
`e35c745fe8238ef4199a6e23cf449b3c42767bf7db9df26ded77b8339275479a`.

Fresh regressions cover 17,331 suite comparisons, 1,542 exact outcome/log/compute
cases and the retained 24 growth, 32 optional, 20 user-ID, 8 extension-log and
30 crank-mint cases. They preserve each harness's observation limits. The
negative array/conversion controls are not promoted or newly runtime-accepted.
No exhaustive behavior, allocator-failure coverage or whole-file identity is
claimed.

The current full partition is **118 raw-local / 405 normalized-only / 62
unmatched**. Incoming-call refinement yields 437 correspondences: 376 unique
plus 61 additional attributed duplicates; 86 duplicates remain unattributed.
Unmatched original windows span 318,016 / 799,648 text bytes (39.8%). Selected
program/source checkpoints are unchanged.

Run `python3 -B research/fees-curve-zero-helper/verify.py` to recompute source,
build, full-body, direct-callee, location and receipt checks. It does not compile
or execute target programs. Exact source maps and the recorded build driver
retain the inputs for a fresh reproduction.

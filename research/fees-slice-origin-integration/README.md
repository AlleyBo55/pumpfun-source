# Integrate four slice-panic locations into the current Fees candidate

The four source-location corrections from `fees-slice-origin-contract` are now
applied to the newer 376-pair research source, including the intervening account
ownership, seed-vector, formatting and common-helper recoveries.

Only whitespace in `src/state.rs` changes. Two `clone_from_slice` statements
move from lines 393/446 to 398/451 and four columns to the right. Their token
sequences and all other 35 input files remain unchanged. No artifact is patched.
A fresh Linux v1.44 compilation differs from its explicitly reused current
parent at **exactly eight bytes**, all belonging to the four location records
in `.data.rel.ro`. The entire `.text` section remains raw-byte identical.

| Original caller | Failure path | Matched source location |
| --- | --- | --- |
| 261,816 | Slice range | `programs/pump-fees/src/state.rs:398:19` |
| 261,816 | Source/destination slice-length mismatch | `programs/pump-fees/src/state.rs:398:33` |
| 265,976 | Slice range | `programs/pump-fees/src/state.rs:451:19` |
| 265,976 | Source/destination slice-length mismatch | `programs/pump-fees/src/state.rs:451:33` |

The checker reuses the previously reviewed contract reader against the actual
current artifacts. It follows each location LDDW and encoded caller target,
checks the range stub and its next target, and checks the length-mismatch
helper's three message pieces, formatter and panic callee. Three mutation tests
verify that source-column changes, message changes and masked call retargeting
are rejected even where normalized instructions remain equal.

## Result and scope

- **376 unique pairs, 147 ambiguous originals, 62 unmatched windows:** unchanged.
- **118 raw-local / 405 normalized-only / 62 unmatched:** unchanged.
- **437 attributed correspondences**, including 61 additional duplicates: unchanged.
- Existing normalized/body, call and runtime gains are preserved; zero new body matches.
- Original whole-file equality remains false; selected checkpoints are unchanged.

Candidate: 860,008 bytes, SHA-256
`c888a57d7270cd9d33af57695a4b1a735a5730941a5369101ab6dbb1f96c0a1a`.

Fresh validation retains 17,331 suite cases, 1,542 exact outcome/log/compute
comparisons, and 24 growth, 32 optional-account, 20 user-ID, 8 extension-log and
30 crank-mint cases. Each harness keeps its own comparison limitations. These
finite cases do not prove exhaustive behavior or trigger every panic path.
The exact panic records and targets are checked statically as described above.

Run `python3 -B research/fees-slice-origin-integration/verify.py` and
`python3 -B research/fees-slice-origin-integration/test_scope.py`. They recheck
retained evidence; they do not compile or execute target programs. Source maps,
artifact hashes and the recorded driver retain the fresh-build recipe.

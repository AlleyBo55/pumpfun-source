# Fee-config extension size logs and formatting helper

Restoring the original no-resize log branches recovers the **complete 448-byte
formatting helper at original address 52,568**, without losing any body matches.
Fees advances to **372 unique structural pairs and 64 unmatched windows**.

The source previously returned silently when `current_size >= 4097`. It now
preserves the two observed branches:

- At 4,097 bytes: `Fee config account already has the correct size`.
- Above 4,097 bytes: `Fee config account already has more than 4097 bytes: SIZE`,
  substituting the actual current size.

The dynamic message invokes `alloc::fmt::format`, reproducing the original
helper. Raw differences in that helper are confined to its three local-call
immediates; all three callee bodies match. The real resize handler invokes it
in both images. That handler still differs: 6,312 original bytes versus 5,528
candidate bytes. Source-coordinate, validation, allocation and full caller
recovery remain open.

The full partition is **118 raw-local / 403 normalized-only / 64 unmatched**.
One previously normalized 24-byte window at 52,376 also becomes raw-equal under
the new layout; it adds no new normalized coverage or source attribution.
Incoming-call refinement yields 435 correspondences, including 63 additionally
attributed duplicates; 86 duplicates remain unattributed. Unmatched original
bodies span 318,872 / 799,648 original text bytes (39.9%).

## Source and build

Only the existing one-line early return in the research root `lib.rs` changes;
all other source bytes and line counts are preserved. This is a Rust source
change compiled with the pinned Linux v1.44 toolchain, with no binary patching.
The parent `research/fees-social-seed-vector` artifact is reused as control.
All 35 parent inputs and the fresh root compile are bound by hashes.

Candidate: 862,664 bytes, SHA-256
`4617fa1c6200daab0516a9a652716c32cf9868f24d47bcada61b6c716e461637`.

## Validation

Eight signed no-resize cases cross sizes 4,097, 4,098, 5,000 and 8,192 with two
funding levels. The parent disagrees on program logs in all eight cases; the new
candidate agrees in all eight. Errors, data, owner, balance changes, events and
inner instructions agree in both candidates. The log check includes every
`Program log:` line, excluding invocation/compute bookkeeping; compute equality
is not claimed for this matrix.

Fresh regression retains 17,331 suite comparisons, 1,542 exact outcome/log/compute
comparisons, 24 growth cases, 32 optional-account cases and 20 seed-length cases.
Each has the scope of its owning harness; this is not exhaustive equivalence.
No selected checkpoint is promoted and no whole-file identity is claimed.

Run `python3 -B research/fees-extend-size-logs/verify.py` to recompute source,
build, body/call and receipt checks. It does not compile or execute programs.
`log_cases.py` runs the additional signed log comparisons against a given ELF.

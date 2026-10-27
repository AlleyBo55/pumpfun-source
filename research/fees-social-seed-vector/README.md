# Social-claim user-ID seed-vector recovery

The V2 social-claim token path now copies the stored user ID into a byte vector
before constructing CPI signing seeds. This recovers the **entire 296-byte
original helper at 51,608**, advancing Fees to **371 unique structural pairs and
65 unmatched windows**, with no lost matches.

The change replaces the direct `state.user_id.as_bytes()` seed reference with
`let user_id = state.user_id.as_bytes().to_vec()` and `user_id.as_slice()` in the
same signing-seed list. All other source bytes are unchanged. Both original and
candidate V2 claim callers invoke this helper. Their complete bodies remain
unmatched (10,664 original bytes versus 10,144 candidate bytes).

The recovered helper differs in raw bytes only inside its two local call
immediates. Both calls bind to complete normalized callee bodies. This is a
complete normalized local match, not a raw whole-file match or a proof of all
caller behavior. There are no source-coordinate/data masks hiding other helper
differences. No hand-written bytecode or artificial unused helper is added.

## Reproduction and validation

Parent: `research/fees-optional-account-ownership`. Its artifact is the reused
control; all 35 source inputs are hash-checked. The new root crate was freshly
compiled with the same pinned Linux v1.44 compiler and retained build flags.
Only `programs/pump-fees/src/social.rs` differs in the research source map.

Candidate: 861,792 bytes, SHA-256
`6c58680b2bcd0c6a7ab616bb5f119c8357e7e4cccdcdae918a935399f6650f1f`.

Fresh validation:

- 17,331 differential comparisons across 18 suites.
- 1,542 exact outcome/log/compute comparisons.
- 24 exotic-growth and 32 optional-account cases retained from the parent work.
- 20 additional native/token claim cases across Token/Token-2022 and empty,
  one-byte, 20-byte, 32-byte ASCII and 32-byte UTF-8 user IDs. These compare errors,
  pre/post accounts, events, inner instructions and return data. Logs are saved
  but not required equal; compute is not claimed by this matrix.

The full partition is **117 raw-local / 403 normalized-only / 65 unmatched**.
Incoming-call refinement yields 434 attributed pairs, including 63 extra
resolved duplicates; 86 duplicates remain unattributed. The unmatched original
bodies span 319,320 of 799,648 original text bytes (39.9%). These measurements do
not promote the candidate into selected source or establish full ELF identity.

Run `python3 -B research/fees-social-seed-vector/verify.py` to recheck hashes,
source transformation, body/call comparisons and retained receipt contents.
This verifier does not compile or execute the target. The recorded build driver
and `seed_cases.py` retain the recipe for fresh builds and focused execution.

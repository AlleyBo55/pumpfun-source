# Restore the full-buffer unchecked FeeConfig boundary

The current research decoder accepted a discriminator-free payload at its
unchecked entry point. Anchor initialization passes a full account buffer.
Restoring the eight-byte prefix removal recovers the complete original
**1,144-byte helper at 18,384**, with no lost normalized or raw matches.
Fees now has **395 unique structural pairs and 43 unmatched windows**.

The checked entry point retains its existing guard and consuming-buffer
behavior. Both entry points now call the same separate payload decoder, whose
complete 2,648-byte body was already matched. The unchecked entry point checks
for eight bytes, consumes that prefix without validating its contents, then
decodes the payload. Its minimum full-account length is 2,512 bytes; stable and
full payload thresholds remain 4,065 and 4,089 (4,073 and 4,097 including the
prefix). This restores the full-account API convention for this research
candidate; the older packets' unchecked-input limitation remains historical.

## Machine-code and data evidence

All 11 direct helper callees match. The real incoming initialization closure
at 302,032 still matches and now calls the recovered helper. The payload decoder
and earlier checked account helper remain matched, including their direct calls.
The helper's two 32-byte owner constants and the decoder's 24-byte error-message
record, relocation and 27-byte message are checked separately.

| Variant | Helper bytes | New complete bodies | Result |
| --- | ---: | ---: | --- |
| Reused parent | 1,024 | 0 | Payload-only unchecked boundary |
| Full prefix, new local slice | 1,144 | 0 | 22 stack-operand differences; does not consume the passed descriptor |
| Full prefix, consumed descriptor | 1,144 | 1 | Complete normalized match |

The masks still cover only local call displacements and actual relocated
pointers, never stack offsets. The owner-ID mutation test shows that an equal
instruction body alone cannot establish referenced-data identity.

## Execution scope

Native Rust 1.94 source tests exercise **35 cases in three tests**: prefix
values, short inputs, checked-discriminator rejection, consumption and format
boundaries. The new prefix regression fails on the parent and passes on the
corrected source. The host projects use the same `types.rs` bytes as their SBF
variants; only a test module is appended to `lib.rs`. These are host source
checks, not original-program VM replay or proof of successful authorization.

Fresh SBF regression passes 17,331 cases across 18 suites, 1,542 exact
outcome/log/compute comparisons, and the 24 growth, 32 optional-account, 20
user-ID, 8 extension-log and 30 crank-mint cases. **Those suites do not invoke
`initialize_fee_config`**; their initialization suite covers the program-global
initializer. Genuine fixed-admin FeeConfig initialization is not validated by this packet.
This distinction is important even though the recovered helper and incoming
closure match locally.

## Artifacts and reproduction

The pinned Linux v1.44 candidate is 868,120 bytes, SHA-256
`bb225a53127295ad130ea795c33f086a33fa07385f29674ac5c0e6f148f9baed`.
All 36 input files, both fresh source variants, the reused parent, build logs,
artifacts, native test evidence and SBF receipts are bound by the packet.
The partition is 118 raw-local / 424 normalized-only / 43 unmatched; the
remaining windows span 248,904 original text bytes (31.1%). Call refinement
retains 65 additional duplicate pairs, totaling 460 correspondences, with 82
unattributed duplicate windows and 18 different-body frontier edges.
No selected source or checkpoint changes. Whole-file identity remains false.

Run `python3 -B research/fees-unchecked-prefix-recovery/verify.py` and
`python3 -B research/fees-unchecked-prefix-recovery/test_scope.py` for retained
evidence verification. These do not compile or execute target programs.
To rerun the host checks with a compatible native Rust toolchain and the locked
dependencies cached, use `python3 research/fees-unchecked-prefix-recovery/run_host_tests.py --output /absolute/new/output-directory`.
That optional command compiles native test executables; it does not run SBF or
read the deployed binary. The recorded host-driver file preserves the original
local execution rather than serving as the portable entry point.

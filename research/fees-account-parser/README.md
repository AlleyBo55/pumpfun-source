# Fees first-account parser attribution

This study follows the first account boundary from the pass-36 query parser into
its immediate callee. It resolves the *local candidate attribution* left ambiguous
by the three identical-looking 200-byte wrappers. It does not establish complete
parser equivalence or change a selected candidate.

| Image | Query's first encoded CALL target | Wrapper's account-parser target | Helper extent |
| --- | ---: | ---: | ---: |
| Captured original | 71,256 | 36,072 | 1,248-byte inferred window |
| Selected candidate | 83,552 | 26,680 | 1,144-byte symbol |

The original query window is `[518976, 520760)` and the candidate query window is
`[127336, 129120)`, as retained by pass 36. All three candidate wrappers equal the
original wrapper after masking only the two CALL immediate words. Their callees
distinguish them:

| Candidate wrapper | Callee | FeeConfig discriminator in callee | Candidate callee's typed downstream symbol |
| --- | ---: | --- | --- |
| 83,152 | 35,856 | Absent | `SocialFeePda::try_deserialize` |
| 83,352 | 30,752 | Absent | `SharingConfig::try_deserialize` |
| 83,552 | 26,680 | Present at 27,320 | `FeeConfig::try_deserialize_unchecked` |

The original helper contains the same literal at 36,696. The literal
`8f3492bbdb7b4c9b` is independently present in the retained official Fees IDL's
`FeeConfig` account declaration, the selected Rust implementation, and
`SHA256("account:FeeConfig")[0:8]`. The symbol ELF's entire `.text` equals the
selected stripped candidate's `.text`. Candidate symbol names are attribution
evidence for the candidate, not recovered original names.

## Concrete source-shape difference

The original helper has distinct error entries for the length check and the
discriminator mismatch. The current implementation combines those conditions.

| Check | Original | Candidate |
| --- | --- | --- |
| Length less than 8 | Branch at 36,672 to 36,936 | Branch at 27,304 to 27,344 |
| Wrong discriminator | Equality test at 36,712; error fallthrough at 36,720 | Equality test at 27,336; error fallthrough at 27,344 |
| Error conversion calls | 36,776 and 36,992, both encoded target 709,368 | 27,400, encoded target 694,392 |

Both original error entries load the same `0300000000000080` raw value, which the
candidate's shared entry also loads. The distinction therefore supports testing
two separate source guards while retaining the current error expression.
`proposed-guard-split.patch` records that small **uncompiled hypothesis**. It does
not change the serializer, unchecked decoder, account types, source paths,
historical coordinates, compiler flags, or active `programs/` files. Whether the
compiler preserves the split, and whether that improves emitted identity, require
a separate controlled source build.

## Verify

```sh
python3 research/fees-account-parser/verify.py
```

The checker hashes the packet and re-derives its recorded calls, complete wrapper
normalizations, candidate symbol bindings, discriminator sites and branch facts
from the original and selected ELF files. All input hashes are recorded in
`analysis.json`. It uses Python's standard library and the unchanged pinned ELF
layout reader. In a sparse checkout, first materialize the two selected candidate
files named in `analysis.json`.

The `.asm` files are bounded analyst listings from the official Linux platform-tools
v1.44 decoder (`e2a1dc7fd15b2dd9d669a516359556bc897b91e73b9433eb3196db3b4f55064e`).
Raw binary fields, rather than listing mnemonics, drive the checker. Original
extents remain inferred; encoded targets are not a historical loader/runtime
relocation proof. No target execution, new behavioral receipt, source promotion,
historical ledger reclassification, or new whole-file match is claimed. The
selected programs and pass-27 pins remain unchanged; core identity remains 0/4.

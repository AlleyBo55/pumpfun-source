# Fees: reject the Darwin v1.44 target-library substitution

The official macOS x86-64 v1.44 package does **not** fix the remaining bounds-check formatting mismatch. Its canonical target-library substitution loses coverage. The validated **353-pair Linux candidate from PR #123 remains the source checkpoint**; this trial is retained as rejected research.

| Evidence | Linux control | Darwin library trial |
| --- | ---: | ---: |
| Unique structural pairs | 353 | 352 |
| Unmatched original windows | 85 | 89 |
| Unique raw-equal local pairs | 57 | 55 |
| Inferred candidate windows | 580 | 580 |
| New unique original matches | — | 0 |
| Bounds-check piece count at +152 | 2 | 2 |

The original 200-byte `panic_bounds_check` window at 784168 stores **3** at +152. Both official-library variants store **2**, so the proposed explanation is rejected. All four original 56-byte Type-ID windows at 45432, 702656, 756232 and 767336 have raw-equal candidate bodies under Linux and no complete structural match under Darwin. Only 767336 was a body-unique pair; the other three were duplicate-body matches. No duplicate attribution or extra coverage is claimed.

All **33 source inputs are identical**. Both builds use the same official Linux v1.44 compiler and canonical `sbpf-solana-solana` target. Only the 25 target-library files come from the official Darwin archive in the trial. Native compiler/linker tools remain Linux tools; the existing Linux toolchain is unchanged. The official release asset ID, URL, exact 410,949,923-byte archive SHA-256 and every extracted target member hash are retained in `archive-check.json`. The full SDK archive is fetched separately, never embedded here. This mixed-host experiment is not claimed as the historical build recipe.

Both candidates pass **1,542 exact outcome/log/compute comparisons**, covering every optional byte plus absence, both pool flags and three caps in one fixed valid configuration. The identical Linux control's earlier 17,331-case receipt from PR #123 is retained and explicitly reused. The rejected Darwin build was **not run through all 18 suites**. The first focused attempt used a sparse publication worktree missing its IDL and ran no cases; rerunning the same copied driver from the primary checkout produced the retained passing receipt. These finite results do not prove exhaustive semantics.

## Verify and reproduce

```sh
python3 research/fees-target-library-control/verify.py
python3 -I research/fees-target-library-control/verify.py
```

The standalone check re-derives the full windows from the ELF bytes, verifies every symbol extent including aliases, checks the precise Type-ID regression and formatting literal, and binds complete overlays, all inputs, 187 unchanged harness hashes, build records, both artifacts and fresh strip replays. The retained controllers and launch commands document the recipe. Reconstruct their source snapshots from the bound revision and overrides; fetch the official archive, verify its complete SHA-256, and retain only the recorded canonical target members in an isolated sysroot. The recorded absolute paths describe this execution and must be adapted when rebuilding. Logs and hashes are retained evidence, not authenticated process traces.

The packet also independently rechecks the **four whole selected artifacts** and the PR #123 Fees research artifact against the pinned captured files at revision `a8f2a7b2`. Their actual raw comparisons remain false: **0/4 core raw identities**. No zero padding or relocation normalization is applied in that audit. This is a dated check of recorded artifacts, not a new source compilation of the other three programs.

Structural body signatures mask actual relocated LDDW addresses and local CALL immediates while preserving scalar/register/stack/branch bytes and import identities. They do not establish all callee or opaque-data meaning. Whole-capture and ELF-extent comparisons fail for both Fees variants. Selected sources, pinned scripts, workflows and checkpoint ledgers are unchanged; no trial is promoted.

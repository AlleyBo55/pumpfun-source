# Configuration setters and V2 ownership combined

Two ordinary Rust methods recover the complete **624-byte** original setters
at **260568** and **261192**. They call the previously recovered fee predicate,
return the observed error, and copy the three fields into the observed slots.
Their error origins name `programs/pump-fees/src/state.rs`, lines **365** and
**372**. All five encoded local calls in each setter reach corresponding
normalized callee bodies, checked independently of the caller's masked CALLs.
The method names are reconstruction choices, not authenticated original symbols.

| Variant | Unique pairs | Unmatched originals | Unique raw pairs |
| --- | ---: | ---: | ---: |
| Reused PR #142 parent | 357 | 81 | 58 |
| Initial setter edit | 357 | 81 | 58 |
| Setters with preserved source lines | 359 | 79 | 58 |
| Setters plus PR #143 V2 ownership | **362** | **76** | **59** |

The initial edit gained both setters but lost original windows 659640 and
660160: removing one source line shifted their embedded error lines from
183/188 to 182/187. Keeping that source line blank restores both matches.
This negative is retained; the matcher was not relaxed to hide the regression.

The final candidate also applies the exact `sharing_update.rs` substitutions
from [PR #143's packet](../fees-sharing-owned-v2/README.md). The combined build
recovers all five windows over PR #142, with none lost: the two setters plus
9528, 44632 and 641744. The 776-byte V2 cleanup at 44632 is raw-byte equal.
The combined result is verified from its actual linked binary, not obtained by
adding counts from independently compiled candidates.

## Build and runtime evidence

The two setter builds and the combined build were freshly compiled with the
unchanged official Linux v1.44 compiler, canonical `sbpf-solana-solana`, locked
inputs and the parent's root path mappings. Every log contains an actual root
compiler invocation and every before/after source map agrees. The control
artifacts and build records are explicitly reused from PR #142, whose control
previously reproduced PR #140 exactly. No fresh control build is claimed here.

The corrected setter and combined candidates each pass **17,331 comparisons
across 18 existing suites**, plus **1,542 exact outcome/log/compute comparisons**.
The initial regressing variant has no runtime-acceptance claim. Broad suites
retain their own comparison fields and finite-coverage limitations; they do not
establish equality of every log, compute count, input or execution path.

The final build has 35 bound inputs. Only the root module, `state.rs` and the V2
sharing declaration differ from the parent; the math helper and other inputs
remain fixed. Source maps, artifacts, logs and receipts are retained. Captured
source whitespace and the explicit blank line are preserved. The scratch driver
is a recorded workflow, not a turnkey SDK installer; rebuild by materializing
`experiment.json`'s source maps and using the recorded command/environment with
local paths.

## Limits and next work

The final candidate remains unequal to the original captured file and meaningful
ELF extent. A matched setter with matching direct callees is not proof of all
callee data, indirect calls or transitive semantics. Public callers are still
unmatched. Continue with the two 4,160-byte tier-setting bodies at **261816** and
**265976**, preserving error precedence, old-vector ownership and copied data.
Selected program sources and checkpoint pins are unchanged.

```sh
python3 -B research/fees-config-setter-recovery/verify.py
python3 -I -B research/fees-config-setter-recovery/verify.py
python3 -B research/fees-config-setter-recovery/test_scope.py
```

The three scope tests distinguish an encoded callee change hidden by CALL
normalization, an unmasked error-line change, and an origin-string mutation that
requires the separate data check.

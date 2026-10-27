# Exotic-fee account growth: corrected rejection precedence

The previous research candidate checked the fee total before growing a short
configuration account and used `realloc(4097, true)`. The original executable
checks the data length first, can fund/grow the account before fee validation,
and passes **false** for realloc's zero-initialization argument.

A new 24-case signed matrix crosses short/full-size accounts, low/funded account
balances, low/funded admin balances, valid fees, an invalid total and addition
overflow. The previous candidate disagrees in four cases. Moving validation later
alone leaves two disagreements; restoring the original zero-init flag removes
all of them. The minimal corrected candidate retains the existing event code.
It also passes fresh 17,331-case existing suites and the 1,542-case exact matrix.

One concrete difference: with a short account, one lamport in the account and
one lamport in the admin, an invalid fee total makes the original fail the
funding transfer. The old candidate instead returned `InvalidFeeTotal` or panicked
on overflow before attempting funding. The corrected candidate agrees with the
original. Full receipts retain account state, balances, events, inner instructions
and logs; the comparison fields and finite coverage are explicit.

## What remains unmatched

**No original body is newly matched.** All ten variants retain 368 unique
structural pairs and 68 unmatched windows. The exotic caller at original address
88552 remains unmatched: the original is 5,520 bytes and the minimal corrected
caller is 5,664 bytes. An argument-order trial is exactly 5,520 bytes but still
fails the complete-body comparison. Equal size is not accepted as recovery.

| Trial | Exotic caller bytes | Zero-init | Boundary mismatches |
| --- | ---: | --- | ---: |
| Reused PR #147 control | 5712 | true | 4 / 24 |
| Later validation | 5664 | true | 2 / 24 |
| Event simplification | 5488 | true | Not executed |
| Zero-init correction with simplified event | 5488 | false | 0 / 24 |
| Shorter scope | 5448 | false | Not executed |
| Owned helper | 5488 | false | Not executed |
| Borrowed helper | 5488 | false | Not executed |
| Early-return helper | 5464 | false | Not executed |
| Reordered helper arguments | 5520 | false | Not executed |
| **Minimal correction** | **5664** | **false** | **0 / 24** |

The helper/scope controls narrow future work on lifetime, register allocation and
block layout. They are not selected as the new research candidate. All were
freshly compiled with the pinned Linux v1.44 compiler and canonical target;
source snapshots, command logs and complete artifacts are retained. The parent
control is explicitly reused. The final source changes only the validation
position and the zero-init flag, preserving source-line count and event behavior.

## Checks and limits

```sh
python3 -B research/fees-exotic-growth-precedence/verify.py
python3 -I -B research/fees-exotic-growth-precedence/verify.py
python3 -B research/fees-exotic-growth-precedence/test_scope.py
```

The static checker re-reads call sites and zero-init operands. Its intraprocedural
CFG treats calls as returning and does not establish path feasibility or
whole-program ordering; the new executed boundary matrix supplies the concrete
rejection-precedence witnesses. Broad-suite passes do not prove equality of all
logs, compute counts or inputs. The exact matrix concerns its own fixed fixture.
No captured bytes, selected program sources, checkpoint pins or matching masks
change. Full caller and whole-program byte identity remain open.

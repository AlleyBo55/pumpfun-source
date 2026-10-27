# Correct the creator input in the Mayhem CPI fixture

The inherited `zero-creator-is-rejected` case supplied a `creator` parameter,
but the harness always serialized the payer's public key. Its earlier successful
comparison was another ordinary creation, not coverage of zero-creator rejection.
The harness now serializes the requested creator and retains each signed
transaction in both sides of the comparison.

The corrected twenty-case run compares captured Pump and Mayhem with the existing
retained reconstructed pair. Both zero-creator cases (Mayhem and normal mode)
reject with Pump's `CreatorShouldNotBeZero` / 6030. Two distinct nonzero creator
controls succeed and store that creator in the resulting bonding curve. The
remaining sixteen cases retain their previous inputs. All twenty comparisons
match across initial/final watched accounts, errors, events, inner instructions,
return data and signed transaction bytes. Raw logs are retained but their entire
contents and compute consumption are not equality gates.

This is a fixture correction and bounded validation, not a new reconstruction or
compiler build. The binary inputs are fixed in `inputs.json`: Pump `5392c9a9…`
and Mayhem `cbe8c8e7…`, both already retained in the repository at base commit
`58519a8e601ed17bc6d931483686a08ee656233d`. These predate the Mayhem initializer
correction in PR #79. No coverage is inferred for a different candidate pair.
Zero-creator rejection occurs in Pump and does not itself validate Mayhem's
initializer. No whole-file byte identity or exhaustive behavior is claimed.

All transactions ran locally in LiteSVM with synthetic accounts, the captured
configuration fixture, and the repository's captured dependency programs.
Python package versions were solders 0.27.1, pyelftools 0.32, jsonalias 0.1.1 and
typing_extensions 4.16.0. No network transaction was submitted.

From the repository root with its pinned Python requirements installed:

```sh
python -B research/mayhem-creator-fixture/verify.py --repo .
python -B -m unittest discover -s research/mayhem-creator-fixture -p 'test_*.py'
python -B repro/behavioral-recovery/scripts/pump_create_mayhem_differential.py \
  --candidate-pump repro/pump/recovered-dispatch-56-from-main-v144/main/candidate.so \
  --candidate-mayhem repro/mayhem/recovered-dispatch-25-from-main-v152/main/candidate.so \
  --output work/corrected-create-mayhem.json.gz
```

The first command validates saved receipts and binary/harness hashes, independently
decodes the serialized Borsh inputs, verifies signatures, checks the two expected
rejections and two persisted creators, and recomputes every selected comparison.
The second proves it rejects the original mislabeled-input bug even with valid
signatures and matching sides, false successes, wrong persisted creators, invalid
signatures and missing cases. Only the last command executes a fresh VM replay;
use a fresh output path. Earlier receipts are historical evidence and remain
unchanged.

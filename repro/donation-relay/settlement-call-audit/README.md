# Settlement direct-call audit

This read-only audit compares four unmatched Relay settlement callers against
the accepted 482-window candidate and the prior constructor-order experiment.
It adds no matched function and changes no candidate. Relay remains **482/492
normalized windows, 130 exact local bodies and ten unmatched**.

## What the direct-call ledger establishes

Every direct local callee reached by a call instruction in these four caller
bodies has a complete normalized-body counterpart. The comparison groups
callees by body length and normalized hash, preserving duplicate/ambiguous
original identities rather than forcing a name match.

| Original window / working name | Original calls | Baseline calls | Constructor-order calls |
| --- | ---: | ---: | ---: |
| 97: distribute after swap | 36 | 36 | 36 |
| 98: distribute without swap | 38 | 38 | 38 |
| 99: just swap | 26 | 27 | 26 |
| 100: swap then distribute | 25 | 25 | 25 |

For 97, 98 and 100, the full multiset of direct callee-body groups and counts
already agrees with the original. For 99, the baseline has one additional memcpy
call; the constructor-order experiment removes it. All four multisets then
agree. These are stronger statements than equal total call counts: the complete
per-callee multiplicities are checked.

**None of the eight comparisons has the same linear call sequence, and none
of the four caller bodies matches.** Linear instruction order is not dynamic
execution order. This audit does not align basic blocks, establish branch
conditions, prove call arguments, close transitive data/callee behavior, or
validate indirect/external calls. Those call forms are retained separately in
the report and excluded from the direct-local-call multiset claim.

Matching call counts therefore cannot rule out missing inline validation,
incorrect arithmetic, wrong arguments or data references, or a different
control-flow arrangement. It does narrow the investigation: claims of a missing
out-of-line operation need to account for this existing ledger first.

## Artifacts and checks

`report.json` retains every direct call offset, target, body hash, possible
original ordinals, candidate symbol label and comparison result. It also retains
external and indirect-call records. Inputs are the pinned original capture and
the symbol-bearing binaries already published in the burn/close and swap-caller
packets. No new compile or runtime execution occurs here. The prior swap-caller
packet owns the constructor experiment's bounded replay evidence.

```sh
python3 -B repro/donation-relay/settlement-call-audit/verify.py
python3 -I -B repro/donation-relay/settlement-call-audit/verify.py
python3 -B repro/donation-relay/settlement-call-audit/test_calls.py
```

The standard-library verifier re-reads executable bytes and preserves the
existing normalization rules. Five tests check changed callees, targets inside
rather than at the start of a function, duplicate calls and order changes. An
in-memory non-call mutation deliberately keeps the call counts while changing
the caller body; this tests the limit of the claim. No captured file is modified.

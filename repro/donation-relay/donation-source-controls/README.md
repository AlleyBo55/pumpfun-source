# Relay: donation source and ownership controls

This packet retains **59 compiled source experiments** and **173 targeted
original/candidate window comparisons**. None recovers a complete targeted
window. The selected research frontier therefore remains **482/492 normalized
windows, 10 unmatched**. No trial is promoted. Some ownership variants remove the already-matched
context-drop window 51 and fall to 481 matches; none adds a matched window.

The target windows are the native donation bodies **92/93**, regular/payer
wrappers **94/95**, and shared donation worker **112**. Comparisons use the
existing strict CALL/relocation normalization. Correct sizes, approximate
instruction similarity and passing unrelated tests are not treated as recovery.

## Hypotheses tested

| Group | Builds | Scope |
| --- | ---: | --- |
| Context construction order | 24 | Every ordering of the four owned AccountInfo fields, across all five public donation wrappers |
| Wrapper argument and event form | 6 | Keep arguments in their struct, inline returned events, or name context/argument temporaries |
| Worker entry ownership | 4 | Keep/destructure the context and arguments independently |
| Worker CPI moves | 7 | Consume different subsets of mint, source token account and token program in the CPI |
| Ownership after initial checks | 8 | Destructure context after message/BPS checks, with different CPI moves |
| Return tuple layouts | 6 | Replace the result struct with each tuple ordering and consistently update its callers |
| Full Linux ownership controls | 4 | Repeat the four worker-entry variants with the Linux compiler |

The four Linux controls have the same targeted normalized body hashes as their
Darwin-compiler/Linux-library counterparts. Both routes remain unmatched for
those variants. The unmodified control builds reproduce their respective
parent candidate files exactly. This is not a general claim that the hosts
produce equal files, and it is not new target-program execution.

The original and reconstructed small wrappers call the String clone, shared
worker and memcpy routines, but their full bodies still differ. The worker's
ownership experiments change cleanup, allocation and spill code without
recovering its full 10,248-byte body. These results rule out the tested source
forms; they do not rule out all equivalent implementations or prove that all
underlying business logic is correct.

## Evidence and limits

Every build starts with the same **56-input** 482-window source from the
[burn/close ownership recovery](../burn-mint-ownership-recovery/README.md). Only
`src/donation_handlers.rs` and/or `src/shared_donation.rs` are overridden. The
packet binds each complete input map, source snapshot, actual root-crate compiler
invocation, unchanged-source check and stripped/unstripped artifact. Identical
artifacts are stored once by content hash. Whitespace-bearing source files are
compressed to preserve their exact compiled bytes.

`report.json` records the complete-inventory counts, gains and losses for each
trial, in addition to every targeted mismatch. A variant can alter unrelated
compiler-generated bodies, so the complete inventory is checked rather than
just searching for a similar target. No runtime validation or exhaustive
semantic equivalence is claimed for these unaccepted variants. The preceding
482-window checkpoint retains its own bounded replay evidence.

```sh
python3 -B repro/donation-relay/donation-source-controls/verify.py
python3 -I -B repro/donation-relay/donation-source-controls/verify.py
python3 -B repro/donation-relay/donation-source-controls/verify.py \
  --materialize /tmp/relay-donation-control --variant context-order-dmfp
```

The verifier requires only the standard library. It verifies parent/package
hashes, reconstructs source input maps, re-analyzes whole function windows and
checks the paired compiler controls. It does not compile or execute target
programs. Recorded controllers and launch commands retain the tested recipes;
adjust source/output paths when rebuilding. Original executable bytes are
comparison inputs, never compiler inputs.

The remaining-work list is unchanged: original ordinals **92–100 and 112**.
Further work needs evidence beyond these rejected construction, ownership and
result-layout variants. In particular, preserve the original context-drop path
while investigating later partial moves around the transfer CPI; these experiments
do not establish that the original fully destructured its context at entry. Selected source files and selected artifacts are unchanged.

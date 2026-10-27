# Donation wrapper value-flow diagnostic

Relay remains **482/492 normalized windows, 130 exact local bodies and ten
unmatched windows**. The regular and payer donation wrappers (original ordinals
94 and 95) still do not match as complete instruction bodies. This packet adds
four conditional caller traces; it does not recover or promote a function.

## Finding

Under the explicit model below, both wrappers pass the same selected context
and argument bytes to the shared worker. Given the same modeled worker result,
they also assemble the same success and error return bytes. Each trace follows
eight nonwrapping increment guards. The differing register and stack assignment
therefore does not itself establish a data-marshaling error on these paths.

| Boundary compared | Bytes per trace | Differences |
| --- | ---: | ---: |
| Selected context fields entering shared worker | 204 | 0 |
| Shared-worker argument fields | 68 | 0 |
| Success return fields | 153 | 0 |
| Error return fields | 24 | 0 |

There are two modes for each of two wrappers: four comparisons, not four newly
matched functions. The report retains each executed local call, branch
assumption, symbolic byte, and its expression. No positional or register
normalization is added to the byte-identity matcher.

## Explicit model and limits

This is a restricted symbolic caller diagnostic, not an emulator or a semantic
equivalence proof. It models only instructions reached in these four traces and
fails on unsupported instructions, unknown branch forms, uninitialized local
memory, and reads of call-clobbered registers.

- Entry arguments are symbolic values. Input address expressions are distinct
  unless their expressions are identical. Arbitrary input aliasing and invalid
  pointers are not covered.
- Eight increment-by-one guards per trace assume that the result is nonzero.
  The verifier checks the guard instruction pattern. Overflow/abort paths are
  outside this result; the model does not silently take arbitrary branches.
- The String clone call is summarized with 24 output bytes derived from its
  24 input bytes. Allocation, heap effects and failure are not executed. The
  candidate clone body matches an ambiguous group containing original 389;
  no unique original attribution is asserted for that duplicate group.
- Original 112 and the named candidate shared worker are deliberately treated
  as a common boundary with identical symbolic success/error results. **Their
  bodies remain unmatched.** Worker account writes and actual runtime outcomes
  are not modeled. Consequently this result cannot validate the worker or make
  the wrappers transitively equivalent.
- The matched memcpy call is summarized as a byte copy. Calls clobber registers
  0–5, and subsequent uninitialized register reads are rejected.

The selected layout covers context bytes 0–31 plus 43 bytes of each 48-byte
AccountInfo at offsets 32, 80, 128 and 176. It excludes padding. Arguments use
bytes 0–67. The success result uses 0–152 (String, config, mint, epoch, amounts,
credit and event discriminant); the error result uses 0–23. These are stated
comparison boundaries, not evidence that every state/data contract is recovered.

The next useful distinction is between caller source/code generation and the
unmatched worker's behavior. This packet narrows one marshaling hypothesis for
ordinary nonoverflow paths; it does not settle compiler provenance, error
precedence, allocation behavior, security, raw bytes or whole-file identity.

## Verification and negative controls

```sh
python3 -B repro/donation-relay/wrapper-value-flow/verify.py
python3 -I -B repro/donation-relay/wrapper-value-flow/verify.py
python3 -B repro/donation-relay/wrapper-value-flow/test_model.py
```

The verifier binds the original and preceding accepted research candidate by
hash, then recomputes all four traces. No new binary is compiled or executed.
The owning burn/close packet retains the candidate's source/build/runtime
receipts; this verifier does not rerun that runtime corpus.

Eight focused tests include in-memory mutations that alter an outgoing bump,
change the returned event discriminator, shorten the copy, and invalidate the
increment guard. They also reject unknown instructions and clobbered registers.
These negative controls demonstrate that the diagnostic detects the tested
faults rather than merely declaring matching summaries. Mutated executable
bytes exist only in test memory; no artifact or source candidate is patched.

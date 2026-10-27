# Donation wrappers: complete partial-argument control family

This study holds the preceding 482-window Relay source fixed and tests every
subset of the five wire-argument fields as local destructured bindings. There
are **32 compiled source forms and 128 targeted original/candidate comparisons**.
No form recovers a complete targeted window. The Relay frontier remains
**482/492 normalized matches, 130 raw local bodies, ten unmatched**.

## Controlled change

The five fields are `amount`, `config_id`, `tip_bps`, `message`, and `credited_to`.
For each subset, chosen fields are bound with a partial Rust struct pattern;
unchosen fields are accessed through `args.field`. All five donation wrapper
source functions receive the same subset. The argument values, shared worker,
context construction order, event fields, and compiler recipe remain fixed.
The target original windows are 92, 93, 94 and 95. Two source wrappers can share
a compiled body, so five source functions do not imply five original targets.

The initial disassembly inspection found the same four AccountInfo clones in
the same order, but different stack/register use. These controls test whether
partial argument binding alone explains that mismatch. They do not cover all
Rust source forms, declaration orders, inlining decisions or compiler versions.
Equal-size bodies and local instruction similarity are not accepted as matches.

## Evidence

`metadata.json` enumerates all 32 distinct subsets. `report.json` gives each
body size/hash, all targeted mismatches and whole-inventory gains/losses. Each
build retains its actual root compiler invocation, 56-input hash map, unchanged
source check, source snapshot, and stripped/unstripped output. Content-identical
artifacts are stored once. The full-field control reproduces the preceding
accepted research candidate and symbols exactly. Whitespace-bearing source snapshots are compressed
without changing their bytes.

The verifier reconstructs the expected source for every subset independently
of the saved snapshot, checks all input hashes, and reanalyzes the full binary
inventory using the existing CALL/relocation normalization. These are
Darwin-compiler/Linux-target-library controls. No fresh Linux-compiler build or
runtime replay is claimed for these rejected candidates. No selected source or
accepted research candidate is replaced.

```sh
python3 -B repro/donation-relay/partial-argument-controls/verify.py
python3 -I -B repro/donation-relay/partial-argument-controls/verify.py
python3 -B repro/donation-relay/partial-argument-controls/verify.py \
  --materialize /tmp/relay-partial-args --variant partial-args-message
```

Verification requires only Python's standard library and does not compile or
execute target programs. The saved controllers retain the tested build recipe;
adjust workspace paths before rebuilding. The two-stage search reused the first
seven verified build records, then compiled every remaining subset.

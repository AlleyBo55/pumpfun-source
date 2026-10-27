# Mayhem initializer: signer phase and existing token vaults

The behavioral overlay checked `mint_authority` while converting it to a
`Signer`, before decoding `mint`. The captured original decodes the mint first
and then reports `ConstraintSigner` (2002). It also accepts an existing canonical
token vault, while the overlay always attempted its creation.

Two source changes reproduce the observed behavior:

```diff
-    #[account(seeds = [b"mint-authority"], bump, seeds::program = state::PUMP_ID)]
-    pub mint_authority: Signer<'info>,
+    #[account(signer, seeds = [b"mint-authority"], bump, seeds::program = state::PUMP_ID)]
+    pub mint_authority: UncheckedAccount<'info>,
...
-    #[account(init, payer = payer, associated_token::mint = mint, associated_token::authority = sol_vault, associated_token::token_program = token_program)]
+    #[account(init_if_needed, payer = payer, associated_token::mint = mint, associated_token::authority = sol_vault, associated_token::token_program = token_program)]
```

The explicit signer and Pump PDA constraints remain present. The existing-vault
path checks its token program owner, mint, token authority and associated address.
The source edits are applied to the optional behavioral overlay only. Active
`programs/`, selected artifacts, status indexes and pinned CI scripts are unchanged.

## Measured results

Each variant was compiled from the same base commit
`58519a8e601ed17bc6d931483686a08ee656233d`, active Mayhem source plus its behavioral
overlay. Only the changes above differ between the retained source snapshots.

| Source variant | 53 signed standalone rejection cases | 17 existing Pump CPI cases | Raw output bytes | Whole-file equality |
| --- | ---: | ---: | ---: | --- |
| Baseline | 35 mismatches | 0 mismatches | 691,120 | No |
| Signer constraint only | 9 mismatches | 0 mismatches | 691,368 | No |
| Signer constraint + conditional vault creation | **0 mismatches** | **0 mismatches** | 695,448 | No |

The final raw ELF SHA-256 is
`8e6a5f8c34a12303096902e50848f556bc7a9d9ce0dc0d9030e632b85b88e166`.
It still differs from the 777,408-byte original at 457,680 total positional byte
locations, including the missing suffix. This is a raw positional comparison,
not aligned instruction distance or a completeness percentage. No bytes are
padded, replaced or copied from the original into any compiler output.

The original five-case harness also changes from 5 mismatches to 2 with the
signer-only edit and then to **0** with both changes. The initial 45-case matrix
is retained separately: saved Darwin and fresh Linux baselines both have 27
mismatches; signer-only has one. The eight additional vault cases exposed that
the initial source hypothesis needed the second change. These overlapping
corpora must not be added together as independent coverage.

The 53-case matrix compares errors, named Anchor errors, complete watched
account snapshots, inner instructions, events and return data. Each pair uses
the same serialized, correctly signed transaction and initial accounts. All
cases reject: missing/short instructions and account lists, invalid mint/global
layouts, incorrect authorities, missing signatures, invalid program accounts,
pre-existing state, and valid or malformed pre-existing vaults. Raw logs are
retained; compute consumption and other unselected log lines are not equality
gates. The independent saved-receipt checker verifies the actual transaction
signatures, recomputes all selected comparisons and detects falsely reported
matches.

Positive coverage comes from the existing 17-case `pump_create_mayhem_differential`
harness. The **captured original Pump is the caller on both sides**, so its real
`invoke_signed` supplies the required PDA signature and isolates the Mayhem
change. Inputs are local synthetic fixtures. These records do not establish
an exhaustive initializer, historical transaction replay, whole-program behavior
or acceptance of other Mayhem handlers. The inherited case called
`zero-creator-is-rejected` does not actually substitute its `creator` parameter
into the payload; it supplies another ordinary creator and is not zero-creator
rejection coverage. The saved CPI harness asserts transaction signatures while
running but does not retain serialized transaction bytes, unlike the new matrix.

## Static correspondence

The retained dispatcher map identifies the initializer call at file offset
515,984 to wrapper 528,112. The wrapper's encoded call at 528,264 reaches the
parser at 430,840; the body call at 528,528 reaches 534,840. These are static
direct-call calculations, not recovered historical symbol names.

The parser's instruction at `0x6b3c0` encodes error 2002. Its named error payload
references the exact 14-byte `mint_authority` string at `0xaded1`. The branch at
`0x6ae58` reaches that error block after the preceding byte load at `0x6ae50`.
The runtime cases bind the signature rejection to that named account. This
does not identify every parser callee or prove transitive semantic equivalence.

`static/` retains bounded LLVM listings of the wrapper and the parser including
its two following inferred helper windows. Verification checks every listed raw
byte against the capture, hexadecimal byte addresses, instruction widths and
continuous coverage of those ranges. It does not independently verify mnemonic
semantics or historical function boundaries.

## Build provenance and retained failure

The local host used Docker Desktop 4.97.0 / Engine 29.9.2 on macOS arm64, with
`linux/amd64` containers using the pinned official image
`rust@sha256:948f9b08a66e7fe01b03a98ef1c7568292e07ec2e4fe90d88c07bb14563c84ff`.
The actual compiler and stripper both come from official platform-tools v1.52,
archive SHA-256
`8b3861e93daf085ec12b65c4fac374d9bec4587a3de16871da6b08ab0c1d907e`, matching the
retained Linux toolchain input pin. The compiler reports Rust 1.89.0-dev and
LLVM 20.1.7. Direct Cargo targets `sbpf-solana-solana` with
`-Zremap-cwd-prefix=` and the unchanged locked release profile.

Dependency acquisition occurs separately. All 215 registry archives match
Cargo.lock checksums. Compilation uses `--locked --offline`, a read-only source
mount, a read-only toolchain mount and Docker `--network none`. Each variant has
its own initially empty target directory. Source, tool and registry file hashes
are checked before/after. No original executable is mounted in these build
containers. Original execution and disassembly use separate analysis steps.
Both unstripped and explicitly stripped outputs are retained; their allocated
sections are checked for equality. This is locally recorded provenance, not
independent hosted attestation or recovery of the historical uploader recipe.

The first signer-only compile failed with E0463 while loading `anchor_syn`.
Its completed `.rlib` and `.rmeta` were byte-identical to the baseline's files.
The exact recorded Cargo command succeeded on retry using that failed attempt's
target directory, with no source/compiler changes. The cause is unresolved;
no general Docker or compiler fix is claimed. The failed log and command remain
under `build/`, with separate retry records. The final vault variant used another
empty target directory and succeeded on its first attempt. The Linux baseline
is eight bytes shorter than the saved Darwin overlay; it is explicitly a new
control and is not described as a raw reproduction of that historical binary.

## Verification and reproduction

Install the repository's pinned Python requirements, then run from its root:

```sh
python -B research/mayhem-initializer-validation/verify.py --repo .
python -B -m unittest discover -s research/mayhem-initializer-validation -p 'test_*.py'
python -B research/mayhem-initializer-validation/validation_matrix.py \
  --repo . --candidate research/mayhem-initializer-validation/build/vault.so \
  --output work/mayhem-initializer-replay.json.gz
```

The checker performs saved-evidence verification, not a new compilation or VM
replay. The last command performs a fresh local VM replay. All outputs must use
fresh paths. Historical reports and artifacts are retained unchanged.

To repeat the compilation, use a clean checkout of the pinned base revision
above, the checksum-verified official v1.52 Linux archive, and Docker. Copy
`build/build_pair.py` and `build/build_vault.py` into a fresh directory. Run
`build_pair.py --repo <base-checkout> --archive <archive> --image <pinned-image>
--output <fresh-directory>/build-01`, then run the copied `build_vault.py` from
that same directory. Its expected `build-01` sibling is intentional. The recorded
`retry_constraint.py` documents the actual failed-attempt recovery and is not
required after a successful fresh pair build. The active overlay on this PR
already contains the two changes; do not use it as the baseline of this experiment.

The historical source layout, original build recipe and complete byte identity
remain unresolved. No selected-source promotion or deployment is implied.

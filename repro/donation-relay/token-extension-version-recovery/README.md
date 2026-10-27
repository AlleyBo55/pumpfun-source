# Relay: recover four Token-2022 helper windows

This follows the [SwapReceipt coordinate recovery](../swap-receipt-coordinate-recovery/README.md).
The new research build has **470/492 complete normalized original-window
matches**, **88 raw local matches**, and **22 unmatched windows**. Four original
windows are gained and no previous normalized window is lost. Whole captured-file
byte identity remains false.

| Original window | Bytes | Matching candidate symbol |
| --- | ---: | --- |
| 240 at 629312 | 944 | `extension::get_tlv_data_info` |
| 242 at 630336 | 1,136 | `ExtensionType::try_get_total_tlv_len` |
| 243 at 631472 | 872 | `ExtensionType::get_required_init_account_extensions` |
| 244 at 632344 | 2,968 | `TokenInstruction::pack` |

These are full body matches under the existing direct-CALL and relocation masks,
not raw-equal functions or proof of all transitive data/behavior.

## Why this dependency path

The original TLV helper differs from the previous closest candidate at one
instruction's accepted extension-tag limit: 28 versus 25. The public Token-2022
8.0.1 source includes the additional extension types. Changing only the root
crate's direct Token-2022 dependency from 7.0.0 to 8.0.1 did **not** recover a
window: Anchor SPL's token-interface path still used its separately selected
6.0.0 dependency. That negative control remains in `builds/direct-v8/`.

The successful trial uses the same Anchor SPL 0.31.1 Rust source, with its manifest's
Token-2022 requirement changed from `6` to `8.0.1`. The root points to that local
crate and keeps direct Token-2022 8.0.1. No Anchor SPL Rust code and no reconstructed
Relay Rust code changes. Cargo lockfiles and both manifest overrides are retained.
This is a measured dependency/source-family hypothesis, **not** identification
of the historical uploader's Cargo manifest or a released Anchor SPL recipe.

| Build | Stripped bytes | SHA-256 | Normalized / unmatched |
| --- | ---: | --- | --- |
| Prior coordinate recovery | 813,968 | `03b725918aca825b316254311ea6ebe83da708bc3775df72c5d04be3b63fe978` | 466 / 26 |
| Direct Token-2022 v8 only | 813,968 | `bba550be99bd37ebd70a4d865f28b0fc5cff67a2362c3faaa681322006507fe6` | 466 / 26 |
| Anchor SPL token-interface v8 | 812,864 | `4256c58be30adeda38bfa1a47102179a6e45666a63876cc568828fdf72daddef` | 470 / 22 |

The successful unstripped SHA-256 is
`f4691718db894fd7de8ae2cb7c58274428773893518527072f7fa61140071a11`.
Both use the measured canonical platform-tools v1.48 target. Dependency resolution
and missing-cache fetches are separate from the offline builds. The failed offline
preparations and their logs are retained in `attempts/`; no success is inferred
from those failures. Lockfiles include optional/unbuilt packages, so their package
count is not the target's compiled dependency count.

## Source and runtime checks

The registry audit checked **187 resolved registry packages / 4,135 files**
against checksum-pinned crate archives. The local Anchor SPL source is verified
separately against the retained public crate, with exactly the manifest override
described above. Program Rust files are bound to the previous recovery's source
snapshot. No captured executable is a compiler input.

All **536 saved records / 534 unique fixtures** were replayed afresh on the
captured original and this candidate. Every original observation reproduced and
all candidate comparisons passed. Signatures, blockhash and transaction-history
checks stay enabled. The comparator still excludes compute-metering lines and
executable image bytes; no broader equivalence or privileged-settlement success
is claimed.

`fresh-runtime.json.gz`, build outputs, logs, command/source records, source
overrides, lockfiles, the registry receipt, and the negative control are retained.
The verifier reuses the previous independent saved-receipt checker with only the
expected candidate digest rebound; its fixture, signature and effect checks are
unchanged.

```sh
python3 -B repro/donation-relay/token-extension-version-recovery/verify.py
# Also recheck the local cache paths recorded by the registry audit:
python3 -B repro/donation-relay/token-extension-version-recovery/verify.py --check-registry
```

The default verifier performs no compilation or VM execution. The optional flag
requires the recorded local registry source paths; it is not a portable cache
installer. Logs and hashes do not authenticate the whole producer process or
establish a unique historical build environment.

`remaining-windows.json` lists all 22 residuals. They still include donation and
settlement business bodies, mint policy, account close, signed CPI, resizing,
the three repeated type-ID bodies and other helpers. Active source and selected
source-15 artifacts are unchanged.

## Third-party material

The two unmodified crate archives under `upstream/` are Anchor SPL 0.31.1 and
SPL Token-2022 8.0.1, distributed under Apache-2.0 as declared by their Cargo
metadata. `upstream/LICENSE-APACHE` contains that license. Their upstream notices
remain in the archives. The manifest override is an explicitly labeled local
modification; this package does not relicense the archived material.

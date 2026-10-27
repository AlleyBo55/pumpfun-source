# Independent hosted reproduction of the Fees guard split

A fresh GitHub-hosted build reproduces **all four complete ELF files** for the
baseline and guard-only variant in [PR75](https://github.com/lalalune/pumpfun-source/pull/75),
at `5f8f2aef2a70e43642e65e10d1db3e7476a533d6`. This includes the unstripped
compiler output and the explicitly stripped output for each source variant.
Equality uses the complete raw files, without padding, alignment or masking.

The source hypothesis and first reported guard result belong to
[PR74](https://github.com/lalalune/pumpfun-source/pull/74) and PR75.
[PR73](https://github.com/lalalune/pumpfun-source/pull/73) supplies the raw Linux
baseline gate. This packet adds a replayable direct-Cargo build in a pinned
container, actual root `rustc` argument capture, an independent host observation,
and portable checks of the complete retained artifacts. It does not repeat PR75's
decoder variants or claim their discovery.

| Output | Bytes | SHA-256 (also identical to PR75) |
| --- | ---: | --- |
| Baseline, unstripped | 1,238,184 | `ce39190dbe53d2ccf8918626948ec1c6ba44d5114f40953c30cd8b904664dfd7` |
| Baseline, stripped | 863,800 | `6c44d9f2ffe9b18c79a6344b256d8acd7a34c10e77b894c51f46512a447b8ce6` |
| Guard split, unstripped | 1,238,272 | `18acea4faf20a7fcbdeca8dd2ba4313bccbab18a2686962d0bb8866d532e24ec` |
| Guard split, stripped | 863,888 | `3362e310dc004c21b21c3370a6482dd14f5819f4fb6e5547d11a816f6c876c86` |

## Controlled build

The successful [run 40375285745](https://github.com/startrack3r/pumpfun-source/actions/runs/40375285745)
executes controller `c065072984f045a4c27e3b746453d4e0379da3e7`.
Its input is exactly 26 source/workspace/IDL files from main
`58519a8e601ed17bc6d931483686a08ee656233d`, retained in `source.tar.gz`.
The only source delta is PR74's separate length and discriminator guards in
`FeeConfig::try_deserialize`; both return the existing InvalidAccountData error.

Public acquisition verifies the complete official Linux platform-tools v1.44
and v1.52 archive hashes. The pinned container is only the host environment;
the compiler is the extracted v1.44 toolchain and stripping explicitly uses
v1.52 `llvm-objcopy --strip-all`. The controller verifies 252 registry archives
against `Cargo.lock` before and after the pair.

Each compilation runs in a separate container with `--network none`, a read-only
root, dropped capabilities, no new privileges and read-only source/tool mounts.
Only public dependency acquisition has networking. Original captures are absent
from the compiler input archive and container mounts. The baseline must match
the complete PR73 stripped ELF before the source change or split build starts.

The target directory and dependency artifacts are reused; `cargo clean -p`
removes the root package before the split build. The two actual root `rustc`
argument lists are identical. The wrapper records arguments and directly execs
the selected compiler; it does not rewrite them. This is argument capture, not
an OS-level process trace. Both compile commands use `--locked --offline`.

## What this confirms

The discriminator-attributed FeeConfig helper starts at 28,728 in both fresh
outputs. Its symbol extent changes from 1,144 to 1,232 bytes. The invalid-data
constant appears once at 29,392 in the baseline and twice at 29,392/29,608 in
the split. The captured original's inferred window is 1,248 bytes, with the same
constant at 36,720/36,936. `analysis.json` retains raw helper hashes, branch and
encoded call observations, plus allocated-section hashes. Stripping preserves
all allocated sections for both builds.

This independently confirms PR75's guard-only result. It is **not equality to the
captured original**, source promotion, exhaustive behavior, or a security claim.
The original helper extent is inferred; encoded CALL targets are not proof of
loader/runtime behavior. This run executes no program or transaction and adds no
differential cases. PR75 owns its separate behavioral and decoder evidence.

## Retained evidence and verification

`runs/` preserves exact provider artifact ZIPs, artifact digest metadata, run/job
metadata and member hashes. The successful ZIP contains compiler outputs,
source maps, actual compiler arguments, command logs and the executed workflow.
The workflow remains inside the evidence archive; this change installs no CI.

Two earlier attempts are retained: run 40373966778 failed with HTTP 504 during
compiler acquisition; run 40374587561 failed before Cargo because the container
user could not write the runner-owned evidence directory. The successful
controller adds bounded download retries and maps the host UID/GID without
relaxing the isolation settings. Neither failed attempt produced a program ELF.

`references/` retains exact PR75 source/descriptor/compressed ELF blobs with
revision, Git blob and SHA-256 identities. The verifier decompresses those
reference outputs and compares every byte with our independently built outputs.
The official tool archives and registry archives are not duplicated here; their
hash checks happened during the retained build. Offline verification checks their
recorded identities and locked checksums, not missing archive bytes.

```sh
python3 -B research/fees-guard-split-build/verify.py
python3 -I -B research/fees-guard-split-build/verify.py
python3 -B -m unittest discover -s research/fees-guard-split-build -p 'test_*.py'
```

Python 3.12+ standard library suffices. Verification reads the hash-bound original
capture from the repository and executes no ELF. There are 19 tests, including
source-delta, padding, actual-argument, offline-build and checksum rejection cases.

Replay requires Linux x86_64, Docker, curl and public acquisition access:

```sh
python3 -B research/fees-guard-split-build/run.py --output /absolute/new/output-directory
```

The output directory must not exist. The controller retains partial evidence on
failure. The 26-file snapshot preserves existing project source and upstream IDLs;
third-party materials retain their original ownership and licensing.

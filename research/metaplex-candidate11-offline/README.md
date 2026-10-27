# Metaplex candidate 11: independent offline compilation gate

**A fresh source build reproduces candidate 11's raw compiler output exactly:**
707,448 bytes, SHA256
`3bbaf27ff0c10ff68d8a195a82f39eadee266f324067bd0a66081710be30b4ec`.
No output padding, binary patching, relocation rewriting or normalization is used.
This reproduces an experimental candidate, not the captured deployment.

[Run 40338395968](https://github.com/startrack3r/pumpfun-source/actions/runs/40338395968)
executes revision `b3b81a8f5aced43de4f42bfc6bb8cc0d268197f0` on an Ubuntu 24.04
host, using the pinned Linux/amd64 image. This completes the raw-output prerequisite
for subsequent compiler-stage diagnostics identified in
[PR #58](https://github.com/lalalune/pumpfun-source/pull/58), following the fresh
compiler observation in [PR #53](https://github.com/lalalune/pumpfun-source/pull/53).
Neither PR is needed to replay this package.

## Inputs and execution

The complete unmodified upstream source archive at
`17e99434af5ead3e989c08f32af33609821d0bc0` is retained as `upstream-source.tar.gz`.
Its SHA256 is `a6a3d4d133c01877cfd3f5bb09bf1759d1c9139d924684f5790c0e08542dd092`.
Every one of its 812 files matches the historical baseline source manifest.
The exact eighteen-file recovery patch has SHA256
`fa954f23beae6c00eca4589e0208bf85a7d4dff185f18ff7863c629b12dd809c`;
all 812 resulting source hashes match candidate 11 before and after compilation.
The archive retains upstream's `LICENSE` and authorship metadata. The recovery
patch is the existing reconstructed source trial, not newly attributed uploader
source.

The image is
`solanafoundation/solana-verifiable-build@sha256:43206149a565ec35da95b1a909f4714f5d5f0d8241c31df24189e517acd18467`.
Its configuration ID is
`8a1c7e411dda3083f89fc82e9fbcbc57cfffed615853f11c124ef3df1443978f`.
The host Cargo toolchain is `1.69.0-x86_64-unknown-linux-gnu`. Official v1.37
platform-tools are authenticated before installation: 362,756,282 bytes,
SHA256 `8d5153589dbe19635affe937663cf4555a7e69a62d91ab4a1df064aaa8d5f066`.
The rustc-driver hash before and after compilation is
`e7d221509c0d5f5430175547b6d972e300892258bfa6e1b0cf1c4058a73ad9f2`.

Dependency acquisition runs separately via `cargo fetch --locked`, which does
not compile the program or its build scripts. All 537 downloaded registry archives
(76,307,184 compressed bytes) match the pinned `Cargo.lock` checksums. The sole
Git dependency, `rooster`, is checked at
`e424745fd5abfe1442fd37f3814d1f908302499d` with no tracked modifications. Cargo uses
the original `/usr/local/cargo/registry/...` and Git cache paths, avoiding path
changes introduced by a vendor directory.

A separate container compiles with `--network none`, `CARGO_NET_OFFLINE=true`,
and both build-wrapper and Cargo offline flags. It receives only the new source,
dependency caches and authenticated tools archive. No captured target or previous
candidate executable is mounted. Its root filesystem is ephemeral and writable;
the tool cache is tmpfs. All capabilities are dropped. The script changes ownership
only of its newly created public source/cache directories so container root can
write them without a DAC override capability. No host account configuration or
GitHub access setting is changed.

The compiler exits successfully. **The post-build SDK helper nevertheless attempts
an optional Criterion v2.3.3 download, which fails DNS resolution with networking
disabled.** The wrapper still exits zero and produces the exact raw candidate.
The complete stderr retains this failure and the compiler warnings; the verifier
reports it explicitly. This is not a claim that every internal SDK command
succeeded or that the SDK is free of network attempts in offline mode.

## Retained evidence and replay

The successful 49-member artifact ZIP is unchanged, SHA256
`e6158bb5e7793ffb2bbfa3246f50a39a0dc22ad47f9ae7e4384625818f972809`, matching the
provider digest. It contains the raw `.so`, all 18 command records and logs,
source manifests and patch, registry archive inventory, executed script/workflow,
source revision and actual result. `receipts.json.gz` retains provider run, job and
artifact metadata plus exact Git source-blob bindings. The workflow itself lives
only on a fork controller branch; upstream's workflow inventory is unchanged.

Python 3.11+ suffices for the default offline check. The optional patch replay
also uses Git in a temporary directory; neither mode executes the compiler or
target program. This package works outside the original repository checkout.

```sh
python3 -B research/metaplex-candidate11-offline/verify.py
python3 -B research/metaplex-candidate11-offline/verify.py --replay-patch
python3 -B research/metaplex-candidate11-offline/test_rebuild.py
python3 -B research/metaplex-candidate11-offline/test_verify.py
```

To compile again, use an isolated Linux x86_64 runner with Docker, curl, Git,
Python and permission to set ownership on its own temporary inputs, plus a fresh
output path. Acquisition requires network access; compilation does not.

```sh
python3 -B research/metaplex-candidate11-offline/rebuild.py --output /tmp/metaplex-candidate11-new
```

Two unsuccessful hosted attempts remain intact:

| Run | Point reached | Retained failure |
| --- | --- | --- |
| [40337545179](https://github.com/startrack3r/pumpfun-source/actions/runs/40337545179) | Before compilation | Container root could not write host-owned cache directories after capabilities were dropped. |
| [40337930953](https://github.com/startrack3r/pumpfun-source/actions/runs/40337930953) | All 537 registry archives authenticated; before compilation | The runner initially looked for the Git dependency manifest at its repository root; the pinned tree puts it under `program/`. |

Their exact artifacts have SHA256
`e7dac6619a291f260c800b88f90f73c07ebf18f5fbed73f99e237b4c99e4cb92` and
`e560f4d739a95b8dcd9c19713c78b77887973a7efdd27a1fa3e2af2940e5d5c3` respectively.
An initial Windows-only source preparation also detected CRLF conversion in the
18 patched files. Explicit per-command Git line-ending settings fixed preparation;
the mismatched files were retained locally, never accepted as candidate source.

## Remaining work

The existing candidate still has 1,509 differing positions in the padded comparison
with the capture, primarily in Utilize. This fresh build does not improve that
distance, recover historical loaded-library identity, choose the historical CPU,
or add runtime coverage. Its raw identity now permits subsequent instrumented
builds to be checked against the same gate before compiler traces are attributed
to candidate 11. The 793,991-byte allocation image and behavioral matches remain
separate evidence; no production or security conclusion follows from this result.

# Current cc1.10.0 consumer and native-build boundary

The current controlled collector build contains cc1.10.0 as a **host-layout library used by the blake3 build script**. It is not an observed SBF cc library unit. The complete239-fingerprint dependency-name census finds exactly one immediate cc edge, in blake3-1.8.2's host build-script unit. This narrows the current graph role but does not prove that changing cc has no output effect or that cc code is linked into the final SBF program.

## Authenticated current metadata and crate inputs

This packet pins the03ac2ad0 current-unit publication manifest, original9760c7 record manifest and exact retained analysis. It copies all239 fingerprint JSON records, all26 recorded build outputs and available stderr/root-output metadata, all176 observed registry manifests, relevant cc/blake3 dep-info, current lock, cache allowlist and build receipts as data. Every copied prior-record blob is authenticated against that raw manifest. No original program capture, decoder, compiler, native probe, SDK or target executes.

The cc source version is bound by current dep-info and registry-manifest/archive observations to1.10.0, checksum86e055fa6e3e40ad6187ba25b6855eeb635d5271f8e0f0e1e9a5826b8d75bea0. Its active fingerprint features are empty. The dependency-name tuple in blake3's build-script JSON is [17558417070209665034,"cc",false,16299391925053461121]. A separately retained **current**16-byte fingerprint file contains ASCII8192ae13991233e2; interpreting those hex bytes as little-endian u64 yields the tuple's final number. This is exact byte/serialization equality, not a claim that it is Rust -Cmetadata, Cargo's complete matching algorithm, or a before/after attestation. The earlier JSON-only unit capture did not include this16-byte file.

Among all176 observed registry manifests, the only cc dependency declaration is blake3-1.8.2 [build-dependencies.cc] version1.1.12. Under ordinary Cargo caret1.x semantics this permits >=1.1.12,<2.0.0; it does not require1.10.0. Thus an older compatible cc release is plausible within the declared range, but this packet does not authenticate publication/availability of a concrete older choice, choose/install one, regenerate a lock or run a build trial. Full transitive constraints and original deployment dependency provenance remain independent gates.

## Immediate consumer features and onward source context

Blake3's host build-script and SBF library records both carry default,std,traits-preview. The library's dependency-name records do not include cc directly. Three recorded SBF-layout units name blake3: solana-blake3-hasher2.2.1, solana-message2.4.0 and solana-program2.3.0. Their exact normalized manifest declarations are retained from lock/allowlist-authenticated archives: all specify1.5.5; message/program request traits-preview, while hasher has a solana-target optional declaration and a non-solana declaration. These are literal metadata/source references, not a new complete target/cfg resolver proof. Opaque fingerprint dependency identifiers are not universally converted into transitive edges by numerical analogy.

Five retained archives contain cc, blake3 and those three immediate blake3 consumer manifests. Every retained Rust/source/manifest member is byte-equal to its authenticated archive. cc source/build helper behavior is read only as source data; none is imported or executed. Source completeness and actual compiler command tracing remain separate matters.

## CC selection is explicitly recorded

A prior parent hypothesis that this build-script's CC path would resolve into v1.44 was incorrect and is retracted. The blake3 run-build fingerprint contains RerunIfEnvChanged CC with value:

`.../cto-wallet-collector-build-01/build-01/sdk/dependencies/platform-tools/llvm/bin/clang`

CFLAGS is null. The current symlink ancestors resolve SDK dependencies/platform-tools to `~/.cache/solana/v1.52/platform-tools`, and the leaf clang alias to clang-20. Its current104,030,072 bytes hash to3c5752d43548edbde66dcd61de941bfa30b4d175e32d3b301bd2de015de75b39. That is distinct from selected Rust v1.44 and is outside the earlier three in-tree v1.44 executable pins. The current pointer/file hash is retained without copying the large executable or running it. It does not prove that this compiler was invoked or had the same bytes/path during the past build.

All26 recorded build outputs lack explicit rustc-link-lib/rustc-link-search directives. Nevertheless, the CC selection record exists. Its `cargo:rerun-if-env-changed=CC` line is emitted unconditionally by blake3 build.rs and is not an invocation trace. Absence of link directives alone does not prove that no C compiler/probe/native output was involved.

The archived blake3 build.rs calls cc::Build through target-specific x86 or ARM native-build paths, with wasm enabling a Rust SIMD cfg rather than native compilation. Given TARGET=sbf-solana-solana and the recorded absent PURE/NEON flags, its main architecture predicates would not enter those cc compilation paths. Recorded output includes cfg-declaration and rerun lines but no ffi/neon selected cfg or explicit link directive. This supports a **conditional source-path inference only**: actual environment/argv/probe execution is not fully recorded here, so no categorical no-native-invocation proof is made. The fact that a build script is a host executable does not imply its TARGET is the host architecture.

## Temporal and byte-identity scope

Root separately completed the176-package official publication/deployment-time witness and reported cc1.10.0 publication after the Pump deployment. That sealed temporal packet is not included or authenticated by this review; its independent review is separate. If established there, stock registry availability can exclude this current resolved graph as the historical public-registry graph even when cc is only a host build dependency and even if no SBF output effect is demonstrated. Private/vendor/pre-release source exceptions remain open. This packet does not promote a date claim from a parent message into authenticated metadata.

No cc version, lock, source, recipe, selected artifact or status is changed. Remaining gates include a concrete pre-deployment candidate registry resolution, complete build-unit/feature/compiler command and native-output tracing if needed, separately reviewed trial builds, comparison of their entire output, and authentic historical provenance. Current host dependency presence is not proof of linked SBF code or whole-original identity.

## Replay

Run `python -B verify.py --expected-seal <manifest SHA256>`. The verifier uses only standard-library data analysis of copied raw Cargo/dep-info/source/archive bytes. It invokes no collector, build script, compiler, VM, target, network or archived executable. `input-bindings.json` identifies each original local path and whether its bytes are prior sealed data, lock/allowlist-authenticated archives or a new current-only file observation. There were no collection or verification failures during this bounded consumer review.

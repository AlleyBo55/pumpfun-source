# Archived Git provenance for mpl-token-metadata 1.13.2-beta.1

One of the five Git revisions left unresolved by the
[published-crate study](../metaplex-published-source/README.md) is preserved by
Software Heritage. Its commit object and the directory chain now connect
**all 162 nongenerated members** of the published `1.13.2-beta.1` crate to
specific Git blobs. This resolves that release's content association with its
declared commit; it does not identify the deployed program's source.

## Recovery and object verification

The crate's checksum-verified `.cargo_vcs_info.json` declares commit
`c65f144e74b5410cde1245ebe3d4412ff7acf7a8` and package path
`programs/token-metadata/program`. The
[archive revision response](https://archive.softwareheritage.org/api/1/revision/c65f144e74b5410cde1245ebe3d4412ff7acf7a8/)
contains a nonsynthetic Git revision dated 2023-08-14, with root tree
`2d81a2ee1408c5f34a63f21eb7850c8a05e39eef`.

The verifier reconstructs the complete commit payload from its tree, parent,
author/committer fields, timestamps, timezones and message, then checks its
Git object SHA-1 against the crate's declared revision. It reconstructs 24
complete directory objects, with Git's byte ordering and modes, and checks
every tree hash. Following those verified parent/child links establishes
the complete path from the commit root to each compared archive member.
Finally, it computes each distributed file's Git blob hash and checks the
tree entry, byte length and archived SHA-256 metadata.

| Published archive contents | Comparison |
| --- | --- |
|160 ordinary files|Exact bytes match their paths beneath the declared package directory.|
|`Cargo.toml.orig`|Exact bytes match the package's original `Cargo.toml` Git blob.|
|`LICENSE`|Exact bytes match root `LICENSE`, as directed by `license-file = "../../../LICENSE"` in the original manifest.|
|Normalized `Cargo.toml` and `.cargo_vcs_info.json`|Cargo-generated files, explicitly excluded from Git file equality; the latter supplies the revision/path declaration.|

The complete published crate is 198,229 bytes, SHA256
`2b6cb247b58f6969d1c97288a5c859f571cdb730904aca99194708e9c21a2d13`.
All five queried releases' original crate archives, the saved registry response
and original download receipts are included so each revision query can be
derived from checksum-verified distributed metadata.

The recovered Utilize blob has SHA256
`203ac94655f6268d5eae95de2b3dffcb47065bbeb713d8da08a9bbdeca29f53e`.
It is the same source already inspected in the published-crate study. This
adds a verifiable Git content association, not a new handler variant or a
reason to repeat a source build.

## Bounded query results

On 2026-10-26, global GitHub commit searches using the five complete SHA strings
returned no commits through the connector. Those saved search responses are
not an exhaustive audit of forks, unreachable objects or private history.
Software Heritage's exact revision endpoint then returned:

|Release|Declared revision|Response|
|---|---|---|
|1.13.1-beta.1|`1f88578d3bb2633ad903740a12423ea2efa8069d`|404, revision not found|
|1.13.1|`f5559314647a1bfdea2738f1c325fe109caebe7b`|404, revision not found|
|2.0.0-beta.1|`1a3d0a05d841bd31a7e8a9d54e9c6be5be0fa4c8`|404, revision not found|
|1.13.2-beta.1|`c65f144e74b5410cde1245ebe3d4412ff7acf7a8`|200; commit, 24 trees and 162 file associations verified|
|1.13.2|`675e159611d4106f8b1d3393168c4b764fa0affd`|404, revision not found|

All five complete responses and their URL/status/size/hash receipts remain.
The four failures mean unresolved at this endpoint and observation time; they
do not prove the commits never existed or are unavailable elsewhere. Original
GitHub failure evidence in the earlier package is preserved unchanged.

## Offline replay

Using Python 3.11 or newer, from the repository root:

```sh
python -B research/metaplex-archived-revision/verify.py
python -B research/metaplex-archived-revision/test_verify.py
python -B research/metaplex-archived-revision/verify.py --git-object-check
```

The first command uses only the standard library and retained files. The
optional last command also checks all 25 reconstructed commit/tree payloads
against `git hash-object --literally` in a fresh temporary directory, with
lazy fetching disabled; it writes no Git objects. It hashes the exact payloads,
not a complete repository fsck. Both modes pass, as do all 14 portable tests
on Windows Python 3.13.7. Tests cover commit/timezone/parent changes, synthetic
revisions, directory order/modes/targets, duplicate names, missing path links,
incorrect package/license mapping, changed file bytes and metadata, missing
negative observations and replay from a minimal relocated package.

An initial optional Git cross-check inside the partial checkout triggered
unsuccessful `.gitmodules` promisor lookups during Git's object validation.
Its stderr is retained in `initial-git-crosscheck.stderr.log`. The corrected
literal-hashing check runs outside the checkout and requires empty stderr;
all 25 object checks then pass without those lookups.

## Limits and licensing

Git hashes establish the relationship among the supplied object bytes and the
published crate's declared commit. This does not authenticate the named author,
prove which GitHub repository hosted that commit, establish complete parent
history, or associate the deployed executable with this release. Only the
24 directory objects needed for these paths are retained; unrelated repository
contents are not claimed to be recovered. The two generated archive files are
not claimed to equal Git files.

No compiler, SDK, VM, original target or candidate executable was run. No raw
byte identity, candidate selection, diagnostic coordinate, source patch or
security claim changes. The archives are unmodified third-party distributions
under their included Metaplex NFT Open Source License; repository licensing
does not replace that license. Source and public commit metadata are retained
solely as reproducible provenance evidence.

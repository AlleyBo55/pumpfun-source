# Portable ATA monomorphization proof verification

The original proof's optional repository check references the former scratch
path `work/ata-toolchain-audit/official/version.md`. That file is published at
`repro/identity-audit/2026-10-25/ata/official/version.md`: both bindings specify
247 bytes and SHA256
`390cb9c02aa9dc28dfbee87f923dc1e0db31d1f41546fe49111d790ef208a2d3`.
The historical command fails on a clean clone because the scratch path is absent.

Run the unchanged proof with the published receipts:

```sh
python3 -B repro/ata/portable-monomorph-proof/verify_ata_monomorph_order.py
python3 -B repro/ata/portable-monomorph-proof/test_verify_ata_monomorph_order.py
```

The wrapper pins the original package manifest to SHA256
`5808bb8fae39ea750f33119b31f8856e91a5c0640cc68a8c0292609378e6cb08`
before parsing it or executing the proof. It verifies that manifest, checks every external
receipt's exact hash and length, and supplies those bytes under their original
names in a temporary directory. It then executes the unchanged proof with its
repository check enabled. Only the version receipt has an explicit published
path alias. Missing, changed, escaping or symlinked inputs fail; an old scratch
file cannot substitute for the published receipt. The temporary directory is
removed after verification. No evidence package or binary is modified.

The regression test executes this workflow from a minimal copied checkout in a
different directory, with no historical scratch file. Negative cases cover
changed external bytes, a missing published receipt, symlink substitution and
proof-script modification, including a script replacement with a rewritten
manifest record.

This repairs reproducibility of the static evidence check. It does not add a
source build, runtime comparison or historical recipe attribution. ATA's
307-position raw residual and the whole-core binary identity count remain
unchanged.

The new wrapper and tests live beside this evidence, preserving the existing pinned root script set. The immutable original proof remains in its own sibling package.

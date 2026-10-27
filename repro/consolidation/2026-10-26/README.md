# Consolidation transition (2026-10-26)

The pass-27 CI guard pins every current asset by SHA-256, including the root
README and the CI workflow. The 2026-10-26 consolidation rewrote the README, so
this package records that change as an explicit, reviewable transition instead of
weakening the guard.

- `transition.json` lists each changed asset with its pass-27 `before` hash and its
  new `after` hash: `README.md` and `.github/workflows/verify.yml`.
- `guard.py` runs an unchanged pass-27 entrypoint (`verify_current.py`,
  `verify_metadata.py` or `verify_portable_crypto.py`). It first checks that this
  package's files match its own manifest (an internal seal that nothing else pins),
  that every pass-27 guard file matches the pass-27 manifest whose hash is hard-coded
  (checked before any pass-27 code is imported), and that `transition.json`
  is exactly the reviewed revision (`TRANSITION_SHA256`) covering exactly
  `REVIEWED_PATHS`. Because those two constants live in `guard.py`, any re-pin is a
  visible code change for review. It
  then applies the transition only while the current-asset check runs. Every other
  pass-27 check, including the pinned script and workflow sets, sources,
  candidates, status files, history and attributes, is unchanged.

```sh
python3 -B repro/consolidation/2026-10-26/guard.py verify_current.py \
  --repo . --metadata repro/layered-passes/pass-27/current-metadata
```

To revise the README again, update its `after` hash in `transition.json`. To re-pin
another asset, add it there with its pass-27 hash as `before`, remove it from
`unchanged`, confirm no immutable checkpoint verifier pins it separately, and add its
path to `REVIEWED_PATHS` in `guard.py`. Either way, set `TRANSITION_SHA256` in
`guard.py` to the new `transition.json` hash and reseal `manifest.json` and
`manifest.sha256`. A data edit alone fails the guard.

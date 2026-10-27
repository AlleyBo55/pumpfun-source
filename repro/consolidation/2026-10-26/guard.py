#!/usr/bin/env python3
"""Run an unchanged pass-27 guard entrypoint with the reviewed consolidation asset transition.

Pass-27 pins every current asset by SHA-256. The consolidation changes exactly the
assets listed in transition.json. Each must still hold its pass-27 hash as the
`before` value; the current file must equal `after`. Every other pass-27 check
(sources, candidates, script/workflow sets, history, attributes, metadata,
signatures) runs unchanged, and the returned bindings stay the pass-27 record.
"""
import hashlib, json, runpy, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P27 = ROOT / 'repro/layered-passes/pass-27/current-guards'
P27_GUARD_SEAL = 'a828f3577eaa3c14c2f66c4c5e75ef06eb05703700cb70f1c4318899eaaecba2'
ENTRYPOINTS = ('verify_current.py', 'verify_metadata.py', 'verify_portable_crypto.py')
# The reviewed transition is pinned in code, so re-pinning another asset or a new
# README revision is a reviewable change to this file, not a data edit plus reseal.
REVIEWED_PATHS = frozenset({'README.md', '.github/workflows/verify.yml'})
TRANSITION_SHA256 = 'dd72c4c56dc9c19c94b23c105e2906f0f340a7bae9cd7f778c5874371ae2524e'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def package_integrity(folder, seal):
    """Check every member of a sealed package before any of its code is imported."""
    sealed = (folder / 'manifest.json', folder / 'manifest.sha256')
    assert sha(sealed[0]) == seal and sealed[1].read_text().split()[0] == seal, ('package seal changed', str(folder))
    manifest = json.loads(sealed[0].read_text())
    rows = manifest.get('files', manifest)
    actual = {str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file() and p not in sealed}
    assert actual == set(rows), ('package membership changed', str(folder))
    for name, row in rows.items():
        path = folder / name
        digest = row['sha256'] if isinstance(row, dict) else row
        assert not path.is_symlink() and sha(path) == digest, name
        if isinstance(row, dict) and 'bytes' in row:
            assert path.stat().st_size == row['bytes'], name


def reviewed_changes():
    assert sha(HERE / 'transition.json') == TRANSITION_SHA256, 'transition.json differs from the reviewed transition'
    transition = json.loads((HERE / 'transition.json').read_text())
    assert transition['base_guard_seal'] == P27_GUARD_SEAL
    changes = transition['asset_changes']
    assert len(changes) == len(REVIEWED_PATHS) and {c['path'] for c in changes} == REVIEWED_PATHS
    return changes


def install_transition(common, changes):
    original = common.Context.current

    def current(self):
        assets = self.F['assets']
        for change in changes:
            assert assets[change['path']] == change['before_sha256'], ('transition base is not the pass-27 pin', change['path'])
            assets[change['path']] = change['after_sha256']
        try:
            return original(self)
        finally:
            for change in changes:
                assets[change['path']] = change['before_sha256']

    common.Context.current = current


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ENTRYPOINTS:
        sys.exit(f'usage: guard.py {{{",".join(ENTRYPOINTS)}}} <pass-27 arguments>')
    package_integrity(HERE, sha(HERE / 'manifest.json'))
    package_integrity(P27, P27_GUARD_SEAL)
    changes = reviewed_changes()
    sys.path.insert(0, str(P27))
    import common
    install_transition(common, changes)
    entrypoint = sys.argv[1]
    sys.argv = [str(P27 / entrypoint), *sys.argv[2:]]
    runpy.run_path(str(P27 / entrypoint), run_name='__main__')


if __name__ == '__main__':
    main()

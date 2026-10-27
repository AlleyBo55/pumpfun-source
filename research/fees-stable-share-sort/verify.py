#!/usr/bin/env python3
"""Verify the stable-sort recovery and original syscall/caller attribution."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    for name, expected in json.loads((HERE / 'manifest.json').read_text()).items():
        path = HERE / name
        assert path.resolve().is_relative_to(HERE)
        assert sha(path.read_bytes()) == expected, name
    experiment = json.loads((HERE / 'experiment.json').read_text())
    assert len(experiment['harness_sha256']) == 187
    for name, expected in experiment['harness_sha256'].items():
        assert sha((ROOT / name).read_bytes()) == expected, name
    for label, variant in experiment['variants'].items():
        assert len(variant['input_sha256']) == 26
        for name, expected in variant['input_sha256'].items():
            override = variant['source_overrides'].get(name)
            path = HERE / override if override else ROOT / name
            assert sha(path.read_bytes()) == expected, (label, name)
        replay = experiment['strip_replay'][label]
        assert replay['exit_code'] == 0
        assert replay['sha256'] == variant['files']['candidate']['sha256']
        build = json.loads((HERE / 'builds' / f'{label}-result.json').read_text())
        assert build['exit_code'] == build['strip_exit_code'] == 0
        assert build['source_unchanged'] and build['input_sha256'] == variant['input_sha256']
    before = (HERE / 'sources/control-sharing-update.rs').read_text()
    after = (HERE / 'sources/stable-sharing-update.rs').read_text()
    assert before.count('keys.sort_unstable();') == 2
    assert after == before.replace('keys.sort_unstable();', 'keys.sort();')
    for name in ('lib.rs', 'types.rs', 'state.rs', 'sharing-config.rs'):
        assert (HERE / f'sources/control-{name}').read_bytes() == (HERE / f'sources/stable-{name}').read_bytes()
    spec = importlib.util.spec_from_file_location('stable_share_sort', HERE / 'map_windows.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    actual = module.analyze()
    assert actual == json.loads(gzip.decompress((HERE / 'analysis.json.gz').read_bytes()))
    for label, descriptor in experiment['behavioral_receipts'].items():
        report = json.loads(gzip.decompress((HERE / descriptor['path']).read_bytes()))
        assert report['candidate_sha256'] == experiment['variants'][label]['files']['candidate']['sha256']
        assert report['original_sha256'] == actual['original_sha256']
        assert report['case_count'] == descriptor['cases'] == 17331
        assert not report['mismatches'] and len(report['suites']) == 18
        for suite in report['suites'].values():
            assert suite['candidate_sha256'] == report['candidate_sha256']
            assert suite['original_sha256'] == report['original_sha256']
            assert not suite.get('mismatches', suite.get('failures'))
            assert suite.get('mismatch_count', 0) == 0
    print('PASS: original validator/callee attribution, complete merge-sort/memmove signatures, two-line source change, and 34,662 cases')


if __name__ == '__main__':
    main()

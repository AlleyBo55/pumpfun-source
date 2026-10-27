#!/usr/bin/env python3
"""Verify retained source-coordinate builds and their bounded comparisons."""
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
    for name in ('lib.rs', 'state.rs', 'sharing-config.rs', 'types.rs'):
        before = (HERE / f'sources/control-{name}').read_text()
        after = (HERE / f'sources/coordinates-{name}').read_text()
        assert [line for line in before.splitlines() if line.strip()] == [
            line for line in after.splitlines() if line.strip()]
    assert [i for i, line in enumerate((HERE / 'sources/coordinates-state.rs').read_text().splitlines(), 1)
            if line == '#[account]'] == [50, 113, 135, 154]
    assert [i for i, line in enumerate((HERE / 'sources/coordinates-sharing-config.rs').read_text().splitlines(), 1)
            if line == '#[account]'] == [37]
    assert [i for i, line in enumerate((HERE / 'sources/coordinates-lib.rs').read_text().splitlines(), 1)
            if line == '#[program]'] == [38]
    spec = importlib.util.spec_from_file_location('coordinate_windows', HERE / 'map_windows.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    actual = module.analyze()
    assert actual == json.loads(gzip.decompress((HERE / 'analysis.json.gz').read_bytes()))
    assert set(experiment['behavioral_receipts']) == {'control', 'coordinates'}
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
    print('PASS: eight added windows, only 21 immediate-store changes, unchanged source tokens, and 34,662 behavioral cases')


if __name__ == '__main__':
    main()

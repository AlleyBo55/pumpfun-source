#!/usr/bin/env python3
"""Check the retained corrected-fixture CPI receipts and rebuild records; executes no program."""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def creator_checker(repo):
    path = repo / 'research/mayhem-creator-fixture/verify.py'
    spec = importlib.util.spec_from_file_location('creator_fixture_verify', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(repo):
    inputs = json.loads((HERE / 'inputs.json').read_text())
    binaries = inputs['binaries']
    for name, row in binaries.items():
        require(sha(repo / row['path']) == row['sha256'], 'Binary changed: ' + name)
    harness_path = repo / inputs['harness_path']
    require(sha(harness_path) == inputs['harness_sha256'], 'Harness changed')
    checker = creator_checker(repo)
    harness = checker.load_harness(repo)
    results = {}
    for name, row in inputs['receipts'].items():
        path = HERE / name
        require(sha(path) == row['sha256'], 'Receipt bytes changed: ' + name)
        report = json.loads(gzip.decompress(path.read_bytes()))
        require(report['script_sha256'] == inputs['harness_sha256'], 'Receipt harness binding: ' + name)
        require(report['original_pump_sha256'] == binaries['original_pump']['sha256'], 'Original Pump binding')
        require(report['original_mayhem_sha256'] == binaries['original_mayhem']['sha256'], 'Original Mayhem binding')
        require(report['candidate_pump_sha256'] == binaries[row['candidate_pump']]['sha256'], 'Candidate Pump binding')
        require(report['candidate_mayhem_sha256'] == binaries[row['candidate_mayhem']]['sha256'], 'Candidate Mayhem binding')
        # Reuse the creator-fixture checker: signatures, Borsh inputs, 6030 rejections,
        # persisted distinct creators and recomputed comparison fields.
        results[name] = checker.check_report(report, harness)
    for name, row in inputs['rebuild'].items():
        path = HERE / name
        require(sha(path) == row['sha256'], 'Rebuild record changed: ' + name)
        record = json.loads(path.read_text())
        comparison = record['comparison']
        require(record['program'] == 'mayhem' and record['selected_toolchain'] == 'v1.52', 'Rebuild recipe')
        require(comparison['candidate_sha256'] == row['candidate_sha256'], 'Rebuild output hash')
        require(comparison['candidate_bytes'] == row['candidate_bytes'], 'Rebuild output size')
        require(comparison['original_sha256'] == binaries['original_mayhem']['sha256'], 'Rebuild comparison target')
        require(comparison['full_byte_equality'] is False, 'Unexpected identity claim')
        libs = [value for key, value in record['source_sha256'].items() if key.endswith('programs/mayhem/src/lib.rs')]
        require(libs == [sha(repo / row['source_lib_rs'])], 'Rebuild source binding: ' + name)
    pre = json.loads((HERE / 'rebuild/pre-correction/build-comparison.json').read_text())
    require(pre['comparison']['candidate_sha256'] == binaries['pre_correction_overlay_mayhem']['sha256'],
            'Pre-correction rebuild does not reproduce the committed candidate')
    summary = {'saved_evidence': 'PASS',
               'cpi_receipts': {name: {'cases': r['cases'], 'mismatches': r['mismatches']} for name, r in results.items()},
               'pre_correction_rebuild_reproduces_committed_candidate': True,
               'post_correction_rebuild_sha256': inputs['rebuild']['rebuild/post-correction/build-comparison.json']['candidate_sha256'],
               'full_byte_equality': False}
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=HERE.parents[1])
    verify(parser.parse_args().repo.resolve())

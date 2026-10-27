"""Retry the recorded command after a dependency-load failure; preserve the failed log."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

root = Path(__file__).resolve().parent / 'build-01'
ev = root / 'evidence'
spec = importlib.util.spec_from_file_location('driver', ev / 'build_pair.py')
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
commands = json.loads((ev / 'commands.json').read_text())
argv = next(r['argv'] for r in commands if r['label'] == 'constraint-build')
records = []
def run(label, command):
    row = {'label': label, 'argv': command, 'exit_code': None}
    records.append(row)
    driver.save(ev / 'retry-commands.json', records)
    with (ev / (label + '.log')).open('xb') as out:
        result = subprocess.run(command, stdout=out, stderr=subprocess.STDOUT)
    row.update(exit_code=result.returncode, log_sha256=driver.sha(ev / (label + '.log')))
    driver.save(ev / 'retry-commands.json', records)
    assert result.returncode == 0, label
run('constraint-build-retry', argv)
shutil.copy2(root / 'constraint-target/sbpf-solana-solana/release/mayhem_recovered.so', ev / 'constraint.symbols.so')
strip = next(r['argv'] for r in commands if r['label'] == 'baseline-strip')
strip = [word.replace('/baseline-source,', '/constraint-source,').replace('/baseline-target,', '/constraint-target,') for word in strip]
run('constraint-strip', strip)
shutil.copy2(root / 'constraint-target/candidate.so', ev / 'constraint.so')
for name in ('baseline', 'constraint'):
    actual = driver.inventory(root / (name + '-source'))
    driver.save(ev / (name + '-source-after.json'), actual)
    assert actual == json.loads((ev / (name + '-source-before.json')).read_text())
before = json.loads(gzip.decompress((ev / 'registry-before.json.gz').read_bytes()))
after = driver.inventory(root / 'cargo-home/registry')
(ev / 'registry-after.json.gz').write_bytes(gzip.compress(json.dumps(after, sort_keys=True).encode(), mtime=0))
assert before == after
assert driver.inventory(root / 'tools') == json.loads(gzip.decompress((ev / 'tools-before.json.gz').read_bytes()))
driver.save(ev / 'result.json', {'status': 'BUILT_AFTER_RECORDED_RETRY',
    'retry_reason': 'First constraint build reported E0463 loading anchor_syn. The completed rlib and rmeta then matched baseline bytes; the exact Cargo command was retried without source or compiler changes.',
    'original_binary_mounted': False, 'source_unchanged_during_builds': True, 'registry_unchanged_during_builds': True,
    'tools_unchanged_during_builds': True,
    'outputs': {p.name: {'sha256': driver.sha(p), 'bytes': p.stat().st_size} for p in ev.glob('*.so')}})
shutil.copy2(__file__, ev / 'retry_constraint.py')
print('Recorded retry and strip completed')

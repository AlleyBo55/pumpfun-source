"""Isolate init_if_needed on the already tested signer-constraint source."""
import gzip
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
source = root / 'vault-source'
shutil.copytree(root / 'constraint-source', source)
lib = source / 'programs/mayhem/src/lib.rs'
before = '#[account(init, payer = payer, associated_token::mint = mint, associated_token::authority = sol_vault, associated_token::token_program = token_program)]'
after = before.replace('account(init,', 'account(init_if_needed,')
text = lib.read_text()
assert text.count(before) == 1
lib.write_text(text.replace(before, after))
shutil.copytree(source, ev / 'vault-source')
inputs = driver.inventory(source)
driver.save(ev / 'vault-source-before.json', inputs)
target = root / 'vault-target'
target.mkdir()
commands = json.loads((ev / 'commands.json').read_text())
build = next(r['argv'] for r in commands if r['label'] == 'baseline-build')
strip = next(r['argv'] for r in commands if r['label'] == 'baseline-strip')
records = []
def run(label, command):
    command = [arg.replace('/baseline-source,', '/vault-source,').replace('/baseline-target,', '/vault-target,') for arg in command]
    row = {'label': label, 'argv': command, 'exit_code': None}
    records.append(row)
    driver.save(ev / 'vault-commands.json', records)
    with (ev / (label + '.log')).open('xb') as out:
        result = subprocess.run(command, stdout=out, stderr=subprocess.STDOUT)
    row.update(exit_code=result.returncode, log_sha256=driver.sha(ev / (label + '.log')))
    driver.save(ev / 'vault-commands.json', records)
    assert result.returncode == 0, label
run('vault-build', build)
shutil.copy2(target / 'sbpf-solana-solana/release/mayhem_recovered.so', ev / 'vault.symbols.so')
run('vault-strip', strip)
shutil.copy2(target / 'candidate.so', ev / 'vault.so')
driver.save(ev / 'vault-source-after.json', driver.inventory(source))
assert driver.inventory(source) == inputs
assert driver.inventory(root / 'tools') == json.loads(gzip.decompress((ev / 'tools-before.json.gz').read_bytes()))
assert driver.inventory(root / 'cargo-home/registry') == json.loads(gzip.decompress((ev / 'registry-before.json.gz').read_bytes()))
driver.save(ev / 'vault-result.json', {'status': 'BUILT', 'original_binary_mounted': False,
    'source_unchanged_during_build': True, 'registry_unchanged_during_build': True, 'tools_unchanged_during_build': True,
    'outputs': {p.name: {'sha256': driver.sha(p), 'bytes': p.stat().st_size} for p in ev.glob('vault*.so')}})
shutil.copy2(__file__, ev / 'build_vault.py')
print('Vault variant built')

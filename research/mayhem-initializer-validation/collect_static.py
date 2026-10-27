"""Retain bounded original initializer disassembly separately from compiler inputs."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = Path('/Users/barry/projects/pumpfun-source')
TOOLS = HERE / 'build-01/tools'
IMAGE = 'rust@sha256:948f9b08a66e7fe01b03a98ef1c7568292e07ec2e4fe90d88c07bb14563c84ff'
OUT = HERE / 'static'
OUT.mkdir(exist_ok=False)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
base = ['docker', 'run', '--rm', '--platform', 'linux/amd64', '--network', 'none',
        '--mount', f'type=bind,src={TOOLS},dst=/tools,readonly',
        '--mount', f'type=bind,src={ROOT}/evidence/original/mayhem,dst=/comparison,readonly',
        IMAGE, '/tools/llvm/bin/llvm-objdump']
records = []
for name, start, end in [('wrapper', 528112, 528568), ('parser', 430840, 447984)]:
    command = base + ['-d', f'--start-address={start}', f'--stop-address={end}', '/comparison/deployed.so']
    result = subprocess.run(command, capture_output=True, check=True)
    assert not result.stderr
    (OUT / (name + '.asm')).write_bytes(result.stdout)
    records.append({'path': name + '.asm', 'start': start, 'end': end, 'argv': command,
                    'exit_code': result.returncode, 'sha256': sha(OUT / (name + '.asm'))})
version = subprocess.check_output(base + ['--version']).decode()
report = {'original_sha256': sha(ROOT / 'evidence/original/mayhem/deployed.so'),
          'objdump_sha256': sha(TOOLS / 'llvm/bin/llvm-objdump'), 'objdump_version': version,
          'address_kind': 'hexadecimal byte addresses; these ELF .text virtual addresses equal file offsets',
          'window_boundaries': 'Inferred direct-call entry boundaries, not historical debug symbols',
          'captures': records}
(OUT / 'capture.json').write_text(json.dumps(report, indent=2) + '\n')
print('Retained two bounded listings')

"""Build a retained Fees snapshot using the pinned canonical v1.44 recipe."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
label = sys.argv[1]
source = ROOT / 'work/fees-parser' / (label + '-source')
output = ROOT / 'work/fees-parser' / (label + '-build')
workspace = ROOT / 'work/fees-parser/baseline-source'
assert source.is_dir() and not output.exists()
names = sorted(str(p.relative_to(source)) for p in source.rglob('*') if p.is_file())
assert len(names) >= 26 and all(not name.startswith('../') for name in names)
sha = lambda raw: hashlib.sha256(raw).hexdigest()
inactive_sources = {}
for old in (workspace / 'programs/pump-fees/src').rglob('*.rs'):
    relative = str(old.relative_to(workspace))
    if relative not in names:
        inactive_sources[relative] = sha(old.read_bytes())
        old.unlink()
inputs = {}
for name in names:
    inputs[name] = sha((source / name).read_bytes())
    (workspace / name).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source / name, workspace / name)
toolchain = ROOT / 'work/toolchains/v1.44'
rustc = toolchain / 'rust/bin/rustc'
assert sha(rustc.read_bytes()) == 'c8807b7ebede8578ac5a257ea333780f9d89bd356064fd8184af7e996cb71a97'
env = os.environ.copy()
env.update(CARGO_HOME=str(ROOT / 'work/fees-parser/cargo-home'),
           RUSTUP_HOME=str(ROOT / 'work/fees-parser/rustup-home'),
           CARGO_TARGET_DIR=str(ROOT / 'work/fees-parser/v144-canonical-target'),
           RUSTC=str(rustc), RUSTFLAGS='-Zremap-cwd-prefix=',
           CC=str(toolchain / 'llvm/bin/clang'), AR=str(toolchain / 'llvm/bin/llvm-ar'))
env['PATH'] = str(toolchain / 'rust/bin') + ':' + env['PATH']
command = [str(toolchain / 'rust/bin/cargo'), 'rustc', '--verbose', '--manifest-path',
           str(workspace / 'programs/pump-fees/Cargo.toml'), '--release', '--target',
           'sbpf-solana-solana', '--locked', '--offline', '--jobs', '2', '--lib', '--',
           '--remap-path-prefix=' + str(workspace / 'programs/pump-fees/src/../../../pump-fees-math') + '/=pump-fees-math/',
           '--remap-path-prefix=' + str(workspace / 'pump-fees-math') + '/=pump-fees-math/',
           '--remap-path-prefix=programs/pump-fees/src/../../../pump-fees-math/=pump-fees-math/']
output.mkdir()
(output / 'launch.json').write_text(json.dumps(dict(command=command, input_sha256=inputs,
    source_snapshot=str(source), rustc_sha256=sha(rustc.read_bytes()), inactive_source_removed=inactive_sources), indent=2) + '\n')
with (output / 'build.log').open('w') as log:
    status = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
strip_status = None
if status == 0:
    image = ROOT / 'work/fees-parser/v144-canonical-target/sbpf-solana-solana/release/pump_fees_candidate.so'
    shutil.copyfile(image, output / 'symbols.so')
    (output / 'artifacts').mkdir()
    strip_status = subprocess.run([str(ROOT / 'work/toolchains/v1.52/llvm/bin/llvm-objcopy'),
        '--strip-all', str(image), str(output / 'artifacts/pump_fees_candidate.so')], capture_output=True).returncode
unchanged = all(sha((workspace / name).read_bytes()) == expected for name, expected in inputs.items())
(output / 'result.json').write_text(json.dumps(dict(exit_code=status, strip_exit_code=strip_status,
    source_unchanged=unchanged, input_sha256=inputs), indent=2) + '\n')
print(label, 'build exit', status, 'strip', strip_status, 'source unchanged', unchanged)
sys.exit(status or strip_status or (not unchanged))

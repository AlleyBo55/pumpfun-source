#!/usr/bin/env python3
"""Build a fixed Mayhem overlay and one signer-constraint change offline in Docker."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tomllib

TOOL_SHA = '8b3861e93daf085ec12b65c4fac374d9bec4587a3de16871da6b08ab0c1d907e'
TARGET = 'sbpf-solana-solana'
BEFORE = '''    #[account(seeds = [b"mint-authority"], bump, seeds::program = state::PUMP_ID)]
    pub mint_authority: Signer<'info>,'''
AFTER = '''    #[account(signer, seeds = [b"mint-authority"], bump, seeds::program = state::PUMP_ID)]
    pub mint_authority: UncheckedAccount<'info>,'''

def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def inventory(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*')) if p.is_file()}

def save(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--archive', type=Path, required=True)
    ap.add_argument('--image', required=True, help='Official rust image pinned by sha256 digest')
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert '@sha256:' in a.image
    assert sha(a.archive) == TOOL_SHA, 'Tool archive checksum mismatch'
    root = a.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    ev = root / 'evidence'
    ev.mkdir()
    shutil.copy2(__file__, ev / 'build_pair.py')
    commands = []
    def run(label, argv):
        row = {'label': label, 'argv': argv, 'exit_code': None}
        commands.append(row)
        save(ev / 'commands.json', commands)
        print(label, flush=True)
        with (ev / (label + '.log')).open('xb') as f:
            result = subprocess.run(argv, stdout=f, stderr=subprocess.STDOUT)
        row.update(exit_code=result.returncode, log_sha256=sha(ev / (label + '.log')))
        save(ev / 'commands.json', commands)
        if result.returncode:
            raise RuntimeError(f'{label} failed ({result.returncode}); see retained log')
    tools = root / 'tools'
    tools.mkdir()
    with tarfile.open(a.archive, 'r:bz2') as tf:
        tf.extractall(tools, filter='data')
    assert sha(tools / 'llvm/bin/llvm-objcopy') == '673b3b86f0b1b8eadd755e29e2f66a7582248ef3bda7a267fbb370b733c1cb69'
    tool_before = inventory(tools)
    (ev / 'tools-before.json.gz').write_bytes(gzip.compress(json.dumps(tool_before, sort_keys=True).encode(), mtime=0))
    baseline = root / 'baseline-source'
    shutil.copytree(a.repo / 'programs/mayhem', baseline / 'programs/mayhem', ignore=shutil.ignore_patterns('target'))
    shutil.copy2(a.repo / 'repro/behavioral-recovery/programs/mayhem/src/lib.rs', baseline / 'programs/mayhem/src/lib.rs')
    changed = root / 'constraint-source'
    shutil.copytree(baseline, changed)
    lib = changed / 'programs/mayhem/src/lib.rs'
    source = lib.read_text()
    assert source.count(BEFORE) == 1
    lib.write_text(source.replace(BEFORE, AFTER))
    for name, path in [('baseline', baseline), ('constraint', changed)]:
        shutil.copytree(path, ev / (name + '-source'))
        save(ev / (name + '-source-before.json'), inventory(path))
    cargo = root / 'cargo-home'
    cargo.mkdir()
    env = {
        'PATH': '/tools/rust/bin:/usr/bin:/bin',
        'CARGO_HOME': '/cargo-home', 'RUSTUP_HOME': '/tmp/unused-rustup',
        'RUSTC': '/tools/rust/bin/rustc', 'RUSTDOC': '/tools/rust/bin/rustdoc',
        'CC': '/tools/llvm/bin/clang', 'AR': '/tools/llvm/bin/llvm-ar',
        'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'CARGO_TARGET_DIR': '/target',
        'CARGO_TARGET_SBPF_SOLANA_SOLANA_RUSTFLAGS': '-Zremap-cwd-prefix=',
    }
    def docker(src, target, network, argv):
        target.mkdir(exist_ok=True)
        cmd = ['docker', 'run', '--rm', '--platform', 'linux/amd64', '--network', network,
               '--mount', f'type=bind,src={src},dst=/src,readonly',
               '--mount', f'type=bind,src={tools},dst=/tools,readonly',
               '--mount', f'type=bind,src={cargo},dst=/cargo-home',
               '--mount', f'type=bind,src={target},dst=/target', '-w', '/src']
        for key, value in env.items():
            cmd += ['--env', f'{key}={value}']
        if network == 'none':
            cmd += ['--env', 'CARGO_NET_OFFLINE=true']
        return cmd + [a.image] + argv
    save(ev / 'host.json', {'image': a.image, 'platform': 'linux/amd64', 'host_uname': list(os.uname()),
                          'tool_archive_sha256': TOOL_SHA, 'build_network': 'none'})
    run('image-inspect', ['docker', 'image', 'inspect', a.image])
    run('compiler-version', docker(baseline, root / 'probe-target', 'none', ['/tools/rust/bin/rustc', '-vV']))
    run('locked-fetch', docker(baseline, root / 'fetch-target', 'bridge',
                              ['/tools/rust/bin/cargo', 'fetch', '--locked', '--manifest-path', '/src/programs/mayhem/Cargo.toml']))
    lock = tomllib.loads((baseline / 'programs/mayhem/Cargo.lock').read_text())
    rows = [p for p in lock['package'] if 'source' in p]
    assert len(rows) == 215 and all(p['source'] == 'registry+https://github.com/rust-lang/crates.io-index' for p in rows)
    for p in rows:
        files = list((cargo / 'registry/cache').glob(f"*/{p['name']}-{p['version']}.crate"))
        assert len(files) == 1 and sha(files[0]) == p['checksum'], p['name']
    registry_before = inventory(cargo / 'registry')
    (ev / 'registry-before.json.gz').write_bytes(gzip.compress(json.dumps(registry_before, sort_keys=True).encode(), mtime=0))
    for name, src in [('baseline', baseline), ('constraint', changed)]:
        target = root / (name + '-target')
        run(name + '-build', docker(src, target, 'none', ['/tools/rust/bin/cargo', 'build', '--release',
            '--target', TARGET, '--locked', '--offline', '--verbose', '--manifest-path', '/src/programs/mayhem/Cargo.toml']))
        output = target / TARGET / 'release/mayhem_recovered.so'
        shutil.copy2(output, ev / (name + '.symbols.so'))
        run(name + '-strip', docker(src, target, 'none', ['/tools/llvm/bin/llvm-objcopy', '--strip-all',
             '/target/' + TARGET + '/release/mayhem_recovered.so', '/target/candidate.so']))
        shutil.copy2(target / 'candidate.so', ev / (name + '.so'))
        current = inventory(src)
        save(ev / (name + '-source-after.json'), current)
        assert current == json.loads((ev / (name + '-source-before.json')).read_text())
    registry_after = inventory(cargo / 'registry')
    (ev / 'registry-after.json.gz').write_bytes(gzip.compress(json.dumps(registry_after, sort_keys=True).encode(), mtime=0))
    assert registry_before == registry_after, 'Registry inputs changed during offline builds'
    assert inventory(tools) == tool_before, 'Tool inputs changed'
    save(ev / 'result.json', {'status': 'BUILT', 'original_binary_mounted': False, 'source_unchanged_during_builds': True,
                             'registry_unchanged_during_builds': True, 'tools_unchanged_during_builds': True,
                             'outputs': {p.name: {'sha256': sha(p), 'bytes': p.stat().st_size} for p in ev.glob('*.so')}})
    print('Pair built successfully', flush=True)

if __name__ == '__main__':
    main()

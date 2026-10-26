#!/usr/bin/env python3
"""Rebuild the unselected collector with authenticated, prepared Darwin tools."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import time
import tomllib

import offline_inputs

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = 'repro/pump/cto-shared6093-v2-signed-acceptance'
SEAL = '4bf6c1ee2403acde6d6f57fcea8c0c1a856ff406130ec28233652ae077bfa1c2'
SOURCE_MAP = '80165bb94946ecc9486a4740e6c284ce4a75a3f7d6d01d38d4956306893978fc'
AVAILABILITY = '41de822c903816115e9633769fb3b684ae66c34f6d56ceb7271c395179ecbc03'
PLAN = '1ad1b9d4b2288deb552fa7d50830027dab41515a8909b912ab904042e8115a1f'
INVENTORY = 'repro/build-tooling/compiler-v144-current-identity/inventory.json'
INVENTORY_SHA = '40ac3a1b7cd95838abadd14d8c991620d4102556e67ff5bd7dd4641bd94e7ed4'
RUSTUP = 'aeb4105778ca1bd3c6b0e75768f581c656633cd51368fa61289b6a71696ac7e1'
CLI = 'e5b55be5bd22122feedfff845237e7d72ec4134dd2f2186acce15907e15d27a0'
STRIP = '12415dc01e08e4f606a1a4eac8c197d560c7883161d266312c821bf5db7bf8be'
ORIGINAL = '7a19affaa2c6187e04a5fe0ea298cee81fa5eb8c24cfcc30d85f615e89f7b02d'
HOST_CARGO = 'cb7151ab1c5fcd42648336a2c98020b1819b0993955c8ba3ed44494772a82bdf'
HOST_RUSTC = '4f26ad57dcb9b12f9791317a1387e3e8d6ad803d4bd20fcdc65142a91e903d45'
EXPECTED = {
    'executable': ('artifacts/pump_recovered.so', 1590856,
                   'fdfdb5f27af9b8c22effd48ea523c06bd037ceedf49df0da8178cad19eed38f5'),
    'unstripped': ('target/sbf-solana-solana/release/pump_recovered.so', 2174728,
                   '1e088e9add0218ebf6745a7f7557a4dc55dc68e86ec97790584db7f169c14bc3'),
}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(path, expected):
    require(path.is_file(), 'missing file: ' + str(path))
    require(sha(path) == expected, 'hash mismatch: ' + str(path))


def source_inputs(repository=ROOT):
    package = repository / PACKAGE
    for name, expected in [('manifest.json', SEAL), ('build-input-source37.json', SOURCE_MAP),
                           ('build-plan/availability.json', AVAILABILITY),
                           ('build-plan/future-plan.json', PLAN)]:
        checked(package / name, expected)
    sources = json.loads((package / 'build-input-source37.json').read_text())
    require(len(sources) == 37, 'expected 37 source inputs')
    for name, expected in sources.items():
        relative = Path(name)
        require(not relative.is_absolute() and '..' not in relative.parts and
                name.startswith('programs/pump/'), 'unsafe source path')
        path = package / 'build-input-source' / relative
        require(not path.is_symlink(), 'source symlink: ' + name)
        checked(path, expected)
    helpers = json.loads((package / 'build-plan/future-plan.json').read_text())['helper_sha256']
    for name, expected in helpers.items():
        checked(package / 'build-plan/helpers' / name, expected)
    return sources, helpers


def sdk_inputs(sdk, expected):
    for name, digest in expected.items():
        path = sdk / name
        checked(path, digest)
        if name.startswith('scripts/') and name.endswith('.sh'):
            require(path.stat().st_mode & 0o111, 'SDK script is not executable: ' + name)
    return len(expected)


def dependencies(home, lock):
    packages = [p for p in tomllib.loads(lock.read_text())['package']
                if p.get('source', '').startswith('registry+')]
    require(len(packages) == 252, 'unexpected lock graph')
    files = 0
    for namespace in ('index.crates.io-1949cf8c6b5b557f', 'index.crates.io-6f17d22bba15001f'):
        for package in packages:
            name = package['name'] + '-' + package['version']
            archive = home / 'registry/cache' / namespace / (name + '.crate')
            checked(archive, package['checksum'])
            source = home / 'registry/src' / namespace / name
            members = set()
            with tarfile.open(archive) as stream:
                for member in stream:
                    require(not member.issym() and not member.islnk(), 'crate link: ' + name)
                    if not member.isfile():
                        continue
                    part = Path(member.name)
                    require(part.parts[0] == name and '..' not in part.parts, 'crate member path')
                    relative = Path(*part.parts[1:])
                    path = source / relative
                    require(not path.is_symlink() and path.read_bytes() == stream.extractfile(member).read(),
                            'cached source differs from archive: ' + str(path))
                    members.add(str(relative))
                    files += 1
            actual = {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()}
            require(not (actual - members - {'.cargo-ok', '.cargo-checksum.json'}),
                    'unexpected cached source files: ' + name)
    return {'locked_packages': len(packages), 'namespace_views': 2, 'source_files_checked': files}


def compiler_tree(root, inventory):
    root = root.resolve()
    expected = {name: row for name, row in inventory.items() if row['type'] in ('regular', 'symlink')}
    actual = {}
    for path in root.rglob('*'):
        if path.is_symlink():
            kind = 'symlink'
        elif path.is_file():
            kind = 'regular'
        elif path.is_dir():
            continue
        else:
            raise ValueError('unexpected compiler member: ' + str(path))
        actual[str(path.relative_to(root))] = kind
    require(actual == {name: row['type'] for name, row in expected.items()}, 'compiler membership differs')
    for name, row in expected.items():
        path = root / name
        if row['type'] == 'regular':
            checked(path, row['sha256'])
        else:
            require(os.readlink(path) == row['target'], 'compiler symlink target differs: ' + name)
            # The official archive includes pinned, dangling LLDB utility links.
            # Their exact target is authenticated; resolution must stay inside the tree.
            require(path.resolve(strict=False).is_relative_to(root), 'compiler symlink escapes tree: ' + name)
    return {'regular_files': sum(r['type'] == 'regular' for r in expected.values()),
            'symlinks': sum(r['type'] == 'symlink' for r in expected.values())}


def host_selection(seed):
    settings = tomllib.loads((seed / 'settings.toml').read_text())
    require(settings == {'version': '12', 'default_toolchain': 'stable-aarch64-apple-darwin',
                         'profile': 'minimal'}, 'unexpected private rustup settings')
    stable = seed / 'toolchains/stable-aarch64-apple-darwin'
    require(stable.is_symlink() and stable.resolve() ==
            (seed / 'toolchains/1.94.0-aarch64-apple-darwin').resolve(), 'private stable alias differs')


def reject_selectors(starts):
    for start in starts:
        for directory in (start, *start.parents):
            for name in ('.cargo/config', '.cargo/config.toml', 'rust-toolchain', 'rust-toolchain.toml'):
                require(not (directory / name).exists(), 'unrecorded selector: ' + str(directory / name))


def preflight(prepared, output, repository=ROOT, *, fresh=True):
    require((platform.system(), platform.machine()) == ('Darwin', 'arm64'), 'Darwin arm64 recipe only')
    require(not fresh or not output.exists(), 'output must be a fresh directory')
    require(not output.is_relative_to(prepared), 'output must be outside prepared tools')
    sources, helpers = source_inputs(repository)
    package = repository / PACKAGE
    sdk = prepared / 'agave-v2.1.21/solana-release/bin/sdk/sbf'
    expected_sdk = json.loads((package / 'build-plan/availability.json').read_text())['sdk_source_sha256']
    sdk_inputs(sdk, expected_sdk)
    checked(repository / INVENTORY, INVENTORY_SHA)
    inventory = json.loads((repository / INVENTORY).read_text())['entries']
    compiler = compiler_tree(prepared / 'platform-tools-v1.44', inventory)
    require(compiler_tree(Path.home() / '.cache/solana/v1.44/platform-tools', inventory) == compiler,
            'actual compiler cache differs')
    checked(prepared / 'agave-v2.1.21/solana-release/bin/cargo-build-sbf', CLI)
    checked(prepared / 'launch/cargo-build-sbf', CLI)
    require((prepared / 'launch/cargo-build-sbf').resolve() ==
            (prepared / 'agave-v2.1.21/solana-release/bin/cargo-build-sbf').resolve(),
            'CLI launcher does not use authenticated SDK location')
    for name in ('rustup', 'cargo', 'rustc', 'rustdoc'):
        checked(prepared / 'launch' / name, RUSTUP)
    checked(prepared / 'rustup-seed/toolchains/1.94.0-aarch64-apple-darwin/bin/cargo', HOST_CARGO)
    checked(prepared / 'rustup-seed/toolchains/1.94.0-aarch64-apple-darwin/bin/rustc', HOST_RUSTC)
    host_selection(prepared / 'rustup-seed')
    install = offline_inputs.install_inputs()
    reject_selectors((output / 'repo/programs/pump', prepared, repository))
    for name in ('config', 'config.toml', 'credentials', 'credentials.toml'):
        require(not (prepared / 'cargo-home' / name).exists(), 'unexpected Cargo home configuration')
    deps = dependencies(prepared / 'cargo-home', package / 'build-input-source/programs/pump/Cargo.lock')
    return {'source37': sources, 'helpers': helpers, 'sdk_files': len(expected_sdk),
            'compiler_regular_files': compiler['regular_files'],
            'compiler_symlinks': compiler['symlinks'], 'dependencies': deps, 'sdk_install_inputs': install}


def outputs(build, returncode):
    require(returncode == 0, 'build failed; retained output is not accepted')
    result = {}
    for name, (relative, length, digest) in EXPECTED.items():
        path = build / relative
        checked(path, digest)
        require(path.stat().st_size == length, 'output length mismatch: ' + name)
        result[name] = {'bytes': length, 'sha256': digest, 'whole_file_equal': True}
    log = (build / 'build.log').read_text()
    failures = [line for line in log.splitlines()
                if re.match(r'^\s*(?:Error:|LLVM ERROR:)', line)]
    require(not failures, 'backend errors were reported')
    return result


def reproduce(prepared, output, repository=ROOT):
    before = preflight(prepared, output, repository)
    output.mkdir(parents=True)
    repo = output / 'repo'
    package = repository / PACKAGE
    for name, expected in before['source37'].items():
        target = repo / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(package / 'build-input-source' / name, target)
        checked(target, expected)
    for name in before['helpers']:
        target = repo / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(package / 'build-plan/helpers' / name, target)
    reference = repo / 'evidence/original/pump/deployed.so'
    reference.parent.mkdir(parents=True)
    checked(repository / 'evidence/original/pump/deployed.so', ORIGINAL)
    shutil.copyfile(repository / 'evidence/original/pump/deployed.so', reference)
    # The frozen helper reads this capture only for its postcompile comparison.
    # It is outside the Rust input tree. Tested candidate bytes are never copied.
    (output / 'tmp').mkdir()
    env = {'HOME': str(Path.home()),
           'PATH': str(prepared / 'launch') + ':' + str(prepared / 'agave-v2.1.21/solana-release/bin') + ':/usr/bin:/bin:/usr/sbin:/sbin',
           'CARGO_HOME': str(prepared / 'cargo-home'), 'RUSTUP_HOME': str(prepared / 'rustup-seed'),
           'CARGO_TARGET_DIR': str(output / 'build/target'), 'CARGO_NET_OFFLINE': 'true',
           'CARGO_TERM_COLOR': 'never', 'PYTHONDONTWRITEBYTECODE': '1',
           'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'TMPDIR': str(output / 'tmp'), 'NO_DNA': '1'}
    command = [sys.executable, '-B', str(repo / 'scripts/build_partial_candidate.py'),
               '--manifest', str(repo / 'programs/pump/Cargo.toml'), '--program', 'pump',
               '--artifact-name', 'pump_recovered.so', '--tools-version', 'v1.44', '--output', str(output / 'build')]
    helper_command = command
    command = offline_inputs.guarded_command(helper_command)
    result = {'status': 'RUNNING', 'command': command, 'helper_command': helper_command,
              'network_guard': before['sdk_install_inputs']['network_guard'], 'cwd': str(repo), 'environment': env,
              'inputs': before, 'started_unix': time.time(), 'candidate_selected': False,
              'reproducer_sha256': sha(Path(__file__))}
    receipt = output / 'reproduction.json'
    receipt.write_text(json.dumps(result, indent=2) + '\n')
    try:
        with (output / 'stdout.log').open('wb') as stdout, (output / 'stderr.log').open('wb') as stderr:
            child = subprocess.run(command, cwd=repo, env=env, stdout=stdout, stderr=stderr, check=False)
        # This is the OS launcher's aggregate exit, not a separately observed
        # helper/compiler/strip child status.
        result['guarded_command_returncode'] = child.returncode
        result['helper_returncode'] = None
        result['outputs'] = outputs(output / 'build', child.returncode)
        for name, expected in before['source37'].items():
            checked(repo / name, expected)
        # Recheck authenticated inputs after the build, without reusing the fresh-output guard.
        after = preflight(prepared, output, repository, fresh=False)
        require(before == after, 'authenticated inputs changed during build')
        checked(Path(__file__), result['reproducer_sha256'])
        attempt = json.loads((output / 'build/build-attempt.json').read_text())
        require(attempt['returncode'] == 0 and attempt['source_unchanged'], 'build-sbf acceptance failed')
        require(attempt['source_sha256'] == attempt['source_after_sha256'] == before['source37'],
                'actual compiled source map differs')
        result.update(status='PASS', build_sbf_returncode=attempt['returncode'], inputs_unchanged=True)
    except Exception as error:
        result.update(status='FAIL', error=repr(error))
        raise
    finally:
        result['finished_unix'] = time.time()
        receipt.write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = reproduce(args.prepared.resolve(), args.output.resolve())
    print(json.dumps({'status': result['status'], 'outputs': result['outputs']}, indent=2))

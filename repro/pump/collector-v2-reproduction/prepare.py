#!/usr/bin/env python3
"""Prepare the exact Darwin ARM tools and locked cache for collector reproduction."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import tarfile
import time
import tomllib
import urllib.request

import offline_inputs


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = 'repro/pump/cto-shared6093-v2-signed-acceptance'
SEAL = '4bf6c1ee2403acde6d6f57fcea8c0c1a856ff406130ec28233652ae077bfa1c2'
SOURCE_MAP = '80165bb94946ecc9486a4740e6c284ce4a75a3f7d6d01d38d4956306893978fc'
PLAN = '1ad1b9d4b2288deb552fa7d50830027dab41515a8909b912ab904042e8115a1f'
AVAILABILITY = '41de822c903816115e9633769fb3b684ae66c34f6d56ceb7271c395179ecbc03'
INVENTORY = 'repro/build-tooling/compiler-v144-current-identity/inventory.json'
INVENTORY_SHA = '40ac3a1b7cd95838abadd14d8c991620d4102556e67ff5bd7dd4641bd94e7ed4'
SDK = 'repro/pump_fees/linux-darwin-v144-attribution/inputs/recorded-sdk-sbf-sdk-snapshot.tar.gz'
SDK_SHA = 'ec657e1d7e5042ee5aff739db538de0c50a1bfc95b641a6fcf28402a5efb6d04'
CLI_SHA = 'e5b55be5bd22122feedfff845237e7d72ec4134dd2f2186acce15907e15d27a0'
STRIP_SHA = '12415dc01e08e4f606a1a4eac8c197d560c7883161d266312c821bf5db7bf8be'
NAMESPACES = ('index.crates.io-1949cf8c6b5b557f', 'index.crates.io-6f17d22bba15001f')
ASSETS = {
    'platform-tools-v1.44.tar.bz2': (
        'https://github.com/anza-xyz/platform-tools/releases/download/v1.44/platform-tools-osx-aarch64.tar.bz2',
        400794156, '66e20d135fddd70ff519baf7ff320d762957f9aedf93a50e23756db23ad79351'),
    'agave-v2.1.21.tar.bz2': (
        'https://github.com/anza-xyz/agave/releases/download/v2.1.21/solana-release-aarch64-apple-darwin.tar.bz2',
        139317260, '8a1291168574840cbb0fe9dd22540f7711f6c2ec0c1fe101ab4bdf44da5f28b0'),
    'rustup-init-1.29.0': (
        'https://static.rust-lang.org/rustup/archive/1.29.0/aarch64-apple-darwin/rustup-init',
        11053296, 'aeb4105778ca1bd3c6b0e75768f581c656633cd51368fa61289b6a71696ac7e1'),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checked(path, expected):
    require(path.is_file() and not path.is_symlink() and sha(path) == expected,
            'missing, symlinked or altered input: ' + str(path))
    return path


def acquire(name, record, downloads, cache=None):
    url, size, expected = record
    target = downloads / name
    cached = cache / name if cache is not None else None
    if cached is not None and cached.exists():
        checked(cached, expected)
        shutil.copyfile(cached, target)
    else:
        with urllib.request.urlopen(url, timeout=60) as response, target.open('xb') as out:
            shutil.copyfileobj(response, out)
    checked(target, expected)
    require(target.stat().st_size == size, 'asset size mismatch: ' + name)
    return target


def safe_extract(archive, destination):
    """Reject unsafe members before extraction, including escaping links."""
    destination.mkdir(parents=True, exist_ok=False)
    with tarfile.open(archive) as stream:
        for member in stream.getmembers():
            path = Path(member.name)
            require(not path.is_absolute() and '..' not in path.parts, 'unsafe archive path')
            tarfile.data_filter(member, str(destination))
        stream.extractall(destination, filter='data')


def restore_sdk(official, retained, archive, expected):
    modes = {str(p.relative_to(official)): p.stat().st_mode & 0o777
             for p in official.rglob('*') if p.is_file() and not p.is_symlink()}
    safe_extract(archive, retained)
    actual = {str(p.relative_to(retained)) for p in retained.rglob('*') if p.is_file()}
    require(actual == set(expected), 'SDK membership differs from the retained 53 files')
    changed = {}
    for name, digest in expected.items():
        path = checked(retained / name, digest)
        require(name in modes, 'SDK member missing from official mode reference: ' + name)
        before = path.stat().st_mode & 0o777
        path.chmod(modes[name])
        if before != modes[name]:
            changed[name] = {'before': oct(before), 'after': oct(modes[name])}
    return changed


def private_proxies(launch, rustup):
    launch.mkdir(exist_ok=False)
    shutil.copyfile(rustup, launch / 'rustup')
    (launch / 'rustup').chmod(0o755)
    for name in ('cargo', 'rustc', 'rustdoc'):
        (launch / name).symlink_to('rustup')


def verify_compiler_tree(compiler, inventory):
    compiler = compiler.resolve()
    files = {name: row for name, row in inventory.items() if row['type'] == 'regular'}
    links = {name: row for name, row in inventory.items() if row['type'] == 'symlink'}
    expected = {name: row['type'] for name, row in {**files, **links}.items()}
    actual = {}
    pending = [compiler]
    while pending:
        for path in pending.pop().iterdir():
            mode = path.lstat().st_mode
            name = str(path.relative_to(compiler))
            if stat.S_ISLNK(mode):
                actual[name] = 'symlink'
            elif stat.S_ISREG(mode):
                actual[name] = 'regular'
            elif stat.S_ISDIR(mode):
                pending.append(path)
            else:
                raise ValueError('unsupported compiler tree entry: ' + name)
    require(actual == expected, 'compiler entry membership mismatch')
    for name, row in links.items():
        path = compiler / name
        require(os.readlink(path) == row['target'], 'compiler symlink target mismatch: ' + name)
        # The official lldb-argdumper link is intentionally dangling. Its exact
        # relative spelling and inside-tree destination still remain pinned.
        require(path.resolve(strict=False).is_relative_to(compiler),
                'compiler symlink resolves outside tree: ' + name)
    for name, row in files.items():
        checked(compiler / name, row['sha256'])
    return len(files)


def ensure_cache_link(path, compiler, inventory=None):
    if path.exists() or path.is_symlink():
        if path.resolve() != compiler.resolve():
            require(inventory is not None,
                    'existing compiler cache points elsewhere; it was not changed: ' + str(path))
        if inventory is not None:
            verify_compiler_tree(path.resolve(), inventory)
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.symlink_to(compiler, target_is_directory=True)
    return True


def run(command, environment, cwd, output, name):
    record = {'command': command, 'start_unix': time.time()}
    with (output / (name + '.stdout')).open('wb') as stdout, (output / (name + '.stderr')).open('wb') as stderr:
        result = subprocess.run(command, env=environment, cwd=cwd, stdout=stdout, stderr=stderr, check=False)
    record.update(returncode=result.returncode, end_unix=time.time())
    (output / (name + '.json')).write_text(json.dumps(record, indent=2) + '\n')
    require(result.returncode == 0, name + ' failed; retained logs and output were not removed')


def prepare(output, download_cache=None, registry_cache=None, repository=ROOT):
    require((platform.system(), platform.machine()) == ('Darwin', 'arm64'), 'requires Darwin arm64')
    repository = repository.resolve()
    output = output.absolute()
    require(not output.exists() and not output.is_symlink(), 'output must be new')
    home = Path.home()
    install_before = offline_inputs.install_inputs(home)
    package = repository / PACKAGE
    checked(package / 'manifest.json', SEAL)
    source_path = checked(package / 'build-input-source37.json', SOURCE_MAP)
    future = json.loads(checked(package / 'build-plan/future-plan.json', PLAN).read_text())
    sdk_map = json.loads(checked(package / 'build-plan/availability.json', AVAILABILITY).read_text())['sdk_source_sha256']
    inventory = json.loads(checked(repository / INVENTORY, INVENTORY_SHA).read_text())['entries']
    checked(repository / SDK, SDK_SHA)
    source = json.loads(source_path.read_text())
    require(len(source) == 37, 'expected 37 source inputs')
    output.mkdir(parents=True)
    receipt = {'status': 'PREPARING', 'source37': source, 'real_HOME': str(home),
               'global_toolchain_aliases_modified': False, 'network_preparation_only': True,
               'sdk_install_inputs': install_before}
    try:
        downloads = output / 'downloads'
        downloads.mkdir()
        cache = download_cache.resolve() if download_cache else None
        assets = {name: acquire(name, record, downloads, cache) for name, record in ASSETS.items()}
        compiler = output / 'platform-tools-v1.44'
        safe_extract(assets['platform-tools-v1.44.tar.bz2'], compiler)
        files = {name: row for name, row in inventory.items() if row['type'] == 'regular'}
        require(len(files) == 2773, 'unexpected compiler inventory')
        verify_compiler_tree(compiler, inventory)
        agave = output / 'agave-v2.1.21'
        safe_extract(assets['agave-v2.1.21.tar.bz2'], agave)
        cli = checked(agave / 'solana-release/bin/cargo-build-sbf', CLI_SHA)
        sdk = cli.parent / 'sdk/sbf'
        official = sdk.with_name('sbf-official-unmodified')
        sdk.rename(official)
        receipt['sdk_mode_restoration'] = restore_sdk(official, sdk, repository / SDK, sdk_map)
        private_proxies(output / 'launch', assets['rustup-init-1.29.0'])
        (output / 'launch/cargo-build-sbf').symlink_to(cli)
        cache_link = home / '.cache/solana/v1.44/platform-tools'
        receipt['compiler_cache_link_created'] = ensure_cache_link(cache_link, compiler, inventory)
        receipt['compiler_cache_path'] = str(cache_link.resolve())
        repo = output / 'repo'
        for name, digest in source.items():
            part = Path(name)
            require(not part.is_absolute() and '..' not in part.parts and name.startswith('programs/pump/'), 'unsafe source path')
            src = checked(package / 'build-input-source' / name, digest)
            target = repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, target)
        for name, digest in future['helper_sha256'].items():
            src = checked(package / 'build-plan/helpers' / name, digest)
            target = repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, target)
        environment = {'HOME': str(home), 'PATH': str(output / 'launch') + ':' + str(cli.parent) + ':/usr/bin:/bin:/usr/sbin:/sbin',
                       'RUSTUP_HOME': str(output / 'rustup-seed'), 'CARGO_HOME': str(output / 'cargo-home'),
                       'CARGO_TARGET_DIR': str(output / 'fetch-target'), 'CARGO_TERM_COLOR': 'never',
                       'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'RUSTUP_NO_UPDATE_CHECK': '1', 'NO_DNA': '1'}
        run([str(output / 'launch/rustup'), 'toolchain', 'install', '1.94.0', '--profile', 'minimal', '--no-self-update'], environment, output, output, 'host-toolchain')
        seed = output / 'rustup-seed'
        (seed / 'toolchains/stable-aarch64-apple-darwin').symlink_to(seed / 'toolchains/1.94.0-aarch64-apple-darwin', target_is_directory=True)
        (seed / 'settings.toml').write_text('version = "12"\ndefault_toolchain = "stable-aarch64-apple-darwin"\nprofile = "minimal"\n')
        packages = [p for p in tomllib.loads((repo / 'programs/pump/Cargo.lock').read_text())['package'] if p.get('source', '').startswith('registry+')]
        require(len(packages) == 252, 'expected 252 locked registry packages')
        registry = registry_cache.resolve() if registry_cache else home / '.cargo/registry'
        local_copies = 0
        for package_row in packages:
            name = package_row['name'] + '-' + package_row['version'] + '.crate'
            matches = [p for p in (registry / 'cache').glob('*/' + name) if not p.is_symlink() and sha(p) == package_row['checksum']]
            if matches:
                target = output / 'cargo-home/registry/cache' / NAMESPACES[0] / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(matches[0], target)
                local_copies += 1
        run([str(output / 'launch/cargo'), 'fetch', '--locked', '--manifest-path', str(repo / 'programs/pump/Cargo.toml')], environment, repo, output, 'fetch')
        for package_row in packages:
            name = package_row['name'] + '-' + package_row['version'] + '.crate'
            checked(output / 'cargo-home/registry/cache' / NAMESPACES[0] / name, package_row['checksum'])
        for part in ('cache', 'index', 'src'):
            shutil.copytree(output / 'cargo-home/registry' / part / NAMESPACES[0], output / 'cargo-home/registry' / part / NAMESPACES[1])
        require(all(sha(repo / name) == digest for name, digest in source.items()), 'fetch changed source or lockfile')
        require(offline_inputs.install_inputs(home) == install_before,
                'SDK install inputs changed during preparation')
        receipt.update(status='PASS', sdk_install_inputs_unchanged=True, compiler_regular_files_verified=len(files), sdk_files_verified=len(sdk_map),
                       locked_archives_verified=len(packages), local_archive_copies=local_copies,
                       asset_sha256={name: sha(path) for name, path in assets.items()})
    except Exception as error:
        receipt.update(status='FAIL', error=str(error))
        raise
    finally:
        (output / 'preparation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--download-cache', type=Path)
    parser.add_argument('--registry-cache', type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.output, args.download_cache, args.registry_cache), indent=2))

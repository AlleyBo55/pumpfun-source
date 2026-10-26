#!/usr/bin/env python3
"""ATA ordering probe: rebuild SPL ATA @ f5ce86 in the pinned Linux image with a
metadata-only perturbation of spl_token_2022, and compare to the deployed program.

Replicates scripts/pump_build_token_dependency.py's associated_token recipe exactly
(same image digest, same `cargo build-bpf ... -- --locked`, same RUSTFLAGS), with one
documented change: an EMPTY feature flag is declared on spl-token-2022 and enabled
from the ATA dependency line. The flag is referenced by no cfg(), so compiled code
is unchanged; only Cargo's -C metadata for spl_token_2022 (and transitively ATA)
changes, which re-rolls the symbol-hash ordering of same-definition monomorphizations.

    python3 probe.py control            # no perturbation: must reproduce candidate2
    python3 probe.py <attempt-name>     # perturbation flag = "ordering-probe-<attempt-name>"
"""
import hashlib, json, os, pathlib, shutil, subprocess, sys, tarfile, time, uuid

HERE = pathlib.Path(__file__).resolve().parent
TARBALL = pathlib.Path('/Users/gilang/ngoding/ata-darwin-build/inputs/spl-f5ce86.tar.gz')
TARBALL_SHA = '1b324f4c0f476f0581556ee6fd1e0fe0b4e74252fd8d5fe690a459611568be5c'
LOCK_SHA = '3c8f402f40488908503e9cc088388c1f95848d79da5141b5cb1a14006d74428b'
COMMIT = 'f5ce86d43dd31ddefb96d4e8cdd67dd073dc5dca'
IMAGE = 'solanafoundation/solana-verifiable-build@sha256:ee9ad7809009a99a70f659f7cba959e0c3c124e10f771b524914fd42f2b605a8'
MANIFEST = 'associated-token-account/program/Cargo.toml'
TOK22 = 'token/program-2022/Cargo.toml'
DEPLOYED = pathlib.Path('/Users/gilang/ngoding/pumpfun-source/evidence/dependencies/associated_token/deployed.so')
DEPLOYED_SHA = '6804554e69fd3a58caa191dc4a58f4c67223d30ca28ab8987f39fc18d2f7374d'
CANDIDATE2_SHA = 'ba8dd8a42ca7bff4b668c72e1b5614e9363b271924d520253f5724760ba2d65b'

sha = lambda b: hashlib.sha256(b).hexdigest()
def run(cmd, **kw): return subprocess.run(cmd, check=True, text=True, capture_output=True, **kw).stdout.strip()

VENDOR = HERE / 'vendor'                      # 632 crates from the authentic lock (cargo vendor --locked)
SDK_CACHE = HERE / 'sdk-cache'                # ~/.cache/solana layout: v1.27/bpf-tools + v2.3.3/criterion
BPF_TOOLS_TAR = HERE / 'inputs/solana-bpf-tools-linux.tar.bz2'
BPF_TOOLS_SHA = '8a2d6a7d8b498202d2ae37062dad94be0c33ca37444e35ab7732927d3fe9a8ff'   # official v1.27 Linux asset

def prepare_tree(attempt, flag):
    tree = HERE / 'trees' / attempt
    if tree.exists(): shutil.rmtree(tree)
    tree.mkdir(parents=True)
    assert sha(TARBALL.read_bytes()) == TARBALL_SHA, 'source tarball hash drift'
    with tarfile.open(TARBALL) as tf: tf.extractall(tree)
    src = tree / f'solana-program-library-{COMMIT}'
    assert sha((src / 'Cargo.lock').read_bytes()) == LOCK_SHA, 'lockfile is not the authentic f5ce86 lock'
    # Offline inputs. Neither changes Cargo's package identities: source replacement keeps
    # crates.io PackageIds (so --locked still verifies the authentic lock), and the SDK's own
    # install.sh is what unpacks bpf-tools when the official tarball is already present.
    (src / '.cargo').mkdir()
    (src / '.cargo/config.toml').write_text('[source.crates-io]\nreplace-with = "vendored-sources"\n'
                                            '[source.vendored-sources]\ndirectory = "/build/.vendor"\n')
    (src / '.vendor').mkdir()   # bind-mount target inside the container
    assert sha(BPF_TOOLS_TAR.read_bytes()) == BPF_TOOLS_SHA, 'bpf-tools tarball hash drift'
    assert (SDK_CACHE / 'v1.27/bpf-tools/rust/bin/rustc').exists(), 'pre-seeded SDK cache missing'
    record = {'attempt': attempt, 'flag': flag, 'source_commit': COMMIT, 'lock_sha256_before': LOCK_SHA,
              'offline_inputs': {'vendored_crates': len(list(VENDOR.iterdir())), 'bpf_tools_linux_sha256': BPF_TOOLS_SHA,
                                 'sdk_cache_mount': '/root/.cache/solana (install.sh reuses it; no network)'}, 'edits': []}
    if flag:
        # Decisive test: perturb the -C metadata of EVERY application crate at once
        # (ATA root + spl-token + spl-token-2022) via no-op empty features. ATA's own
        # feature is enabled with `cargo build-bpf --features <flag>`; the two dependency
        # features are enabled from ATA's dependency lines. No feature is referenced by any
        # cfg(), so compiled code is identical. If the output still equals candidate2, the
        # reserve_for_push ordering is governed by none of these crates (sysroot alloc).
        edits = [
            (MANIFEST, '[features]\nno-entrypoint = []\ntest-bpf = []\n',
             f'[features]\nno-entrypoint = []\ntest-bpf = []\n{flag} = []\n'),
            (MANIFEST, 'spl-token = { version = "3.4", path = "../../token/program", features = ["no-entrypoint"] }',
             f'spl-token = {{ version = "3.4", path = "../../token/program", features = ["no-entrypoint", "{flag}"] }}'),
            (MANIFEST, 'spl-token-2022 = { version = "0.4", path = "../../token/program-2022", features = ["no-entrypoint"] }',
             f'spl-token-2022 = {{ version = "0.4", path = "../../token/program-2022", features = ["no-entrypoint", "{flag}"] }}'),
            ('token/program/Cargo.toml', '[features]\nno-entrypoint = []\n', f'[features]\nno-entrypoint = []\n{flag} = []\n'),
            (TOK22, '[features]\nno-entrypoint = []\n', f'[features]\nno-entrypoint = []\n{flag} = []\n'),
        ]
        for rel, old, new in edits:
            p = src / rel; before = p.read_text()
            assert before.count(old) == 1, f'anchor not found exactly once in {rel}'
            p.write_text(before.replace(old, new))
            record['edits'].append({'file': rel, 'added_feature': flag})
    return src, record

def build(src, attempt, record):
    out = HERE / 'results' / attempt
    out.mkdir(parents=True, exist_ok=True)
    workdir = run(['docker', 'run', '--rm', '--platform', 'linux/amd64', IMAGE, 'pwd'])
    assert workdir.startswith('/') and workdir != '/'
    name = 'ata-probe-' + uuid.uuid4().hex[:8]
    container = run(['docker', 'run', '--rm', '--platform', 'linux/amd64', '--name', name, '--network', 'none',
                     '--mount', f'type=bind,source={src},target={workdir}',
                     '--mount', f'type=bind,source={VENDOR},target={workdir}/.vendor,readonly',
                     '--mount', f'type=bind,source={SDK_CACHE},target=/root/.cache/solana',
                     '-d', IMAGE, 'sleep', 'infinity'])
    t0 = time.time()
    try:
        active = run(['docker', 'exec', '-w', '/', container, 'rustup', 'show', 'active-toolchain']).split()[0]
        # Identical to candidate2's recipe plus --offline (vendored crates, pre-seeded SDK cache, no network).
        feat = ['--features', record['flag']] if record['flag'] else []
        cmd = ['docker', 'exec', '-e', 'RUSTUP_TOOLCHAIN=' + active, '-e', 'RUSTFLAGS=-D warnings', '-w', workdir,
               container, 'cargo', 'build-bpf', '--offline', *feat, '--manifest-path', workdir.rstrip('/') + '/' + MANIFEST, '--', '--locked']
        record['command'] = [c.replace(container, '<container>') for c in cmd]
        with (out / 'build.log').open('w') as log:
            r = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, text=True)
        record['build_returncode'] = r.returncode
        if r.returncode:
            print((out / 'build.log').read_text()[-6000:]); raise SystemExit(f'build failed: {attempt}')
        tool = run(['docker', 'exec', container, 'rustup', 'toolchain', 'list'])
        record['container_toolchains'] = tool
    finally:
        subprocess.run(['docker', 'stop', '-t', '1', container], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    record['build_seconds'] = round(time.time() - t0, 1)
    record['lock_sha256_after'] = sha((src / 'Cargo.lock').read_bytes())
    assert record['lock_sha256_after'] == LOCK_SHA, 'build modified the lockfile'
    so = src / 'target/deploy/spl_associated_token_account.so'
    b = so.read_bytes(); shutil.copyfile(so, out / 'spl_associated_token_account.so')
    dep = DEPLOYED.read_bytes(); assert sha(dep) == DEPLOYED_SHA
    n = min(len(b), len(dep)); diffs = sum(1 for i in range(n) if b[i] != dep[i]) + abs(len(b) - len(dep))
    record.update({'output_bytes': len(b), 'output_sha256': sha(b), 'deployed_sha256': DEPLOYED_SHA,
                   'differing_positions_vs_deployed': diffs, 'byte_identical_to_deployed': b == dep,
                   'equals_candidate2': sha(b) == CANDIDATE2_SHA})
    (out / 'result.json').write_text(json.dumps(record, indent=2) + '\n')
    return record

if __name__ == '__main__':
    attempt = sys.argv[1]
    flag = None if attempt == 'control' else f'ordering-probe-{attempt}'
    src, record = prepare_tree(attempt, flag)
    rec = build(src, attempt, record)
    print(json.dumps({k: rec[k] for k in ('attempt', 'flag', 'build_seconds', 'output_sha256',
                                          'differing_positions_vs_deployed', 'byte_identical_to_deployed', 'equals_candidate2')}, indent=2))
    sys.exit(0 if rec['byte_identical_to_deployed'] else 2)

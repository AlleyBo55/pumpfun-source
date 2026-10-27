"""Verify retained raw candidate11 reproduction; no compiler or target execution."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import tomllib
import zipfile

import rebuild

PACKAGE = Path(__file__).resolve().parent
RECEIPTS_SHA256 = '86b1bb2756a9d4f4205a6e0a627ca13c478e8c5c0bad420e5d94ab02771e4702'
RUNS = {
    40337545179: ('250a9f9c24a20aaf23479a05be892ff18cc0854b', 'failure',
                  'e7dac6619a291f260c800b88f90f73c07ebf18f5fbed73f99e237b4c99e4cb92'),
    40337930953: ('e5b2ec8c24458b82c46b1381e5928825de60a8bd', 'failure',
                  'e560f4d739a95b8dcd9c19713c78b77887973a7efdd27a1fa3e2af2940e5d5c3'),
    40338395968: ('b3b81a8f5aced43de4f42bfc6bb8cc0d268197f0', 'success',
                  'e6158bb5e7793ffb2bbfa3246f50a39a0dc22ad47f9ae7e4384625818f972809'),
}
require, sha = rebuild.require, rebuild.sha


def sealed(raw, digest, label):
    require(sha(raw) == digest, 'Changed evidence: ' + label)
    return raw


def artifact(package, receipt):
    run = receipt['run']
    revision, conclusion, digest = RUNS[run['id']]
    require(run['head_sha'] == revision and run['conclusion'] == conclusion
            and run['status'] == 'completed' and run['run_attempt'] == 1, 'Run identity differs')
    require(run['repository']['full_name'] == 'startrack3r/pumpfun-source'
            and run['actor']['login'] == 'startrack3r', 'Run account differs')
    job, = receipt['jobs']['jobs']
    require(job['run_id'] == run['id'] and job['conclusion'] == conclusion, 'Job differs')
    provider, = receipt['artifacts']['artifacts']
    require(provider['workflow_run']['id'] == run['id']
            and provider['workflow_run']['head_sha'] == revision
            and provider['digest'] == 'sha256:' + digest, 'Artifact provider identity differs')
    raw = sealed((package / f'{run["id"]}.zip').read_bytes(), digest, 'artifact ZIP')
    require(len(raw) == provider['size_in_bytes'], 'Artifact length differs')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)) and all('/' not in n and '\\' not in n for n in names),
                'Unexpected artifact member names')
        members = {name: archive.read(name) for name in names}
    require(members['source-commit.txt'] == (revision + '\n').encode(), 'Executed revision differs')
    for row in receipt['source_files']:
        raw = sealed(members[row['member']], row['sha256'], row['member'])
        require(len(raw) == row['bytes'], 'Source length differs')
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        require(hashlib.sha1(blob).hexdigest() == row['git_blob_sha1'], 'Source Git blob differs')
    state = json.loads(members['observation.json'])
    for row in state['commands']:
        for channel in ('stdout', 'stderr'):
            record = row[channel]
            require(record['file'] == row['label'] + '.' + channel + '.log', 'Log name differs')
            raw = sealed(members[record['file']], record['sha256'], record['file'])
            require(len(raw) == record['bytes'], 'Log size differs')
    return members, state


def derive(members, state, source_files):
    require(state['status'] == 'RAW_MATCH' and state['cleanup_succeeded'] is True, 'Build or cleanup failed')
    require(state['image'] == rebuild.IMAGE and state['source_commit'] == rebuild.SOURCE_COMMIT,
            'Build input identity differs')
    require(state['program_replays'] == 0 and state['captured_executable_mounted'] is False
            and state['build_network'] == 'none', 'Build scope differs')
    rows = {row['label']: row for row in state['commands']}
    require(len(rows) == len(state['commands']) == 18 and all(row['returncode'] == 0 for row in rows.values()),
            'Command count or exit status differs')
    expected = set(rebuild.PINS) | {'observation.json', 'rebuild.py', 'executed-workflow.yml', 'source-commit.txt',
        'actual-source-before.json.gz', 'actual-source-after.json.gz', 'acquisition.json',
        'registry-archives.json.gz', 'raw-result.json', 'token_metadata.so'}
    for row in rows.values():
        expected.update(row[channel]['file'] for channel in ('stdout', 'stderr'))
    require(set(members) == expected, 'Actual artifact inventory differs')

    def text(label, channel='stdout'):
        return members[rows[label][channel]['file']].decode()

    def command(label, expected):
        require(rows[label]['command'] == expected, 'Command differs: ' + label)

    for name, digest in rebuild.PINS.items():
        sealed(members[name], digest, name)
    patched = json.loads(members['source-manifest.json'])
    for name in ('actual-source-before.json.gz', 'actual-source-after.json.gz'):
        require(json.loads(gzip.decompress(members[name])) == patched, 'Compiled source manifest differs')
    acquisition = json.loads(members['acquisition.json'])
    require(acquisition['source_archive_sha256'] == rebuild.SOURCE_SHA256
            and acquisition['tools_archive_sha256'] == rebuild.TOOLS_SHA256
            and acquisition['tools_archive_bytes'] == rebuild.TOOLS_BYTES, 'Acquisition identity differs')
    image, = json.loads(text('inspect-image'))
    require(image['Id'] == rebuild.IMAGE_ID and rebuild.IMAGE in image['RepoDigests'], 'Image differs')
    lock = tomllib.loads(source_files['programs/token-metadata/Cargo.lock'].decode())
    expected_crates = {(p['name'], p['version']): p['checksum'] for p in lock['package']
                       if p.get('source', '').startswith('registry+')}
    archives = json.loads(gzip.decompress(members['registry-archives.json.gz']))
    require(len(archives) == len(expected_crates) == 537
            and {(row['name'], row['version']): row['sha256'] for row in archives} == expected_crates,
            'Registry archives differ from pinned lockfile')
    git_source, = [p for p in lock['package'] if p.get('source', '').startswith('git+')]
    require(text('git-dependency-revision').strip() == git_source['source'].split('#')[1], 'Git dependency differs')
    start = rows['start-offline-build-container']['command']
    require(start[:9] == ['docker', 'run', '--rm', '--platform', 'linux/amd64', '--cap-drop', 'ALL',
                         '--security-opt', 'no-new-privileges'], 'Container setup differs')
    mounts = [start[i + 1] for i, value in enumerate(start) if value == '--mount']
    root = rows['apply-patch']['cwd']
    out = str(Path(root).parent).replace('\\', '/')
    # Runner paths are POSIX strings even when this verifier runs on Windows.
    require(mounts == [f'type=bind,source={root},target=/build',
        f'type=bind,source={out}/registry,target=/usr/local/cargo/registry',
        f'type=bind,source={out}/git-cache,target=/usr/local/cargo/git',
        f'type=bind,source={out}/downloads/platform-tools.tar.bz2,target=/input/platform-tools.tar.bz2,readonly'],
        'Build mounts differ')
    require(start[start.index('--network') + 1] == 'none'
            and 'CARGO_NET_OFFLINE=true' in start, 'Build networking differs')
    container = text('start-offline-build-container').strip()
    command('build-candidate11', ['docker', 'exec', '-e', 'RUSTUP_TOOLCHAIN=' + rebuild.HOST_TOOLCHAIN,
        '-w', '/build/programs/token-metadata', container, 'cargo', 'build-sbf', '--offline', '--',
        '--config', 'registries.crates-io.protocol="sparse"', '--locked', '--offline',
        '--manifest-path', rebuild.MANIFEST])
    for label in ('driver-before', 'driver-after'):
        require(text(label).split()[0] == rebuild.DRIVER_SHA256, 'Compiler driver differs')
    raw = members['token_metadata.so']
    require(len(raw) == rebuild.RAW_BYTES and sha(raw) == rebuild.RAW_SHA256, 'Raw candidate11 gate differs')
    result = json.loads(members['raw-result.json'])
    require(result == state['raw'] and result['raw_candidate11_equal'] is True
            and result['bytes'] == len(raw) and result['sha256'] == sha(raw)
            and result['padding_bytes_added'] == 0 and result['binary_rewritten'] is False
            and result['deployed_identity_claimed'] is False, 'Raw identity scope differs')
    build_log = text('build-candidate11', 'stderr')
    require('Finished release' in build_log and 'Criterion/releases/download/v2.3.3/' in build_log
            and "unable to resolve host address 'github.com'" in build_log,
            'Retained SDK auxiliary-download failure differs')
    return {'successful_run': 40338395968, 'raw_bytes': len(raw), 'raw_sha256': sha(raw),
        'raw_candidate11_equal': True, 'source_files': len(patched), 'locked_registry_archives': len(archives),
        'registry_archive_bytes': sum(row['bytes'] for row in archives),
        'commands': len(rows), 'artifact_members': len(members), 'network_during_compilation': 'none',
        'sdk_auxiliary_download_failure_retained': True, 'padding_bytes_added': 0,
        'deployed_identity_claimed': False, 'program_replays': 0}


def verify(package=PACKAGE, replay_patch=False):
    receipts = json.loads(sealed(gzip.decompress((package / 'receipts.json.gz').read_bytes()),
                                RECEIPTS_SHA256, 'receipts'))
    require([row['run']['id'] for row in receipts] == list(RUNS), 'Run set differs')
    for receipt in receipts[:-1]:
        members, state = artifact(package, receipt)
        require(state['status'] == 'FAILED' and not any(row['label'] == 'build-candidate11'
                for row in state['commands']), 'Original pre-compiler failure differs')
    members, state = artifact(package, receipts[-1])
    require((package / 'rebuild.py').read_bytes() == members['rebuild.py'], 'Executed rebuild script differs')
    baseline = json.loads(sealed(members['upstream-source-manifest.json'],
                                rebuild.PINS['upstream-source-manifest.json'], 'baseline manifest'))
    source_files = rebuild.source_members(package / 'upstream-source.tar.gz', baseline)
    result = derive(members, state, source_files)
    if replay_patch:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'source'
            source.mkdir()
            for name, raw in source_files.items():
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            patch = root / 'source.patch'
            patch.write_bytes(members['source.patch'])
            subprocess.run(['git', '-c', 'core.autocrlf=false', '-c', 'core.eol=lf', 'apply', str(patch)],
                           cwd=source, capture_output=True, check=True)
            rebuild.check_source(source, json.loads(members['source-manifest.json']))
    result.update(patch_replayed=replay_patch, retained_failed_runs=list(RUNS)[:-1])
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=PACKAGE)
    parser.add_argument('--replay-patch', action='store_true', help='Also apply the patch using Git in a temporary directory')
    args = parser.parse_args()
    print(json.dumps(verify(args.package, args.replay_patch), indent=2))

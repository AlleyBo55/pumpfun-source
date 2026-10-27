"""Offline Git-object and distributed-crate provenance check; no compiler/network."""
import argparse
from datetime import datetime
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
import tempfile
import tomllib

PACKAGE = Path(__file__).resolve().parent
VERSIONS = ['1.13.1-beta.1', '1.13.1', '2.0.0-beta.1', '1.13.2-beta.1', '1.13.2']
REVISION = 'c65f144e74b5410cde1245ebe3d4412ff7acf7a8'
ROOT_TREE = '2d81a2ee1408c5f34a63f21eb7850c8a05e39eef'
PINS = {
    'crate-metadata.json': 'c0acb63ab9bf0873cd2cd4996fbae2ea25aa36e04fc1c1bbdc3cabbc2e8e3f26',
    'download-receipts.json': '283f921b1d904b346409147876b7f12725f04a28478e34159621390078585280',
    'revision-receipts.json': 'bc53fe09cea904162933383050417e51a0e57b36b7202ac2e366ec6e0f3fb7bb',
    'directory-receipts.json': '7f33f14cb2494bf391bfd8ee2fbd22d31985e2c4e98ae7a49166a92c72ed87b3',
    'github-search-observations.json': '543cb92b857596cfa4cf6953fdcc9330fb4e07844dfc5ca8b78f92ef29ed2395',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git_hash(kind, raw):
    return hashlib.sha1(kind.encode() + b' ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def sealed(raw, digest, label):
    require(sha(raw) == digest, 'Changed evidence: ' + label)
    return raw


def git_identifier(value):
    require(isinstance(value, str) and re.fullmatch('[0-9a-f]{40}', value), 'Invalid Git identifier')
    return value


def person(value, date):
    parsed = datetime.fromisoformat(date)
    require(parsed.tzinfo is not None and parsed.microsecond == 0, 'Unsupported commit timestamp')
    require('\n' not in value['fullname'] and '\0' not in value['fullname'], 'Invalid Git identity field')
    return value['fullname'] + ' ' + str(int(parsed.timestamp())) + ' ' + parsed.strftime('%z')


def commit_payload(revision):
    require(revision['type'] == 'git' and revision['synthetic'] is False
            and revision['extra_headers'] == [] and revision['metadata'] == {},
            'Unsupported or synthetic revision encoding')
    payload = ('tree ' + git_identifier(revision['directory']) + '\n'
        + ''.join('parent ' + git_identifier(row['id']) + '\n' for row in revision['parents'])
        + 'author ' + person(revision['author'], revision['date']) + '\n'
        + 'committer ' + person(revision['committer'], revision['committer_date']) + '\n\n'
        + revision['message']).encode()
    require(git_hash('commit', payload) == revision['id'], 'Git commit hash differs')
    return payload


def tree_payload(entries, identifier):
    require(isinstance(entries, list), 'Directory response must be a complete entry list')
    require(len({row['name'] for row in entries}) == len(entries), 'Duplicate tree name')
    allowed = {0o40000: 'dir', 0o100644: 'file', 0o100755: 'file', 0o120000: 'file', 0o160000: 'rev'}
    for row in entries:
        require(row['dir_id'] == identifier and allowed.get(row['perms']) == row['type'], 'Tree mode/type/parent differs')
        require(row['name'] not in ('', '.', '..') and not any(c in row['name'] for c in ('/', '\0')),
                'Invalid tree name')
        git_identifier(row['target'])
    data = b''.join(format(row['perms'], 'o').encode() + b' ' + row['name'].encode() + b'\0'
                    + bytes.fromhex(row['target']) for row in sorted(entries,
                        key=lambda row: row['name'].encode() + (b'/' if row['type'] == 'dir' else b'')))
    require(git_hash('tree', data) == identifier, 'Git tree hash differs')
    return data


def crate_members(raw, version):
    prefix = 'mpl-token-metadata-' + version + '/'
    result = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
        for member in archive:
            require(member.isfile() and member.name.startswith(prefix), 'Unexpected crate member type/path')
            name = member.name[len(prefix):]
            path = PurePosixPath(name)
            require(name not in result and not path.is_absolute() and '..' not in path.parts
                    and '\\' not in name, 'Invalid or duplicate crate path')
            result[name] = archive.extractfile(member).read()
    return result


def locate(path, directories):
    identifier, chain = ROOT_TREE, [ROOT_TREE]
    parts = path.split('/')
    for index, part in enumerate(parts):
        require(identifier in directories, 'Missing tree in proof path')
        candidates = [row for row in directories[identifier] if row['name'] == part]
        require(len(candidates) == 1, 'Missing or duplicate Git path entry: ' + path)
        row, = candidates
        if index < len(parts)-1:
            require(row['type'] == 'dir', 'Intermediate Git path is not a directory')
            identifier = row['target']
            chain.append(identifier)
    return row, chain


def compare_crate(members, directories, vcs):
    require(vcs == {'git': {'sha1': REVISION}, 'path_in_vcs': 'programs/token-metadata/program'},
            'Embedded crate revision/path differs')
    package = tomllib.loads(members['Cargo.toml.orig'].decode())['package']
    require(package['license-file'] == '../../../LICENSE', 'Declared license mapping differs')
    require(package['version'] == '1.13.2-beta.1' and package['name'] == 'mpl-token-metadata',
            'Original Cargo package identity differs')
    rows = []
    excluded = ['.cargo_vcs_info.json', 'Cargo.toml']
    require(all(name in members for name in excluded), 'Cargo metadata missing')
    for name, raw in members.items():
        if name in excluded:
            continue
        path = 'LICENSE' if name == 'LICENSE' else vcs['path_in_vcs'] + '/' + ('Cargo.toml' if name == 'Cargo.toml.orig' else name)
        entry, chain = locate(path, directories)
        digest = git_hash('blob', raw)
        require(entry['type'] == 'file' and entry['perms'] in (0o100644, 0o100755)
                and entry['target'] == digest, 'Distributed file differs from Git blob: ' + name)
        require(entry['length'] == len(raw) and entry['checksums']['sha256'] == sha(raw)
                and entry['checksums']['sha1_git'] == digest, 'Archived content metadata differs: ' + name)
        rows.append({'archive_member': name, 'git_path': path, 'bytes': len(raw), 'sha256': sha(raw),
                     'git_blob_sha1': digest, 'directory_chain': chain})
    return rows, excluded


def derive(package=PACKAGE, git_check=False):
    pinned = {name: json.loads(sealed((package / name).read_bytes(), digest, name)) for name, digest in PINS.items()}
    registry = {row['num']: row for row in pinned['crate-metadata.json']['versions']}
    downloads = {row['version']: row for row in pinned['download-receipts.json']['archives']}
    require(pinned['download-receipts.json']['metadata_sha256'] == PINS['crate-metadata.json'], 'Registry receipt binding differs')
    expected_archives = {'mpl-token-metadata-' + version + '.crate' for version in VERSIONS}
    require({path.name for path in (package / 'archives').iterdir()} == expected_archives, 'Crate archive inventory differs')
    crates, declarations = {}, {}
    for version in VERSIONS:
        filename = 'archives/mpl-token-metadata-' + version + '.crate'
        raw = sealed((package / filename).read_bytes(), registry[version]['checksum'], filename)
        receipt = downloads[version]
        require(receipt['status'] == 200 and receipt['verified'] is True and receipt['bytes'] == len(raw)
                and receipt['sha256'] == receipt['expected_sha256'] == sha(raw), 'Crate acquisition receipt differs')
        crates[version] = crate_members(raw, version)
        declarations[version] = json.loads(crates[version]['.cargo_vcs_info.json'])
    receipts = pinned['revision-receipts.json']
    require([row['version'] for row in receipts] == VERSIONS, 'Revision query coverage differs')
    observations, revision = [], None
    for receipt in receipts:
        commit = declarations[receipt['version']]['git']['sha1']
        require(receipt['commit'] == commit and receipt['url'] == receipt['final_url']
                == 'https://archive.softwareheritage.org/api/1/revision/' + commit + '/', 'Revision query binding differs')
        raw = sealed((package / receipt['response_file']).read_bytes(), receipt['sha256'], receipt['response_file'])
        require(len(raw) == receipt['bytes'] and receipt['content_type'] == 'application/json', 'Revision response metadata differs')
        data = json.loads(raw)
        if commit == REVISION:
            require(receipt['status'] == 200 and data['id'] == commit and data['directory'] == ROOT_TREE, 'Recovered revision differs')
            revision = data
        else:
            require(receipt['status'] == 404 and data == {'exception':'NotFoundExc',
                'reason':'Revision with sha1_git ' + commit + ' not found.'}, 'Unresolved revision evidence differs')
        observations.append({'version':receipt['version'], 'declared_commit':commit, 'archive_status':receipt['status']})
    searches = pinned['github-search-observations.json']
    require(set(searches) == {row['declared_commit'] for row in observations}, 'Global GitHub search coverage differs')
    require(all(row['status'] == 'fulfilled' and row['value']['isError'] is False
                and row['value']['structuredContent'] == {'commits':[]} for row in searches.values()), 'Global GitHub search result differs')
    objects = [('commit', REVISION, commit_payload(revision))]
    directories = {}
    for receipt in pinned['directory-receipts.json']:
        raw = sealed((package / receipt['response_file']).read_bytes(), receipt['sha256'], receipt['response_file'])
        require(len(raw) == receipt['bytes'] and receipt['status'] == 200, 'Directory response differs')
        identifier = Path(receipt['response_file']).stem
        require(receipt['url'] == 'https://archive.softwareheritage.org/api/1/directory/' + identifier + '/', 'Directory query differs')
        require(identifier not in directories, 'Duplicate directory response')
        directories[identifier] = json.loads(raw)
        objects.append(('tree', identifier, tree_payload(directories[identifier], identifier)))
    require({p.stem for p in (package / 'directories').iterdir()} == set(directories), 'Directory file inventory differs')
    require(len(directories) == 24, 'Directory proof count differs')
    rows, excluded = compare_crate(crates['1.13.2-beta.1'], directories, declarations['1.13.2-beta.1'])
    require(len(rows) == 162 and len(crates['1.13.2-beta.1']) == 164, 'Compared crate inventory differs')
    require(set(directories) == {identifier for row in rows for identifier in row['directory_chain']}, 'Unused directory evidence')
    utilize = crates['1.13.2-beta.1']['src/processor/uses/utilize.rs']
    require(sha(utilize) == '203ac94655f6268d5eae95de2b3dffcb47065bbeb713d8da08a9bbdeca29f53e', 'Utilize source differs')
    if git_check:
        # Hash literal payloads without repository discovery/fsck or promisor
        # fetches for referenced objects such as .gitmodules. No objects written.
        with tempfile.TemporaryDirectory() as temporary:
            for kind, expected, raw in objects:
                process = subprocess.run(['git','hash-object','--literally','-t',kind,'--stdin'],
                    input=raw, capture_output=True, cwd=temporary,
                    env=dict(os.environ, GIT_NO_LAZY_FETCH='1'), check=True)
                require(not process.stderr and process.stdout.decode().strip() == expected,
                        'Independent Git hash-object check differs')
    return {'revision_observations':observations, 'revision':REVISION, 'root_tree':ROOT_TREE,
        'git_commit_verified':True, 'git_trees_verified':len(directories), 'distributed_files_matched':len(rows),
        'excluded_generated_members':excluded, 'matched_files':rows,
        'utilize_sha256':sha(utilize), 'new_handler_source_variant':False,
        'deployed_source_identified':False, 'compiler_executed':False, 'independent_git_check':git_check}


def check(package=PACKAGE, git_check=False):
    result = derive(package, git_check)
    expected = dict(result, independent_git_check=False)
    require(json.loads((package / 'findings.json').read_bytes()) == expected, 'Saved findings differ')
    return {name:value for name,value in result.items() if name != 'matched_files'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,default=PACKAGE)
    parser.add_argument('--git-object-check',action='store_true',help='Cross-check reconstructed commit/tree payloads using Git hash-object, without writing objects')
    args = parser.parse_args()
    print(json.dumps(check(args.package,args.git_object_check),indent=2))

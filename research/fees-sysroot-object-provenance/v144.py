"""Static v1.44 sysroot provenance; no release code is executed."""
import gzip
import hashlib
import tarfile
import verify as v
import cross_program as cross


def objects(package):
    provenance = v.read_json(package / 'v144/provenance.json')
    rows = provenance['objects']
    expected = {row['object_sha256'] + '.o': row for row in rows}
    v.require(len(expected) == len(rows) == 10, 'unexpected v144 object set')
    found = {}
    with tarfile.open(package / 'v144/objects.tar.gz', 'r:gz') as archive:
        for member in archive:
            v.require(member.isfile() and member.name in expected and member.name not in found,
                      'unexpected v144 object archive member')
            row = expected[member.name]
            v.require(member.size == row['object_bytes'], 'v144 object size differs')
            raw = archive.extractfile(member).read()
            v.require(v.digest(raw) == row['object_sha256'], 'v144 object digest differs')
            found[member.name] = raw
    v.require(set(found) == set(expected), 'missing v144 object')
    return found


def relative_calls(code):
    v.require(len(code) % 8 == 0, 'unaligned SBF body')
    result, at = [], 0
    while at < len(code):
        instruction = code[at:at + 8]
        if instruction[0] == 0x18:
            v.require(at + 16 <= len(code), 'truncated LDDW')
            at += 16
            continue
        if instruction[:2] == b'\x85\x10':
            result.append(at)
        at += 8
    return result


def analyze(package=v.HERE, repo=v.REPO):
    p = v.read_json(package / 'v144/provenance.json')
    asset = p['asset']
    prior = p['previous_toolchain_receipt']
    raw = v.local_path(repo, prior['path']).read_bytes()
    v.require((len(raw), v.digest(raw)) == (prior['bytes'], prior['sha256']), 'changed prior v144 receipt')
    old = v.read_json(v.local_path(repo, prior['path']))
    v.require((old['url'], old['asset_size_bytes'], old['asset_sha256'], old['official_api_digest']) ==
              (asset['url'], asset['bytes'], asset['sha256'], None), 'prior v144 acquisition differs')
    release = v.read_json(package / 'v144/release-metadata.json')
    row, = [a for a in release['assets'] if a['id'] == asset['asset_id']]
    v.require(release['tag_name'] == 'v1.44' and
              (row['browser_download_url'], row['size'], row['digest']) ==
              (asset['url'], asset['bytes'], None) and asset['publisher_digest'] is None,
              'v144 release receipt differs')
    receipt = v.read_json(package / 'v144/download-receipt.json')
    v.require(receipt['exit'] == 0 and all(receipt[k] == asset[k] for k in asset), 'v144 download receipt differs')
    v.require((package / 'v144/version.md').read_text().startswith(p['rust_commit'] + ' '), 'v144 Rust revision differs')
    for source in v.read_json(package / 'v144/license-sources.json'):
        content = v.local_path(package / 'v144', source['path']).read_bytes()
        if source.get('compression') == 'gzip':
            content = gzip.decompress(content)
        v.require(v.digest(content) == source['sha256'] and
                  hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest() == source['blob_sha1'],
                  'v144 source/license bytes differ')
    raw_objects = objects(package)
    parent = v.read_json(package / 'provenance.json')
    ledger = cross.analyze(package, repo)  # Rechecks hashes and all six call-bounded raw reference windows.
    symbols = v.Elf((v.local_path(repo, parent['builds']['v144-build-01']) / 'unstripped.so').read_bytes())
    captures = {name: v.Elf(v.local_path(repo, path).read_bytes()) for name, path in parent['cross_program_captures'].items()}
    results = []
    for row in p['objects']:
        target = row['rlib'].split('/')[3]
        elf = v.Elf(raw_objects[row['object_sha256'] + '.o'])
        v.require((elf.kind, elf.machine, elf.flags) == (1, row['machine'], row['flags']), 'v144 object header differs')
        function = elf.function(row['function']['symbol'])
        v.require(function == row['function'], 'v144 symbol differs')
        relocs = elf.object_relocations(function)
        code = v.body(elf, function)
        calls = relative_calls(code)
        v.require(relocs == row['relocations'] == [] and not calls, 'v144 helper contains relocations or relative calls')
        key = 'v144_integer_entry' if function['symbol'] == '__multi3' else 'v144_core_fmt_write'
        reference = symbols.function(ledger['helpers'][key]['symbol'])
        same = code == v.body(symbols, reference)
        matches = {name: cross.raw_occurrences(capture, code) for name, capture in captures.items()}
        generic = target in ('sbf-solana-solana', 'sbpf-solana-solana')
        v.require(same == generic, 'unexpected v144 target comparison')
        for name, hits in matches.items():
            expected = [r['start'] for r in ledger['captures'][name]['helper_occurrences'][key]] if generic else []
            v.require(hits == expected, 'unexpected v144 capture occurrences')
        results.append(dict(target=target, object_sha256=row['object_sha256'], function=function,
            object_relocations=relocs, relative_calls=calls, raw_equals_linked_reference=same,
            linked_reference_symbol=reference['symbol'], captured_exact_occurrences=matches))
    v.require({r['target'] for r in results} == {'sbf-solana-solana', 'sbpf-solana-solana',
              'sbpfv1-solana-solana', 'sbpfv2-solana-solana', 'sbpfv3-solana-solana'}, 'unexpected target set')
    return dict(objects=results, retained_complete_objects=10, positive_generic_object_bodies=4,
                raw_capture_windows=6, compiler_executions=0, normalized_comparisons=0,
                generic_target_alias_distinguished=False, unique_historical_compiler_proved=False,
                archive_to_object_rechecked=False)


def check_archive(path, package=v.HERE):
    """Hash the complete release first; read selected regular members in memory."""
    p = v.read_json(package / 'v144/provenance.json')
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    v.require((path.stat().st_size, digest) == (p['asset']['bytes'], p['asset']['sha256']), 'v144 archive size/digest differs')
    selected = {row['path']: row for row in p['selected_rlibs']}
    v.require(len(selected) == len(p['selected_rlibs']) == 10, 'unexpected v144 rlib set')
    wanted = set(selected) | {'version.md'}
    by_rlib = {row['rlib']: row for row in p['objects']}
    v.require(set(by_rlib) == set(selected), 'v144 object/rlib association differs')
    raw_objects = objects(package)
    seen, checked = set(), []
    with tarfile.open(path, 'r|bz2') as archive:
        for member in archive:
            name = member.name.removeprefix('./')
            if name not in wanted:
                continue
            v.require(name not in seen and member.isfile(), 'duplicate or nonregular v144 member')
            seen.add(name)
            raw = archive.extractfile(member).read()
            if name == 'version.md':
                v.require(raw == (package / 'v144/version.md').read_bytes(), 'v144 version member differs')
                continue
            row = selected[name]
            v.require((len(raw), v.digest(raw)) == (row['bytes'], row['sha256']), 'v144 rlib differs')
            expected = by_rlib[name]
            matches = [r for r in v.ar_members(raw) if r[0] == expected['object_member']]
            v.require(len(matches) == 1, 'missing v144 ar object')
            _, offset, payload = matches[0]
            v.require(offset == expected['object_offset'] and
                      payload == raw_objects[expected['object_sha256'] + '.o'], 'v144 archive object differs')
            checked.append(name)
    v.require(seen == wanted, 'missing v144 selected archive member')
    return dict(archive_sha256=digest, selected_rlibs_verified=len(checked),
                complete_objects_equal_archive_members=len(checked), version_md_verified=True,
                publisher_digest_available=False, historical_compiler_identified=False)

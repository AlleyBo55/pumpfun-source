"""Offline verification of the paired v1.37 llc block-layout experiment."""
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import struct
import tarfile
import zipfile

import probe

P = Path(__file__).resolve().parent
RUNS = {
    40365560810: ('d96845bbc3598b4144cf27a5c6d2e5dea471806b', 'failure', '4bc48e2f028c8ff8799950ee105f13885158dc12d4b16cd0c9ac7a1e226486a9'),
    40365964291: ('46d93e56ece6bb2f9222cb145ee9f906a3c90d8f', 'failure', 'dca6a1b253e9c150920926de56bf4ddcab7374411bfa5d7e9ac4c8195a996f55'),
    40366528602: ('40c72c1c209a3d67cb667ab58578263a3168c3ea', 'success', '3aeec015a49f8d8341bdbb457e51499a6b95f10eb7ea9e315894587c7aff820c'),
}
RUST = '764ce69bd00903f5c59f44b6aa72649b173f568c'
LLVM = '7b8db05b564faffb522434b73b7082662171f94a'
STAGES = [
    'Before Finalize ISel and expand pseudo-instructions (finalize-isel)',
    'Before Control Flow Optimizer (branch-folder)',
    'After Control Flow Optimizer (branch-folder)',
    'After Branch Probability Basic Block Placement (block-placement)',
    'After SBF PreEmit Peephole Optimization (sbf-mi-pemit-peephole)',
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def obj(raw):
    return json.loads(raw)


def zip_members(raw):
    result = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        for info in archive.infolist():
            path = PurePosixPath(info.filename)
            require(not info.is_dir() and not path.is_absolute() and '..' not in path.parts and
                    '\\' not in info.filename and info.file_size < 1_000_000, 'unexpected ZIP member')
            require(info.filename not in result, 'duplicate ZIP member')
            result[info.filename] = archive.read(info)
    return result


def ir_blocks(raw):
    text = raw.decode()
    pieces = re.split(r'^([a-z_]+):[^\n]*\n', text, flags=re.M)
    order = pieces[1::2]
    require(len(order) == 5 and len(set(order)) == 5, 'unexpected IR blocks')
    blocks = {pieces[i]: '\n'.join(line.strip() for line in pieces[i + 1].removesuffix('}\n').splitlines()
                                  if line.strip() and line.strip() != '}')
              for i in range(1, len(pieces), 2)}
    return order, blocks


def stage_analysis(raw):
    text = raw.decode()
    banner = '*** Final LLVM Code input to ISel ***\n'
    require(text.count(banner) == 1, 'missing final IR')
    ir = text.split(banner, 1)[1].split('# *** IR Dump ', 1)[0].strip() + '\n'
    parts = re.split(r'^# \*\*\* IR Dump (.*?) \*\*\*:\n', text, flags=re.M)
    stages = dict(zip(parts[1::2], parts[2::2]))
    require(list(stages) == STAGES, 'unexpected or missing machine stages')
    results = {}
    for label, stage in stages.items():
        blocks = list(re.finditer(r'^bb\.(\d+)\.([^:\n]+):', stage, re.M))
        matches = [i for i, match in enumerate(blocks) if match[2] == 'remaining_check']
        require(len(matches) == 1, 'missing remaining-use machine block')
        index, = matches
        start = blocks[index].start()
        end = blocks[index + 1].start() if index + 1 < len(blocks) else stage.index('# End machine code')
        body = stage[start:end].rstrip() + '\n'
        conditional = re.findall(r'^  (JUG[TE]_rr .+)$', body, re.M)
        require(len(conditional) == 1, 'missing unsigned machine comparison')
        results[label] = dict(stage_sha256=sha(stage.encode()), remaining_block=body,
            conditional=conditional[0], unconditional_jumps=re.findall(r'^  (JMP .+)$', body, re.M),
            next_layout_block=blocks[index + 1].group(0) if index + 1 < len(blocks) else None)
    return ir.encode(), results


def elf_text(raw):
    require(raw[:7] == b'\x7fELF\x02\x01\x01' and len(raw) >= 64, 'not ELF64LE')
    kind, machine = struct.unpack_from('<HH', raw, 16)
    flags = struct.unpack_from('<I', raw, 48)[0]
    require((kind, machine, flags) == (1, 247, 0), 'unexpected probe object ABI')
    table = struct.unpack_from('<Q', raw, 40)[0]
    stride, count, strings_index = struct.unpack_from('<HHH', raw, 58)
    require(stride == 64 and table + count * stride <= len(raw) and strings_index < count, 'bad section table')
    sections = [struct.unpack_from('<IIQQQQIIQQ', raw, table + i * stride) for i in range(count)]
    for s in sections:
        require(s[1] == 8 or s[4] + s[5] <= len(raw), 'section outside object')
    names_section = sections[strings_index]
    names = raw[names_section[4]:names_section[4] + names_section[5]]
    text, = [s for s in sections if names[s[0]:].split(b'\0', 1)[0] == b'.text']
    code = raw[text[4]:text[4] + text[5]]
    require(len(code) == 88, 'unexpected tiny function length')
    instructions = []
    for at in range(0, len(code), 8):
        op, regs, off, imm = struct.unpack_from('<BBhi', code, at)
        row = dict(offset=at, raw=code[at:at + 8].hex(), opcode=op, dst=regs & 15,
                   src=regs >> 4, displacement=off, immediate=imm)
        if op in (0x15, 0x2d, 0x3d, 0x05):
            row['target'] = at + 8 + off * 8
        instructions.append(row)
    return dict(object_bytes=len(raw), object_sha256=sha(raw), machine=machine, flags=flags,
                text_file_offset=text[4], text_bytes=len(code), text_sha256=sha(code),
                instructions=instructions, unconditional_jump_count=sum(i['opcode'] == 5 for i in instructions))


def check_commands(members, success):
    observation = obj(members['observation.json'])
    commands = observation['commands']
    for command in commands:
        for stream in ('stdout', 'stderr'):
            record = command[stream]
            raw = members[record['file']]
            require((len(raw), sha(raw)) == (record['bytes'], record['sha256']), 'command log digest differs')
    if not success:
        return observation
    require(observation['status'] == 'COMPILED' and observation['cleanup_returncode'] == 0 and
            all(c['returncode'] == 0 for c in commands), 'successful observation is incomplete')
    by_name = {c['label']: c for c in commands}
    require(len(by_name) == len(commands), 'duplicate command label')
    start = by_name['start']['command']
    require(start[start.index('--network') + 1] == 'none' and '--read-only' in start and
            probe.IMAGE in start, 'compilation isolation differs')
    image, = obj(members['image-inspect.stdout.log'])
    require(image['Id'] == probe.IMAGE_ID and probe.IMAGE in image['RepoDigests'], 'image identity differs')
    archive = obj(members['archive.json'])
    require((archive['bytes'], archive['sha256'], archive['url']) ==
            (probe.ARCHIVE_BYTES, probe.ARCHIVE_SHA, probe.URL), 'archive receipt differs')
    for i, (name, identity) in enumerate(archive['selected'].items()):
        command = by_name['installed-' + str(i)]
        require(command['command'][-1] == probe.TOOLS + '/' + name and
                members[command['stdout']['file']].decode().split()[0] == identity['sha256'],
                'installed tool differs from archive')
    arguments = []
    for variant in ('far-error', 'near-error'):
        command = by_name[variant + '-compile']['command']
        require(command[:2] == ['docker', 'exec'] and command[3] == probe.TOOLS + '/llvm/bin/llc', 'wrong compiler entry')
        require(command[-3:] == ['/input/ir/' + variant + '.ll', '-o', '/tmp/' + variant + '.o'], 'wrong input/output')
        arguments.append(command[4:-3])
        require(members[variant + '-read-object.stdout.log'] == members[variant + '.o'], 'object transfer differs')
    require(arguments[0] == arguments[1] == ['-mtriple=sbf', '-mcpu=generic', '-mattr=+solana', '-O3', '-filetype=obj',
            '-print-isel-input', '-print-before=finalize-isel,branch-folder',
            '-print-after=branch-folder,block-placement,sbf-mi-pemit-peephole'], 'compiler arguments differ')
    return observation


def analyze_members(members):
    check_commands(members, True)
    inputs = probe.inputs()
    results = {}
    for variant, expected in inputs.items():
        require(members[variant + '.ll'] == expected, 'IR input changed')
        final_ir, stages = stage_analysis(members[variant + '-compile.stderr.log'])
        require(ir_blocks(final_ir) == ir_blocks(expected), 'final selection IR changed blocks or order')
        obj_result = elf_text(members[variant + '.o'])
        expected_branch = '2d42040000000000' if variant == 'far-error' else '3d24040000000000'
        require(obj_result['instructions'][2]['raw'] == expected_branch, 'emitted remaining-use branch changed')
        expected_opcode = 'JUGT_rr' if variant == 'far-error' else 'JUGE_rr'
        require(all(row['conditional'].startswith(expected_opcode + ' ') for row in stages.values()),
                'conditional direction differs between stages')
        require(not stages[STAGES[2]]['unconditional_jumps'] and obj_result['unconditional_jump_count'] == 0,
                'tiny experiment unexpectedly retains extra jump')
        results[variant] = dict(input_sha256=sha(expected), final_ir_sha256=sha(final_ir),
                               block_order=ir_blocks(expected)[0], stages=stages, object=obj_result)
    require(ir_blocks(inputs['far-error'])[1] == ir_blocks(inputs['near-error'])[1], 'named CFG blocks differ')
    return dict(variants=results, same_named_input_blocks=True,
                final_ir_preserves_each_input_block_order=True, code_instructions_per_variant=11,
                reproduces_candidate12_extra_jump=False, raw_program_identity_improved=False,
                historical_source_identified=False)


def evidence(package=P):
    rows = obj(gzip.decompress((package / 'provider-receipts.json.gz').read_bytes()))
    require({r['run']['id'] for r in rows} == set(RUNS), 'missing run receipts')
    artifacts = {}
    for row in rows:
        run, artifact = row['run'], row['artifact']
        head, conclusion, digest = RUNS[run['id']]
        require(run['head_sha'] == head and run['status'] == 'completed' and run['conclusion'] == conclusion,
                'provider run binding differs')
        require(run['repository']['full_name'] == 'startrack3r/pumpfun-source', 'unexpected provider repository')
        raw = (package / row['zip_file']).read_bytes()
        require(sha(raw) == digest and artifact['digest'] == 'sha256:' + digest and
                artifact['workflow_run']['head_sha'] == head and artifact['workflow_run']['id'] == run['id'],
                'provider archive binding differs')
        members = zip_members(raw)
        require(members['source-commit.txt'].decode().strip() == head, 'executed revision differs')
        observation = check_commands(members, conclusion == 'success')
        artifacts[run['id']] = members
        if run['id'] == 40365560810:
            require(observation['error'] == 'Missing tools' and len(observation['commands']) == 1,
                    'first acquisition/lookup failure missing')
        if run['id'] == 40365964291:
            require(observation['error'].startswith('far-error-copy failed') and
                    b'Could not find the file /tmp/far-error.o' in members['far-error-copy.stderr.log'],
                    'second collection failure missing')
    successful = artifacts[40366528602]
    require(successful['probe.py'] == (package / 'probe.py').read_bytes(), 'executed controller differs')
    require(successful['test_probe.py'] == (package / 'test_probe.py').read_bytes(), 'executed input tests differ')
    return successful


def check_sources(package=P):
    receipts = obj((package / 'compiler-source-receipts.json').read_bytes())
    with tarfile.open(package / 'compiler-source.tar.gz', 'r:gz') as archive:
        members = archive.getmembers()
        require(all(m.isfile() for m in members) and len({m.name for m in members}) == len(members), 'source tar shape differs')
        data = {m.name: archive.extractfile(m).read() for m in members}
    require(set(data) == {r['path'] for r in receipts} and len(data) == 7, 'source set differs')
    for row in receipts:
        raw = data[row['path']]
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'] and
                hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['blob_sha1'],
                'source bytes differ')
    root = obj((package / 'rust-root-tree.json').read_bytes())
    src = obj((package / 'rust-src-tree.json').read_bytes())
    require(root['sha'] == RUST and not root['truncated'] and not src['truncated'], 'incomplete Rust metadata')
    entry, = [r for r in root['tree'] if r['path'] == 'src']
    require(entry['sha'] == src['sha'], 'Rust src tree differs')
    entry, = [r for r in src['tree'] if r['path'] == 'llvm-project']
    require((entry['sha'], entry['mode'], entry['type']) == (LLVM, '160000', 'commit'), 'LLVM gitlink differs')
    return data


def verify(package=P):
    manifest = obj((package / 'manifest.json').read_bytes())
    actual = {p.relative_to(package).as_posix() for p in package.rglob('*') if p.is_file()
              and '__pycache__' not in p.parts and p.name != 'manifest.json'}
    require(actual == set(manifest), 'packet file set differs')
    for name, digest in manifest.items():
        require(sha((package / name).read_bytes()) == digest, 'packet file changed: ' + name)
    check_sources(package)
    members = evidence(package)
    require(members['version.md'].decode().startswith(RUST + ' '), 'release Rust identity differs')
    result = analyze_members(members)
    require(result == obj((package / 'analysis.json').read_bytes()), 'analysis differs')
    return dict(verified=True, successful_run=40366528602, retained_failed_runs=2,
                same_named_input_blocks=True, direction_changes_before_finalize_isel=True,
                candidate12_extra_jump_reproduced=False, raw_program_identity_improved=False)


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))

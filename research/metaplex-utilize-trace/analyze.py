"""Derive a bounded Utilize branch attribution from raw-identical compiler output.

This is an evidence-specific check, not a general LLVM IR or MIR interpreter.
"""
import re
import struct

from trace import RAW_BYTES, RAW_SHA256, require, sha

FUNCTION = '_ZN14token_metadata9processor4uses7utilize15process_utilize17h9789c7990f4c0b83E'
STAGES = [
    ('before-codegenprepare', '*** IR Dump Before CodeGen Prepare (codegenprepare) ***'),
    ('before-finalize-isel', '# *** IR Dump Before Finalize ISel and expand pseudo-instructions (finalize-isel) ***:'),
    ('after-finalize-isel', '# *** IR Dump After Finalize ISel and expand pseudo-instructions (finalize-isel) ***:'),
    ('after-branch-folder', '# *** IR Dump After Control Flow Optimizer (branch-folder) ***:'),
    ('after-block-placement', '# *** IR Dump After Branch Probability Basic Block Placement (block-placement) ***:'),
    ('after-preemit-peephole', '# *** IR Dump After SBF PreEmit Peephole Optimization (sbf-mi-pemit-peephole) ***:'),
]
FLAGS = ['-Cllvm-args=-print-before=codegenprepare,finalize-isel',
         '-Cllvm-args=-print-after=finalize-isel,branch-folder,block-placement,sbf-mi-pemit-peephole']


def ordered(text, statements):
    offset = 0
    for statement in statements:
        found = text.find(statement, offset)
        require(found >= 0, 'Missing or reordered data/control-flow evidence: ' + statement)
        offset = found + len(statement)


def snapshots(log):
    starts = [m.start() for m in re.finditer(rb'(?m)^(?:# )?\*\*\* IR Dump ', log)] + [len(log)]
    result = []
    for start, end in zip(starts, starts[1:]):
        raw = log[start:end]
        if not any(FUNCTION.encode() in line for line in raw.splitlines()[:3]):
            continue
        require(len(result) < len(STAGES), 'Extra Utilize snapshot')
        name, header = STAGES[len(result)]
        require(raw.splitlines()[0].decode() == header, 'Missing, reordered or unexpected compiler stage')
        # The empty separator after a machine-function dump belongs to neither
        # function. Keep the complete dump as an exact contiguous log slice.
        if name != 'before-codegenprepare':
            terminator = ('# End machine code for function ' + FUNCTION + '.\n').encode()
            require(terminator in raw, 'Incomplete machine function dump')
            raw = raw[:raw.index(terminator) + len(terminator)]
        result.append((name, raw, {'file': 'snapshots/' + name + '.txt',
            'log_byte_offset': start, 'log_line': log.count(b'\n', 0, start) + 1,
            'bytes': len(raw), 'sha256': sha(raw)}))
    require(len(result) == len(STAGES), 'Incomplete Utilize snapshots')
    return result


def machine_blocks(text):
    matches = list(re.finditer(r'(?m)^bb\.(\d+)(?:[^\n]*):\n', text))
    return {int(match[1]): text[match.start():matches[i+1].start() if i+1 < len(matches)
            else text.index('# End machine code')] for i, match in enumerate(matches)}


def machine_guard(text, virtual):
    blocks = machine_blocks(text)
    requested, remaining = ('%47:gpr', '%22:gpr') if virtual else ('$r9', '$r7')
    require(re.search(re.escape(requested) + r' = (?:COPY|MOV_rr) \$r5\n', blocks[0]),
            'Requested-use argument binding differs')
    load = ('%22:gpr = LDD %stack.26, 8' if virtual else '$r7 = LDD $r10, -184')
    require(load + ' :: (dereferenceable load (s64) from %ir.231)' in text, 'Remaining-use load differs')
    pattern = re.compile(r'(?m)^  JUGT_rr ' + re.escape(requested + ', ' + remaining) + r', %bb\.(\d+)\n')
    candidates = [(number, body, pattern.search(body)) for number, body in blocks.items() if pattern.search(body)]
    require(len(candidates) == 1, 'Expected one unsigned requested > remaining branch')
    number, body, branch = candidates[0]
    error = int(branch[1])
    require('(%ir-block.239):' in blocks[error] and 'LD_imm64 369367187456' in blocks[error],
            'Branch does not reach the observed error 86 block')
    tail = body[branch.end():]
    jump = re.search(r'^  JMP %bb\.(\d+)\s*$', tail)
    if jump:
        success, continuation = int(jump[1]), 'explicit-jump'
    else:
        require(not tail.strip(), 'Unexpected instruction after conditional branch')
        numbers = list(blocks)
        success, continuation = numbers[numbers.index(number)+1], 'fallthrough'
    require('(%ir-block.243):' in blocks[success], 'Success edge does not reach remaining-use subtraction')
    if virtual:
        require('SUB_rr %22:gpr(tied-def 0), %47:gpr' in blocks[success], 'Virtual subtraction differs')
    else:
        ordered(blocks[success].replace('MOV_rr', 'COPY'),
                ['$r1 = COPY $r7', '$r1 = SUB_rr killed $r1(tied-def 0), $r9'])
    return {'guard_block': number, 'condition': 'requested_uses > remaining_uses (unsigned)',
        'taken_error_block': error, 'other_success_block': success, 'other_edge': continuation,
        'requested_register': requested, 'remaining_register': remaining}


def derive(log, raw):
    # A trace whose associated raw output differs must never acquire this attribution.
    require(len(raw) == RAW_BYTES and sha(raw) == RAW_SHA256, 'Raw candidate11 gate differs')
    parts = snapshots(log)
    ir = parts[0][1].decode()
    ordered(ir, ['%231 = getelementptr inbounds %135, ptr %32, i64 0, i32 2',
        '%232 = load i64, ptr %231, align 8', '%233 = icmp ult i64 %232, %4',
        '%234 = select i1 %230, i1 true, i1 %233', 'br i1 %234, label %239, label %243',
        '239: ', 'store i32 86, ptr %240, align 4', '243: ', '%244 = sub i64 %232, %4'])
    stages = []
    for i, (name, data, location) in enumerate(parts):
        fact = {'stage': name, **location}
        if i == 0:
            fact.update(condition='remaining_uses < requested_uses (unsigned)',
                        remaining_value='%232', requested_value='%4', taken_error_block=239,
                        other_success_block=243, other_edge='combined-zero-total-remaining-guard')
        else:
            fact.update(machine_guard(data.decode(), virtual=i < 3))
        stages.append(fact)
    branch = raw[238832:238840]
    opcode, registers, displacement, immediate = struct.unpack('<BBhi', branch)
    require(branch.hex() == '2d79120000000000' and opcode == 0x2d and registers == 0x79
            and immediate == 0, 'Final raw guard differs')
    return {'scope': 'candidate11-only; no deployed-source or historical-compiler identification',
        'run_id': 40343712336, 'raw_bytes': len(raw), 'raw_sha256': sha(raw),
        'trace_bytes': len(log), 'trace_sha256': sha(log), 'function': FUNCTION,
        'stages': stages, 'raw_guard': {'file_offset': 238832, 'hex': branch.hex(),
            'condition': 'r9 > r7 (unsigned)', 'taken_error_offset': 238840 + displacement * 8,
            'other_success_offset': 238840},
        'earliest_captured_machine_direction': 'before-finalize-isel',
        'first_pass_introducing_direction_identified': False,
        'deployed_identity_claimed': False}, parts


def invocation(raw):
    require(raw.endswith(b'\0'), 'Compiler argv is not NUL-terminated')
    args = raw[:-1].decode().split('\0')
    require(args[:5] == ['rustc', '--crate-name', 'token_metadata', '--edition=2021', 'program/src/lib.rs'],
            'Compiler invocation differs')
    require(args[-2:] == FLAGS and [arg for arg in args if 'llvm-args=' in arg] == FLAGS,
            'Diagnostic options differ')
    require(args[args.index('--target')+1] == 'sbf-solana-solana'
            and '--emit=dep-info,link' in args and 'opt-level=z' in args
            and 'codegen-units=1' in args and 'overflow-checks=on' in args, 'Codegen options differ')
    require(not any('target-cpu=' in arg or 'target-feature=' in arg for arg in args),
            'Explicit target CPU/features differ')
    return args

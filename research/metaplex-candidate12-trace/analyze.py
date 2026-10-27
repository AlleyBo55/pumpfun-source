"""Reproduce bounded observations from candidate12's raw-gated compiler trace.

The snapshots are exact contiguous log bytes, not compilable LLVM modules.
"""
import re
import struct

from trace import RAW_BYTES, RAW_SHA256, require, sha

FUNCTION = '_ZN14token_metadata9processor4uses7utilize15process_utilize17h9789c7990f4c0b83E'
FLAGS = [
    '-Cllvm-args=-print-before=codegenprepare,finalize-isel',
    '-Cllvm-args=-print-after=codegenprepare,finalize-isel,branch-folder,block-placement,sbf-mi-pemit-peephole',
    '-Cllvm-args=-print-isel-input', '-Cllvm-args=-filter-print-funcs=' + FUNCTION,
    '-Cllvm-args=-debug-pass=Structure',
]
STAGES = [
    ('before-codegenprepare', '*** IR Dump Before CodeGen Prepare (codegenprepare) ***'),
    ('after-codegenprepare', '*** IR Dump After CodeGen Prepare (codegenprepare) ***'),
    ('final-isel-input', '*** Final LLVM Code input to ISel ***'),
    ('before-finalize-isel', '# *** IR Dump Before Finalize ISel and expand pseudo-instructions (finalize-isel) ***:'),
    ('after-finalize-isel', '# *** IR Dump After Finalize ISel and expand pseudo-instructions (finalize-isel) ***:'),
    ('after-branch-folder', '# *** IR Dump After Control Flow Optimizer (branch-folder) ***:'),
    ('after-block-placement', '# *** IR Dump After Branch Probability Basic Block Placement (block-placement) ***:'),
    ('after-preemit-peephole', '# *** IR Dump After SBF PreEmit Peephole Optimization (sbf-mi-pemit-peephole) ***:'),
]


def ordered(text, statements):
    offset = 0
    for statement in statements:
        found = text.find(statement, offset)
        require(found >= 0, 'Missing or reordered data/control-flow evidence: ' + statement)
        offset = found + len(statement)


def snapshots(log):
    result, previous = [], -1
    for index, (name, header) in enumerate(STAGES):
        marker = (header + '\n').encode()
        require(log.count(marker) == 1, 'Missing or duplicate compiler stage: ' + name)
        banner = log.index(marker)
        require(banner > previous, 'Reordered compiler stage')
        previous = banner
        if index < 3:
            matches = list(re.finditer(rb'(?ms)^define void @' + re.escape(FUNCTION.encode())
                                      + rb'[^\n]*\n.*?^}\n', log[banner:]))
            require(matches, 'Missing complete IR function')
            match = matches[0]
            start = banner + match.start()
            between = log[banner + len(marker):start]
            require(all(not line or line.startswith(b'; Function Attrs:') for line in between.splitlines()),
                    'Intervening data after IR banner')
            raw = match[0]
        else:
            start = banner
            marker = ('# End machine code for function ' + FUNCTION + '.\n').encode()
            require(marker in log[start:], 'Incomplete machine function')
            end = log.index(marker, start) + len(marker)
            raw = log[start:end]
            require(FUNCTION.encode() in raw.splitlines()[1], 'Wrong machine function')
        result.append((name, raw, {'file': 'snapshots/' + name + '.txt',
            'log_byte_offset': start, 'log_line': log.count(b'\n', 0, start) + 1,
            'bytes': len(raw), 'sha256': sha(raw)}))
    return result


def machine_blocks(text):
    matches = list(re.finditer(r'(?m)^bb\.(\d+)(?:[^\n]*):\n', text))
    return {int(match[1]): text[match.start():matches[i+1].start() if i+1 < len(matches)
            else text.index('# End machine code')] for i, match in enumerate(matches)}


def invocation(raw):
    require(raw.endswith(b'\0'), 'Compiler argv is not NUL-terminated')
    args = raw[:-1].decode().split('\0')
    require(args[:5] == ['rustc', '--crate-name', 'token_metadata', '--edition=2021', 'program/src/lib.rs'],
            'Compiler invocation differs')
    require(args[-len(FLAGS):] == FLAGS and [arg for arg in args if 'llvm-args=' in arg] == FLAGS,
            'Diagnostic options differ')
    require(args[args.index('--target')+1] == 'sbf-solana-solana'
            and '--emit=dep-info,link' in args and 'opt-level=z' in args
            and 'codegen-units=1' in args and 'overflow-checks=on' in args, 'Codegen options differ')
    require(not any('target-cpu=' in arg or 'target-feature=' in arg for arg in args),
            'Explicit target CPU/features differ')
    return args


def machine_guard(text, virtual):
    blocks = machine_blocks(text)
    requested, remaining = ('%47:gpr', '%22:gpr') if virtual else ('$r9', '$r7')
    require(re.search(re.escape(requested) + r' = (?:COPY|MOV_rr) \$r5\n', blocks[0]),
            'Requested-use argument binding differs')
    load = '%22:gpr = LDD %stack.26, 8' if virtual else '$r7 = LDD $r10, -184'
    require(load + ' :: (dereferenceable load (s64) from %ir.236)' in text,
            'Remaining-use load differs')
    pattern = re.compile(r'(?m)^  JUGT_rr ' + re.escape(requested + ', ' + remaining) + r', %bb\.(\d+)\n')
    candidates = [(n, body, pattern.search(body)) for n, body in blocks.items() if pattern.search(body)]
    require(len(candidates) == 1, 'Expected one unsigned requested > remaining branch')
    number, body, branch = candidates[0]
    error = int(branch[1])
    require('(%ir-block.235):' in body, 'Remaining guard IR origin differs')
    error_ir = 248 if virtual else 239
    require(f'(%ir-block.{error_ir}):' in blocks[error]
            and 'LD_imm64 369367187456' in blocks[error], 'Branch does not reach error 86')
    jump = re.fullmatch(r'  JMP %bb\.(\d+)\s*', body[branch.end():])
    require(jump, 'Explicit success jump missing or changed')
    success = int(jump[1])
    require('(%ir-block.243):' in blocks[success], 'Success does not reach subtraction')
    if virtual:
        require('SUB_rr %22:gpr(tied-def 0), %47:gpr' in blocks[success], 'Virtual subtraction differs')
        require('(%ir-block.239):' in blocks[37] and 'LD_imm64 369367187456' in blocks[37]
                and 'JEQ_ri %47:gpr, 0, %bb.37' in blocks[33]
                and 'JUGT_rr %47:gpr, %21:gpr, %bb.37' in blocks[85],
                'Distinct zero/total error target differs')
    else:
        ordered(blocks[success].replace('MOV_rr', 'COPY'),
                ['$r1 = COPY $r7', '$r1 = SUB_rr killed $r1(tied-def 0), $r9'])
        # Both earlier guards now share the remaining guard's error destination.
        require(f'JEQ_ri $r9, 0, %bb.{error}' in text
                and f'JUGT_rr $r9, $r1, %bb.{error}' in text, 'Shared error target differs')
    numbers = list(blocks)
    following = numbers[numbers.index(number)+1]
    return {'guard_block': number, 'guard_ir_block': 235,
        'condition': 'requested_uses > remaining_uses (unsigned)',
        'taken_error_block': error, 'taken_error_ir_block': error_ir,
        'success_block': success, 'success_edge': 'explicit-jump',
        'next_layout_block': following, 'error_is_next_layout_block': error == following,
        'requested_register': requested, 'remaining_register': remaining}


def derive(log, raw):
    require(len(raw) == RAW_BYTES and sha(raw) == RAW_SHA256, 'Raw candidate12 gate differs')
    parts = snapshots(log)
    require(parts[1][1] == parts[2][1], 'Post-CodeGenPrepare and final IR differ')
    rows = []
    for index, (name, data, location) in enumerate(parts):
        row = {'stage': name, **location}
        if index < 3:
            error = 247 if index == 0 else 248
            pointer = 248 if index == 0 else 249
            ordered(data.decode(), ['%226 = icmp eq i64 %4, 0',
                '%229 = icmp ult i64 %228, %4', '%230 = select i1 %226, i1 true, i1 %229',
                'br i1 %230, label %239, label %235',
                '235:', '%236 = getelementptr inbounds %135, ptr %32, i64 0, i32 2',
                '%237 = load i64, ptr %236, align 8', '%238 = icmp ult i64 %237, %4',
                f'br i1 %238, label %{error}, label %243',
                '239:', 'store i32 86, ptr %240, align 4',
                '243:', '%244 = sub i64 %237, %4', f'{error}:',
                f'store i32 86, ptr %{pointer}, align 4'])
            row.update(remaining_guard_ir_block=235, zero_total_error_ir_block=239,
                       remaining_error_ir_block=error, success_ir_block=243)
        else:
            row.update(machine_guard(data.decode(), virtual=index < 5))
        rows.append(row)
    require([row['error_is_next_layout_block'] for row in rows[3:]] == [False, False, True, True, True],
            'Observed error-layout transition differs')
    branch, jump = raw[238832:238840], raw[238840:238848]
    require(branch.hex() == '2d79010000000000' and jump.hex() == '0500070000000000',
            'Final raw guard/jump differs')
    _, _, error_displacement, _ = struct.unpack('<BBhi', branch)
    _, _, success_displacement, _ = struct.unpack('<BBhi', jump)
    return {'scope': 'retained rejected candidate12; no new source variant or deployed identity',
        'run_id': 40352331268, 'raw_bytes': len(raw), 'raw_sha256': sha(raw),
        'trace_bytes': len(log), 'trace_sha256': sha(log), 'function': FUNCTION, 'stages': rows,
        'after_codegenprepare_equals_final_isel_input': True,
        'raw_guard': {'file_offset': 238832, 'hex': branch.hex(),
            'taken_error_offset': 238840 + error_displacement * 8},
        'raw_success_jump': {'file_offset': 238840, 'hex': jump.hex(),
            'success_offset': 238848 + success_displacement * 8},
        'error_target_convergence_interval': 'after Finalize ISel through the captured post-branch-folder point',
        'specific_error_merging_pass_identified': False,
        'first_pass_introducing_direction_identified': False,
        'deployed_identity_claimed': False}, parts

"""Check the observed final-IR to selected-machine-code boundary for Utilize."""
import re

import analyze
from trace import RAW_BYTES, RAW_SHA256, require, sha

FLAGS = [analyze.FLAGS[0], '-Cllvm-args=-print-after=codegenprepare',
    '-Cllvm-args=-print-isel-input', '-Cllvm-args=-filter-print-funcs=' + analyze.FUNCTION,
    '-Cllvm-args=-debug-pass=Structure']
IR_HEADERS = ['*** IR Dump Before CodeGen Prepare (codegenprepare) ***',
    '*** IR Dump After CodeGen Prepare (codegenprepare) ***',
    '*** Final LLVM Code input to ISel ***']
NAMES = ['before-codegenprepare.ll', 'after-codegenprepare.ll', 'final-isel-input.ll']


def ir_bodies(log):
    pattern = rb'(?ms)^define void @' + re.escape(analyze.FUNCTION.encode()) + rb'[^\n]*\n.*?^}\n'
    return list(re.finditer(pattern, log))


def guard(text):
    analyze.ordered(text, ['%226 = icmp eq i64 %4, 0',
        '%227 = getelementptr inbounds %135, ptr %32, i64 0, i32 3',
        '%228 = load i64, ptr %227, align 8', '%229 = icmp ult i64 %228, %4',
        '%230 = select i1 %226, i1 true, i1 %229',
        '%231 = getelementptr inbounds %135, ptr %32, i64 0, i32 2',
        '%232 = load i64, ptr %231, align 8', '%233 = icmp ult i64 %232, %4',
        '%234 = select i1 %230, i1 true, i1 %233', 'br i1 %234, label %239, label %243',
        '239:', 'store i32 86, ptr %240, align 4', '243:', '%244 = sub i64 %232, %4'])
    start = text.index('  %226 = icmp eq i64 %4, 0\n')
    end = text.index('  br i1 %234, label %239, label %243\n', start)
    end += len('  br i1 %234, label %239, label %243\n')
    return text[start:end].encode()


def derive(log, raw, baseline_ir, baseline_machine):
    require(len(raw) == RAW_BYTES and sha(raw) == RAW_SHA256, 'Raw candidate11 gate differs')
    matches = ir_bodies(log)
    require(len(matches) == 3, 'Expected three complete Utilize IR bodies')
    parts, rows = {}, []
    for name, header, match in zip(NAMES, IR_HEADERS, matches):
        marker = (header + '\n').encode()
        require(log.count(marker) == 1, 'IR stage banner differs')
        banner_offset = log.index(marker)
        between = log[banner_offset + len(marker):match.start()]
        require(all(not line or line.startswith(b'; Function Attrs:') for line in between.splitlines()),
                'Wrong function or intervening data after IR stage banner')
        parts[name] = match[0]
        rows.append({'file': name, 'banner': header, 'log_byte_offset': match.start(),
            'log_line': log.count(b'\n', 0, match.start()) + 1,
            'bytes': len(match[0]), 'sha256': sha(match[0])})
    before, after, final = [parts[name] for name in NAMES]
    require(after == final, 'Post-CodeGenPrepare and final selection-input bodies differ')
    guards = [guard(body.decode()) for body in (before, after, final)]
    require(guards[0] == guards[1] == guards[2], 'Combined guard changed before selection')
    baseline_match, = ir_bodies(baseline_ir)
    require(before == baseline_match[0], 'Earlier run optimized-IR body differs')

    header = (analyze.STAGES[1][1] + '\n').encode()
    require(log.count(header) == 1, 'Selected-machine stage count differs')
    start = log.index(header)
    end_marker = ('# End machine code for function ' + analyze.FUNCTION + '.\n').encode()
    require(log.count(end_marker) == 1, 'Machine function count differs')
    end = log.index(end_marker, start) + len(end_marker)
    machine = log[start:end]
    require(machine == baseline_machine, 'Earlier run selected-machine dump differs')
    selected = analyze.machine_guard(machine.decode(), virtual=True)
    blocks = analyze.machine_blocks(machine.decode())
    numbers = list(blocks)
    current = selected['guard_block']
    following = numbers[numbers.index(current)+1]
    require(current == 83 and following == 34 and '(%ir-block.235):' in blocks[following],
            'Selected guard layout differs')
    require('JEQ_ri %47:gpr, 0, %bb.36' in blocks[33]
            and 'JUGT_rr %47:gpr, %21:gpr, %bb.36' in blocks[84], 'Zero/total short-circuit guards differ')
    require([n for n in numbers if n in (33, 84, 83, 34, 36, 38)] == [33, 84, 83, 34, 36, 38],
            'Machine short-circuit block order differs')
    # The emitted pass structure independently names the selector followed by
    # the inserted printer and then finalization. It is not a per-node DAG trace.
    sequence = ('      SBF DAG->DAG Pattern Instruction Selection\n'
                '      MachineFunction Printer\n'
                '      Finalize ISel and expand pseudo-instructions\n')
    require(sequence.encode() in log, 'Recorded selector/finalization sequence differs')
    parts['before-finalize-isel.txt'] = machine
    rows.append({'file': 'before-finalize-isel.txt', 'banner': analyze.STAGES[1][1],
        'log_byte_offset': start, 'log_line': log.count(b'\n', 0, start)+1,
        'bytes': len(machine), 'sha256': sha(machine)})
    return {'run_id': 40347761346, 'raw_bytes': len(raw), 'raw_sha256': sha(raw),
        'trace_bytes': len(log), 'trace_sha256': sha(log), 'function': analyze.FUNCTION,
        'snapshots': rows, 'after_codegenprepare_equals_final_isel_input': True,
        'comparison_method': 'exact function text bytes; stage banners excluded; no normalization',
        'combined_guard_unchanged': True, 'combined_guard_sha256': sha(guards[0]),
        'earlier_run_before_codegenprepare_body_equal': True,
        'earlier_run_before_finalize_machine_equal': True,
        'selected_guard': selected, 'selected_next_layout_block': following,
        'selected_next_layout_ir_block': 235, 'selected_error_is_next_layout_block': False,
        'observed_expansion_interval': 'final LLVM input through SBF DAG selection, before Finalize ISel',
        'internal_dag_event_observed': False, 'deployed_identity_claimed': False}, parts


def invocation(raw, baseline):
    require(raw.endswith(b'\0'), 'Compiler argv is not NUL-terminated')
    args = raw[:-1].decode().split('\0')
    require(args[-len(FLAGS):] == FLAGS, 'Boundary diagnostic options differ')
    previous = analyze.invocation(baseline)
    require(args[:-len(FLAGS)] == previous[:-len(analyze.FLAGS)],
            'Non-diagnostic compiler arguments changed')
    return args

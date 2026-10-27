"""Compare the new raw-gated run with the retained candidate11 boundary run."""
import json
import re

import analyze
from trace import RAW_BYTES, RAW_SHA256, require, sha

REFERENCE_RUN = 40347761346
REFERENCE_HEAD = 'c75ac9c5397ddf53c1ed7516c3ccc77611a02bbc'
REFERENCE_ZIP = 'dbc3e9edd72bf3bb5cf7b3f9d6e8d51a1b87266853e36683e828bf12d906a699'
REFERENCE_RECEIPT = '30586b83baf609acbd216c2526a459796291bf73c0775f2dd0f5751245b1feea'
REFERENCE_RAW = '3bbaf27ff0c10ff68d8a195a82f39eadee266f324067bd0a66081710be30b4ec'
REFERENCE_IR = '53c696eb06a494644b27443547e74a0675bc1ae84eff069be0ffb4f0bcfea538'


def derive(current, reference):
    require(len(current['token_metadata.so']) == RAW_BYTES
            and sha(current['token_metadata.so']) == RAW_SHA256, 'Raw candidate12 gate differs')
    require(len(reference['token_metadata.so']) == 707448
            and sha(reference['token_metadata.so']) == REFERENCE_RAW, 'Reference raw candidate11 differs')
    require(current['upstream-source-manifest.json'] == reference['upstream-source-manifest.json'],
            'Baseline source manifest differs')
    before = json.loads(reference['source-manifest.json'])
    after = json.loads(current['source-manifest.json'])
    require(before.keys() == after.keys() and len(before) == 812, 'Source inventory differs')
    changed = [name for name in before if before[name] != after[name]]
    require(changed == ['programs/token-metadata/program/src/processor/uses/utilize.rs'],
            'Contrast changes more than the retained Utilize source')
    current_args = analyze.invocation(current['rustc-4272.argv'])
    previous_raw = reference['rustc-4272.argv']
    require(previous_raw.endswith(b'\0'), 'Reference argv truncated')
    previous_args = previous_raw[:-1].decode().split('\0')
    previous_flags = list(analyze.FLAGS)
    previous_flags[1] = '-Cllvm-args=-print-after=codegenprepare'
    require(previous_args[-len(previous_flags):] == previous_flags
            and current_args[:-len(analyze.FLAGS)] == previous_args[:-len(previous_flags)],
            'Non-diagnostic compiler arguments differ')
    log = reference['build-candidate11-isel-input.stderr.log']
    marker = b'*** Final LLVM Code input to ISel ***\n'
    require(log.count(marker) == 1, 'Reference final IR banner differs')
    start = log.index(marker)
    match = re.search(rb'(?ms)^define void @' + re.escape(analyze.FUNCTION.encode())
                      + rb'[^\n]*\n.*?^}\n', log[start:])
    require(match and sha(match[0]) == REFERENCE_IR, 'Reference final IR differs')
    analyze.ordered(match[0].decode(), ['%226 = icmp eq i64 %4, 0',
        '%230 = select i1 %226, i1 true, i1 %229', '%233 = icmp ult i64 %232, %4',
        '%234 = select i1 %230, i1 true, i1 %233', 'br i1 %234, label %239, label %243',
        '239:', 'store i32 86, ptr %240, align 4', '243:', '%244 = sub i64 %232, %4'])
    final = analyze.snapshots(current['build-candidate12-traced.stderr.log'])[2][1]
    require(final != match[0], 'Contrast final IR unexpectedly equal')
    return {'candidate11_reference_run': REFERENCE_RUN,
        'candidate11_raw_sha256': REFERENCE_RAW,
        'candidate11_final_ir_sha256': REFERENCE_IR,
        'candidate12_final_ir_sha256': sha(final),
        'source_files': len(before), 'changed_source_files': changed,
        'non_diagnostic_compiler_arguments_equal': True,
        'candidate11_guard_shape': 'combined zero/total/remaining predicate to one error block',
        'candidate12_guard_shape': 'zero/total predicate followed by separate remaining guard and distinct error block',
        'new_source_variant_proposed': False, 'historical_deployed_input_identified': False}

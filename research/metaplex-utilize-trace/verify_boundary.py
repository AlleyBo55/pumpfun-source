"""Verify the additional instruction-selection boundary capture offline."""
import gzip
import io
import json
from pathlib import Path
import tarfile

import analyze_boundary
import verify

PACKAGE = Path(__file__).resolve().parent
RUNS = {40347761346: ('c75ac9c5397ddf53c1ed7516c3ccc77611a02bbc', 'success',
    'dbc3e9edd72bf3bb5cf7b3f9d6e8d51a1b87266853e36683e828bf12d906a699')}
RECEIPT_SHA256 = '30586b83baf609acbd216c2526a459796291bf73c0775f2dd0f5751245b1feea'
JOB_LOG_SHA256 = 'e8cf561ab28c35b624928fdf1d77c20188129c03863370a910b75c3e884c7d4e'
SOURCE_ARCHIVE_SHA256 = 'bb3912f6552662ad16aa6ae5062aa1cbad978b6a756ec0e4cfed493b84094ef3'
SOURCE_RECEIPTS_SHA256 = '6e8942f6295c755bfdb45679b4e2886fd707b55603dd22c3bec64f6414314d5e'
require, sealed = verify.require, verify.sealed


def sources(root):
    receipts = json.loads(sealed((root / 'compiler-source-receipts.json').read_bytes(),
                                 SOURCE_RECEIPTS_SHA256, 'compiler source receipts'))
    raw = sealed((root / 'compiler-source.tar.gz').read_bytes(), SOURCE_ARCHIVE_SHA256, 'compiler source archive')
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
        entries = archive.getmembers()
        require(len(entries) == len(receipts) == 6
                and [entry.name for entry in entries] == [row['path'] for row in receipts],
                'Compiler source inventory differs')
        result = {}
        for entry, row in zip(entries, receipts):
            require(entry.isfile() and row['status'] == 200, 'Compiler source type/status differs')
            raw = sealed(archive.extractfile(entry).read(), row['sha256'], row['path'])
            require(len(raw) == row['bytes'], 'Compiler source length differs')
            result[row['path']] = raw
    require('llvm/LICENSE.TXT' in result, 'LLVM license missing')
    pipeline = result['llvm/lib/CodeGen/TargetPassConfig.cpp'].decode()
    verify.analyze.ordered(pipeline, ['if (PrintISelInput)',
        '*** Final LLVM Code input to ISel ***', '// All passes which modify the LLVM IR are now complete;',
        '} else if (addInstSelector())', 'addPass(&FinalizeISelID);',
        'printAndVerify("After Instruction Selection");'])
    return result


def load(package=PACKAGE):
    root = package / 'isel-boundary'
    receipt = json.loads(sealed(gzip.decompress((root / 'receipt.json.gz').read_bytes()), RECEIPT_SHA256, 'boundary receipt'))
    members, state = verify.artifact(root, receipt, runs=RUNS)
    for name in ('boundary.py', 'rustc-isel-wrapper.sh'):
        require((package / name).read_bytes() == members[name], 'Boundary executed source differs: ' + name)
    job = sealed(gzip.decompress((root / 'hosted-job.log.gz').read_bytes()), JOB_LOG_SHA256, 'boundary job log')
    require(b'Ran 3 tests' in job and b' OK' in job, 'Boundary hosted wrapper tests differ')
    return members, state


def check(package=PACKAGE):
    baseline = verify.verify(package)
    root = package / 'isel-boundary'
    members, state = load(package)
    source_files = verify.rebuild.source_members(package / 'upstream-source.tar.gz',
        json.loads(members['upstream-source-manifest.json']))
    result = verify.derive(members, state, source_files, runner_name='boundary.py',
        wrapper_name='rustc-isel-wrapper.sh', build_label='build-candidate11-isel-input', run_id=40347761346)
    original_receipt = json.loads(gzip.decompress((package / 'receipt.json.gz').read_bytes()))
    original, _ = verify.artifact(package, original_receipt)
    argv = analyze_boundary.invocation(members['rustc-4272.argv'], original['rustc-4272.argv'])
    require(json.loads((root / 'compiler-argv.json').read_bytes()) == argv, 'Boundary saved argv differs')
    analysis, parts = analyze_boundary.derive(members['build-candidate11-isel-input.stderr.log'],
        members['token_metadata.so'], (package / 'snapshots/before-codegenprepare.txt').read_bytes(),
        (package / 'snapshots/before-finalize-isel.txt').read_bytes())
    require(json.loads((root / 'analysis.json').read_bytes()) == analysis, 'Boundary saved analysis differs')
    for name, raw in parts.items():
        require((root / name).read_bytes() == raw, 'Boundary saved snapshot differs: ' + name)
    result.update(boundary_snapshots=len(parts), compiler_source_files=len(sources(root)),
                  prior_run_verified=baseline['successful_run'],
                  after_codegenprepare_equals_final_isel_input=True, internal_dag_event_observed=False)
    return result


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))

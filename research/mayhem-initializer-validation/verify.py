#!/usr/bin/env python3
"""Recheck saved byte, source, signature and differential evidence; execute no target."""
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
from solders.transaction import Transaction

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from validation_matrix import cases

ORIGINAL = 'a87fa9f866272514e6acb852b668c4a08aeb173d56c883039991d114d1199bdb'
PUMP = '7a19affaa2c6187e04a5fe0ea298cee81fa5eb8c24cfcc30d85f615e89f7b02d'
HASHES = {
    'baseline': '77b8e81cd813f3e987f5e87bb9765eed132f63b3d3fd73363a92e3a4ff64c436',
    'constraint': 'b62b45f8d26d8ce132b878977d82969c7515aea2931e7eae9aac33df5e069f3f',
    'vault': '8e6a5f8c34a12303096902e50848f556bc7a9d9ce0dc0d9030e632b85b88e166',
    'retained': 'cbe8c8e71f0c256326cf639f303b3d939244320637531d79041585c9358020e2',
}
FIELDS = ['error', 'anchor_errors', 'before', 'after', 'events', 'inner', 'return', 'signed_transaction_base64']

def require(ok, message):
    if not ok:
        raise ValueError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read_json(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)

def check_matrix(report, candidate, count, mismatch_count, runner_hash):
    require(report['original_sha256'] == ORIGINAL and report['candidate_sha256'] == candidate, 'Matrix binary binding')
    require(report['runner_sha256'] == runner_hash, 'Matrix runner binding')
    require(report['compared_fields'] == FIELDS, 'Comparison scope changed')
    require(report['case_count'] == count == len(report['cases']), 'Matrix case count')
    require([r['case'] for r in report['cases']] == cases()[:count], 'Matrix input cases changed')
    failures = []
    for row in report['cases']:
        left, right = row['original'], row['candidate']
        require(left['before'] == right['before'], 'Initial fixture mismatch')
        require(left['signed_transaction_base64'] == right['signed_transaction_base64'], 'Transaction inputs differ')
        raw = base64.b64decode(left['signed_transaction_base64'], validate=True)
        tx = Transaction.from_bytes(raw)
        require(bytes(tx) == raw and all(tx.verify_with_results()), 'Invalid transaction signature')
        require(left['error'] is not None, 'Standalone rejection unexpectedly successful')
        diff = [key for key in FIELDS if left[key] != right[key]]
        require(diff == row['differences'], 'Falsely reported difference fields')
        if diff:
            failures.append(row['case']['name'])
    require(failures == report['mismatches'] and len(failures) == mismatch_count, 'Falsely reported mismatch count')
    return {'cases': count, 'mismatches': len(failures), 'signed_transactions_verified': count}

def allocated_sections(data):
    require(data[:6] == b'\x7fELF\x02\x01', 'Expected ELF64 little-endian')
    offset = struct.unpack_from('<Q', data, 40)[0]
    entry_size, count, names_idx = struct.unpack_from('<HHH', data, 58)
    require(entry_size == 64 and 0 < count and names_idx < count and offset + count * 64 <= len(data), 'Bad section table')
    rows = [struct.unpack_from('<IIQQQQIIQQ', data, offset + i*64) for i in range(count)]
    names_row = rows[names_idx]
    names = data[names_row[4]:names_row[4] + names_row[5]]
    result = {}
    for row in rows:
        name = names[row[0]:].split(b'\0', 1)[0].decode()
        if row[2] & 2:
            require(name not in result, 'Duplicate allocated section')
            require(row[1] == 8 or row[4] + row[5] <= len(data), 'Truncated allocated section')
            result[name] = (row[3], row[5], b'' if row[1] == 8 else data[row[4]:row[4] + row[5]])
    return result

def check_listing(original, text, start, end):
    pattern = re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+){8,16})\t(.+)$')
    pc = start
    in_text = False
    for line in text.splitlines():
        if line == 'Disassembly of section .text:':
            require(not in_text, 'Repeated text section')
            in_text = True
            continue
        if not in_text or not line.strip() or re.fullmatch(r'[0-9a-f]+ <.*>:', line):
            continue
        row = pattern.fullmatch(line)
        require(row is not None, 'Unparsed disassembly row')
        raw = bytes.fromhex(row[2])
        require(len(raw) in (8, 16) and (len(raw) == 16) == (raw[0] == 0x18), 'Instruction width')
        require('<unknown>' not in row[3] and not row[3].startswith('.'), 'Undecoded listing row')
        require(int(row[1], 16) == pc and pc + len(raw) <= end, 'Noncontiguous listing')
        require(raw == original[pc:pc + len(raw)], 'Listing bytes differ from capture')
        pc += len(raw)
    require(pc == end, 'Incomplete bounded listing')
    return end - start

def verify(repo):
    manifest = read_json(HERE / 'manifest.json')
    actual = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()
              and p.name != 'manifest.json' and '__pycache__' not in p.parts}
    require(actual == set(manifest), 'Package inventory changed')
    for name, expected in manifest.items():
        path = HERE / name
        require(not path.is_symlink() and sha(path.read_bytes()) == expected, 'Package bytes changed: ' + name)
    original = (repo / 'evidence/original/mayhem/deployed.so').read_bytes()
    require(sha(original) == ORIGINAL, 'Wrong original capture')
    require(sha((repo / 'evidence/original/pump/deployed.so').read_bytes()) == PUMP, 'Wrong Pump CPI driver')
    inputs = read_json(HERE / 'inputs.json')
    for name, expected in inputs['harness_sha256'].items():
        require(sha((HERE / 'harness' / name).read_bytes()) == expected, 'Retained harness changed')
    before = read_json(HERE / 'build/registry-before.json.gz')
    require(before == read_json(HERE / 'build/registry-after.json.gz'), 'Registry before/after differs')
    source_name = 'programs/mayhem/src/lib.rs'
    baselines = {}
    for variant in ('baseline', 'constraint', 'vault'):
        root = HERE / 'build' / (variant + '-source')
        observed = {p.relative_to(root).as_posix():sha(p.read_bytes()) for p in root.rglob('*') if p.is_file()}
        require(observed == read_json(HERE / 'build' / (variant+'-source-before.json')) ==
                read_json(HERE / 'build' / (variant+'-source-after.json')), 'Source inventory differs')
        baselines[variant] = {p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}
    source = baselines['baseline'][source_name].decode()
    a = '    #[account(seeds = [b"mint-authority"], bump, seeds::program = state::PUMP_ID)]\n    pub mint_authority: Signer<\'info>,'
    b = '    #[account(signer, seeds = [b"mint-authority"], bump, seeds::program = state::PUMP_ID)]\n    pub mint_authority: UncheckedAccount<\'info>,'
    c = '#[account(init, payer = payer, associated_token::mint = mint, associated_token::authority = sol_vault, associated_token::token_program = token_program)]'
    d = c.replace('account(init,', 'account(init_if_needed,')
    require(source.count(a) == source.count(c) == 1, 'Ambiguous source edits')
    expected = dict(baselines['baseline'])
    expected[source_name] = source.replace(a, b).encode()
    require(expected == baselines['constraint'], 'Unexpected signer-only source change')
    expected[source_name] = source.replace(a, b).replace(c, d).encode()
    require(expected == baselines['vault'], 'Unexpected final source change')
    raw_reports = read_json(HERE / 'raw-comparisons.json')
    for variant in ('baseline', 'constraint', 'vault'):
        data = (HERE / 'build' / (variant+'.so')).read_bytes()
        require(sha(data) == HASHES[variant], 'Candidate hash changed')
        require(allocated_sections(data) == allocated_sections((HERE/'build'/(variant+'.symbols.so')).read_bytes()), 'Strip changed allocated sections')
        row = raw_reports[variant]
        different = sum(a != b for a,b in zip(original,data))
        require(row['original_sha256'] == ORIGINAL and row['candidate_sha256'] == HASHES[variant], 'Comparison hash')
        require(row['original_bytes'] == len(original) and row['candidate_bytes'] == len(data), 'Comparison length')
        require(row['different_positions_in_shared_length'] == different and
                row['total_differing_positions'] == different + abs(len(original)-len(data)), 'Comparison byte count')
        require(row['full_byte_equality'] == (original == data) is False, 'False raw identity claim')
    for file in ('commands.json', 'retry-commands.json', 'vault-commands.json'):
        for row in read_json(HERE / 'build' / file):
            require(sha((HERE/'build'/(row['label']+'.log')).read_bytes()) == row['log_sha256'], 'Command log mismatch')
            require(row['exit_code'] == (101 if row['label'] == 'constraint-build' else 0), 'Unexpected command result')
            if 'build' in row['label'] or 'strip' in row['label']:
                command = row['argv']
                require(command[command.index('--network')+1] == 'none', 'Build was not network isolated')
                require(not any('/comparison' in p or '/evidence/original/' in p for p in command), 'Original mounted during compilation')
    matrices = {}
    for file, variant, count, bad, version in [
        ('retained-baseline-matrix', 'retained',45,27,1), ('fresh-baseline-matrix','baseline',45,27,1),
        ('constraint-matrix','constraint',45,1,1), ('baseline-expanded-matrix','baseline',53,35,2),
        ('constraint-expanded-matrix','constraint',53,9,2), ('vault-matrix','vault',53,0,2)]:
        runner = HERE / ('validation_matrix_v1.py' if version == 1 else 'validation_matrix.py')
        report = read_json(HERE/'runtime'/(file+'.json.gz'))
        require(report['harness_sha256'] == inputs['harness_sha256']['mayhem_initialize_state_differential.py'], 'Matrix fixture binding')
        matrices[file] = check_matrix(report, HASHES[variant], count, bad, sha(runner.read_bytes()))
    for variant in ('baseline','constraint','vault'):
        report = read_json(HERE/'runtime'/(variant+'-cpi.json.gz'))
        require(report['candidate_pump_sha256'] == report['original_pump_sha256'] == PUMP, 'CPI Pump driver')
        require(report['original_mayhem_sha256'] == ORIGINAL and report['candidate_mayhem_sha256'] == HASHES[variant], 'CPI Mayhem binding')
        require(report['script_sha256'] == inputs['harness_sha256']['pump_create_mayhem_differential.py'], 'CPI harness binding')
        require(len(report['cases']) == 17 and report['mismatches'] == [], 'CPI case count or mismatches')
        for row in report['cases']:
            diff = [key for key in ('before','after','error','events','inner','return') if row['original'][key] != row['candidate'][key]]
            require(diff == row['diff'] == [], 'False CPI match')
    for file, variant, bad in [('retained-baseline-five','retained',5), ('constraint-five','constraint',2), ('vault-five','vault',0)]:
        report = read_json(HERE/'runtime'/(file+'.json'))
        require(report['original_sha256'] == ORIGINAL and report['candidate_sha256'] == HASHES[variant], 'Five-case binary binding')
        require(report['case_count'] == len(report['cases']) == 5, 'Five-case count')
        failures = []
        for row in report['cases']:
            equal = all(row['original'][key] == row['candidate'][key] for key in ('error','anchor_error','state_created'))
            require(equal == row['equal'], 'False five-case equality')
            if not equal: failures.append(row['case']['name'])
        require(failures == [r['case'] for r in report['mismatches']] and len(failures) == bad, 'Five-case mismatches')
    static = read_json(HERE/'static/capture.json')
    require(static['original_sha256'] == ORIGINAL, 'Static original binding')
    for row in static['captures']:
        require(sha((HERE/'static'/row['path']).read_bytes()) == row['sha256'], 'Listing hash')
        check_listing(original, (HERE/'static'/row['path']).read_text(), row['start'], row['end'])
    require(original[0x6b3c0:0x6b3c8] == bytes.fromhex('b7010000d2070000'), 'Original 2002 instruction')
    require(original[0xaded1:0xaded1+14] == b'mint_authority', 'Original named constraint')
    for pc, target in ((515984,528112),(528264,430840),(528528,534840)):
        opcode, regs, off, immediate = struct.unpack_from('<BBhi', original, pc)
        require(opcode == 0x85 and regs == 0x10 and pc+8+immediate*8 == target, 'Initializer call correspondence')
    require(0x6ae58 + 8 + struct.unpack_from('<h',original,0x6ae58+2)[0]*8 == 0x6b3c0, 'Signer error branch')
    print(json.dumps({'saved_evidence': 'PASS', 'final_validation_cases': 53, 'final_validation_mismatches': 0,
                      'existing_cpi_cases': 17, 'existing_cpi_mismatches': 0, 'full_byte_equality': False}, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=HERE.parents[1])
    verify(parser.parse_args().repo.resolve())

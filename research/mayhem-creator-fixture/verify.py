#!/usr/bin/env python3
"""Check saved signed inputs and results; does not compile or replay programs."""
import argparse
import base64
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

from solders.pubkey import Pubkey
from solders.transaction import Transaction

HERE = Path(__file__).resolve().parent
FIELDS = ('before', 'after', 'error', 'events', 'inner', 'return', 'signed_transaction_base64')
ZERO = '11111111111111111111111111111111'
USER = 'D9R1yZCctRaqnQyD6dTthaKxYX6s9TUUT8undKVMPNGc'
DISTINCT = 'Bqqt1tFkrCw35zoLcqDXK4yAmo5bw725EZkgeMMy28qw'
CURVE = '3KBNm2F83WL33PQ6Ljvowfi3iCBrUkPLDY7dNcguehD4'
ERROR = 'TransactionErrorInstructionError((1, Tagged(InstructionErrorCustom(6030))))'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_harness(repo):
    path = repo / 'repro/behavioral-recovery/scripts/pump_create_mayhem_differential.py'
    spec = importlib.util.spec_from_file_location('creator_harness', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_report(report, harness):
    require([r['case'] for r in report['cases']] == harness.cases(), 'Case inventory changed')
    require(len(report['cases']) == 20, 'Expected twenty cases')
    failures = []
    for row in report['cases']:
        case = row['case']
        left, right = row['original'], row['candidate']
        require(left['before'] == right['before'], 'Initial fixtures differ')
        require(left['signed_transaction_base64'] == right['signed_transaction_base64'], 'Transactions differ')
        raw = base64.b64decode(left['signed_transaction_base64'], validate=True)
        tx = Transaction.from_bytes(raw)
        require(bytes(tx) == raw and all(tx.verify_with_results()), 'Invalid signature')
        instructions = [ix for ix in tx.message.instructions
                        if tx.message.account_keys[ix.program_id_index] == harness.PROGRAM]
        require(len(instructions) == 1, 'Expected one Pump instruction')
        payload = bytes(instructions[0].data)
        require(payload[:8] == hashlib.sha256(b'global:create_v2').digest()[:8], 'Wrong instruction')
        # Decode independently of the harness serializer, including all Borsh lengths.
        offset = 8
        for field, default in [('name', 'Synthetic Coin'), ('symbol', 'SYNTH'),
                               ('uri', 'https://example.invalid/metadata.json')]:
            require(offset + 4 <= len(payload), 'Missing string length')
            size = struct.unpack_from('<I', payload, offset)[0]
            offset += 4
            expected = case.get(field, default).encode()
            require(size == len(expected) and payload[offset:offset + size] == expected, 'String input differs')
            offset += size
        creator = case.get('creator', USER)
        require(payload[offset:offset + 32] == bytes(Pubkey.from_string(creator)), 'Creator input differs')
        offset += 32
        require(payload[offset:offset + 1] == bytes([bool(case.get('is_mayhem_mode', True))]), 'Mode input differs')
        require(payload[offset + 1:] == bytes.fromhex(case.get('optional_args', '')), 'Optional inputs differ')
        diff = [field for field in FIELDS if left[field] != right[field]]
        require(diff == row['diff'], 'Reported differences are false')
        if diff:
            failures.append(case['case'])
        if case['case'].startswith('zero-creator'):
            require(creator == ZERO, 'Zero case changed')
            for result in (left, right):
                require(result['error'] == ERROR, 'Zero creator did not reject with 6030')
                require(any('Error Code: CreatorShouldNotBeZero. Error Number: 6030.' in log
                            for log in result['logs']), 'Named creator error missing')
                require(result['after'][CURVE] is None, 'Rejected creation left a curve')
        if case['case'].startswith('distinct-creator'):
            require(creator == DISTINCT and creator != USER, 'Distinct creator control changed')
            for result in (left, right):
                require(result['error'] is None, 'Distinct creator rejected')
                account = result['after'][CURVE]
                data = bytes.fromhex(account['data'])
                require(account['owner'] == str(harness.PROGRAM) and len(data) == 166,
                        'Wrong curve account')
                # BondingCurve: discriminator, five u64 reserves/supply, bool, Pubkey.
                require(data[:8] == bytes([23, 183, 248, 55, 96, 216, 172, 96])
                        and data[49:81] == bytes(Pubkey.from_string(DISTINCT)), 'Persisted creator differs')
    require(failures == report['mismatches'] == [], 'Differential mismatch')
    return {'saved_evidence': 'PASS', 'cases': 20, 'mismatches': 0,
            'zero_creator_rejections': 2, 'distinct_creator_successes': 2}


def verify(repo):
    inputs = json.loads((HERE / 'inputs.json').read_text())
    report_path = HERE / 'corrected-pair.json.gz'
    report = json.loads(gzip.decompress(report_path.read_bytes()))
    require(digest(report_path) == inputs['report_sha256'], 'Receipt bytes changed')
    for field, record in inputs['binaries'].items():
        require(digest(repo / record['path']) == report[field] == record['sha256'], 'Binary binding differs')
    script = repo / inputs['harness_path']
    require(digest(script) == report['script_sha256'] == inputs['harness_sha256'], 'Harness binding differs')
    return check_report(report, load_harness(repo))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=HERE.parents[1])
    print(json.dumps(verify(parser.parse_args().repo.resolve()), indent=2))

"""Execute every optional-byte value against the original and one candidate."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from fee_recovery_fixture import FeeFixture, AccountMeta, Instruction, Transaction, FailedTransactionMetadata


def execute(fixture, data):
    before = fixture.vm.get_account(fixture.key)
    instruction = Instruction(fixture.program, data, [AccountMeta(fixture.key, False, False),
                              AccountMeta(fixture.config_program, False, False)])
    transaction = Transaction.new_signed_with_payer([instruction], fixture.payer.pubkey(),
                   [fixture.payer], fixture.vm.latest_blockhash())
    result = fixture.vm.send_transaction(transaction)
    if isinstance(result, FailedTransactionMetadata):
        outcome, metadata = dict(error=str(result.err())), result.meta()
    else:
        outcome, metadata = dict(fees=list(struct.unpack('<QQQ', result.return_data().data))), result
    after = fixture.vm.get_account(fixture.key)
    assert before.data == after.data and before.lamports == after.lamports
    return dict(outcome=outcome, logs=metadata.logs(), compute_units=metadata.compute_units_consumed())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expected-differences', type=int, default=0,
                        help='Only for reproducing the known baseline differences; proposal uses zero.')
    args = parser.parse_args()
    fixtures = [FeeFixture(), FeeFixture(args.candidate)]
    for fixture in fixtures:
        fixture.config([(0, (1, 2, 3)), (1000, (11, 12, 13))],
                       [(0, (4, 5, 6)), (1000, (14, 15, 16))], (7, 8, 9), (10, 11, 12))
    discriminator = bytes(next(item['discriminator'] for item in fixtures[0].idl['instructions']
                               if item['name'] == 'get_fees'))
    rows, failures, outcome_failures, log_failures, compute_differences = [], [], [], [], []
    for cap in (0, 1000, 2**128 - 1):
        for pool in (0, 1):
            for flag in [b''] + [bytes([value]) for value in range(256)]:
                data = discriminator + bytes([pool]) + cap.to_bytes(16, 'little') + bytes(8) + flag
                a, b = [execute(fixture, data) for fixture in fixtures]
                row = dict(cap=cap, pool=pool, flag_hex=flag.hex(), original=a, candidate=b)
                rows.append(row)
                if a['outcome'] != b['outcome']:
                    outcome_failures.append(len(rows) - 1)
                if a['logs'] != b['logs']:
                    log_failures.append(len(rows) - 1)
                if a['outcome'] != b['outcome'] or a['logs'] != b['logs']:
                    failures.append(len(rows) - 1)
                if a['compute_units'] != b['compute_units']:
                    compute_differences.append(len(rows) - 1)
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    report = dict(scope='Every optional-byte value plus absence, both valid pool flags, three caps, one fixed valid account configuration; exact outcomes and raw logs compared, compute differences reported separately. No RPC or on-chain action.',
        original_sha256=sha(ROOT / 'evidence/original/pump_fees/deployed.so'),
        candidate_sha256=sha(args.candidate), case_count=len(rows),
        failures=failures, outcome_failures=outcome_failures, log_failures=log_failures,
        compute_differences=compute_differences,
        expected_baseline_differences=args.expected_differences, cases=rows)
    args.output.write_text(json.dumps(report, separators=(',', ':')) + '\n')
    print(json.dumps(dict(cases=len(rows), failures=len(failures), compute_differences=len(compute_differences))))
    assert not outcome_failures
    assert len(failures) == len(compute_differences) == args.expected_differences


if __name__ == '__main__':
    main()

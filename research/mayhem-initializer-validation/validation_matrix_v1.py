#!/usr/bin/env python3
"""Compare initializer rejection precedence using signed, offline LiteSVM transactions."""
import argparse
import base64
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
from solders.account import Account
from solders.compute_budget import set_compute_unit_limit
from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.transaction_metadata import FailedTransactionMetadata

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def cases():
    result = [{'name': 'valid-mint-unsigned-pda'}]
    result += [{'name': f'account-count-{n}', 'account_count': n} for n in range(10)]
    result += [{'name': f'mint-{m}', 'mint': m} for m in
               ('missing', 'system-owned', 'wrong-owner', 'empty', 'short', 'uninitialized', 'legacy-token')]
    result += [{'name': f'global-{m}', 'global': m} for m in
               ('missing', 'wrong-owner', 'wrong-discriminator', 'short', 'wrong-address')]
    result += [{'name': f'authority-{m}-mint-{mint}', 'authority': m, 'mint': mint}
               for m in ('wrong-unsigned', 'wrong-signed') for mint in ('valid', 'missing')]
    result += [{'name': 'payer-unsigned', 'payer_signer': False},
               {'name': 'payer-readonly', 'payer_writable': False},
               {'name': 'wrong-system-program', 'wrong_program': 'system'},
               {'name': 'wrong-token-program', 'wrong_program': 'token'},
               {'name': 'wrong-ata-program', 'wrong_program': 'ata'},
               {'name': 'preexisting-token-vault', 'vault_exists': True},
               {'name': 'preexisting-mayhem-state', 'state_exists': True},
               {'name': 'discriminator-only', 'trailing_bytes': 0},
               {'name': 'trailing-one-byte', 'trailing_bytes': 1},
               {'name': 'trailing-64-bytes', 'trailing_bytes': 64}]
    result += [{'name': f'instruction-prefix-{n}', 'payload_length': n} for n in range(8)]
    return result

def execute(m, binary, c):
    fixture = m.Fixture(binary)
    vm = fixture._vm()
    fee_payer = Keypair.from_seed(bytes([37]) * 32)
    wrong_authority = Keypair.from_seed(bytes([38]) * 32)
    wrong_address = Keypair.from_seed(bytes([39]) * 32).pubkey()
    vm.set_account(fee_payer.pubkey(), Account(10**12, b'', m.SYS))
    global_key = m.GLOBAL
    global_account = vm.get_account(global_key)
    mode = c.get('global', 'valid')
    if mode == 'missing':
        vm.set_account(global_key, Account(0, b'', m.SYS))
    elif mode == 'wrong-owner':
        vm.set_account(global_key, Account(global_account.lamports, global_account.data, m.TOKEN2022))
    elif mode == 'wrong-discriminator':
        vm.set_account(global_key, Account(global_account.lamports, bytes(8) + global_account.data[8:], m.MAY))
    elif mode == 'short':
        vm.set_account(global_key, Account(global_account.lamports, global_account.data[:12], m.MAY))
    elif mode == 'wrong-address':
        global_key = wrong_address
        vm.set_account(global_key, global_account)
    mode = c.get('mint', 'valid')
    mint_data = fixture._mint(m.MINT_AUTHORITY_PUMP)
    mint_owner = m.TOKEN2022
    if mode == 'system-owned':
        mint_owner = m.SYS
    elif mode == 'wrong-owner':
        mint_owner = m.MAY
    elif mode == 'legacy-token':
        mint_owner = m.TOKEN
    elif mode == 'empty':
        mint_data = b''
    elif mode == 'short':
        mint_data = mint_data[:81]
    elif mode == 'uninitialized':
        mint_data = mint_data[:45] + b'\0' + mint_data[46:]
    if mode != 'missing':
        vm.set_account(m.MINT, Account(10**9, mint_data, mint_owner))
    if c.get('vault_exists'):
        vm.set_account(m.VAULT, Account(10**8, fixture._tokacct(m.MINT, m.SOLV), m.TOKEN2022))
    if c.get('state_exists'):
        state_data = hashlib.sha256(b'account:MayhemState').digest()[:8] + bytes(98)
        vm.set_account(m.STATE, Account(10**8, state_data, m.MAY))
    else:
        vm.set_account(m.STATE, Account(0, b'', m.SYS))
    mode = c.get('authority', 'pda')
    authority = m.MINT_AUTHORITY_PUMP if mode == 'pda' else wrong_authority.pubkey()
    vm.set_account(authority, Account(10**9, b'', m.SYS))
    keys = [m.PAYER.pubkey(), global_key, authority, m.SOLV, m.MINT, m.VAULT, m.STATE, m.SYS, m.TOKEN2022, m.ATA]
    if c.get('wrong_program'):
        i = {'system': 7, 'token': 8, 'ata': 9}[c['wrong_program']]
        keys[i] = wrong_address
        vm.set_account(wrong_address, Account(10**9, b'', m.SYS))
    signers = {0: c.get('payer_signer', True), 2: mode == 'wrong-signed'}
    writable = {3, 5, 6} | ({0} if c.get('payer_writable', True) else set())
    metas = [AccountMeta(k, signers.get(i, False), i in writable) for i, k in enumerate(keys)]
    metas = metas[:c.get('account_count', 10)]
    needed = {x.pubkey for x in metas if x.is_signer}
    signer_keys = [fee_payer] + [kp for kp in (m.PAYER, wrong_authority) if kp.pubkey() in needed]
    payload = m.DISC + bytes(c.get('trailing_bytes', 0))
    if 'payload_length' in c:
        payload = payload[:c['payload_length']]
    tx = Transaction.new_signed_with_payer([set_compute_unit_limit(1_400_000), Instruction(m.MAY, payload, metas)],
                                           fee_payer.pubkey(), signer_keys, vm.latest_blockhash())
    assert all(tx.verify_with_results()), 'Every actual signature must verify'
    watch = sorted(set(keys + [fee_payer.pubkey(), m.STATE, m.VAULT]), key=str)
    def snapshot():
        result = {}
        for key in watch:
            account = vm.get_account(key)
            if account and account.executable:
                continue
            result[str(key)] = None if account is None else {
                'lamports': account.lamports, 'owner': str(account.owner), 'data': account.data.hex()}
        return result
    before = snapshot()
    result = vm.send_transaction(tx)
    failed = isinstance(result, FailedTransactionMetadata)
    meta = result.meta() if failed else result
    raw = json.loads(meta.to_json())
    logs = meta.logs()
    anchor = [line.split('Program log: ')[-1] for line in logs if 'AnchorError' in line]
    return {'error': str(result.err()) if failed else None, 'anchor_errors': anchor,
            'before': before, 'after': snapshot(), 'events': [line for line in logs if line.startswith('Program data:')],
            'inner': raw['inner_instructions'], 'return': raw.get('return_data'), 'logs': logs,
            'signed_transaction_base64': base64.b64encode(bytes(tx)).decode(), 'signatures_verified': True}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--candidate', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    if a.output.exists():
        ap.error('output must be a fresh path')
    harness = a.repo / 'repro/behavioral-recovery/scripts/mayhem_initialize_state_differential.py'
    spec = importlib.util.spec_from_file_location('baseline_harness', harness)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    original = a.repo / 'evidence/original/mayhem/deployed.so'
    fields = ['error', 'anchor_errors', 'before', 'after', 'events', 'inner', 'return', 'signed_transaction_base64']
    results = []
    for c in cases():
        x, y = execute(m, original, c), execute(m, a.candidate, c)
        diff = [f for f in fields if x[f] != y[f]]
        assert x['error'] is not None, 'This standalone matrix contains rejection cases only'
        results.append({'case': c, 'original': x, 'candidate': y, 'differences': diff})
        print(c['name'], ':', 'MATCH' if not diff else ','.join(diff), flush=True)
    mismatches = [r['case']['name'] for r in results if r['differences']]
    report = {'schema': 'mayhem-initializer-validation-v1', 'original_sha256': digest(original),
              'candidate_sha256': digest(a.candidate), 'harness_sha256': digest(harness), 'runner_sha256': digest(__file__),
              'compared_fields': fields, 'scope': 'Signed offline standalone rejection matrix; no positive initializer or whole-file identity claim.',
              'case_count': len(results), 'mismatches': mismatches, 'cases': results}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_bytes(gzip.compress(json.dumps(report, indent=2, sort_keys=True).encode(), mtime=0))
    print(f'{len(results)} cases; {len(mismatches)} mismatches', flush=True)
    return bool(mismatches)

if __name__ == '__main__':
    raise SystemExit(main())

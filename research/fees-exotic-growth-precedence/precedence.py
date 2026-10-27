from pathlib import Path
import argparse,hashlib,itertools,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from fees_config_differential import ConfigFixture,AUTH,Account,fees

def run(candidate):
    rows=[]
    for allocation,lamports,balance,triple in itertools.product([2512,4097],[1,10**9],[1,10**9],[(1,2,3),(10001,0,0),(2**64-1,1,0)]):
        case=dict(instruction='set_exotic_flat_fees',arg=fees(triple).hex(),allocation=allocation,lamports=lamports)
        results=[]
        for binary in [ROOT/'evidence/original/pump_fees/deployed.so',candidate]:
            fixture=ConfigFixture(binary);old=fixture.vm.get_account(AUTH.pubkey());fixture.vm.set_account(AUTH.pubkey(),Account(balance,old.data,old.owner));results.append(fixture.run(case))
        a,b=results;fields=['error','data_hex','lamports','owner','balance_deltas','events','inner_instructions'];match=all(a[k]==b[k]for k in fields)
        rows.append(dict(case=case,authority_lamports=balance,fees=list(triple),original=a,candidate=b,match=match))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    return dict(scope='24 signed synthetic cases crossing growth, funding, valid/invalid fee total and addition overflow; only listed behavior fields compared, logs retained.',fields=fields,original_sha256=sha(ROOT/'evidence/original/pump_fees/deployed.so'),candidate_sha256=sha(candidate),case_count=len(rows),mismatches=[i for i,r in enumerate(rows)if not r['match']],cases=rows)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=run(a.candidate);a.output.write_text(json.dumps(r,separators=(',',':'))+'\n');print({k:r[k]for k in ['case_count','mismatches']})

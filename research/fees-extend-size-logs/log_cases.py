"""Signed no-resize cases with explicit program-log equality."""
from pathlib import Path
import argparse,hashlib,itertools,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import fees_extend_differential as h
FIELDS=['error','data_hex','lamports','owner','balance_deltas','events','inner_instructions','program_logs']
def cases():return [dict(name=f'{size}-{funding}',allocation=size,lamports=funding)for size,funding in itertools.product([4097,4098,5000,8192],[1,10**9])]
def validate(r):
    assert r['fields']==FIELDS and r['case_count']==len(r['cases'])==8
    assert [x['case']for x in r['cases']]==cases()
    failures=[]
    for i,x in enumerate(r['cases']):
        for side in ['original','candidate']:
            v=x[side];assert v['program_logs']==[l for l in v['logs']if l.startswith('Program log:')]
        same=all(x['original'][k]==x['candidate'][k]for k in FIELDS);assert same==x['match']
        if not same:failures.append(i)
        size=x['case']['allocation'];message='Fee config account already has the correct size'if size==4097 else f'Fee config account already has more than 4097 bytes: {size}'
        assert 'Program log: '+message in x['original']['program_logs']
    assert r['mismatches']==failures
    return failures
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--allow-mismatch',action='store_true');a=p.parse_args();original=h.ExtendFixture(ROOT/'evidence/original/pump_fees/deployed.so');candidate=h.ExtendFixture(a.candidate);rows=[]
    for c in cases():
        x,y=original.run(c),candidate.run(c)
        for v in [x,y]:v['program_logs']=[l for l in v['logs']if l.startswith('Program log:')]
        rows.append(dict(case=c,original=x,candidate=y,match=all(x[k]==y[k]for k in FIELDS)))
    r=dict(fields=FIELDS,case_count=len(rows),cases=rows,mismatches=[i for i,x in enumerate(rows)if not x['match']],original_sha256=hashlib.sha256((ROOT/'evidence/original/pump_fees/deployed.so').read_bytes()).hexdigest(),candidate_sha256=hashlib.sha256(a.candidate.read_bytes()).hexdigest());validate(r);a.output.write_text(json.dumps(r,indent=2)+'\n');print('cases',len(rows),'mismatches',r['mismatches']);raise SystemExit(bool(r['mismatches'])and not a.allow_mismatch)

"""Signed optional-account prefix cases through the real create entrypoint."""
from pathlib import Path
import argparse,hashlib,itertools,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import fees_sharing_create_differential as h
FIELDS=['error','sharing','curve','payer_lamports','authority_lamports','sharing_lamports','pool','pool_lamports','curve_lamports','events','inner']
def cases():
    return [dict(name=f'{pool}-{wrong}-{count}',pool=pool,account_count=count,**({'wrong':wrong}if wrong else{}))for pool,wrong,count in itertools.product([False,True],[None,'pool','pump_amm_program','pump_amm_event_authority'],[10,11,12,13])]
def validate(r):
    assert r['fields']==FIELDS and r['case_count']==len(r['cases'])==32
    assert [x['case']for x in r['cases']]==cases()
    mismatches=[]
    for i,x in enumerate(r['cases']):
        assert x['original']['case']==x['candidate']['case']==x['case']
        same=all(x['original'][k]==x['candidate'][k]for k in FIELDS)
        assert x['match']==same
        if not same:mismatches.append(i)
    assert r['mismatches']==mismatches
    return mismatches
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();rows=[]
    for c in cases():
        x,y=h.run(c),h.run(c,a.candidate);rows.append(dict(case=c,original=x,candidate=y,match=all(x[k]==y[k]for k in FIELDS)))
    r=dict(fields=FIELDS,case_count=len(rows),cases=rows,mismatches=[i for i,x in enumerate(rows)if not x['match']],original_sha256=hashlib.sha256((ROOT/'evidence/original/pump_fees/deployed.so').read_bytes()).hexdigest(),candidate_sha256=hashlib.sha256(a.candidate.read_bytes()).hexdigest())
    validate(r);a.output.write_text(json.dumps(r,indent=2)+'\n');print('cases',len(rows),'mismatches',r['mismatches']);raise SystemExit(bool(r['mismatches']))

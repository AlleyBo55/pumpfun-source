from pathlib import Path
import argparse,hashlib,itertools,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import fees_donation_crank_probe as h
TOKEN22='TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb'
FIELDS=['error','before','after','inner','events']
def cases():
    return [dict(name=f'{q}-{o}-{n}',quote=str(quote),mint_owner=owner,mint_length=n,amount=0)for (q,quote),(o,owner),n in itertools.product([('native',h.QUOTE),('other',h.MINT)],[('token',str(h.TOKEN)),('token22',TOKEN22),('wrong',str(h.PROGRAM))],[0,81,82,83,165])]
class Override:
    def __init__(self,vm,c):self.vm=vm;self.c=c
    def __getattr__(self,name):return getattr(self.vm,name)
    def set_account(self,key,account):
        if str(key)==self.c['quote']:
            n=self.c['mint_length'];data=(account.data+bytes(max(0,n-len(account.data))))[:n]
            account=h.Account(account.lamports,data,h.Pubkey.from_string(self.c['mint_owner']),account.executable,account.rent_epoch)
        return self.vm.set_account(key,account)
def run(binary,c):
    f=h.CrankFixture(binary);f.vm=Override(f.vm,c);r=f.run(c);r['events']=[x for x in r['logs']if x.startswith('Program data:')];return r
def validate(r):
    assert r['fields']==FIELDS and r['case_count']==len(r['cases'])==30
    assert [x['case']for x in r['cases']]==cases()
    bad=[]
    for i,x in enumerate(r['cases']):
        for side in ['original','candidate']:
            row=x[side];assert row['case']==x['case']and row['events']==[l for l in row['logs']if l.startswith('Program data:')]
            assert row['before']['quote']['owner']==x['case']['mint_owner']and len(bytes.fromhex(row['before']['quote']['data']))==x['case']['mint_length']
        same=all(x['original'][k]==x['candidate'][k]for k in FIELDS);assert same==x['match']
        if not same:bad.append(i)
    assert r['mismatches']==bad
    return bad
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--allow-mismatch',action='store_true');a=p.parse_args();rows=[];original=ROOT/'evidence/original/pump_fees/deployed.so'
    for c in cases():
        x,y=run(original,c),run(a.candidate,c);rows.append(dict(case=c,original=x,candidate=y,match=all(x[k]==y[k]for k in FIELDS)))
    r=dict(fields=FIELDS,case_count=len(rows),cases=rows,mismatches=[i for i,x in enumerate(rows)if not x['match']],original_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),candidate_sha256=hashlib.sha256(a.candidate.read_bytes()).hexdigest());validate(r);a.output.write_text(json.dumps(r,indent=2)+'\n');print('cases',len(rows),'mismatches',r['mismatches']);raise SystemExit(bool(r['mismatches'])and not a.allow_mismatch)

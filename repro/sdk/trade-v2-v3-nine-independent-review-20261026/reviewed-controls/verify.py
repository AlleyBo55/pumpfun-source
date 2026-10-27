"""Saved source/IDL only; no SDK import, original image, decoder or runtime."""
from pathlib import Path
import json,hashlib,tarfile,base64,re
P=Path(__file__).absolute().parent;H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();J=lambda n:json.loads((P/n).read_text())
m=J('manifest.json');assert set(m)|{'manifest.json'}=={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()}
for n,r in m.items():
 q=Path(n);assert not q.is_absolute()and'..'not in q.parts;f=P
 for part in q.parts:assert part in[x.name for x in f.iterdir()];f=f/part;assert not f.is_symlink()
 assert H(f)==r['sha256']and f.stat().st_size==r['bytes']
assert H(P/'controls/manifest.json')=='ee143e26fcf33efee56fb421e6a2e604baa029ae4e51b07c7b170d1c74f19052';prior=J('controls/manifest.json')
for n in ['archive-bindings.json','source-bindings.json','analysis.json','controls/prior-record-manifest.json']:
 local='controls/'+n;assert H(P/local)==prior[n]['sha256']
archives={}
for r in J('controls/archive-bindings.json'):
 raw=(P/r['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==r['sha256']and len(raw)==r['bytes']and hashlib.sha1(raw).hexdigest()==r['sha1'];assert'sha512-'+base64.b64encode(hashlib.sha512(raw).digest()).decode()==r['integrity'];archives[r['file']]=tarfile.open(P/r['file'],'r:gz')
for n,r in J('source-bindings.json').items():
 t=archives[r['archive']];member=t.getmember(r['member']);assert member.isfile();assert t.extractfile(member).read()==(P/n).read_bytes();assert H(P/n)==r['sha256']and(P/n).stat().st_size==r['bytes']
for t in archives.values():t.close()
old=J('controls/analysis.json');sites=J('sites.json');assert len(sites)==9 and {s['site_id']for s in sites}=={s['id']for s in old['remaining_sites']};assert len({s['site_id']for s in sites})==9
assert all(s['runtime_executions']==0 for s in sites)
camel=lambda n:re.sub(r'_([a-z])',lambda m:m[1].upper(),n)
for s in sites:
 kind='pump'if ':package/src/sdk.ts:'in s['site_id']else'amm';pkg=s['site_id'].split(':')[0];idl=J('sources/pump/package/src/idl/pump.json'if kind=='pump'else'sources/'+pkg+'/package/src/idl/pump_amm.json');ix=next(r for r in idl['instructions']if r['name']==s['instruction']);assert s['IDL_args']==ix['args'];assert len(s['IDL_order'])==len(ix['accounts'])==17
 for expected,a in zip(s['IDL_order'],ix['accounts']):
  key=camel(a['name']);assert expected=={'name':a['name'],'key':key,'signer':a.get('signer',False),'writable':a.get('writable',False),'optional':a.get('optional',False),'address':a.get('address'),'pda':a.get('pda'),'relations':a.get('relations',[]),'supplied_expression':s['supplied_fields'].get(key)}
 assert s['omitted_IDL_fields']==[r['key']for r in s['IDL_order']if r['supplied_expression']is None]
 assert len(s['supplied_fields'])==(10 if kind=='pump'else 17)
 assert s['accounts_mode']==('accountsPartial'if kind=='pump'else'accountsStrict')
 text=(P/s['source']).read_text();assert s['method']in text and ('.accountsPartial('if kind=='pump'else'.accountsStrict(this.tradeV2Accounts(swapSolanaState))')in text
for r in J('line-witnesses.json'):assert(P/r['file']).read_text().splitlines()[r['start_line']-1:r['end_line']]==r['exact_lines']
# Literal critical branch/numeric witnesses, never evaluate JavaScript.
s=(P/'sources/pump/package/src/sdk.ts').read_text();assert 'quoteAmount.mul(new BN(Math.floor(slippage * 10))).div(new BN(1000))'in s and 'minTokensOut: lessSlippage(amount, slippage, 1)'in s and 'quoteAmount: lessSlippage(quoteAmount, slippage)'in s
s=(P/'sources/pump/package/src/swap/util.ts').read_text();assert 'return !pool.isCashbackCoin;'in s
s=(P/'sources/pump/package/src/swap/buy.ts').read_text();assert 'const vault = tradeV2 ? booked.sub(buybackFee) : quoteAmountIn.add(lpFee);'in s
print(json.dumps({'state':'PASS_SOURCE_ONLY_NINE_DYNAMIC_OBJECT_MAPPINGS','AMM_strict_sites':6,'AMM_fields_each':17,'Pump_partial_sites':3,'Pump_fields_each':10,'Pump_omissions_each':7,'original_inventory_static_total':25,'SDK_JS_provider_signing_VM_original_reads':0,'runtime_or_target_compatibility_claim':False},sort_keys=True))

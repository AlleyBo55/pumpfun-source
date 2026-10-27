"""Recompute sweep context recovery and preserved body/data contracts."""
from pathlib import Path
import gzip,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
wm=module('sweep_windows',HERE/'window_map.py')
def calls(image,f):
 rel=dict(wm.m.relocations(image));return {i['offset']:i['call_target']for i in wm.m.instructions(image,f['address'],f['bytes'])if'call_target'in i and rel.get(f['address']+i['offset'],0)&0xffffffff!=10}
def tokens(image,f):
 rel=dict(wm.m.relocations(image));out=[]
 for i in wm.m.instructions(image,f['address'],f['bytes']):
  t=[i[k]for k in ['opcode','destination','source','displacement','immediate']]
  if'call_target'in i or(i['opcode']==0x18 and rel.get(f['address']+i['offset'],0)&0xffffffff==8):t[-1]=0
  out.append(t)
 return out
def exit_data(image,f):
 ins={i['offset']:i for i in wm.m.instructions(image,f['address'],f['bytes'])}
 offsets=[312,808,888]if f['bytes']==944 else [320,824,904]
 return dict(owner=wm.m.at_address(image,ins[48]['lddw_value'],32).hex(),labels=[wm.m.at_address(image,ins[k]['lddw_value'],ins[k+16]['immediate']).decode()for k in offsets])
def analyze():
 e=json.loads((HERE/'experiment.json').read_text());o=(ROOT/'evidence/original/pump_fees/deployed.so').read_bytes();ow=wm.windows(o);oi={f['address']:f for f in ow};variants={};covered={};rawcovered={};details=[];data={};layout={}
 for label,v in e['variants'].items():
  b=gzip.decompress((HERE/v['files']['symbols']['path']).read_bytes());c=gzip.decompress((HERE/v['files']['candidate']['path']).read_bytes());cw=wm.windows(b);ci={f['address']:f for f in cw};assert wm.m.section_data(b,'.text')==wm.m.section_data(c,'.text');r=wm.compare(ow,cw);variants[label]=dict(r,candidate_windows=len(cw),equals_original_capture=c==o,equals_original_elf_extent=c==o[:wm.m.elf_layout(o)['elf_extent']]);covered[label]={x['original']['address']for x in r['unique_pairs']}|{f['address']for g in r['ambiguous']for f in g['original']};rawcovered[label]={f['address']for f in ow if f['raw_sha256']in{x['raw_sha256']for x in cw}}
  f=next(f for f in cw if'SweepBuyback'in(f['name']or'')and'AccountsExit'in f['name']);layout[label]=tokens(b,f);data[label]=exit_data(b,f)
  if label=='origins':
   pairs={x['original']['address']:x['candidate']['address']for x in r['unique_pairs']}
   sc=module('crank_slice',ROOT/'research/fees-slice-origin-contract/analyze.py');slice_contract=sc.contract(b,cw,pairs)
   cc=module('crank_common',ROOT/'research/fees-curve-zero-helper/analyze.py');common_locations=cc.locations(b,ci[pairs[75880]]);assert common_locations==cc.locations(o,oi[75880])
   bo=module('crank_buyback',ROOT/'research/fees-buyback-context-origin/analyze.py');buyback_origin=bo.error_origin(b,ci[pairs[358312]]);bo.check_origin(buyback_origin)
   for address in [370640,379920,651272,351128,358312,364568,370080,424824,656832]:
    left=oi[address];right=ci[pairs[address]];a,z=calls(o,left),calls(b,right);assert a.keys()==z.keys()
    details.append(dict(original=left,candidate=right,calls=[dict(offset=k,original_target=t,candidate_target=z[k],equal=oi[t]['signature']==ci[z[k]]['signature'])for k,t in a.items()]))
 layout['original']=tokens(o,oi[379920]);data['original']=exit_data(o,oi[379920])
 return dict(variants=variants,details=details,exit_data=data,exit_tokens=layout,preserved_slice_contract=slice_contract,preserved_common_locations=common_locations,preserved_buyback_origin=buyback_origin,deltas={label:dict(added_original_windows=sorted(covered[label]-covered['control']),lost_original_windows=sorted(covered['control']-covered[label]))for label in ['boxes','owned','all_owned','origins']},raw_delta=dict(added_original_windows=sorted(rawcovered['origins']-rawcovered['control']),lost_original_windows=sorted(rawcovered['control']-rawcovered['origins'])))
if __name__=='__main__':
 r=analyze();(HERE/'analysis.json.gz').write_bytes(gzip.compress((json.dumps(r,indent=2)+'\n').encode(),mtime=0));print(json.dumps(dict(deltas=r['deltas'],raw_delta=r['raw_delta'],calls=[dict(address=x['original']['address'],bytes=x['original']['bytes'],total=len(x['calls']),different=[c for c in x['calls']if not c['equal']])for x in r['details']]),indent=2))

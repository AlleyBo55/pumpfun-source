from pathlib import Path
import gzip,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('buyback_windows',HERE/'window_map.py');wm=importlib.util.module_from_spec(s);s.loader.exec_module(wm)
def calls(image,f):
 rel=dict(wm.m.relocations(image));return {r['offset']:r['call_target']for r in wm.m.instructions(image,f['address'],f['bytes'])if 'call_target'in r and rel.get(f['address']+r['offset'],0)&0xffffffff!=10}
def error_origin(image,f):
 ins={i['offset']:i for i in wm.m.instructions(image,f['address'],f['bytes'])}
 return dict(path=wm.m.at_address(image,ins[2400]['lddw_value'],ins[2448]['immediate']).decode(),line=ins[2440]['immediate'],error=ins[2424]['immediate'])
def check_origin(value):
 assert value==dict(path='programs/pump-fees/src/instructions/buyback/mod.rs',line=12,error=4101)
def analyze():
 e=json.loads((HERE/'experiment.json').read_text());o=(ROOT/'evidence/original/pump_fees/deployed.so').read_bytes();ow=wm.windows(o);oi={f['address']:f for f in ow};variants={};covered={};rawcovered={};details=[];exit_data={};origins={}
 for label,v in e['variants'].items():
  images={}
  for kind,d in v['files'].items():
   b=gzip.decompress((HERE/d['path']).read_bytes());assert hashlib.sha256(b).hexdigest()==d['sha256']and len(b)==d['bytes'];images[kind]=b
  c,b=images['candidate'],images['symbols'];cw=wm.windows(b);ci={f['address']:f for f in cw};assert wm.m.section_data(c,'.text')==wm.m.section_data(b,'.text');r=wm.compare(ow,cw);variants[label]=dict(r,candidate_windows=len(cw),equals_original_capture=c==o,equals_original_elf_extent=c==o[:wm.m.elf_layout(o)['elf_extent']]);covered[label]={x['original']['address']for x in r['unique_pairs']}|{f['address']for g in r['ambiguous']for f in g['original']};rawcovered[label]={f['address']for f in ow if f['raw_sha256']in {x['raw_sha256']for x in cw}}
  if label=='origins':
   pairs={x['original']['address']:x['candidate']['address']for x in r['unique_pairs']}
   spec=importlib.util.spec_from_file_location('preserved_slice_contract',ROOT/'research/fees-slice-origin-contract/analyze.py');sc=importlib.util.module_from_spec(spec);spec.loader.exec_module(sc);slice_contract=sc.contract(b,cw,pairs)
   spec=importlib.util.spec_from_file_location('preserved_common_contract',ROOT/'research/fees-curve-zero-helper/analyze.py');cc=importlib.util.module_from_spec(spec);spec.loader.exec_module(cc);common_locations=cc.locations(b,ci[pairs[75880]]);assert common_locations==cc.locations(o,oi[75880])
   for address in [351128,358312,364568,370080]:
    left=oi[address];right=next(f for f in cw if f['signature']==left['signature']);a,z=calls(o,left),calls(b,right);assert a.keys()==z.keys()
    if address==358312:
     for which,image,f in [('original',o,left),('candidate',b,right)]:
      origins[which]=error_origin(image,f);check_origin(origins[which])
    if address==370080:
     for which,image,f in [('original',o,left),('candidate',b,right)]:
      ins={i['offset']:i for i in wm.m.instructions(image,f['address'],f['bytes'])};exit_data[which]=dict(owner=wm.m.at_address(image,ins[48]['lddw_value'],32).hex(),labels=[wm.m.at_address(image,ins[k]['lddw_value'],ins[n]['immediate']).decode()for k,n in [(320,336),(504,520)]])
    details.append(dict(original=left,candidate=right,calls=[dict(offset=k,original_target=t,candidate_target=z[k],equal=oi[t]['signature']==ci[z[k]]['signature'])for k,t in a.items()]))
 return dict(origins=origins,exit_data=exit_data,preserved_slice_contract=slice_contract,preserved_common_locations=common_locations,variants=variants,details=details,deltas={label:dict(added_original_windows=sorted(covered[label]-covered['control']),lost_original_windows=sorted(covered['control']-covered[label]))for label in ['origins']},raw_delta=dict(added_original_windows=sorted(rawcovered['origins']-rawcovered['control']),lost_original_windows=sorted(rawcovered['control']-rawcovered['origins'])))
if __name__=='__main__':
 r=analyze();(HERE/'analysis.json.gz').write_bytes(gzip.compress((json.dumps(r,indent=2)+'\n').encode(),mtime=0));print(json.dumps(dict(deltas=r['deltas'],raw_delta=r['raw_delta'],calls=[dict(address=x['original']['address'],bytes=x['original']['bytes'],total=len(x['calls']),different=[c for c in x['calls']if not c['equal']])for x in r['details']]),indent=2))

"""Check the unchecked full-buffer boundary and complete local body recovery."""
from pathlib import Path
import gzip,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
wm=module('prefix_windows',HERE/'window_map.py');old=module('decoder_record',ROOT/'research/fees-decoder-body-match/analyze.py')
def calls(image,f):
 rel=dict(wm.m.relocations(image));return {i['offset']:i['call_target']for i in wm.m.instructions(image,f['address'],f['bytes'])if'call_target'in i and rel.get(f['address']+i['offset'],0)&0xffffffff!=10}
def tokens(image,f):
 rel=dict(wm.m.relocations(image));out=[]
 for i in wm.m.instructions(image,f['address'],f['bytes']):
  t=[i[k]for k in ['opcode','destination','source','displacement','immediate']]
  if'call_target'in i or(i['opcode']==0x18 and rel.get(f['address']+i['offset'],0)&0xffffffff==8):t[-1]=0
  out.append(t)
 return out
def pointers(image,f):
 ins={i['offset']:i for i in wm.m.instructions(image,f['address'],f['bytes'])};return [wm.m.at_address(image,ins[k]['lddw_value'],32).hex()for k in [32,96]]
def analyze():
 e=json.loads((HERE/'experiment.json').read_text());o=(ROOT/'evidence/original/pump_fees/deployed.so').read_bytes();ow=wm.windows(o);oi={f['address']:f for f in ow};variants={};coverage={};raw={};details={};records={'original':old.message_record(o,wm.m.instructions(o,257264,2648))};owner={'original':pointers(o,oi[18384])};helper_tokens={'original':tokens(o,oi[18384])};boundaries={}
 for label,v in e['variants'].items():
  b=gzip.decompress((HERE/v['files']['symbols']['path']).read_bytes());c=gzip.decompress((HERE/v['files']['candidate']['path']).read_bytes());cw=wm.windows(b);ci={f['address']:f for f in cw};assert wm.m.section_data(b,'.text')==wm.m.section_data(c,'.text');r=wm.compare(ow,cw);variants[label]=dict(r,whole_file_equal=c==o,candidate_bytes=len(c));pairs={x['original']['address']:x['candidate']['address']for x in r['unique_pairs']};coverage[label]=set(pairs)|{f['address']for g in r['ambiguous']for f in g['original']};hashes={f['raw_sha256']for f in cw};raw[label]={f['address']for f in ow if f['raw_sha256']in hashes}
  caller=ci[pairs[302032]];helper=ci[calls(b,caller)[6040]];payload=ci[pairs[257264]];records[label]=old.message_record(b,wm.m.instructions(b,payload['address'],payload['bytes']));owner[label]=pointers(b,helper);helper_tokens[label]=tokens(b,helper);boundaries[label]=dict(caller=caller,helper=helper,payload=payload)
  if label=='origins':
   for address in [18384,302032,257264,36072]:
    left=oi[address];right=ci[pairs[address]];a,z=calls(o,left),calls(b,right);assert a.keys()==z.keys();details[str(address)]=dict(original=left,candidate=right,calls=[dict(offset=k,original_target=t,candidate_target=z[k],equal=oi[t]['signature']==ci[z[k]]['signature'])for k,t in a.items()])
 return dict(variants=variants,boundaries=boundaries,helper_tokens=helper_tokens,owner_constants=owner,message_records=records,details=details,deltas={label:dict(added=sorted(coverage[label]-coverage['control']),lost=sorted(coverage['control']-coverage[label]))for label in ['local','origins']},raw_delta=dict(added=sorted(raw['origins']-raw['control']),lost=sorted(raw['control']-raw['origins'])))
if __name__=='__main__':
 r=analyze();(HERE/'analysis.json.gz').write_bytes(gzip.compress((json.dumps(r,indent=2)+'\n').encode(),mtime=0));print(json.dumps(dict(deltas=r['deltas'],raw_delta=r['raw_delta'],details={k:dict(calls=len(v['calls']),different=[c for c in v['calls']if not c['equal']])for k,v in r['details'].items()}),indent=2))

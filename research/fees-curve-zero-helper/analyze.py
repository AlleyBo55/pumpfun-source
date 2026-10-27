from pathlib import Path
import gzip,hashlib,importlib.util,json,struct
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('curve_windows',HERE/'window_map.py');wm=importlib.util.module_from_spec(s);s.loader.exec_module(wm)
def calls(image,f,rel=None):
 if rel is None:rel=dict(wm.m.relocations(image))
 return {r['offset']:r['call_target']for r in wm.m.instructions(image,f['address'],f['bytes'])if 'call_target'in r and rel.get(f['address']+r['offset'],0)&0xffffffff!=10}
def locations(image,f):
 out=[]
 for i in wm.m.instructions(image,f['address'],f['bytes']):
  if i['offset']not in (136,480):continue
  pointer,length,line,column=struct.unpack('<QQII',wm.m.at_address(image,i['lddw_value'],24));pointer=pointer>>32 if pointer>2**32 else pointer
  out.append(dict(offset=i['offset'],path=wm.m.at_address(image,pointer,length).decode(),line=line,column=column))
 return out
def analyze():
 e=json.loads((HERE/'experiment.json').read_text());original=(ROOT/'evidence/original/pump_fees/deployed.so').read_bytes();ow=wm.windows(original);oi={x['address']:x for x in ow};left=oi[75880];out={};covered={};rawcovered={};details={}
 for label,v in e['variants'].items():
  images={}
  for kind,d in v['files'].items():
   b=gzip.decompress((HERE/d['path']).read_bytes());assert hashlib.sha256(b).hexdigest()==d['sha256']and len(b)==d['bytes'];images[kind]=b
  c,b=images['candidate'],images['symbols'];cw=wm.windows(b);ci={x['address']:x for x in cw};assert wm.m.section_data(c,'.text')==wm.m.section_data(b,'.text')
  r=wm.compare(ow,cw);out[label]=dict(r,candidate_windows=len(cw),equals_original_capture=c==original,equals_original_elf_extent=c==original[:wm.m.elf_layout(original)['elf_extent']]);covered[label]={x['original']['address']for x in r['unique_pairs']}|{f['address']for g in r['ambiguous']for f in g['original']};rawcovered[label]={f['address']for f in ow if f['raw_sha256']in {x['raw_sha256']for x in cw}}
  if label!='control':
   right=next(f for f in cw if 'legacy_curve_quote_is_zero' in (f['name']or''));details[label]=dict(window=right,matches=right['signature']==left['signature'])
  if label=='origins':
   a,z=calls(original,left),calls(b,right);assert a.keys()==z.keys();rel=dict(wm.m.relocations(b));details[label].update(calls=[dict(offset=k,original_target=t,candidate_target=z[k],equal=oi[t]['signature']==ci[z[k]]['signature'])for k,t in a.items()],original_locations=locations(original,left),candidate_locations=locations(b,right),incoming_calls=[dict(caller=f['address'],caller_name=f['name'],offset=k)for f in cw for k,t in calls(b,f,rel).items()if t==right['address']])
 return dict(variants=out,details=details,delta=dict(added_original_windows=sorted(covered['origins']-covered['control']),lost_original_windows=sorted(covered['control']-covered['origins'])),raw_delta=dict(added_original_windows=sorted(rawcovered['origins']-rawcovered['control']),lost_original_windows=sorted(rawcovered['control']-rawcovered['origins'])))
if __name__=='__main__':
 r=analyze();(HERE/'analysis.json.gz').write_bytes(gzip.compress((json.dumps(r,indent=2)+'\n').encode(),mtime=0));print(json.dumps(dict(delta=r['delta'],raw_delta=r['raw_delta'],details=r['details']),indent=2))

"""Recompute full-window deltas for root-only codegen-unit controls."""
from pathlib import Path
import gzip,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('codegen_windows',HERE/'window_map.py');wm=importlib.util.module_from_spec(s);s.loader.exec_module(wm)
def tokens(image,f):
 rel=dict(wm.m.relocations(image));out=[]
 for i in wm.m.instructions(image,f['address'],f['bytes']):
  v=[i[k]for k in ['opcode','destination','source','displacement','immediate']]
  if 'call_target'in i:v[-1]=0
  if i['opcode']==0x18 and rel.get(f['address']+i['offset'],0)&0xffffffff==8:v[-1]=0
  out.append(v)
 return out
def analyze():
 e=json.loads((HERE/'experiment.json').read_text());o=(ROOT/'evidence/original/pump_fees/deployed.so').read_bytes();ow=wm.windows(o);original=next(f for f in ow if f['address']==650064);rows={};covered={};rawcovered={};control=None
 for label,v in e['variants'].items():
  b=gzip.decompress((HERE/v['files']['symbols']['path']).read_bytes());c=gzip.decompress((HERE/v['files']['candidate']['path']).read_bytes());cw=wm.windows(b);assert wm.m.section_data(b,'.text')==wm.m.section_data(c,'.text');r=wm.compare(ow,cw)
  covered[label]={p['original']['address']for p in r['unique_pairs']}|{f['address']for g in r['ambiguous']for f in g['original']};rawcovered[label]={f['address']for f in ow if f['raw_sha256']in{x['raw_sha256']for x in cw}}
  f=next(f for f in cw if '__global'in(f['name']or'')and'initialize_buyback'in f['name']);ins=wm.m.instructions(b,f['address'],f['bytes'])
  rows[label]=dict(candidate_sha256=hashlib.sha256(c).hexdigest(),candidate_bytes=len(c),unique=len(r['unique_pairs']),ambiguous_original=sum(len(g['original'])for g in r['ambiguous']),unmatched=len(r['unmatched_original']),added=sorted(covered[label]-covered['cgu1']),lost=sorted(covered['cgu1']-covered[label]),raw_added=sorted(rawcovered[label]-rawcovered['cgu1']),raw_lost=sorted(rawcovered['cgu1']-rawcovered[label]),wrapper=dict(address=f['address'],bytes=f['bytes'],normalized_equal=f['signature']==original['signature'],initial_halfword_stores=[i for i in ins if i['opcode']==0x6a and i['immediate']==65535]))
  if label=='cgu1':control=dict(original=tokens(o,original),candidate=tokens(b,f))
 return dict(rows=rows,control_wrapper_tokens=control)
if __name__=='__main__':
 r=analyze();(HERE/'analysis.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['rows'],indent=2))

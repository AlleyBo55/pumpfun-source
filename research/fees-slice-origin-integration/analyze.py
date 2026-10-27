"""Rebind four slice-panic locations to the current Fees candidate."""
from pathlib import Path
import gzip,hashlib,importlib.util,json,struct
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
wm=module('integrated_windows',HERE/'window_map.py')
up=module('slice_contract',ROOT/'research/fees-slice-origin-contract/analyze.py')
contract=up.contract
file_offset=up.file_offset
def analyze():
 e=json.loads((HERE/'experiment.json').read_text());o=(ROOT/'evidence/original/pump_fees/deployed.so').read_bytes();ow=wm.windows(o);variants={};images={};contracts={}
 for label,v in e['variants'].items():
  data={}
  for kind,d in v['files'].items():
   raw=gzip.decompress((HERE/d['path']).read_bytes());assert hashlib.sha256(raw).hexdigest()==d['sha256']and len(raw)==d['bytes'];data[kind]=raw
  images[label]=data;cw=wm.windows(data['symbols']);assert wm.m.section_data(data['candidate'],'.text')==wm.m.section_data(data['symbols'],'.text');r=wm.compare(ow,cw);variants[label]=dict(r,candidate_windows=len(cw),equals_original_capture=data['candidate']==o,equals_original_elf_extent=data['candidate']==o[:wm.m.elf_layout(o)['elf_extent']]);pairs={x['original']['address']:x['candidate']['address']for x in r['unique_pairs']};contracts[label]=contract(data['symbols'],cw,pairs,columns=(15,29)if label=='control'else(19,33),lines=(393,446)if label=='control'else(398,451))
 original=contract(o,ow,{f['address']:f['address']for f in ow})
 a,b=images['control']['candidate'],images['origins']['candidate'];assert len(a)==len(b);actual=[[i,x,y]for i,(x,y)in enumerate(zip(a,b))if x!=y];expected=[]
 for before,after in zip(contracts['control']['locations'],contracts['origins']['locations']):
  assert before['record_address']==after['record_address']and before['file']==after['file']
  for offset,key in [(16,'line'),(20,'column')]:
   address=file_offset(b,after['record_address']+offset)
   for j,(x,y)in enumerate(zip(struct.pack('<I',before[key]),struct.pack('<I',after[key]))):
    if x!=y:expected.append([address+j,x,y])
 assert actual==sorted(expected)and len(actual)==8
 assert wm.m.section_data(a,'.text')==wm.m.section_data(b,'.text')
 for label in ['control','origins']:
  for field in ['pieces','panic_callee_signature','formatter_signature']:assert contracts[label][field]==original[field]
 assert [(r['file'],r['line'],r['column'])for r in contracts['origins']['locations']]==[(r['file'],r['line'],r['column'])for r in original['locations']]
 return dict(variants=variants,contracts=dict(original=original,**contracts),byte_changes=actual,entire_text_raw_equal=True)
if __name__=='__main__':
 r=analyze();(HERE/'analysis.json.gz').write_bytes(gzip.compress((json.dumps(r,indent=2)+'\n').encode(),mtime=0));print('PASS: eight location bytes, unchanged entire text, four original contracts')

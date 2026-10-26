"""Derive only retained JSON metadata and existing admitted-text anchors.
No ELF read, instruction decode, callee/body acquisition or runtime execution.
"""
from pathlib import Path
import gzip,hashlib,json
P=Path(__file__).parent
H=lambda b:hashlib.sha256(b).hexdigest()
J=lambda n:json.loads((P/n).read_text())
G=lambda n:json.loads(gzip.decompress((P/n).read_bytes()))
STARTS=[1108280,1565736,604312,141840,169240,169712,1715000]
EXPECTED={1108280:(1112888,4608),1565736:(1566664,928),604312:(606400,2088),141840:(169240,27400),169240:(169712,472),169712:(170160,448),1715000:(1715104,104)}
def derive():
 old=G('retained-full-inventory.json.gz'); inventories={'71ec':old['before'],'d75':old['after'],'6e':G('retained-6e-inventory.json.gz'),'fdf':G('new-inventory.json.gz')};out={}; identities=None
 for tag,inv in inventories.items():
  assert len(inv['original_windows'])==1035
  by={r['start']:r for r in inv['original_windows']};assert 157128 not in by
  selected={};names={r['start']:r.get('names',[])for r in inv['candidate_symbol_windows']}
  for start in STARTS:
   r=by[start];assert(r['end'],r['size'])==EXPECTED[start]
   selected[str(start)]={k:r[k]for k in['start','end','size','raw_sha256','normalized_sha256','pattern_candidates','call_consistent_candidates']}
   pairs=[r for r in inv['pattern_comparisons']if r['original']==start]
   selected[str(start)]['relations']=[{'candidate':r['candidate'],'names':names.get(r['candidate'],[]),'normalized_equal':r['normalized_instruction_equal'],'call_fixed_point':r['call_consistent_fixed_point'],'raw_equal':r.get('raw_body_equal',r.get('raw_body_sha256_equal')),'semantic_equivalence':r.get('semantic_equivalence'),'transitive_data_equal':r.get('transitive_data_equal')}for r in pairs]
  identity={start:{k:by[start][k]for k in['start','end','size','raw_sha256','normalized_sha256']}for start in STARTS}
  if identities is None:identities=identity
  else:assert identity==identities
  assert not selected['1108280']['pattern_candidates']and not selected['604312']['pattern_candidates']
  assert len(selected['1565736']['pattern_candidates'])==2 and len(selected['1565736']['call_consistent_candidates'])==1
  assert len(selected['1715000']['pattern_candidates'])==len(selected['1715000']['call_consistent_candidates'])==1
  assert all(not r['raw_equal']for r in selected['1715000']['relations'])
  assert not selected['169240']['pattern_candidates']and not selected['169712']['pattern_candidates']
  out[tag]=selected
 parent=next(r for r in old['before']['original_windows']if r['start']==141840)
 branch=[r for r in parent['branches']if r['target']==157128];assert len(branch)==1 and branch[0]['site']==150200 and branch[0]['inside_window']
 text=(P/'admitted-controls/141840.asm').read_text();anchors=[line for line in text.splitlines()if line.startswith(('150200:','157128:'))];assert len(anchors)==2 and '->157128'in anchors[0]
 current=inventories['fdf'];current_by={r['start']:r for r in current['candidate_symbol_windows']}
 counterparts=[]
 for pc,size,label in[(471544,96,'shared_token_frozen'),(471104,440,'shared_token_raw_amount'),(1292560,928,'associated_token::create_idempotent'),(1387344,104,'AccountInfo::data_is_empty')]:
  r=current_by[pc];assert r['size']==size
  counterparts.append({'start':pc,'bytes':size,'names':r['names'],'label':label,'raw_sha256':r['raw_sha256'],'normalized_sha256':r['normalized_sha256']})
 calls=[{'site':c['site'],'target':c['target']}for c in parent['calls']if c['target']in[1108280,1565736,604312,169240,169712]]
 return {'state':'PASS_METADATA_ONLY_CORRECTION_NOT_ABI_PROOF','original_window_count_each':1035,'windows':out,'native157128':{'kind':'existing branch inside admitted parent, not a separate inferred function entry','parent':[141840,169240],'branch':branch[0],'existing_admitted_text_anchors':anchors},'retained_parent_selected_call_sites':calls,'current_fdf_counterparts':counterparts,'boundary_scope':'Entry-to-next-entry inferred windows; not historical function-boundary proof. Normalized and call-fixed-point relations are syntactic evidence, not ABI, transitive data, or semantic proof.','new_original_ELF_reads_body_decode_callee_acquisition_VM_compiler_network':0}
if __name__=='__main__':print(json.dumps(derive(),indent=2,sort_keys=True))

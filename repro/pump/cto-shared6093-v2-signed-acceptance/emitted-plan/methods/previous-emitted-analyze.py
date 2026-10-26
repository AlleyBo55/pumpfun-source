"""Saved-candidate-only ELF review; original comparisons use admitted saved text only."""
from pathlib import Path
import json,hashlib,importlib.util,struct
P=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
Elf=load(P/'reference-elf-method.py','reference').Elf
ROOTS=[441928,471392,471792,472224,472600,938496,1122592,1357408]
HELPERS=[1266144,1374992,1366568,1375048,1313056,1383304,1288152,1294456,1376192,1376392,1382608,1382728,1382936,1375960,1456712]
def analyze(base=P.parent):
 E=base/'pumpfun-source/work/cto-wallet-build-01/analysis';cb=(E/'candidate.so').read_bytes();ub=(E/'unstripped.so').read_bytes();c,u=Elf(cb),Elf(ub);syms={}
 for s in u.symbols:
  if s['type']==2 and s['size']:syms.setdefault(s['start'],[]).append(s)
 fs=[]
 for a in ROOTS+HELPERS:
  ss=syms[a];assert len({s['size']for s in ss})==1;z=ss[0]['size'];assert c.at(a,z)==u.at(a,z)
  f=c.function(a,z,[s['name']for s in ss]);f['code_hex']=c.at(a,z).hex()
  for call in f['direct_calls']:call['actual_named_callee']=[s['name']for s in syms.get(call['target'],[])]
  fs.append(f)
 old=Elf((base/'pr12-selected-cto-emitted-review/git-inputs/main/unstripped.so').read_bytes());comparisons=[]
 for before,after in [(936512,938496),(1120608,1122592)]:
  prior=next(s for s in old.symbols if s['type']==2 and s['start']==before);f=old.function(before,prior['size'],[prior['name']]);g=next(f for f in fs if f['start']==after)
  def named_calls(fun,elf):
   return [[s['name']for s in elf.symbols if s['type']==2 and s['start']==v['target']]for v in fun['direct_calls']]
  comparisons.append(dict(before=before,after=after,bytes_before=prior['size'],bytes_after=g['bytes'],normalized_equal=f['normalized_sha256']==g['normalized_sha256'],callee_names_equal=named_calls(f,old)==named_calls(g,u)))
 def ins(pc):
  b=c.at(pc,8);op,r,off,imm=struct.unpack('<BBhi',b);v=dict(pc=pc,hex=b.hex(),opcode=op,register_byte=r,offset=off,immediate=imm)
  if op==0x18:v['literal']=struct.unpack_from('<I',b,4)[0]+(struct.unpack_from('<I',c.at(pc+8,8),4)[0]<<32)
  if op in (0x85,):v['target']=pc+8+8*imm
  elif op&7 in(5,6)and op not in(0x95,0x8d):v['branch_target']=pc+8+8*off
  return v
 # These are candidate anchors, not new extraction of original bodies.
 anchors=[444088,444112,444184,444352,444392,446032,446184,446352,446392,448656,448680,449808,449832,449848,449936,448728,448744,448824,448856,448872,448880,448920,448952,448960,448968,449112,449152,449304,449416,449448,449600,453112,453120,456952,456976,457000,457040,457064,457096,458856,459032,457400,457576,457952,457992,458040,458112,458296,458664,458696,457184,457264,466352,466400,466424,466464,466488,466512,466528,466552,466576,466608,466616,466896,466936,466944,466952,466960,466984,467000,467256,467440,467504,467920,467984,468088,468728,468952,470984]
 execute=fs[0];calls={v['pc']:v['target']for v in execute['direct_calls']}
 expected={444112:1456712,444184:1456712,444392:1357408,446392:1357408,449152:1357408,457952:1288152,458112:472224,458664:1294456,466352:1382608,466400:1376392,466488:1382608,466576:1382728,466608:1376392,466896:1366568,466984:1375960,467920:1266144,468728:1375048,470984:1375048}
 for pc,target in expected.items():assert calls[pc]==target
 assert [v['pc']for v in execute['direct_calls']if v['target']==1288152]==[457952]
 assert [v['pc']for v in execute['direct_calls']if v['target']==472600]==[454536]
 assert ins(444088)['literal']==1466624
 literal=c.at(1466624,32);assert literal.hex()=='069b8857feab8184fb687f634618c035dac439dc1aeb3b5598a0f00000000001'
 assert ins(448880)['branch_target']==453120 and ins(448952)['branch_target']==453120
 assert ins(466616)['branch_target']==467440
 codes=[]
 for pc in range(execute['start'],execute['end'],8):
  v=ins(pc)
  if v['opcode']==0x62 and v['immediate']in[6019,6091,6092]:codes.append(v)
 assert [(x['pc'],x['immediate'])for x in codes]==[(444352,6091),(446352,6019),(449112,6092)]
 return dict(candidate_sha256=H(cb),candidate_bytes=len(cb),symbols_sha256=H(ub),symbols_bytes=len(ub),functions=fs,selected71ec_comparisons=comparisons,candidate_anchors=[ins(x)for x in anchors],named_constructor_code_stores=codes,native_mint_literal=dict(address=1466624,hex=literal.hex()),scope='23 full named candidate bodies, complete per-body calls/relocations/indirect calls; data references retain bounded <=64byte samples only, not whole pointee extents; no original ELF read or new original body decode')
if __name__=='__main__':
 (P/'proof.json').write_text(json.dumps(analyze(),indent=2,sort_keys=True)+'\n')

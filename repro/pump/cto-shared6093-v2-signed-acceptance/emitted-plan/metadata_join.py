"""UNEXECUTED adapted candidate-only join. Requires reviewed plan seal before use.
Never imports/runs the historical original-reading full_inventory driver.
"""
from pathlib import Path
import argparse,collections,gzip,hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'methods'))
from elf_reader import Elf
from layer_inventory import windows,enrich,cover
H=lambda b:hashlib.sha256(b).hexdigest()
def join(candidate,symbols,retained):
 c,sym=Elf(candidate),Elf(symbols)
 assert c.b[c.lo:c.hi]==sym.b[sym.lo:sym.hi]
 assert c.pattern(c.lo,c.hi-c.lo)==sym.pattern(sym.lo,sym.hi-sym.lo)
 assert all(s[3]==s[4]for e in(c,sym)for n,s in e.secs.items()if n=='.text')
 os=retained['original_windows'];assert len(os)==1035
 cs=enrich(c,windows(c,sym.funcs));ci=enrich(c,windows(c));ob={r['start']:r for r in os};cb={r['start']:r for r in cs}
 idx=collections.defaultdict(list)
 for r in os:idx[r['size'],r['normalized_sha256']].append(r)
 pairs=[]
 for r in cs:
  r['pattern_candidates']=[]
  for v in idx[r['size'],r['normalized_sha256']]:
   if v['relocations']!=r['relocations']:continue
   r['pattern_candidates'].append(v['start']);pairs.append((r['start'],v['start']))
 possible=set(pairs);rounds=[]
 # Byte-for-byte fixed-point body copied from prior analyze_images, using saved os.
 while True:
  bad=[]
  for ca,oa in possible:
   r=cb[ca];v=ob[oa];oc={x['offset']:x for x in v['calls']}
   for call in r['calls']:
    x=oc.get(call['offset'])
    if x is None:bad.append((ca,oa));break
    if call['kind']=='signed_relative' and x['kind']=='signed_relative':
     ct,ot=call['target'],x['target']
     # Self/local entry still requires consistent relative location or a retained target relation.
     if ca<=ct<r['end'] and oa<=ot<v['end'] and ct-ca==ot-oa:continue
     if ct in cb and ot in ob and (ct,ot) not in possible:bad.append((ca,oa));break
  if not bad:break
  rounds.append(len(set(bad)));possible-=set(bad)
 for r in cs:r['call_consistent_candidates']=[oa for ca,oa in pairs if ca==r['start']and(ca,oa)in possible]
 orig_rows=[]
 for r in os:
  orig_rows.append({'start':r['start'],'end':r['end'],'size':r['size'],'raw_sha256':r['raw_sha256'],'normalized_sha256':r['normalized_sha256'],'pattern_candidates':[ca for ca,oa in pairs if oa==r['start']],'call_consistent_candidates':[ca for ca,oa in pairs if oa==r['start']and(ca,oa)in possible],'semantic_equivalence':None})
 pair_rows=[{'candidate':ca,'original':oa,'bytes':cb[ca]['size'],'normalized_instruction_equal':True,'relocation_pattern_equal':True,'raw_body_sha256_equal':cb[ca]['raw_sha256']==ob[oa]['raw_sha256'],'raw_body_direct_comparison':None,'call_consistent_fixed_point':(ca,oa)in possible,'semantic_equivalence':None,'transitive_data_equal':None}for ca,oa in pairs]
 summary={'original_windows':len(os),'candidate_symbol_windows':len(cs),'candidate_inferred_windows':len(ci),'candidate_with_pattern':sum(bool(r['pattern_candidates'])for r in cs),'candidate_with_call_consistent_pattern':sum(bool(r['call_consistent_candidates'])for r in cs),'original_with_call_consistent_pattern':sum(bool(r['call_consistent_candidates'])for r in orig_rows),'pattern_pairs':len(pairs),'call_consistent_pairs':len(possible),'raw_equal_pairs':sum(r['raw_body_sha256_equal']for r in pair_rows),'ambiguous_candidate_rows':sum(len(r['call_consistent_candidates'])>1 for r in cs)}
 return {'scope':'Adapted metadata join; original1035 retained records only. Candidate parser/window/enrich and matching/fixed-point criteria unchanged. No original bytes read/decoded. Hash equality is not a fresh direct original raw-byte comparison. No semantic/data/ABI closure.','candidate_sha256':H(c.b),'candidate_bytes':len(c.b),'symbols_sha256':H(sym.b),'symbols_bytes':len(sym.b),'original_sha256':retained['original']['sha256'],'original_bytes':retained['original']['bytes'],'whole_file_equal':False if len(c.b)!=retained['original']['bytes']else None,'positional_differences':None,'near_pattern_hypotheses':None,'sections_original':retained['original']['sections'],'candidate_symbol_windows':cs,'candidate_inferred_windows':ci,'original_windows':orig_rows,'pattern_comparisons':pair_rows,'call_pruning_rounds':rounds,'candidate_symbol_coverage':cover(c,cs),'candidate_inferred_coverage':cover(c,ci),'summary':summary}
def main():
 a=argparse.ArgumentParser();a.add_argument('--expected-plan-seal',required=True);a.add_argument('--candidate',type=Path,required=True);a.add_argument('--symbols',type=Path,required=True);a.add_argument('--expect-retained-side',choices=['before','after']);a.add_argument('--output',type=Path,required=True);args=a.parse_args()
 assert H((P/'manifest.json').read_bytes())==args.expected_plan_seal
 assert not args.output.exists()
 saved=json.loads(gzip.decompress((P/'retained-full-inventory.json.gz').read_bytes()));
 for before,after in zip(saved['before']['original_windows'],saved['after']['original_windows'],strict=True):
  for key in ['start','size','end','raw_sha256','normalized_sha256','calls','branches','relocations','boundary']:assert before[key]==after[key]
 r=join(args.candidate,args.symbols,saved['before'])
 if args.expect_retained_side:
  old=saved[args.expect_retained_side];assert r['candidate_sha256']==old['candidate']['sha256']and r['symbols_sha256']==old['symbol_artifact']['sha256']
  assert r['summary']=={k:v for k,v in old['summary'].items()if k!='near_hypotheses'}
  assert {(x['candidate'],x['original'],x['call_consistent_fixed_point'],x['raw_body_sha256_equal'])for x in r['pattern_comparisons']}=={(x['candidate'],x['original'],x['call_consistent_fixed_point'],x['raw_body_equal'])for x in old['pattern_comparisons']}
  assert r['call_pruning_rounds']==old['call_pruning_rounds'];r['baseline_replay_match']=True
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(gzip.compress((json.dumps(r,separators=(',',':'))+'\n').encode(),mtime=0));print(json.dumps(r['summary'],indent=2))
if __name__=='__main__':main()

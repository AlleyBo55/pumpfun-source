"""UNEXECUTED saved-inventory replay/transition comparison. No ELF read or decode."""
from pathlib import Path
import argparse,collections,gzip,hashlib,json
P=Path(__file__).resolve().parent
def read(p):return json.loads(gzip.decompress(p.read_bytes()))
def strongest(d):
 pairs=collections.defaultdict(list)
 for r in d['pattern_comparisons']:pairs[r['original']].append(r)
 out={}
 for r in d['original_windows']:
  ps=pairs[r['start']];raw=sum(x['raw_body_sha256_equal']for x in ps);calls=sum(x['call_consistent_fixed_point']for x in ps)
  out[r['start']]={'status':'raw'if raw else'call-consistent'if calls else'normalized'if ps else'unmatched','normalized_pairs':len(ps),'raw_pairs':raw,'call_consistent_pairs':calls,'original_end':r['end'],'original_raw_sha256':r['raw_sha256']}
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--expected-plan-seal',required=True);ap.add_argument('--inventory',type=Path,required=True);ap.add_argument('--require-6e-replay-equal',action='store_true');ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 assert hashlib.sha256((P/'manifest.json').read_bytes()).hexdigest()==a.expected_plan_seal and not a.output.exists()
 old=read(P/'retained-6e-inventory.json.gz');new=read(a.inventory)
 if a.require_6e_replay_equal:assert old==new
 before,after=strongest(old),strongest(new);assert set(before)==set(after)and len(after)==1035
 rows=[{'original_start':n,'before':before[n],'after':after[n]}for n in before];counts=collections.Counter((r['before']['status'],r['after']['status'])for r in rows)
 result={'scope':'Saved1035metadata strongeststatus accounting; raw means retainedoriginalhash vs candidatehash, notfreshraworiginalcomparison; no semantic/header/ABI/transitive proof','baseline6e_replay_equal':bool(a.require_6e_replay_equal),'before_candidate':old['candidate_sha256'],'after_candidate':new['candidate_sha256'],'summary_before':old['summary'],'summary_after':new['summary'],'transitions':[{'before':x,'after':y,'count':n}for(x,y),n in sorted(counts.items())],'changed_strongest_rows':[r for r in rows if r['before']['status']!=r['after']['status']],'all1035_rows':rows,'original_reads_decoders_or_runtime':0}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['all1035_rows','changed_strongest_rows']},indent=2))
if __name__=='__main__':main()

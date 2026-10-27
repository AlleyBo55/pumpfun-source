"""Check normalized caller bodies, with outgoing-call evidence for duplicates."""
from pathlib import Path
import gzip,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('event_windows',HERE/'window_map.py')
wm=importlib.util.module_from_spec(spec);spec.loader.exec_module(wm)
sha=lambda raw:hashlib.sha256(raw).hexdigest()
TARGETS=[98232,100840,115160,117688]
def local_calls(image,f):
    rel=dict(wm.m.relocations(image))
    return {r['offset']:r['call_target']for r in wm.m.instructions(image,f['address'],f['bytes'])if 'call_target'in r and rel.get(f['address']+r['offset'],0)&0xffffffff!=10}
def compare_calls(original,candidate,left,right,ow,cw):
    a,b=local_calls(original,left),local_calls(candidate,right);assert a.keys()==b.keys()
    la={f['address']:f for f in ow};rb={f['address']:f for f in cw};rows=[]
    for offset,target in a.items():
        other=b[offset];assert target in la and other in rb
        rows.append(dict(offset=offset,original_target=target,candidate_target=other,bytes=la[target]['bytes'],signature=la[target]['signature'],equal=la[target]['signature']==rb[other]['signature']))
    return rows
def analyze():
    e=json.loads((HERE/'experiment.json').read_text());original=(ROOT/'evidence/original/pump_fees/deployed.so').read_bytes();assert sha(original)=='4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e';ow=wm.windows(original);variants={};covered={};callers=[]
    for label,v in e['variants'].items():
        images={}
        for kind,d in v['files'].items():
            raw=gzip.decompress((HERE/d['path']).read_bytes());assert sha(raw)==d['sha256']and len(raw)==d['bytes'];images[kind]=raw
        candidate,symbols=images['candidate'],images['symbols'];cw=wm.windows(symbols);assert wm.m.section_data(candidate,'.text')==wm.m.section_data(symbols,'.text')
        comparison=wm.compare(ow,cw);covered[label]={p['original']['address']for p in comparison['unique_pairs']}|{f['address']for group in comparison['ambiguous']for f in group['original']}
        variants[label]=dict(comparison,candidate_windows=len(cw),unique_raw_pairs=sum(p['original']['raw_sha256']==p['candidate']['raw_sha256']for p in comparison['unique_pairs']),equals_original_capture=candidate==original,equals_original_elf_extent=candidate==original[:wm.m.elf_layout(original)['elf_extent']])
        if label=='origins':
            for address in TARGETS:
                left=next(f for f in ow if f['address']==address);options=[f for f in cw if f['signature']==left['signature']];evaluated=[]
                for option in options:
                    rows=compare_calls(original,symbols,left,option,ow,cw);evaluated.append((option,rows))
                accepted=[(f,rows)for f,rows in evaluated if all(r['equal']for r in rows)]
                assert len(accepted)==1
                right,rows=accepted[0];callers.append(dict(original=address,candidate=right['address'],bytes=left['bytes'],body_candidates=[f['address']for f in options],selection='body_unique'if len(options)==1 else'outgoing_callee_disambiguated',calls=rows,rejected=[dict(candidate=f['address'],conflicting_call_offsets=[r['offset']for r in rs if not r['equal']])for f,rs in evaluated if f['address']!=right['address']]))
    assert len({x['candidate']for x in callers})==4
    return dict(variants=variants,callers=callers,deltas={label:dict(added_original_windows=sorted(values-covered['control']),lost_original_windows=sorted(covered['control']-values))for label,values in covered.items()if label!='control'})
if __name__=='__main__':
    r=analyze();(HERE/'analysis.json.gz').write_bytes(gzip.compress((json.dumps(r,indent=2,sort_keys=True)+'\n').encode(),mtime=0));print(r['deltas'])

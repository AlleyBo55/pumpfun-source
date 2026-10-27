"""Compare all windows and independently bind each recovered setter's callees."""
from pathlib import Path
import gzip, hashlib, importlib.util, json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('setter_windows',HERE/'window_map.py')
wm=importlib.util.module_from_spec(spec);spec.loader.exec_module(wm)
sha=lambda raw:hashlib.sha256(raw).hexdigest()

def local_calls(image,function):
    relocations=dict(wm.m.relocations(image))
    return {r['offset']:r['call_target']for r in wm.m.instructions(image,function['address'],function['bytes'])if 'call_target'in r and relocations.get(function['address']+r['offset'],0)&0xffffffff!=10}

def paired_calls(original,candidate,left,right,left_windows,right_windows):
    left_calls,right_calls=local_calls(original,left),local_calls(candidate,right)
    assert left_calls.keys()==right_calls.keys()
    la={r['address']:r for r in left_windows};rb={r['address']:r for r in right_windows};result=[]
    for offset,target in left_calls.items():
        other=right_calls[offset];assert target in la and other in rb
        assert la[target]['signature']==rb[other]['signature']
        result.append(dict(offset=offset,original_target=target,candidate_target=other,bytes=la[target]['bytes'],signature=la[target]['signature']))
    return result

def origin_and_fields(image,function):
    rows=wm.m.instructions(image,function['address'],function['bytes'])
    source=next(r['lddw_value']for r in rows if r['offset']==480)
    return dict(file=wm.m.at_address(image,source,31).decode(),line=next(r['immediate']for r in rows if r['opcode']==0x62 and r['displacement']==-248),field_stores=[r['displacement']for r in rows if r['opcode']==0x7b and r['destination']==7])

def analyze():
    meta=json.loads((HERE/'experiment.json').read_text());original=(ROOT/'evidence/original/pump_fees/deployed.so').read_bytes()
    assert sha(original)=='4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
    ow=wm.windows(original);variants={};known={};details={}
    for label,variant in meta['variants'].items():
        images={}
        for kind,descriptor in variant['files'].items():
            raw=gzip.decompress((HERE/descriptor['path']).read_bytes());assert len(raw)==descriptor['bytes']and sha(raw)==descriptor['sha256'];images[kind]=raw
        candidate,symbols=images['candidate'],images['symbols'];cw=wm.windows(symbols)
        assert wm.m.section_data(candidate,'.text')==wm.m.section_data(symbols,'.text')
        comparison=wm.compare(ow,cw);known[label]={p['original']['address']for p in comparison['unique_pairs']}
        variants[label]=dict(comparison,candidate_windows=len(cw),unique_raw_pairs=sum(p['original']['raw_sha256']==p['candidate']['raw_sha256']for p in comparison['unique_pairs']),equals_original_capture=candidate==original,equals_original_elf_extent=candidate==original[:wm.m.elf_layout(original)['elf_extent']])
        if label!='control':
            details[label]=[]
            for address in [260568,261192]:
                pair=next(p for p in comparison['unique_pairs']if p['original']['address']==address);a,b=pair['original'],pair['candidate']
                origin=origin_and_fields(original,a);other=origin_and_fields(symbols,b);assert origin==other
                details[label].append(dict(original=a['address'],candidate=b['address'],bytes=a['bytes'],source_and_fields=origin,calls=paired_calls(original,symbols,a,b,ow,cw)))
    return dict(variants=variants,setters=details,deltas={label:dict(added_original_windows=sorted(known[label]-known['control']),lost_original_windows=sorted(known['control']-known[label]))for label in ['negative','setters','origins']})
if __name__=='__main__':
    r=analyze();(HERE/'analysis.json.gz').write_bytes(gzip.compress((json.dumps(r,indent=2,sort_keys=True)+'\n').encode(),mtime=0));print(r['deltas'])

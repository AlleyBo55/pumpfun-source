"""Recompute exact normalized windows and their first-level callee/data checks."""
from pathlib import Path
import gzip,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('tier_windows',HERE/'window_map.py')
wm=importlib.util.module_from_spec(spec);spec.loader.exec_module(wm)
sha=lambda raw:hashlib.sha256(raw).hexdigest()
TARGETS=[54864,261816,265976,784168]
def local_calls(image,f):
    rel=dict(wm.m.relocations(image))
    return {r['offset']:r['call_target']for r in wm.m.instructions(image,f['address'],f['bytes'])if 'call_target'in r and rel.get(f['address']+r['offset'],0)&0xffffffff!=10}
def calls(original,candidate,left,right,ow,cw):
    a,b=local_calls(original,left),local_calls(candidate,right);assert a.keys()==b.keys()
    li={f['address']:f for f in ow};ri={f['address']:f for f in cw};rows=[]
    for offset,target in a.items():
        other=b[offset];assert target in li and other in ri
        assert li[target]['signature']==ri[other]['signature']
        rows.append(dict(offset=offset,original_target=target,candidate_target=other,bytes=li[target]['bytes'],signature=li[target]['signature']))
    return rows
def origins(image,f):
    rows=wm.m.instructions(image,f['address'],f['bytes']);rel=dict(wm.m.relocations(image));source=[]
    for r in rows:
        if 'lddw_value'in r and f['address']+r['offset']in rel:
            try:value=wm.m.at_address(image,r['lddw_value'],31)
            except StopIteration:continue
            if value==b'programs/pump-fees/src/state.rs':source.append(r['offset'])
    assert len(source)==5
    return dict(file='programs/pump-fees/src/state.rs',source_offsets=source,error_lines=[r['immediate']for r in rows if r['opcode']==0x62 and r['displacement']==-256],error_codes=[r['immediate']for r in rows if r['opcode']==0x62 and r['displacement']==-128],final_vector_stores=[r['displacement']for r in rows if r['opcode']==0x7b and r['destination']==2])
def analyze():
    meta=json.loads((HERE/'experiment.json').read_text());original=(ROOT/'evidence/original/pump_fees/deployed.so').read_bytes();assert sha(original)=='4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
    ow=wm.windows(original);variants={};known={};recovered=[]
    for label,v in meta['variants'].items():
        image={}
        for kind,d in v['files'].items():
            raw=gzip.decompress((HERE/d['path']).read_bytes());assert sha(raw)==d['sha256']and len(raw)==d['bytes'];image[kind]=raw
        candidate,symbols=image['candidate'],image['symbols'];cw=wm.windows(symbols);assert wm.m.section_data(candidate,'.text')==wm.m.section_data(symbols,'.text')
        result=wm.compare(ow,cw);known[label]={p['original']['address']for p in result['unique_pairs']};variants[label]=dict(result,candidate_windows=len(cw),unique_raw_pairs=sum(p['original']['raw_sha256']==p['candidate']['raw_sha256']for p in result['unique_pairs']),equals_original_capture=candidate==original,equals_original_elf_extent=candidate==original[:wm.m.elf_layout(original)['elf_extent']])
        if label=='origins':
            for addr in TARGETS:
                pair=next(p for p in result['unique_pairs']if p['original']['address']==addr);a,b=pair['original'],pair['candidate'];r=dict(original=addr,candidate=b['address'],bytes=a['bytes'],calls=calls(original,symbols,a,b,ow,cw))
                if addr in [261816,265976]:
                    info=origins(original,a);assert info==origins(symbols,b);r['origins']=info
                recovered.append(r)
    return dict(variants=variants,recovered=recovered,deltas={name:dict(added_original_windows=sorted(values-known['control']),lost_original_windows=sorted(known['control']-values))for name,values in known.items()if name!='control'})
if __name__=='__main__':
    r=analyze();(HERE/'analysis.json.gz').write_bytes(gzip.compress((json.dumps(r,indent=2,sort_keys=True)+'\n').encode(),mtime=0));print(r['deltas'])

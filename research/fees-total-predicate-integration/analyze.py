"""Recompute full body coverage and the fee predicate's reachable panic leaf."""
from pathlib import Path
import gzip
import hashlib
import importlib.util
import json
import struct
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('fee_total_windows',HERE/'window_map.py')
wm=importlib.util.module_from_spec(spec);spec.loader.exec_module(wm)
sha=lambda raw:hashlib.sha256(raw).hexdigest()

def relocated_slice(image,address):
    packed,length=struct.unpack('<QQ',wm.m.at_address(image,address,16))
    assert dict(wm.m.relocations(image))[address]&0xffffffff==8
    assert packed&0xffffffff==0
    return wm.m.at_address(image,packed>>32,length)

def predicate_details(image,windows,address):
    function=next(f for f in windows if f['address']==address)
    ins=wm.m.instructions(image,address,function['bytes'])
    assert function['bytes']==192
    location_address=next(r['lddw_value']for r in ins if r['opcode']==0x18)
    _,_,line,column=struct.unpack('<QQII',wm.m.at_address(image,location_address,24))
    target=next(r['call_target']for r in ins if 'call_target'in r)
    callee=next(f for f in windows if f['address']==target)
    callee_ins=wm.m.instructions(image,target,callee['bytes'])
    pieces=next(r['lddw_value']for r in callee_ins if r['opcode']==0x18)
    callers=[dict(caller=f['address'],offset=r['offset'])for f in windows for r in wm.m.instructions(image,f['address'],f['bytes'])if r.get('call_target')==address]
    return dict(address=address,bytes=function['bytes'],signature=function['signature'],
                location=dict(file=relocated_slice(image,location_address).decode(),line=line,column=column),
                panic_callee=dict(address=target,bytes=callee['bytes'],signature=callee['signature'],message=relocated_slice(image,pieces).decode()),callers=callers)

def analyze():
    meta=json.loads((HERE/'experiment.json').read_text())
    original=(ROOT/'evidence/original/pump_fees/deployed.so').read_bytes()
    assert sha(original)=='4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
    ow=wm.windows(original);target=next(f for f in ow if f['address']==700568)
    variants={};sets={}
    details={'original':predicate_details(original,ow,700568)}
    for label,variant in meta['variants'].items():
        files={}
        for kind,descriptor in variant['files'].items():
            raw=gzip.decompress((HERE/descriptor['path']).read_bytes())
            assert sha(raw)==descriptor['sha256'] and len(raw)==descriptor['bytes'];files[kind]=raw
        symbols=files['symbols'];candidate=files['candidate'];cw=wm.windows(symbols)
        assert wm.m.section_data(symbols,'.text')==wm.m.section_data(candidate,'.text')
        comparison=wm.compare(ow,cw);sets[label]={p['original']['address']for p in comparison['unique_pairs']}
        variants[label]=dict(comparison,candidate_windows=len(cw),unique_raw_pairs=sum(p['original']['raw_sha256']==p['candidate']['raw_sha256']for p in comparison['unique_pairs']),equals_original_capture=candidate==original,equals_original_elf_extent=candidate==original[:wm.m.elf_layout(original)['elf_extent']])
        if label!='control':
            matches=[f for f in cw if f['signature']==target['signature']]
            assert len(matches)==1
            details[label]=predicate_details(symbols,cw,matches[0]['address'])
    return dict(original_sha256=sha(original),variants=variants,predicates=details,deltas={label:dict(added_original_windows=sorted(sets[label]-sets['control']),lost_original_windows=sorted(sets['control']-sets[label]))for label in ['predicate','origins']})

if __name__=='__main__':
    result=analyze();(HERE/'analysis.json.gz').write_bytes(gzip.compress((json.dumps(result,indent=2,sort_keys=True)+'\n').encode(),mtime=0))
    print(result['deltas'])

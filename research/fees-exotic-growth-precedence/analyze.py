"""Re-read candidate coverage and the observed growth/validation call sites."""
from pathlib import Path
import gzip,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('exotic_windows',HERE/'window_map.py')
wm=importlib.util.module_from_spec(spec);spec.loader.exec_module(wm)
sha=lambda b:hashlib.sha256(b).hexdigest()
def graph(image,f):
    g={}
    for r in wm.m.instructions(image,f['address'],f['bytes']):
        off=r['offset'];nxt=off+len(bytes.fromhex(r['raw']));op=r['opcode']
        if op==0x95:g[off]=[]
        elif op&7 in (5,6)and op!=0x85:g[off]=[off+8+r['displacement']*8]+([]if op==0x05 else[nxt])
        else:g[off]=[nxt]if nxt<f['bytes']else[]
    assert all(x in g for ys in g.values()for x in ys)
    return g
def reaches(g,start,target,avoid=None):
    pending=[start];seen=set()
    while pending:
        x=pending.pop()
        if x==avoid or x in seen:continue
        if x==target:return True
        seen.add(x);pending+=g[x]
    return False
def behavior_sites(image,f,targets):
    rows=wm.m.instructions(image,f['address'],f['bytes']);by={r['offset']:r for r in rows};calls={}
    for label,address in targets.items():
        matches=[r['offset']for r in rows if r.get('call_target')==address];assert len(matches)==1,(label,matches);calls[label]=matches[0]
    flag=by[calls['realloc']-8];assert flag['opcode']==0xb7 and flag['destination']==4
    g=graph(image,f)
    return dict(calls=calls,realloc_zero_init=flag['immediate'],data_len_dominates_validation=not reaches(g,0,calls['validate'],calls['data_len']),growth_can_precede_validation=reaches(g,calls['realloc'],calls['validate']))
def analyze():
    e=json.loads((HERE/'experiment.json').read_text());original=(ROOT/'evidence/original/pump_fees/deployed.so').read_bytes();assert sha(original)=='4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e';ow=wm.windows(original);f=next(f for f in ow if f['address']==88552);targets=dict(data_len=731512,realloc=732352,validate=261192);source=behavior_sites(original,f,targets);variants={};covered={}
    for label,v in e['variants'].items():
        images={}
        for kind,d in v['files'].items():
            raw=gzip.decompress((HERE/d['path']).read_bytes());assert sha(raw)==d['sha256']and len(raw)==d['bytes'];images[kind]=raw
        candidate,symbols=images['candidate'],images['symbols'];cw=wm.windows(symbols);assert wm.m.section_data(candidate,'.text')==wm.m.section_data(symbols,'.text');r=wm.compare(ow,cw);pairs={p['original']['address']:p['candidate']['address']for p in r['unique_pairs']}
        mapped={k:pairs[a]for k,a in targets.items()};body=next(x for x in cw if '19pump_fees_candidate20set_exotic_flat_fees'in x['name']);covered[label]={p['original']['address']for p in r['unique_pairs']}|{a['address']for group in r['ambiguous']for a in group['original']}
        variants[label]=dict(r,candidate_windows=len(cw),unique_raw_pairs=sum(p['original']['raw_sha256']==p['candidate']['raw_sha256']for p in r['unique_pairs']),exotic=dict(address=body['address'],bytes=body['bytes'],complete_body_match=body['signature']==f['signature'],**behavior_sites(symbols,body,mapped)),equals_original_capture=candidate==original,equals_original_elf_extent=candidate==original[:wm.m.elf_layout(original)['elf_extent']])
    return dict(original_exotic=dict(address=88552,bytes=5520,**source),variants=variants,deltas={name:dict(added_original_windows=sorted(xs-covered['control']),lost_original_windows=sorted(covered['control']-xs))for name,xs in covered.items()if name!='control'},cfg_scope='Conservative intraprocedural graph treats calls as returning; reachability is not feasibility or whole-program equivalence.')
if __name__=='__main__':
    r=analyze();(HERE/'analysis.json.gz').write_bytes(gzip.compress((json.dumps(r,indent=2,sort_keys=True)+'\n').encode(),mtime=0));print({k:(len(v['unique_pairs']),len(v['unmatched_original']),v['exotic'])for k,v in r['variants'].items()})

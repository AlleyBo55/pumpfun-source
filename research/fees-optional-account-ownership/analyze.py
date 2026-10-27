"""Recompute complete body recovery and direct-callee closure."""
from pathlib import Path
import gzip,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('optional_windows',HERE/'window_map.py');wm=importlib.util.module_from_spec(s);s.loader.exec_module(wm)
def local_calls(image,f):
    rel=dict(wm.m.relocations(image))
    return {r['offset']:r['call_target']for r in wm.m.instructions(image,f['address'],f['bytes'])if 'call_target'in r and rel.get(f['address']+r['offset'],0)&0xffffffff!=10}
def analyze():
    original=(ROOT/'evidence/original/pump_fees/deployed.so').read_bytes();e=json.loads((HERE/'experiment.json').read_text());ow=wm.windows(original);variants={};covered={};callers=[];targets=[]
    for label,v in e['variants'].items():
        images={}
        for kind,d in v['files'].items():
            raw=gzip.decompress((HERE/d['path']).read_bytes());assert hashlib.sha256(raw).hexdigest()==d['sha256']and len(raw)==d['bytes'];images[kind]=raw
        c,s=images['candidate'],images['symbols'];cw=wm.windows(s);assert wm.m.section_data(c,'.text')==wm.m.section_data(s,'.text')
        comparison=wm.compare(ow,cw);covered[label]={p['original']['address']for p in comparison['unique_pairs']}|{f['address']for g in comparison['ambiguous']for f in g['original']}
        variants[label]=dict(comparison,candidate_windows=len(cw),unique_raw_pairs=sum(p['original']['raw_sha256']==p['candidate']['raw_sha256']for p in comparison['unique_pairs']),equals_original_capture=c==original,equals_original_elf_extent=c==original[:wm.m.elf_layout(original)['elf_extent']])
        if label=='origins':
            oi={x['address']:x for x in ow};ci={x['address']:x for x in cw}
            for address in [10232,41560]:
                left=oi[address];right=next(x for x in cw if x['signature']==left['signature']);a,b=local_calls(original,left),local_calls(s,right);assert a.keys()==b.keys()
                calls=[dict(offset=k,original_target=t,candidate_target=b[k],equal=oi[t]['signature']==ci[b[k]]['signature'])for k,t in a.items()]
                targets.append(dict(original=left,candidate=right,calls=calls,raw_equal=left['raw_sha256']==right['raw_sha256']))
            parent=oi[445160];current=next(x for x in cw if 'CreateFeeSharingConfig' in (x['name']or '')and '12try_accounts17'in x['name'])
            for label2,image,window in [('original',original,parent),('candidate',s,current)]:
                calls=local_calls(image,window);index=oi if label2=='original'else ci
                callers.append(dict(label=label2,window=window,recovered_target_calls=[dict(offset=k,target=t)for k,t in calls.items()if index[t]['signature']in {oi[10232]['signature'],oi[41560]['signature']}]))
    return dict(variants=variants,delta=dict(added_original_windows=sorted(covered['origins']-covered['control']),lost_original_windows=sorted(covered['control']-covered['origins'])),targets=targets,callers=callers)
if __name__=='__main__':
    r=analyze();(HERE/'analysis.json.gz').write_bytes(gzip.compress((json.dumps(r,indent=2)+'\n').encode(),mtime=0));print(json.dumps(dict(delta=r['delta'],counts={k:[len(v['unique_pairs']),len(v['unmatched_original']),v['unique_raw_pairs']]for k,v in r['variants'].items()},targets=[dict(address=x['original']['address'],raw_equal=x['raw_equal'],calls=x['calls'])for x in r['targets']]),indent=2))

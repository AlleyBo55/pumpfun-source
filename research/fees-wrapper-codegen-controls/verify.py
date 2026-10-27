"""Validate retained builds and rejected codegen controls, without executing targets."""
from pathlib import Path
import gzip,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 manifest=json.loads((HERE/'manifest.json').read_text());assert set(manifest)=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()and p.name!='manifest.json'and '__pycache__'not in p.parts}
 for n,h in manifest.items():assert sha((HERE/n).read_bytes())==h,n
 e=json.loads((HERE/'experiment.json').read_text());parent=json.loads((ROOT/e['parent']/'experiment.json').read_text())['variants']['origins']
 for n in [1,2,4,8,16]:
  label=f'cgu{n}';v=e['variants'][label];assert v['input_sha256']==parent['input_sha256']and v['source_paths']==parent['source_paths']and len(v['input_sha256'])==36
  for name,h in v['input_sha256'].items():assert sha((ROOT/v['source_paths'][name]).read_bytes())==h,name
  launch=json.loads((HERE/f'builds/{label}-launch.json').read_text());result=json.loads((HERE/f'builds/{label}-result.json').read_text());log=(HERE/f'builds/{label}-build.log').read_bytes()
  assert launch['inputs']==v['input_sha256']and launch['rustc_sha256']=='c8807b7ebede8578ac5a257ea333780f9d89bd356064fd8184af7e996cb71a97'
  cmd=launch['command'];assert cmd[-1]==f'-Ccodegen-units={n}'and cmd.index('--')<len(cmd)-1 and cmd.count('RUSTFLAGS=-Zremap-cwd-prefix=')==1
  assert result['compiled_root']and result['source_unchanged']and result['exit_code']==0 and log.count(b'--crate-name pump_fees_candidate ')==1 and sha(log)==result['log_sha256']
  for kind,d in v['files'].items():
   raw=gzip.decompress((HERE/d['path']).read_bytes());assert sha(raw)==d['sha256']==result[kind+'_sha256']and len(raw)==d['bytes']
  if n==1:assert all(v['files'][k]['sha256']==parent['files'][k]['sha256']for k in ['candidate','symbols'])
 spec=importlib.util.spec_from_file_location('cgu_analysis',HERE/'analyze.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);a=m.analyze();assert a==json.loads((HERE/'analysis.json').read_text())
 expected=[(380,147,58,0),(262,138,185,127),(241,153,191,133),(233,131,221,163),(235,129,221,163)]
 for n,(u,am,left,lost)in zip([1,2,4,8,16],expected):
  r=a['rows'][f'cgu{n}'];assert (r['unique'],r['ambiguous_original'],r['unmatched'],len(r['lost']))==(u,am,left,lost)and not r['added']and not r['raw_added']and not r['wrapper']['normalized_equal']
  assert len(r['wrapper']['initial_halfword_stores'])==(0 if n==1 else 1)
 from difflib import SequenceMatcher
 c=a['control_wrapper_tokens'];ops=[x for x in SequenceMatcher(None,list(map(tuple,c['original'])),list(map(tuple,c['candidate'])),autojunk=False).get_opcodes()if x[0]!='equal'];assert len(ops)==2
 assert sorted(x[0]for x in ops)==['delete','replace']
 for tag,l,r,x,y in ops:
  if tag=='delete':assert c['original'][l:r]==[[106,10,0,-562,65535]]
  else:assert c['original'][l:r]==[[21,1,0,22,0]]and c['candidate'][x:y]==[[21,1,0,21,0]]
 print('PASS: exact control; four rejected root-CGU variants; no gains; wrapper remains unmatched')
if __name__=='__main__':main()

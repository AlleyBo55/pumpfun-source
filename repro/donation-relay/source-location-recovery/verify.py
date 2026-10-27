#!/usr/bin/env python3
"""Recheck compiled source-coordinate recovery and exact bounded Location values."""
from pathlib import Path
import argparse,gzip,hashlib,importlib.util,json,shutil,tempfile
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
LABELS=['program-column','event-locations','mint-borrow-location','remainder-push-location','combined','combined-linux']
def H(b):return hashlib.sha256(b).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def encoded(x):return(json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def check_manifest(path):
 records=read(path/'manifest.json');actual={str(f.relative_to(path))for f in path.rglob('*')if f.is_file()and f.name!='manifest.json'and '__pycache__'not in f.parts};assert actual==set(records)
 for n,h in records.items():
  f=path/n;assert not f.is_symlink()and f.resolve().is_relative_to(path)and H(f.read_bytes())==h,n
def load():
 for n,h in read(P/'parents.json').items():
  path=ROOT/n;assert H(path.read_bytes())==h,n;check_manifest(path.parent)
 return module('coordinate_parser',ROOT/'repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py'),module('coordinate_locations',ROOT/'research/relay-location-data-audit/audit.py'),module('coordinate_proposals',ROOT/'research/relay-location-data-audit/proposals.py')
def source(props,label):
 data=props.full_sources();_,groups=props.proposals();changes={}
 for group,items in groups.items():
  if label==group or label.startswith('combined'):changes.update(items)
 data.update(changes);return data,changes

def analyze(parser,original,image,symbols):
 with tempfile.TemporaryDirectory()as tmp:
  d=Path(tmp);(d/'original.so').write_bytes(original);(d/'candidate.so').write_bytes(image);(d/'unstripped.so').write_bytes(symbols);shutil.copyfile(ROOT/'repro/donation-relay/swap-receipt-coordinate-recovery/original-windows.json',d/'original-windows.json');return parser.analyze(d)

def pairs(parser,locations,original,symbols,analysis):
 o=parser.Elf(original);c=parser.Elf(symbols);result=[]
 for match in analysis['match-ledger.json']:
  if len(match['normalized_candidate_indices'])!=1:continue
  a=analysis['original-function-ledger.json'][match['ordinal']];b=analysis['candidate-function-ledger.json'][match['normalized_candidate_indices'][0]]
  assert len(a['data_references'])==len(b['data_references'])
  for x,y in zip(a['data_references'],b['data_references']):
   assert x['offset']==y['offset'];u=locations.read_location(o,x['target']);v=locations.read_location(c,y['target'])
   if u and v:result.append(dict(original_ordinal=match['ordinal'],reference_offset=x['offset'],original=u,candidate=v,equal=locations.key(u)==locations.key(v)))
 return result

def derive():
 parser,locations,props=load();old=ROOT/'repro/donation-relay/mint-fee-pair-recovery';original=(ROOT/'evidence/dependencies/donation_relay/deployed.so').read_bytes();control=gzip.decompress((old/'candidate.so.gz').read_bytes());control_symbols=gzip.decompress((old/'symbols.so.gz').read_bytes());base=analyze(parser,original,control,control_symbols);bp=pairs(parser,locations,original,control_symbols,base)
 assert len(bp)==346 and sum(not p['equal']for p in bp)==43
 keys={(p['original_ordinal'],p['reference_offset'])for p in bp};assert len(keys)==346;variants={};expected=[10,35,42,42,0,0]
 for label,remaining in zip(LABELS,expected):
  d=P/'builds'/label;files,changes=source(props,label);folder=P/'overrides'/label
  assert {str(f.relative_to(folder)):f.read_bytes()for f in folder.rglob('*')if f.is_file()}==changes
  launch=read(d/'launch.json');build=read(d/'result.json');assert launch['inputs']=={n:H(b)for n,b in files.items()}
  assert build['exit_code']==0 and build['source_unchanged']and build['build_log_sha256']==H((d/'build.log').read_bytes())
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text()
  image=gzip.decompress((d/'candidate.so.gz').read_bytes());symbols=gzip.decompress((d/'symbols.so.gz').read_bytes());assert H(image)==build['candidate_sha256']and H(symbols)==build['symbols_sha256']
  result=analyze(parser,original,image,symbols);assert result['comparison-summary.json']==read(d/'comparison-summary.json')and result['match-ledger.json']==read(d/'match-ledger.json');summary=result['comparison-summary.json']
  assert summary['original_normalized_match_windows']==480 and not summary['whole_file_equal']
  assert[bool(r['normalized_candidate_indices'])for r in base['match-ledger.json']]==[bool(r['normalized_candidate_indices'])for r in result['match-ledger.json']]
  items=pairs(parser,locations,original,symbols,result);assert len(items)==346;assert{(p['original_ordinal'],p['reference_offset'])for p in items}==keys
  assert sum(not p['equal']for p in items)==remaining
  if label=='program-column':assert[(i,a,b)for i,(a,b)in enumerate(zip(control,image))if a!=b]==[(773492,5,1)]and len(image)==len(control)
  variants[label]=dict(summary=summary,recognized_pairs=len(items),equal_pairs=sum(p['equal']for p in items),different_pairs=remaining,location_pairs=items,source_inputs=len(files))
 runtime={}
 for label in ['combined','combined-linux']:
  report=read(P/'builds'/label/'fresh-runtime.json.gz');assert report['candidate_sha256']==variants[label]['summary']['candidate_sha256']and report['runner_sha256']==H((P/'replay_saved.py').read_bytes());h=ROOT/'repro/donation-relay/local-validation-proposal/harness_proposal.py';assert report['harness_sha256']==H(h.read_bytes())and report['token2022_sha256']==H((ROOT/'evidence/dependencies/spl_token_2022/deployed.so').read_bytes());frozen={}
  for n,digest in report['input_reports'].items():
   f=ROOT/n;assert H(f.read_bytes())==digest
   for i,row in enumerate(read(f)['cases']):frozen[str(f.relative_to(ROOT/'repro/donation-relay/distribution-worker-source-recovery/settlement'))+':'+str(i)]=row
  helper=module('location_receipt_check_'+label,ROOT/'repro/donation-relay/swap-receipt-coordinate-recovery/verify.py');helper.EXPECTED['recovered']=report['candidate_sha256'];runtime[label]=helper.check_runtime(report,frozen,module('location_runtime_'+label,h))
 return dict(baseline_pairs=bp,variants=variants,runtime=runtime,scope='Bounded relocated Location values in uniquely normalized-matched windows only; not whole-program data or semantic closure.')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--materialize',type=Path);ap.add_argument('--variant',choices=LABELS,default='combined');args=ap.parse_args()
 if not args.write:check_manifest(P)
 if args.materialize:
  assert not args.materialize.exists();_,_,props=load();files,_=source(props,args.variant)
  for n,b in files.items():f=args.materialize/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
  print('Materialized',len(files),'exact source inputs');return
 report=derive()
 if args.write:
  (P/'location-values.json').write_bytes(encoded(report));(P/'manifest.json').write_bytes(encoded({str(f.relative_to(P)):H(f.read_bytes())for f in sorted(P.rglob('*'))if f.is_file()and f.name!='manifest.json'and'__pycache__'not in f.parts}))
 else:
  check_manifest(P);assert report==read(P/'location-values.json')
 print(json.dumps({label:dict(normalized=v['summary']['original_normalized_match_windows'],raw=v['summary']['original_raw_match_windows'],different_locations=v['different_pairs'])for label,v in report['variants'].items()},indent=2))
if __name__=='__main__':main()

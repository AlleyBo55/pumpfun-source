#!/usr/bin/env python3
"""Re-derive source bindings, full-window matches and signed replay evidence."""
from pathlib import Path
import argparse,gzip,hashlib,importlib.util,json,re,shutil,tarfile,tempfile,tomllib
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
OLD=ROOT/'repro/donation-relay/swap-receipt-coordinate-recovery'
PARENT=ROOT/'repro/donation-relay/token-extension-version-recovery'
def H(b):return hashlib.sha256(b).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def check_manifest(p):
 records=read(p/'manifest.json');actual={str(f.relative_to(p))for f in p.rglob('*')if f.is_file()and f.name!='manifest.json'and '__pycache__'not in f.parts}
 assert actual==set(records)
 for n,h in records.items():
  f=p/n;assert not f.is_symlink()and f.resolve().is_relative_to(p)and H(f.read_bytes())==h,n

def sources(label,record):
 result={str(f.relative_to(OLD/'sources/recovered')):f.read_bytes()for f in(OLD/'sources/recovered').rglob('*')if f.is_file()}
 if record.get('vendored_anchor_spl'):
  with tarfile.open(PARENT/'upstream/anchor-spl-0.31.1.crate')as t:
   for f in t.getmembers():
    if f.isfile():result['anchor-spl/'+f.name.split('/',1)[1]]=t.extractfile(f).read()
  for f in(PARENT/'source-overrides/anchor-v8/anchor-spl').rglob('*'):
   if f.is_file():result['anchor-spl/'+str(f.relative_to(PARENT/'source-overrides/anchor-v8/anchor-spl'))]=f.read_bytes()
 folder=P/'sources'/label
 for n in ['Cargo.toml','Cargo.lock']:result[n]=(folder/n).read_bytes()
 for n in ['settlement_handlers.rs','mint_policy.rs']:
  if(folder/n).exists():result['src/'+n]=(folder/n).read_bytes()
 return result

def main(check_sdk=False,materialize=None,output=None):
 check_manifest(P)
 for n,h in read(P/'parent.json').items():assert H((ROOT/n).read_bytes())==h,n
 check_manifest(OLD);check_manifest(PARENT)
 variants=read(P/'variants.json')
 if materialize:
  assert output is not None and not output.exists()
  for n,b in sources(materialize,variants[materialize]).items():
   f=output/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
  print('Materialized',materialize,'at',output);return
 a=module('framework_recovery_elf',OLD/'analyze.py');helper=module('framework_recovery_receipts',OLD/'verify.py')
 original=(ROOT/'evidence/dependencies/donation_relay/deployed.so').read_bytes();assert H(original)==helper.ORIGINAL
 ledgers={};summaries={};images={};details={}
 counts={'native-pinned':474,'native-current':475,'linux-libs-pinned':477,'linux-libs-current':478,'share-values':479,'mint-reverse':470,'mint-newer-bool':470,'mint-older-bool':470}
 frozen={};harness_path=ROOT/'repro/donation-relay/local-validation-proposal/harness_proposal.py'
 for label,record in variants.items():
  d=P/'builds'/label;launch=read(d/'launch.json');result=read(d/'result.json')
  source=sources(label,record);assert launch['inputs']=={n:H(b)for n,b in source.items()},label
  assert launch['target']=='sbpf-solana-solana'and'--locked'in launch['command']and'--offline'in launch['command']
  image=gzip.decompress((d/'candidate.so.gz').read_bytes());symbols=gzip.decompress((d/'symbols.so.gz').read_bytes());images[label]=(image,symbols)
  assert H(image)==record['candidate_sha256']==result['candidate_sha256']and H(symbols)==result['symbols_sha256']
  assert result['exit_code']==0 and result['source_unchanged']and result['log_sha256']==H((d/'build.log').read_bytes())
  with tempfile.TemporaryDirectory()as tmp:
   t=Path(tmp);(t/'original.so').write_bytes(original);(t/'candidate.so').write_bytes(image);(t/'unstripped.so').write_bytes(symbols);shutil.copyfile(OLD/'original-windows.json',t/'original-windows.json');computed=a.analyze(t)
  summaries[label]=computed['comparison-summary.json'];ledgers[label]=computed['match-ledger.json'];details[label]=computed
  assert summaries[label]==read(d/'comparison-summary.json')and ledgers[label]==read(d/'match-ledger.json')
  assert summaries[label]['original_normalized_match_windows']==counts[label]and not summaries[label]['whole_file_equal']
  if(d/'fresh-runtime.json.gz').exists():
   report=read(d/'fresh-runtime.json.gz');assert report['runner_sha256']==H((P/'replay_saved.py').read_bytes())and report['harness_sha256']==H(harness_path.read_bytes())
   assert report['candidate_sha256']==record['candidate_sha256']and report['token2022_sha256']==H((ROOT/'evidence/dependencies/spl_token_2022/deployed.so').read_bytes())
   for n,h in report['input_reports'].items():
    f=ROOT/n;assert H(f.read_bytes())==h
    for i,row in enumerate(read(f)['cases']):frozen[str(f.relative_to(ROOT/'repro/donation-relay/distribution-worker-source-recovery/settlement'))+':'+str(i)]=row
   helper.EXPECTED['recovered']=record['candidate_sha256'];helper.check_runtime(report,frozen,module('framework_runtime_'+label.replace('-','_'),harness_path))
 base=read(PARENT/'builds/anchor-v8/match-ledger.json')
 for label,ledger in ledgers.items():assert not[r['ordinal']for old,r in zip(base,ledger)if old['normalized_candidate_indices']and not r['normalized_candidate_indices']],label
 edges=[('native-pinned','native-current',[344]),('native-pinned','linux-libs-pinned',[56,267,351]),('native-current','linux-libs-current',[56,267,351]),('linux-libs-current','share-values',[4])]
 for before,after,expected in edges:
  assert[r['ordinal']for old,r in zip(ledgers[before],ledgers[after])if not old['normalized_candidate_indices']and r['normalized_candidate_indices']]==expected
 assert[r['ordinal']for old,r in zip(base,ledgers['native-pinned'])if not old['normalized_candidate_indices']and r['normalized_candidate_indices']]==[172,282,300,332]
 before=sources('linux-libs-current',variants['linux-libs-current']);after=sources('share-values',variants['share-values'])
 assert[n for n in before if before[n]!=after[n]]==['src/settlement_handlers.rs']
 old=b'BpsSumDoesNotEqualTenThousand,204));';new=b'BpsSumDoesNotEqualTenThousand,204).with_values((sum,10000)));'
 assert before['src/settlement_handlers.rs'].replace(old,new)==after['src/settlement_handlers.rs']
 share=details['share-values'];functions=share['candidate-function-ledger.json']
 helper_targets={functions[i]['start']for i in ledgers['share-values'][4]['normalized_candidate_indices']}
 callers=[f for f in functions if any(c['target']in helper_targets for c in f['direct_calls'])]
 assert len(callers)==3
 for expected in ['19distribute_non_swap17h','16distribute_after17h','20swap_then_distribute17h']:
  assert any(any(expected in n for n in f['names'])for f in callers)
 original_helper=share['original-function-ledger.json'][4]['start']
 assert[f['ordinal']for f in share['original-function-ledger.json']if any(c['target']==original_helper for c in f['direct_calls'])]==[97,98,100]
 for ordinal in [56,267,351]:assert ledgers['share-values'][ordinal]['raw_candidate_indices']
 residue=[r['ordinal']for r in ledgers['share-values']if not r['normalized_candidate_indices']]
 assert residue==[90,92,93,94,95,96,97,98,99,100,106,109,112]
 assert read(P/'remaining-windows.json')==[r for r in ledgers['share-values']if r['ordinal']in residue]
 registry=read(P/'registry-audit.json');lock=tomllib.loads(after['Cargo.lock'].decode());checks={(x['name'],x['version']):x['checksum']for x in lock['package']if 'checksum'in x}
 assert registry['package_count']==len(registry['packages'])==177 and registry['file_count']==4006
 for x in registry['packages']:assert x['archive_sha256']==checks[x['name'],x['version']]
 expected=['0x77694f7f95096e5','0xf26e267850bd6732']
 for filename,want in [('linux-v148-sbpf-solana-solana.s',True),('darwin-linux-sysroot.s',True),('linux-v148-sbf-solana-solana.s',False),('linux-v149-sbf-solana-solana.s',False),('linux-v149-sbpf-solana-solana.s',False)]:
  assembly=(P/'probes'/filename).read_text();match=re.search(r'(_ZN\w+Error7type_id[^:\n]*):\n(.*?)\.Lfunc_end',assembly,re.S);assert match
  values=[hex(int(x)%(1<<64))for x in re.findall(r'lddw r\d+, (-?\d+)',match[2])];assert(values==expected)==want
 if check_sdk:
  sdk=Path('/Users/shawwalters/Documents/Codex/2026-10-24/pumpfun-source/work/relay-linux-v148/sdk')
  for n,h in read(P/'sdk/sdk-files.json').items():assert H((sdk/n).read_bytes())==h,n
 print(json.dumps(dict(verified=True,normalized_windows=479,raw_windows=summaries['share-values']['original_raw_match_windows'],remaining=residue,whole_file_identity=False,runtime_records=536),indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--check-sdk',action='store_true');ap.add_argument('--materialize',choices=list(read(P/'variants.json')));ap.add_argument('--output',type=Path);args=ap.parse_args();main(args.check_sdk,args.materialize,args.output)

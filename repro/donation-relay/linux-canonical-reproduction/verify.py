#!/usr/bin/env python3
"""Recheck fully Linux source-build outputs and their signed replay evidence."""
from pathlib import Path
import argparse,gzip,hashlib,importlib.util,json,shutil,tempfile
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
OLD=ROOT/'repro/donation-relay/swap-receipt-coordinate-recovery'
FRAMEWORK=ROOT/'repro/donation-relay/framework-sysroot-recovery'
TOKEN=ROOT/'repro/donation-relay/token-extension-version-recovery'
def H(b):return hashlib.sha256(b).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def verify():
 manifest=read(P/'manifest.json');actual={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()and f.name!='manifest.json'and '__pycache__'not in f.parts};assert set(manifest)==actual
 for n,h in manifest.items():
  f=P/n;assert not f.is_symlink()and f.resolve().is_relative_to(P)and H(f.read_bytes())==h,n
 for n,h in read(P/'parents.json').items():assert H((ROOT/n).read_bytes())==h,n
 ancestor=module('linux_ancestor',FRAMEWORK/'verify.py');ancestor.check_manifest(OLD);ancestor.check_manifest(TOKEN);ancestor.check_manifest(FRAMEWORK)
 a=module('linux_analysis',OLD/'analyze.py');helper=module('linux_receipt_checks',OLD/'verify.py');original=(ROOT/'evidence/dependencies/donation_relay/deployed.so').read_bytes();assert H(original)==helper.ORIGINAL
 meta=read(P/'variants.json');ledgers={};images={}
 for label,record in meta.items():
  d=P/label;result=read(d/'result.json');launch=read(d/'launch.json');expected=read(ROOT/record['reference_launch'])['inputs'];assert launch['inputs']==expected
  assert '--target'in launch['command']and'sbpf-solana-solana'in launch['command']and '--locked'in launch['command']and '--offline'in launch['command']
  assert '/sdk/rust/bin/cargo'in launch['command']and result['source_unchanged']and result['exit_code']==0
  assert H((d/'build.log').read_bytes())==result['build_log_sha256']
  image=gzip.decompress((d/'candidate.so.gz').read_bytes());symbols=gzip.decompress((d/'symbols.so.gz').read_bytes());assert H(image)==result['candidate_sha256']==record['candidate_sha256']and H(symbols)==result['symbols_sha256']
  images[label]=image
  if label=='final':assert 'Compiling donation-relay-source-proposal' in (d/'build.log').read_text() and '--crate-name donation_relay_source_proposal' in (d/'build.log').read_text()
  with tempfile.TemporaryDirectory()as tmp:
   t=Path(tmp);(t/'original.so').write_bytes(original);(t/'candidate.so').write_bytes(image);(t/'unstripped.so').write_bytes(symbols);shutil.copyfile(OLD/'original-windows.json',t/'original-windows.json');computed=a.analyze(t)
  assert computed['comparison-summary.json']==read(d/'comparison-summary.json')and computed['match-ledger.json']==read(d/'match-ledger.json');ledgers[label]=computed['match-ledger.json']
  assert computed['comparison-summary.json']['original_normalized_match_windows']==record['normalized_windows']
  assert not computed['comparison-summary.json']['whole_file_equal']
  reference=read(ROOT/record['reference_ledger']);assert [bool(r['normalized_candidate_indices'])for r in reference]==[bool(r['normalized_candidate_indices'])for r in ledgers[label]] if label in ('framework','final') else True
  if label in ('framework','final'):
   assert (d/'fresh-runtime.json.gz').exists()
   report=read(d/'fresh-runtime.json.gz');assert report['candidate_sha256']==H(image)and report['runner_sha256']==H((P/'replay_saved.py').read_bytes());h=ROOT/'repro/donation-relay/local-validation-proposal/harness_proposal.py';assert report['harness_sha256']==H(h.read_bytes())
   assert report['token2022_sha256']==H((ROOT/'evidence/dependencies/spl_token_2022/deployed.so').read_bytes());frozen={}
   for n,digest in report['input_reports'].items():
    f=ROOT/n;assert H(f.read_bytes())==digest
    for i,row in enumerate(read(f)['cases']):frozen[str(f.relative_to(ROOT/'repro/donation-relay/distribution-worker-source-recovery/settlement'))+':'+str(i)]=row
   helper.EXPECTED['recovered']=H(image);helper.check_runtime(report,frozen,module('linux_harness_'+label,h))
 control_base=read(TOKEN/'builds/anchor-v8/match-ledger.json')
 assert [r['ordinal']for x,r in zip(control_base,ledgers['control'])if not x['normalized_candidate_indices']and r['normalized_candidate_indices']]==[56,267,351]
 assert not [r['ordinal']for x,r in zip(control_base,ledgers['control'])if x['normalized_candidate_indices']and not r['normalized_candidate_indices']]
 assert [(i,x,y)for i,(x,y)in enumerate(zip(images['framework'],images['final']))if x!=y]==[(66185,18,33),(66193,2,1),(66201,2,1)]
 assert [r['ordinal']for x,r in zip(ledgers['framework'],ledgers['final'])if not x['normalized_candidate_indices']and r['normalized_candidate_indices']]==[106]
 cross=read(P/'cross-host-comparison.json');native=gzip.decompress((ROOT/'repro/donation-relay/mint-fee-pair-recovery/candidate.so.gz').read_bytes());linux=images['final']
 assert cross==dict(darwin_linux_sysroot_sha256=H(native),linux_sha256=H(linux),darwin_bytes=len(native),linux_bytes=len(linux),equal=native==linux,common_position_differences=sum(x!=y for x,y in zip(native,linux)))
 assert meta['control']['normalized_windows']==473 and meta['framework']['normalized_windows']==479 and meta['final']['normalized_windows']==480
 assert [r['ordinal']for r in ledgers['final']if not r['normalized_candidate_indices']]==[90,92,93,94,95,96,97,98,99,100,109,112]
 print(json.dumps(dict(verified=True,control_normalized=473,final_normalized=480,remaining=12,whole_file_identity=False),indent=2))
if __name__=='__main__':verify()

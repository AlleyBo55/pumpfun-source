#!/usr/bin/env python3
from pathlib import Path
import gzip,hashlib,importlib.util,json,shutil,tempfile
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def H(b):return hashlib.sha256(b).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 parent=read(P/'parent.json');F=ROOT/parent['path'];assert H((F/'manifest.json').read_bytes())==parent['manifest_sha256']
 base=module('mint_pair_parent',F/'verify.py');base.check_manifest(P);base.check_manifest(F)
 source=base.sources('share-values',read(F/'variants.json')['share-values']);old=source['src/mint_policy.rs']
 before=b'let fee_basis_points=u16::from(fee.older_transfer_fee.transfer_fee_basis_points) | u16::from(fee.newer_transfer_fee.transfer_fee_basis_points);\n   if fee_basis_points!=0 {return Ok(false);}'
 after=b'if (u16::from(fee.older_transfer_fee.transfer_fee_basis_points),u16::from(fee.newer_transfer_fee.transfer_fee_basis_points)) != (0,0) {return Ok(false);}'
 assert old.count(before)==1;source['src/mint_policy.rs']=(P/'mint_policy.rs').read_bytes();assert source['src/mint_policy.rs']==old.replace(before,after)
 launch=read(P/'launch.json');result=read(P/'result.json');assert launch['inputs']=={n:H(b)for n,b in source.items()};assert result['exit_code']==0 and result['source_unchanged']and result['log_sha256']==H((P/'build.log').read_bytes())
 image=gzip.decompress((P/'candidate.so.gz').read_bytes());symbols=gzip.decompress((P/'symbols.so.gz').read_bytes());assert H(image)==result['candidate_sha256']=='da61931f49713668c567791c4b36a49c3a75a1004ed331020054bcb13521f2c6';assert H(symbols)==result['symbols_sha256']
 control=gzip.decompress((F/'builds/share-values/candidate.so.gz').read_bytes());assert len(image)==len(control)==818072
 assert[(i,a,b)for i,(a,b)in enumerate(zip(control,image))if a!=b]==[(66185,18,33),(66193,2,1),(66201,2,1)]
 old=ROOT/'repro/donation-relay/swap-receipt-coordinate-recovery';base.check_manifest(old);a=module('mint_pair_elf',old/'analyze.py');original=(ROOT/'evidence/dependencies/donation_relay/deployed.so').read_bytes()
 with tempfile.TemporaryDirectory()as tmp:
  d=Path(tmp);(d/'original.so').write_bytes(original);(d/'candidate.so').write_bytes(image);(d/'unstripped.so').write_bytes(symbols);shutil.copyfile(old/'original-windows.json',d/'original-windows.json');computed=a.analyze(d)
 assert computed['comparison-summary.json']==read(P/'comparison-summary.json')and computed['match-ledger.json']==read(P/'match-ledger.json');summary=computed['comparison-summary.json'];assert summary['original_normalized_match_windows']==480 and summary['unmatched_original_windows']==12 and not summary['whole_file_equal']
 serial=P/'serial-control';sr=read(serial/'result.json');sb=gzip.decompress((serial/'candidate.so.gz').read_bytes());ss=gzip.decompress((serial/'symbols.so.gz').read_bytes());assert H(sb)==sr['candidate_sha256']and H(ss)==sr['symbols_sha256']and sr['source_unchanged']and sr['exit_code']==0
 assert H((serial/'build.log').read_bytes())==sr['log_sha256']
 serial_source=dict(source);serial_source['src/mint_policy.rs']=(serial/'mint_policy.rs').read_bytes();assert read(serial/'launch.json')['inputs']=={n:H(b)for n,b in serial_source.items()}
 se=a.Elf(ss);sf=next(f for f in se.symbols if 'typed_mint_safe' in f['name']);assert sf['size']==3432
 prev=read(F/'builds/share-values/match-ledger.json');now=computed['match-ledger.json'];assert[r['ordinal']for l,r in zip(prev,now)if not l['normalized_candidate_indices']and r['normalized_candidate_indices']]==[106];assert not[r['ordinal']for l,r in zip(prev,now)if l['normalized_candidate_indices']and not r['normalized_candidate_indices']]
 report=read(P/'fresh-runtime.json.gz');assert report['candidate_sha256']==H(image)and report['runner_sha256']==H((P/'replay_saved.py').read_bytes());h=ROOT/'repro/donation-relay/local-validation-proposal/harness_proposal.py';assert report['harness_sha256']==H(h.read_bytes())and report['token2022_sha256']==H((ROOT/'evidence/dependencies/spl_token_2022/deployed.so').read_bytes());frozen={}
 for n,digest in report['input_reports'].items():
  f=ROOT/n;assert H(f.read_bytes())==digest
  for i,row in enumerate(read(f)['cases']):frozen[str(f.relative_to(ROOT/'repro/donation-relay/distribution-worker-source-recovery/settlement'))+':'+str(i)]=row
 helper=module('mint_pair_receipts',old/'verify.py');helper.EXPECTED['recovered']=H(image);helper.check_runtime(report,frozen,module('mint_pair_runtime',h))
 print(json.dumps(dict(verified=True,normalized=480,raw=summary['original_raw_match_windows'],remaining=12,gain=106,changed_output_bytes=3,replay_records=536),indent=2))
if __name__=='__main__':main()

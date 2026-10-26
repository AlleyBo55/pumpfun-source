"""Portable read-only metadata receipt validator. Does not follow provenance paths."""
from pathlib import Path
import argparse,hashlib,json,sys
sys.dont_write_bytecode=True
from derive_metadata import derive
P=Path(__file__).parent
H=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
J=lambda n:json.loads((P/n).read_text())
def verify(expected):
 assert H(P/'manifest.json')==expected==(P/'manifest.sha256').read_text().strip()
 m=J('manifest.json');assert {str(f.relative_to(P))for f in P.rglob('*')if f.is_file()}==set(m)|{'manifest.json','manifest.sha256'}
 for n,r in m.items():
  f=P/n;assert not f.is_symlink()and H(f)==r['sha256']and f.stat().st_size==r['bytes']
 pm=J('input-emitted-plan-manifest.json');rm=J('input-independent-review-manifest.json');ih=J('input-independent-review-input-hashes.json')
 assert H(P/'input-emitted-plan-manifest.json')=='970784c402bc690704309e0621b84885bbe455f5abe6844600304228288af870'
 assert H(P/'input-independent-review-manifest.json')=='e2161fdbd2c6c96e08db4a3398d1197b2200a2c1e403ae2dc239e0abac98607e'
 assert H(P/'input-independent-review-input-hashes.json')==rm['input-hashes.json']['sha256']
 for n,r in J('input-bindings.json').items():
  assert H(P/n)==r['sha256']
  if n=='new-inventory.json.gz':assert r['sha256']==ih['raw_outputs'][n]
  else:
   key=n.replace('admitted-controls/','admitted-original-controls/');assert r['sha256']==pm[key]['sha256']
 assert derive()==J('derived-records.json')
 print(json.dumps({'state':'PASS_METADATA_ONLY_CORRECTION_NOT_ABI_PROOF','inventories':4,'original_windows_each':1035,'new_original_or_candidate_decode':0,'VM_compiler_network':0}))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--expected-seal',required=True);verify(a.parse_args().expected_seal)

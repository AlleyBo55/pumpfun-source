"""Preparation hashes/syntax/delta only. No candidate or original decoding."""
from pathlib import Path,PurePosixPath
import argparse,ast,difflib,gzip,hashlib,json
P=Path(__file__).resolve().parent;H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();J=lambda p:json.loads(p.read_text())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--expected-seal',required=True);a=ap.parse_args();assert __debug__ and H(P/'manifest.json')==a.expected_seal==(P/'manifest.sha256').read_text().strip();m=J(P/'manifest.json')
 assert set(m)=={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()}-{'manifest.json','manifest.sha256'}
 for n,r in m.items():
  rel=PurePosixPath(n);assert not rel.is_absolute()and'..'not in rel.parts;f=P/n;assert not f.is_symlink()and f.stat().st_size==r['bytes']and H(f)==r['sha256']
 old=J(P/'predecessor-emitted-plan-manifest.json');assert H(P/'predecessor-emitted-plan-manifest.json')=='aa5756b2edd1457235eabd979ce9ff8b5d11492ab887e7a4dd84a15aa0d7c14b'
 assert H(P/'metadata_join.py')==old['metadata_join.py']['sha256']
 for n,r in old.items():
  if n.startswith('methods/')or n.startswith('admitted-original-controls/')or n=='retained-full-inventory.json.gz':assert H(P/n)==r['sha256']
 for n in['metadata_join.py','candidate_bodies.py','compare_inventory.py','verify_plan.py']:ast.parse((P/n).read_text())
 reference=(P/'methods/layer_inventory.py').read_text();fixed=reference[reference.index(' while True:'):reference.index(' comparisons=[]')];assert fixed in(P/'metadata_join.py').read_text()
 assert H(P/'build-plan-MANIFEST.json')=='29069875549ea325beeafc10059c6893218211c327d08a6f90bce70df10e5ae2'
 review=J(P/'retained-6e-review-manifest.json');assert H(P/'retained-6e-review-manifest.json')=='49b796714e91f7909f4ab5f09eb3d37f6f39c902c196ea30c42c1c9d3cbdd6bc'
 assert H(P/'retained-6e-input-hashes.json')==review['input-hashes.json']['sha256'];bindings=J(P/'retained-6e-input-hashes.json')['raw_outputs']
 assert H(P/'retained-6e-inventory.json.gz')==bindings['new-inventory.json.gz']and H(P/'retained-6e-candidate-proof.json')==bindings['candidate-bodies/proof.json']
 # Retained saved JSON metadata only, not an image decoder.
 saved=json.loads(gzip.decompress((P/'retained-6e-inventory.json.gz').read_bytes()));assert saved['candidate_sha256']=='6e0c9002d09e0cee6cc738b3a9e0983a8d0cd89374fa2cc7c41fa45910515b9e'and len(saved['original_windows'])==1035
 oldb=(P/'predecessor-candidate_bodies.py').read_text();newb=(P/'candidate_bodies.py').read_text();d=J(P/'body-derivation.json')
 for before,after in d['replacements']:assert oldb.count(before)==1;oldb=oldb.replace(before,after)
 assert oldb==newb and H(P/'predecessor-candidate_bodies.py')==old['candidate_bodies.py']['sha256']
 assert(P/'candidate-bodies-adaptation.diff').read_text()==''.join(difflib.unified_diff((P/'predecessor-candidate_bodies.py').read_text().splitlines(True),newb.splitlines(True),fromfile='aa5756/candidate_bodies.py',tofile='shared-v2/candidate_bodies.py'))
 assert len(J(P/'build-plan-source-proposed.json'))==37 and J(P/'build-plan-source-proposed.json')['programs/pump/src/admin_cto.rs']=='950d6ec8c07072a3305c905509018f95b40d53e9ab25a4c1bda96b42c2a2fe58'
 assert not(P.parent/'cto-shared6093-v2-emitted-review').exists(),'fresh analysisoutput required'
 print('PASS PREPARATION ONLY: exactmetadatajoin/methods/1035retainedrecords/35controls; declared2sharedhelperallowlist+scope context; no candidate decode,originalread,native/VM/analysisexecution.')
if __name__=='__main__':main()

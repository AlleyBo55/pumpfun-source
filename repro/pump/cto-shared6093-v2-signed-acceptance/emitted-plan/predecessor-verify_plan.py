"""Preparation-only hashes/syntax/method-delta verification. No candidate analysis."""
from pathlib import Path
import argparse,ast,hashlib,json
P=Path(__file__).resolve().parent;H=lambda b:hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--expected-seal',required=True);args=ap.parse_args();assert __debug__
 raw=(P/'manifest.json').read_bytes();assert H(raw)==args.expected_seal
 m=json.loads(raw);actual={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()}-{'manifest.json','manifest.sha256'};assert actual==set(m)
 for n,r in m.items():
  f=P/n;assert not f.is_symlink();b=f.read_bytes();assert len(b)==r['bytes']and H(b)==r['sha256']
 for n in ['metadata_join.py','candidate_bodies.py','verify_plan.py']:ast.parse((P/n).read_text())
 old=(P/'methods/layer_inventory.py').read_text();new=(P/'metadata_join.py').read_text();a=old.index(' while True:');b=old.index(' comparisons=[]',a);assert old[a:b]in new
 assert H((P/'methods/reference_elf.py').read_bytes())==H((P/'methods/previous-emitted-reference-elf-method.py').read_bytes())
 assert H((P/'methods/render.py').read_bytes())==H((P/'methods/previous-emitted-render.py').read_bytes())
 assert H((P/'build-plan-MANIFEST.json').read_bytes())=='ff7a857b5394b57c61eebb19cf6265fa001b18b2d0f3db4936fd00c48cbb2fa0'
 print('PASS PREPARATION ONLY: sealed methods/controls and syntax; fixed-point loop unchanged; no metadata join, candidate decode, original read, runtime or native command executed.')
if __name__=='__main__':main()

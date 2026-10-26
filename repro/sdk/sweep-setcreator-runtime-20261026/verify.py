"""Portable saved-data replay only; never imports SDKs or native crypto utilities."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json
P=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main(expected):
 assert __debug__
 assert H(P/'manifest.json')==expected==(P/'manifest.sha256').read_text().strip()
 m=json.loads((P/'manifest.json').read_text());assert not any(f.is_symlink()for f in P.rglob('*'));assert {str(f.relative_to(P))for f in P.rglob('*')if f.is_file()}==set(m)|{'manifest.json','manifest.sha256'}
 for n,r in m.items():
  q=PurePosixPath(n);assert not q.is_absolute()and'..'not in q.parts;assert H(P/n)==r['sha256']and(P/n).stat().st_size==r['bytes']
 from audit_saved import audit
 result=audit(False);assert result==json.loads((P/'final-audit-result.json').read_text())
 print('PASS: saved10SDK observations,8instruction objects/84metas,2actualresolvererrors,316hash-boundmodules; no SDK/Node/Solders rerun')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--expected-seal',required=True);main(a.parse_args().expected_seal)

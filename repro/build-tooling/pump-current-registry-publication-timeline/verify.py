from pathlib import Path,PurePosixPath
import argparse,hashlib,json
from analyze import analyze
P=Path(__file__).resolve().parent;H=lambda b:hashlib.sha256(b).hexdigest()
a=argparse.ArgumentParser();a.add_argument('--expected-seal',required=True);v=a.parse_args();assert __debug__
raw=(P/'manifest.json').read_bytes();assert H(raw)==v.expected_seal==(P/'manifest.sha256').read_text().strip();m=json.loads(raw)
assert not any(f.is_symlink()for f in P.rglob('*'))
assert set(m)|{'manifest.json','manifest.sha256'}=={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()}
for n,r in m.items():
 q=PurePosixPath(n);assert not q.is_absolute()and'..'not in q.parts;b=(P/n).read_bytes();assert H(b)==r['sha256']and len(b)==r['bytes']
u=(P/'unit-record-manifest.json').read_bytes();assert H(u)=='9760c7c71676eefc98c023f1eea876c75f1af06ef4b9932f63361aed8aad140f';assert H((P/'current-unit-analysis.json').read_bytes())==json.loads(u)['analysis.json']['sha256']
d=analyze();assert d==json.loads((P/'analysis.json').read_text());late=d['published_after_deployment'];assert len(late)==1 and late[0]['name']=='cc'and late[0]['version']=='1.10.0'
print('PASS176officialchecksums/timestamps, one postdeployment version cc1.10.0; historical graph/output effect remain unproved')

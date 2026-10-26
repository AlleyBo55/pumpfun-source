"""Passive portable verification of eight SDK source expansions."""
from pathlib import Path,PurePosixPath
import argparse,base64,hashlib,io,json,tarfile
from analyze import analyze
P=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
J=lambda n:json.loads((P/n).read_bytes())
def verify(expected):
 assert __debug__
 assert H((P/'manifest.json').read_bytes())==expected==(P/'manifest.sha256').read_text().strip()
 m=J('manifest.json');assert not any(x.is_symlink()for x in P.rglob('*'));assert {str(x.relative_to(P))for x in P.rglob('*')if x.is_file()}==set(m)|{'manifest.json','manifest.sha256'}
 for n,r in m.items():
  q=PurePosixPath(n);assert not q.is_absolute()and'..'not in q.parts;raw=(P/n).read_bytes();assert H(raw)==r['sha256']and len(raw)==r['bytes']
 assert H((P/'controls/MANIFEST.json').read_bytes())=='a20815957ffd0f261737ee2ea20850f66d94b239d0379f2cc4caaf3e577376bb'
 old=J('controls/MANIFEST.json')['files']
 for name,path in [('ts_static.py','ts_static.py'),('sdk-matrix.json','controls/sdk-matrix.json')]:assert H((P/path).read_bytes())==old[name]['sha256']
 assert H((P/'controls/prior-record-manifest.json').read_bytes())=='33e756fc21ac913ba7455e3d1391900fbbe038180f8c593b7d542b8b0295ce7a'
 assert H((P/'archive-bindings.json').read_bytes())==J('controls/prior-record-manifest.json')['archive-bindings.json']['sha256']
 archives={}
 for r in J('archive-bindings.json'):
  raw=(P/r['file']).read_bytes();assert H(raw)==r['sha256']and len(raw)==r['bytes']and hashlib.sha1(raw).hexdigest()==r['sha1'];assert 'sha512-'+base64.b64encode(hashlib.sha512(raw).digest()).decode()==r['integrity']
  t=tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz');assert len({x.name for x in t.getmembers()})==len(t.getmembers());archives[r['file']]=t
 for n,r in J('source-bindings.json').items():
  t=archives[r['archive']];member=t.getmember(r['member']);assert member.isfile();raw=t.extractfile(member).read();assert raw==(P/n).read_bytes()and H(raw)==r['sha256']and len(raw)==r['bytes']
 d=analyze();assert d==J('analysis.json');assert d['new_expanded_site_count']==8 and len(d['remaining_sites'])==d['remaining_unexpanded_site_count']==9
 assert all(not r['excluded']or'interface metadata only'in r['excluded']for r in d['remaining_sites'])
 print('PASS:8 static SDK object sites;4 AMM sweeps12/12,2 Pump sweeps9/13,2 conditional creator sites1or3/5;9 original dynamic sites remain. No JavaScript/RPC/target execution or client compatibility claim.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--expected-seal',required=True);verify(p.parse_args().expected_seal)

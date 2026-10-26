"""Verify copied admitted text and bounded assertions; no decoder or original read."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json
P=Path(__file__).resolve().parent;H=lambda b:hashlib.sha256(b).hexdigest()
def verify(seal):
 assert __debug__,'Use Python without -O'
 raw=(P/'manifest.json').read_bytes();assert H(raw)==seal==(P/'manifest.sha256').read_text().strip()
 m=json.loads(raw);assert not any(f.is_symlink()for f in P.rglob('*'))
 assert set(m)|{'manifest.json','manifest.sha256'}=={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()}
 for n,r in m.items():
  q=PurePosixPath(n);assert not q.is_absolute()and'..'not in q.parts
  b=(P/n).read_bytes();assert H(b)==r['sha256']and len(b)==r['bytes'],n
 q=P/'admitted-original-control';raw=(q/'manifest.json').read_bytes();assert H(raw)=='1b64277d77a8c42900a2c5bec8c6e3d4e6998b42febec2ef4a1898260b74bd38';controls=json.loads(raw)
 parent_raw=(P/'emitted-parent-manifest.json').read_bytes();assert H(parent_raw)=='df2338c443a3ffdb174c1f3098f05c29e4c011bd954ab78b72302e7c5776920c';parent=json.loads(parent_raw)
 copied_raw=(P/'emitted-parent-original-copy-bindings.json').read_bytes();assert H(copied_raw)==parent['original-copy-bindings.json']['sha256']and len(copied_raw)==parent['original-copy-bindings.json']['bytes'];copied=json.loads(copied_raw)
 assert copied['manifest_sha256']==H(raw)and len(copied['files'])==39 and len(controls)==47
 assert set(copied['files'])|{'manifest.json'}=={str(f.relative_to(q))for f in q.rglob('*')if f.is_file()}
 for n,r in copied['files'].items():
  assert r==controls[n]==parent['original-control/'+n]
  b=(q/n).read_bytes();assert H(b)==r['sha256']and len(b)==r['bytes']
 assert len(list(q.glob('*.asm')))==35
 raw=(P/'collector-control-manifest.json').read_bytes();assert H(raw)=='a16e512a56262ec8a45c09b25b4f341b6e139d0bca4b3ba0396e01fe61054bbb';prior=json.loads(raw)
 for name in['141840.asm','177296.asm']:
  b=(q/name).read_bytes();r=prior['controls/'+name];assert H(b)==r['sha256']and len(b)==r['bytes']
 b=(P/'collector-prior-report.md').read_bytes();r=prior['REPORT.md'];assert H(b)==r['sha256']and len(b)==r['bytes']
 body=(q/'141840.asm').read_text().splitlines();anchors=json.loads((P/'text-anchors.json').read_text())
 for group,rows in anchors.items():
  assert rows
  for line in rows:assert body.count(line)==1
 # Literal preexisting display-line assertions; no binary instruction parsing.
 required=['149920: 0500a40000000000                 JUMP op=5 r0,0 ->151240',
 '151304: 150153ff00000000                 JUMP op=15 r1,0 ->149928',
 '151368: 15014fff00000000                 JUMP op=15 r1,0 ->149960',
 '149952: 0500db0000000000                 JUMP op=5 r0,0 ->151712',
 '157088: 150784fc02000000                 JUMP op=15 r7,2 ->149960',
 '150200: 1501610300000000                 JUMP op=15 r1,0 ->157128',
 '150352: 1501a50700000000                 JUMP op=15 r1,0 ->166016',
 '150384: 15065e0300000000                 JUMP op=15 r6,0 ->157288']
 for line in required:assert line in body
 assert '1108536: 85100000610c0000                 CALL 1133896'in(q/'1108280.asm').read_text()
 assert not(q/'1133896.asm').exists()and not(q/'249168.asm').exists()
 findings=json.loads((P/'findings.json').read_text());assert findings['state']=='PASS_ORDERING_REVIEW_FIELD_MAP_INSUFFICIENT'
 assert findings['named_field_mapping_proven']is False and findings['shared6093_composition_ready']is False and findings['candidate_layout_used_as_proof']is False
 assert findings['separate_error_origins']==[660,719]
 for key in['new_original_capture_reads','new_body_or_callee_acquisition','new_decoder_or_parser_invocations','new_build_runtime_network_executions','active_source_or_status_changes']:assert findings[key]==0
 print('PASS existing35-text controls and shared6093 ordering obligations. Named field map remains INSUFFICIENT; no Rust patch or full effect/ABI acceptance.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--expected-seal',required=True);a=p.parse_args();verify(a.expected_seal)

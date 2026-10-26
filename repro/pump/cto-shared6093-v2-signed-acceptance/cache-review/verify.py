"""Pure retained generated-bookkeeping review replay; no native commands or original input reads."""
from pathlib import Path
import hashlib,json
from analyze import analyze
P=Path(__file__).resolve().parent;H=lambda b:hashlib.sha256(b).hexdigest();J=lambda p:json.loads(p.read_text())
m=J(P/'manifest.json');assert set(m)=={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()and f!=P/'manifest.json'}
for n,r in m.items():
 f=P/n;assert not f.is_symlink();b=f.read_bytes();assert H(b)==r['sha256']and len(b)==r['bytes']
d=analyze();assert d==J(P/'review.json');l=J(P/'live-bindings.json');assert l['status']=='PASS_READONLY_FRESH_CACHE_SNAPSHOT_BINDING'and l['writes_to_build_cache_or_controller']==0 and l['controller_receipt_sha256_before']==l['controller_receipt_sha256_after']==J(P/'snapshot.json')['controller_receipt_sha256'];assert len(d['approved_archive_paths_not_entered_in_SQLite'])==27
print(json.dumps({'status':d['status'],'original_controller_state':d['controller_original_state'],'helper_exit':d['helper_exit'],'build_sbf_aggregate_exit':d['build_sbf_aggregate_exit'],'compiler_child_exit':None,'strip_child_exit':None,'counts':d['counts'],'source_size_null_rows':d['source_size_null_rows'],'additional_builds':0,'target_executions':0,'controller_receipt_mutations':0},indent=2))

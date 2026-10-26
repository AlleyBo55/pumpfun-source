"""Optional read-only binding of the saved snapshot to the terminal build's fresh private cache."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;J=lambda p:json.loads(p.read_text());H=lambda b:hashlib.sha256(b).hexdigest()
def verify_live():
 snap=J(P/'snapshot.json');build=Path(snap['build_path']);cache=build/'cargo-home';receipt=build/'controller-result.json';before=H(receipt.read_bytes());assert before==snap['controller_receipt_sha256'];allowed=J(P/'cache-allowlist.json')['files'];expected=set(allowed)|set(snap['additions']);actual=set()
 for f in cache.rglob('*'):
  assert not f.is_symlink(),str(f)
  if f.is_file():actual.add(str(f.relative_to(cache)))
 assert actual==expected
 for n,row in allowed.items():assert(cache/n).stat().st_size==row['bytes'],n
 copied={}
 for n,row in snap['additions'].items():
  raw=(cache/n).read_bytes();assert H(raw)==row['sha256']and len(raw)==row['bytes']and raw==(P/'cache-additions'/n).read_bytes();copied[n]={'bytes':len(raw),'sha256':H(raw)}
 assert H(receipt.read_bytes())==before
 return {'status':'PASS_READONLY_FRESH_CACHE_SNAPSHOT_BINDING','controller_receipt_sha256_before':before,'controller_receipt_sha256_after':before,'actual_added_paths_exact':sorted(snap['additions']),'existing_allowed_files':len(allowed),'existing_allowed_file_sizes_match':True,'old_file_hashes_independently_recomputed':False,'old_file_hash_scope':'Original controller before/after equality retained. This optional binding checks old file sizes/path set only.','generated_file_bindings':copied,'fresh_cache_opened_with_SQLite':False,'writes_to_build_cache_or_controller':0}
if __name__=='__main__':print(json.dumps(verify_live(),indent=2))

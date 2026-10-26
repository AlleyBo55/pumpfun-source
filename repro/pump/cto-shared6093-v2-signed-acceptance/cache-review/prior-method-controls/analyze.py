"""Read-only review of four generated Cargo bookkeeping files; no build or target execution."""
from pathlib import Path,PurePosixPath
import hashlib,json,sqlite3
P=Path(__file__).resolve().parent;H=lambda b:hashlib.sha256(b).hexdigest();J=lambda p:json.loads(p.read_text())
SQL={
'git_checkout':'CREATE TABLE git_checkout ( git_id INTEGER NOT NULL, name TEXT UNIQUE NOT NULL, size INTEGER, timestamp INTEGER NOT NULL, PRIMARY KEY (git_id, name), FOREIGN KEY (git_id) REFERENCES git_db (id) ON DELETE CASCADE )',
'git_db':'CREATE TABLE git_db ( id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL, timestamp INTEGER NOT NULL )',
'global_data':'CREATE TABLE global_data ( last_auto_gc INTEGER NOT NULL )',
'registry_crate':'CREATE TABLE registry_crate ( registry_id INTEGER NOT NULL, name TEXT NOT NULL, size INTEGER NOT NULL, timestamp INTEGER NOT NULL, PRIMARY KEY (registry_id, name), FOREIGN KEY (registry_id) REFERENCES registry_index (id) ON DELETE CASCADE )',
'registry_index':'CREATE TABLE registry_index ( id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL, timestamp INTEGER NOT NULL )',
'registry_src':'CREATE TABLE registry_src ( registry_id INTEGER NOT NULL, name TEXT NOT NULL, size INTEGER, timestamp INTEGER NOT NULL, PRIMARY KEY (registry_id, name), FOREIGN KEY (registry_id) REFERENCES registry_index (id) ON DELETE CASCADE )',
'sqlite_sequence':'CREATE TABLE sqlite_sequence(name,seq)'}
INDEXES={'sqlite_autoindex_git_checkout_1':'git_checkout','sqlite_autoindex_git_checkout_2':'git_checkout','sqlite_autoindex_git_db_1':'git_db','sqlite_autoindex_registry_crate_1':'registry_crate','sqlite_autoindex_registry_index_1':'registry_index','sqlite_autoindex_registry_src_1':'registry_src'}
def analyze():
 snap=J(P/'snapshot.json');assert H((P/'plan-manifest.json').read_bytes())==snap['plan_seal']=='ff7a857b5394b57c61eebb19cf6265fa001b18b2d0f3db4936fd00c48cbb2fa0';pm=J(P/'plan-manifest.json')
 for n in ['cache-allowlist.json','future-plan.json']:assert H((P/n).read_bytes())==pm[n]
 cr=J(P/'controller-result.json');assert H((P/'controller-result.json').read_bytes())==snap['controller_receipt_sha256']and cr['proposal_manifest']==snap['plan_seal']
 assert cr['state']=='requires-cache-review'and cr['helper_exit']==cr['build_sbf_aggregate_exit']==0 and cr['compiler_child_exit']is None and cr['strip_child_exit']is None
 assert cr['source_unchanged']and cr['private_cache_existing_unchanged']and cr['tool_sdk_before']==cr['tool_sdk_after']and cr['cache_additions_require_review']
 assert cr['backend_error_lines']==cr['stack_llvm_diagnostics']==[]
 expected={'.package-cache':H(b''),'.package-cache-mutate':H(b''),'.global-cache':'f121b589f2fcda615d8a58762ae5e4b63b92b1970e56f53e50256cd1f6eaa467','registry/CACHEDIR.TAG':'6d9d1d216e0f83abc5e5662ca62c92b4f23009466b54fa27321a69acdb778bb2'};assert cr['private_cache_additions']==expected and set(snap['additions'])==set(expected)
 for n,h in expected.items():
  f=P/'cache-additions'/n;b=f.read_bytes();assert not f.is_symlink()and H(b)==h==snap['additions'][n]['sha256']and len(b)==snap['additions'][n]['bytes']
 assert (P/'cache-additions/registry/CACHEDIR.TAG').read_bytes().startswith(b'Signature: 8a477f597d28d172789f06886806bc55')
 db=P/'cache-additions/.global-cache';before=H(db.read_bytes());assert not Path(str(db)+'-wal').exists()and not Path(str(db)+'-shm').exists()
 c=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True)
 try:
  c.execute('PRAGMA query_only=ON');c.execute('PRAGMA trusted_schema=OFF');quick=c.execute('PRAGMA quick_check').fetchall();assert quick==[('ok',)];foreign=c.execute('PRAGMA foreign_key_check').fetchall();assert foreign==[]
  schema=[list(x)for x in c.execute('SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name')];assert schema==J(P/'schema.json');assert len(schema)==len(SQL)+len(INDEXES)
  for typ,name,table,sql in schema:
   if typ=='table':assert name==table and name in SQL and' '.join(sql.split())==SQL[name]
   else:assert typ=='index'and name in INDEXES and table==INDEXES[name]and sql is None
  tables={n:[list(x)for x in c.execute('SELECT * FROM "'+n+'" ORDER BY rowid')]for n in SQL}
 finally:c.close()
 assert H(db.read_bytes())==before
 assert tables['git_db']==tables['git_checkout']==[]and len(tables['registry_index'])==2 and len(tables['global_data'])==1
 assert all(isinstance(v,int)and v>=0 for row in tables['global_data']for v in row)
 registries={i:name for i,name,ts in tables['registry_index']};assert len(registries)==2 and all(isinstance(ts,int)and ts>0 for i,name,ts in tables['registry_index'])
 assert tables['sqlite_sequence']==[['registry_index',max(registries)]]
 cache=J(P/'cache-allowlist.json');assert cache['lock_packages']==252;approved=cache['files'];crate_paths={};src_dirs={}
 for n,row in approved.items():
  path=PurePosixPath(n);assert not path.is_absolute()and'..'not in path.parts
  if path.parts[:2]==('registry','cache'):crate_paths[n]=row
  elif path.parts[:2]==('registry','src'):
   prefix='/'.join(path.parts[:4]);v=src_dirs.setdefault(prefix,{'files':0,'approved_bytes':0});v['files']+=1;v['approved_bytes']+=row['bytes']
 assert set(registries.values())=={PurePosixPath(n).parts[2]for n in crate_paths}=={PurePosixPath(n).parts[2]for n in src_dirs}
 seen_crates=set();seen_src=set();bindings=[]
 for registry_id,name,size,ts in tables['registry_crate']:
  assert registry_id in registries and'/'not in name and'\\'not in name and isinstance(size,int)and isinstance(ts,int)and ts>0;n='registry/cache/'+registries[registry_id]+'/'+name;assert n in crate_paths and n not in seen_crates;seen_crates.add(n);assert size==crate_paths[n]['bytes'];bindings.append({'table':'registry_crate','path':n,'size':size,'approved_sha256':crate_paths[n]['sha256']})
 for registry_id,name,size,ts in tables['registry_src']:
  assert registry_id in registries and'/'not in name and'\\'not in name and isinstance(ts,int)and ts>0;n='registry/src/'+registries[registry_id]+'/'+name;assert n in src_dirs and n not in seen_src;seen_src.add(n);assert size is None or size==src_dirs[n]['approved_bytes'];bindings.append({'table':'registry_src','path':n,'recorded_size':size,**src_dirs[n],'size_scope':'NULL unobserved in SQLite; approved directory file sum retained, not claimed observed DB size'if size is None else'equals approved regular-file byte sum'})
 assert seen_crates<set(crate_paths)and seen_src==set(src_dirs)and len(seen_crates)==len(seen_src)==477
 assert seen_crates=={n.replace('registry/src/','registry/cache/',1)+'.crate'for n in seen_src}
 return {'status':'PASS_GENERATED_BOOKKEEPING_ONLY_UNSELECTED','controller_original_state':cr['state'],'helper_exit':cr['helper_exit'],'build_sbf_aggregate_exit':cr['build_sbf_aggregate_exit'],'compiler_child_exit':None,'strip_child_exit':None,'controller_receipt_unchanged':True,'sqlite_open_mode':'ro','quick_check':[list(x)for x in quick],'foreign_key_check':foreign,'schema':schema,'tables':tables,'row_bindings':bindings,'counts':{n:len(rows)for n,rows in tables.items()},'new_files':expected,'all_477_archive_and_477_source_rows_approved':True,'approved_archive_paths_not_entered_in_SQLite':sorted(set(crate_paths)-seen_crates),'source_size_null_rows':sum(x[2]is None for x in tables['registry_src']),'acceptance':'Separate review accepts these four generated bookkeeping files only. Original terminal requires-cache-review/exit2 remains unchanged; no retry, automatic source/artifact selection or byte identity claim.'}
if __name__=='__main__':
 d=analyze();(P/'review.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:d[k]for k in ['status','controller_original_state','counts','source_size_null_rows']},indent=2))

"""Pure official metadata/archive/source comparison. Never imports or executes Rust/native code."""
from pathlib import Path,PurePosixPath
import hashlib,json,tarfile,io,tomllib,difflib
P=Path(__file__).resolve().parent;J=lambda p:json.loads(p.read_text());H=lambda b:hashlib.sha256(b).hexdigest()
def analyze():
 http=J(P/'metadata-http.json')+J(P/'additional-http.json');assert len(http)==34 and all(r['status']==200 for r in http)
 for r in http:
  b=(P/r['file']).read_bytes();assert H(b)==r['sha256']and len(b)==r['bytes'];assert r['url'].startswith(('https://crates.io/api/v1/crates/','https://static.crates.io/crates/'))
 source37=J(P/'context/source37.json');assert H((P/'context/build-plan-manifest.json').read_bytes())=='ff7a857b5394b57c61eebb19cf6265fa001b18b2d0f3db4936fd00c48cbb2fa0';pm=J(P/'context/build-plan-manifest.json');assert H((P/'context/cache-allowlist.json').read_bytes())==pm['cache-allowlist.json']and H((P/'context/source37.json').read_bytes())==pm['source-proposed.json']
 for n in ['Cargo.lock','Cargo.toml']:assert H((P/'context'/('current-'+n)).read_bytes())==source37['programs/pump/'+n]
 units=J(P/'context/current-unit-analysis.json');um=J(P/'context/current-unit-record-manifest.json');assert H((P/'context/current-unit-record-manifest.json').read_bytes())=='9760c7c71676eefc98c023f1eea876c75f1af06ef4b9932f63361aed8aad140f'and H((P/'context/current-unit-analysis.json').read_bytes())==um['analysis.json']['sha256']
 cache=J(P/'context/cache-allowlist.json')['files'];lock={(x['name'],x['version']):x for x in tomllib.loads((P/'context/current-Cargo.lock').read_text())['package']};primary=tomllib.loads((P/'context/current-Cargo.toml').read_text());assert all(primary['dependencies'][n]['version']=='=0.31.1'for n in['anchor-lang','anchor-spl'])
 inventories=J(P/'source-inventory.json');by={};metadata=[]
 for r in inventories:
  name,version=r['name'],r['version'];key=(name,version);assert key not in by;by[key]=r;meta=J(P/'metadata'/f'{name}-{version}.json')['version'];raw=(P/r['archive']).read_bytes();assert H(raw)==r['archive_sha256']==meta['checksum']and len(raw)==meta['crate_size']
  with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz')as archive:
   files={}
   for member in archive.getmembers():
    path=PurePosixPath(member.name);assert not path.is_absolute()and'..'not in path.parts and path.parts[0]==name+'-'+version
    if member.isdir():continue
    assert member.isfile();rel=PurePosixPath(*path.parts[1:]).as_posix();assert rel not in files;b=archive.extractfile(member).read();row=r['files'][rel];assert row=={'sha256':H(b),'bytes':len(b),'archive_mode':member.mode,'retained_file':str(PurePosixPath('source')/name/version/rel)};assert(P/row['retained_file']).read_bytes()==b;files[rel]=row
  assert files==r['files'];md=tomllib.loads((P/r['files']['Cargo.toml']['retained_file']).read_text());assert md==r['package_manifest']and md['package']['name']==name and md['package']['version']==version
  assert md['package']['license']==meta['license']=='Apache-2.0';assert md['package']['repository']==meta['repository'];assert not r['license_files']
  metadata.append({'name':name,'version':version,'published_at':meta['created_at'],'updated_at':meta['updated_at'],'checksum':meta['checksum'],'repository':meta['repository'],'license':meta['license'],'yanked':meta['yanked'],'published_by':meta.get('published_by'),'trustpub_data':meta.get('trustpub_data'),'vcs':r['vcs'],'source_rust_files':sum(n.endswith('.rs')for n in files),'standalone_license_files':r['license_files']})
 assert len(by)==22
 for b in J(P/'cached-archive-bindings.json'):
  key=(b['name'],b['version']);r=by[key];meta=J(P/'metadata'/f'{key[0]}-{key[1]}.json')['version'];rel='registry/cache/index.crates.io-6f17d22bba15001f/'+key[0]+'-'+key[1]+'.crate';assert b['sha256']==r['archive_sha256']==meta['checksum']==lock[key]['checksum']==cache[rel]['sha256']and b['selected_lock_checksum']==b['metadata_checksum']==b['sha256']
 comparisons=J(P/'comparisons.json');assert len(comparisons)==10
 for c in comparisons:
  name=c['name'];a=by[name,'0.31.1']['files'];b=by[name,'0.31.2']['files'];assert c['added']==sorted(set(b)-set(a))==[]and c['removed']==sorted(set(a)-set(b))==[];changed=sorted(n for n in a if a[n]['sha256']!=b[n]['sha256']);assert c['changed']==changed
  rs={n for n in a if n.endswith('.rs')};assert rs=={n for n in b if n.endswith('.rs')}and c['rust_files0311']==c['rust_files0312']==len(rs);assert c['rust_changed']==[n for n in changed if n.endswith('.rs')];assert c['all_rust_source_byte_identical']==(not c['rust_changed'])
  expected_changes=['.cargo_vcs_info.json','Cargo.lock','Cargo.toml','Cargo.toml.orig']+(['src/lib.rs']if name=='anchor-attribute-program'else[]);assert changed==sorted(expected_changes)
  for n in changed:
   old=(P/a[n]['retained_file']).read_text();new=(P/b[n]['retained_file']).read_text();expected=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=f'{name}/0.31.1/{n}',tofile=f'{name}/0.31.2/{n}'));assert(P/'diffs'/name/(n+'.diff')).read_text()==expected
  oldmd=json.loads(json.dumps(by[name,'0.31.1']['package_manifest']));newmd=by[name,'0.31.2']['package_manifest'];oldmd['package']['version']='0.31.2';oldmd['package']['repository']='https://github.com/otter-sec/anchor'
  if name!='anchor-syn':assert oldmd['dependencies']['anchor-syn']['version']=='0.31.1';oldmd['dependencies']['anchor-syn']['version']='0.31.2'
  assert oldmd==newmd
 oldprog=(P/by['anchor-attribute-program','0.31.1']['files']['src/lib.rs']['retained_file']).read_text();newprog=(P/by['anchor-attribute-program','0.31.2']['files']['src/lib.rs']['retained_file']).read_text();assert oldprog.count('0.31.1')==3 and oldprog.replace('0.31.1','0.31.2')==newprog
 macro_names=sorted(c['name']for c in comparisons if c['name']!='anchor-syn');lang=by['anchor-lang','0.31.1']['package_manifest'];api_deps=J(P/'dependencies/anchor-lang-0.31.1.json')['dependencies'];reqs={n:next(x['req']for x in api_deps if x['crate_id']==n and x['kind']=='normal')for n in macro_names};assert all(v=='^0.31.1'for v in reqs.values())and all(lang['dependencies'][n]['version']=='0.31.1'for n in macro_names)
 current_versions={r['name']:r['version']for r in units['observed_registry_packages'].values()if r['name']in macro_names+['anchor-syn']};assert len(current_versions)==10 and all(v=='0.31.2'for v in current_versions.values())
 # Source locations below are descriptive exact-identifier witnesses, not macro execution.
 targets=[('anchor-attribute-error','0.31.1','src/lib.rs','pub fn error('),('anchor-attribute-error','0.31.1','src/lib.rs','fn create_error('),('anchor-syn','0.31.1','src/codegen/error.rs','pub fn generate('),('anchor-syn','0.31.1','src/codegen/accounts/constraints.rs','fn generate_constraint_owner('),('anchor-lang','0.31.1','src/lib.rs','macro_rules! require_gte'),('anchor-lang','0.31.1','src/error.rs','pub fn with_source('),('anchor-lang','0.31.1','src/error.rs','pub fn with_values(')]
 locations=[]
 for name,version,file,needle in targets:
  r=by[name,version]['files'][file];text=(P/r['retained_file']).read_text();assert text.count(needle)==1;at=text.index(needle);locations.append({'package':name,'version':version,'file':r['retained_file'],'source_sha256':r['sha256'],'line':text[:at].count('\n')+1,'identifier':needle,'macro_pair_file_identical':name!='anchor-lang'})
 return {'scope':'Official crate metadata and exact source comparison only; no compiler/macro expansion/runtime/target experiment','package_version_records':metadata,'macro_package_pairs':10,'rust_source_files_per_macro_version':sum(c['rust_files0311']for c in comparisons),'rust_files_byte_identical':sum(c['rust_files0311']-len(c['rust_changed'])for c in comparisons),'changed_rust_file':'anchor-attribute-program/src/lib.rs','changed_rust_content':'Only two doc/example version-tag URLs and cfg-gated interface deprecated since string 0.31.1->0.31.2; no functional macro implementation body difference found','normalized_manifest_only_changes':['package.version','package.repository','nine macro dependency anchor-syn version0.31.1->0.31.2'],'framework_exact_pins':{n:primary['dependencies'][n]['version']for n in['anchor-lang','anchor-spl']},'official_lang_normalized_macro_requirements':reqs,'observed_current_macro_versions':current_versions,'locations_relevant_to_error_origin_values_and_accounts':locations,'source_level_error_require_gte_ownership_or_serialization_fix_found':False,'transitive_resolutions_or_cargo_identity_can_still_differ':True,'historical_macro_graph_proved':False,'BPF_output_or_macro_expansion_equivalence_proved':False,'license_text_scope':'Apache-2.0 declarations retained; no standalone LICENSE/COPYING/NOTICE member exists in these22 archives','native_compiler_VM_target_or_source_executions':0}
if __name__=='__main__':
 d=analyze();(P/'analysis.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:d[k]for k in['macro_package_pairs','rust_source_files_per_macro_version','rust_files_byte_identical','changed_rust_content','source_level_error_require_gte_ownership_or_serialization_fix_found']},indent=2))

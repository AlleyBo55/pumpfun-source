"""Independent passive archive/metadata audit; no live network/native/source execution."""
from pathlib import Path,PurePosixPath
import collections,difflib,hashlib,io,json,subprocess,sys,tarfile,tomllib
P=Path(__file__).resolve().parent;R=P.parent/'anchor031-macro-version-audit';J=lambda p:json.loads(p.read_text());H=lambda b:hashlib.sha256(b).hexdigest();SEAL='d88372caef6c64996b49e5063af87dd52bd16f18d2575ec35c19d2b1cc6f11df'
def snap():return{str(f.relative_to(R)):H(f.read_bytes())for f in R.rglob('*')if f.is_file()}
before=snap();assert H((R/'manifest.json').read_bytes())==SEAL;manifest=J(R/'manifest.json');assert set(manifest)==set(before)-{'manifest.json','manifest.sha256'}
for n,row in manifest.items():assert H((R/n).read_bytes())==row['sha256']and(R/n).stat().st_size==row['bytes']
http=J(R/'metadata-http.json')+J(R/'additional-http.json');assert len(http)==34;roles=collections.Counter();api={};download=set()
for row in http:
 raw=(R/row['file']).read_bytes();assert H(raw)==row['sha256']and len(raw)==row['bytes']and row['status']==200 and row['url']==row['final_url']
 name=row['name'];version=row.get('version',row.get('requested_version'));url=row['url']
 if url.startswith('https://static.crates.io/'):
  assert url==f'https://static.crates.io/crates/{name}/{name}-{version}.crate';roles['archive']+=1;download.add((name,version))
 elif url.endswith('/dependencies'):
  assert url==f'https://crates.io/api/v1/crates/{name}/{version}/dependencies';roles['dependencies']+=1
 else:
  assert url==f'https://crates.io/api/v1/crates/{name}/{version}';d=json.loads(raw)['version'];assert d['crate']==name and d['num']==version;api[name,version]=d;roles['version']+=1
assert roles=={'archive':10,'dependencies':2,'version':22}
files={};metas={};vcs={}
for row in J(R/'source-inventory.json'):
 name,version=row['name'],row['version'];key=name,version;raw=(R/row['archive']).read_bytes();assert H(raw)==api[key]['checksum']==row['archive_sha256'];assert len(raw)==api[key]['crate_size']
 members={}
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz')as archive:
  for m in archive.getmembers():
   path=PurePosixPath(m.name);assert not path.is_absolute()and'..'not in path.parts and path.parts[0]==name+'-'+version
   if m.isdir():continue
   assert m.isfile();relative='/'.join(path.parts[1:]);assert relative not in members;b=archive.extractfile(m).read();members[relative]=b
   recorded=row['files'][relative];assert recorded['sha256']==H(b)and recorded['bytes']==len(b)and(R/recorded['retained_file']).read_bytes()==b
 assert set(members)==set(row['files']);files[key]=members;metas[key]=tomllib.loads(members['Cargo.toml'].decode());vcs[key]=json.loads(members['.cargo_vcs_info.json']);assert vcs[key]==row['vcs']
assert len(files)==22
pairs=[n for n,v in files if v=='0.31.2'];assert len(pairs)==10
rust_total=0;identical=0;source_changes=[];syn_edges=0
for name in pairs:
 a,b=files[name,'0.31.1'],files[name,'0.31.2'];assert set(a)==set(b)
 rust=[n for n in a if n.endswith('.rs')];rust_total+=len(rust);identical+=sum(a[n]==b[n]for n in rust)
 changed=[n for n in rust if a[n]!=b[n]];assert changed==(['src/lib.rs']if name=='anchor-attribute-program'else[])
 for n in changed:
  old=a[n].decode();new=b[n].decode();assert old.count('0.31.1')==3 and old.replace('0.31.1','0.31.2')==new
  source_changes.append({'name':name,'file':n,'literal_version_changes':3})
 md=json.loads(json.dumps(metas[name,'0.31.1']));newmd=metas[name,'0.31.2'];md['package']['version']='0.31.2';md['package']['repository']='https://github.com/otter-sec/anchor'
 if'anchor-syn'in md.get('dependencies',{}):syn_edges+=1;assert md['dependencies']['anchor-syn']['version']=='0.31.1';md['dependencies']['anchor-syn']['version']='0.31.2'
 else:assert name in['anchor-syn','anchor-derive-space']
 assert md==newmd
assert(rust_total,identical,syn_edges)==(66,65,8)
macro=[n for n in pairs if n!='anchor-syn'];lang=metas['anchor-lang','0.31.1'];deps=J(R/'dependencies/anchor-lang-0.31.1.json')['dependencies']
assert len(macro)==9
for name in macro:assert lang['dependencies'][name]['version']=='0.31.1'and next(x['req']for x in deps if x['crate_id']==name and x['kind']=='normal')=='^0.31.1'
for(name,version),md in api.items():
 if name not in pairs:continue
 assert not md['yanked']
 if version=='0.31.1':assert md['created_at'].startswith('2025-04-20T')and md['published_by']['login']=='solana-foundation-tech'and md['repository']=='https://github.com/coral-xyz/anchor'and vcs[name,version]['git']['sha1']=='47284f8f0b9844c6b83234aa90f556bad00e12ed'
 else:assert md['created_at'].startswith('2026-09-14T')and md['published_by']is None and md['repository']=='https://github.com/otter-sec/anchor'and md['trustpub_data']=={'provider':'github','repository':'otter-sec/anchor','run_id':'34869152022','sha':'6f152a48f266eb187b2a3cc22f1cc7d1ae5bdbd3'}and vcs[name,version]['git']['sha1']==md['trustpub_data']['sha']
lock={(x['name'],x['version']):x for x in tomllib.loads((R/'context/current-Cargo.lock').read_text())['package']};cache=J(R/'context/cache-allowlist.json')['files'];cached=J(R/'cached-archive-bindings.json');assert len(cached)==12 and not(download&{(r['name'],r['version'])for r in cached})
for row in cached:
 key=row['name'],row['version'];rel='registry/cache/index.crates.io-6f17d22bba15001f/'+row['name']+'-'+row['version']+'.crate';assert row['sha256']==H((R/row['file']).read_bytes())==lock[key]['checksum']==api[key]['checksum']==cache[rel]['sha256']
pre=(R/'analyze.pre-completion.py').read_text();now=(R/'analyze.py').read_text();derivation=J(R/'analyzer-completion-derivation.json');assert len(derivation['literal_replacements'])==5 and H(pre.encode())==derivation['original_sha256']and H(now.encode())==derivation['completed_sha256']
for old,new in derivation['literal_replacements']:assert pre.count(old)==1;pre=pre.replace(old,new)
assert pre==now
failures=J(R/'completion-preparation-errors.json');assert'Author summary; not raw receipt'in failures['scope']and all(k in failures for k in['observed_initial_completion_run','second_observed_completion_run','third_observed_completion_run'])
child=subprocess.run([sys.executable,'-B',str(R/'verify.py'),'--expected-seal',SEAL],cwd=R,capture_output=True);(P/'portable-verify.stdout').write_bytes(child.stdout);(P/'portable-verify.stderr').write_bytes(child.stderr);assert child.returncode==0 and snap()==before
result={'state':'PASS_PASSIVE_ANCHOR031_MACRO_SOURCE_AND_REGISTRY_WITNESS','publication_seal':SEAL,'archives':22,'HTTP_bodies':34,'HTTP_roles':dict(roles),'cached_archives_checksum_lock_cache_API_equal':12,'macro_syn_pairs':10,'Rustfiles_per_version':66,'Rustfiles_identical':65,'only_Rust_changes':source_changes,'macro_to_syn_edges':8,'derive_space_has_no_syn_edge':True,'lang_normal_macro_caret31_1_edges':9,'publisher_VCS_fields_bound_to_actual_archive_bytes':True,'completion_exact_literal_replacements':5,'three_prior_failures_authored_not_raw':True,'portable_verify_exit':0,'packet_unchanged':True,'network_compiler_macro_VM_SDK_source_or_original_decoder_executions':0,'historical_compiled_output_or_macro_expansion_proof':False,'limits':['Registry publisher/VCS metadata does not independently authenticate GitHub run/commit content','No macro execution or compiled-output equivalence follows source-negative comparison','Package identities/transitive resolutions/Cargo metadata/order remain distinct','Date mapping to historical deployment remains separate unproved evidence']}
(P/'review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

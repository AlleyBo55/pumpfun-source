"""Passive Cargo metadata/source-consumer review. No builds, probes or native execution."""
from pathlib import Path
import hashlib,json,tomllib,tarfile,io
P=Path(__file__).resolve().parent;J=lambda n:json.loads((P/n).read_text());H=lambda b:hashlib.sha256(b).hexdigest()
def analyze():
 publication=(P/'controls/unit-publication-manifest.json').read_bytes();assert H(publication)=='03ac2ad0eabbd58d97c034640357262572422a6044f04206303ffe586f5a5bb9';publication=json.loads(publication)
 raw=(P/'controls/unit-record-manifest.json').read_bytes();assert H(raw)=='9760c7c71676eefc98c023f1eea876c75f1af06ef4b9932f63361aed8aad140f';assert H(raw)==publication['record/manifest.json']['sha256'];record=json.loads(raw)
 for binding in J('input-bindings.json'):
  b=(P/binding['file']).read_bytes();assert H(b)==binding['sha256']and len(b)==binding['bytes'];auth=binding['authentication']
  if isinstance(auth,dict)and'unit_record_manifest_key'in auth:
   r=record[auth['unit_record_manifest_key']];assert H(b)==r['sha256']and len(b)==r['bytes']
 a=J('unit/analysis.json');assert len(a['units'])==239 and len(a['observed_registry_packages'])==176 and len(a['build_script_directives'])==26
 for u in a['units']:
  raw=J('unit/target-metadata/'+u['file']);assert raw==u['fingerprint_fields']
 cc=next(u for u in a['units']if u['package_directory_label']=='cc');assert cc['file']=='release/.fingerprint/cc-c6c3546ecf3e2f7f/lib-cc.json'and cc['domain']=='host-layout'and cc['features']==[]
 consumers=[{'consumer_file':u['file'],'consumer_domain':u['domain'],'kind':u['kind'],'features':u['features'],'source_versions':u['source_versions'],'edge':d}for u in a['units']for d in u['fingerprint_fields']['deps']if d[1]=='cc'];assert len(consumers)==1
 edge=consumers[0]['edge'];assert edge==[17558417070209665034,'cc',False,16299391925053461121]
 raw=(P/'current/release/.fingerprint/cc-c6c3546ecf3e2f7f/lib-cc').read_bytes();assert raw==b'8192ae13991233e2'and int.from_bytes(bytes.fromhex(raw.decode()),'little')==edge[3]
 # Equality above is literal byte/LE serialization, not a -Cmetadata or complete Cargo-graph proof.
 lock={(r['name'],r['version']):r for r in tomllib.loads((P/'unit/context/Cargo.lock').read_text())['package']};cache=J('unit/context/cache-allowlist.json')['files'];archives={}
 for f in sorted((P/'archives').glob('*.crate')):
  name,version=f.stem.rsplit('-',1);b=f.read_bytes();digest=H(b);assert digest==lock[name,version]['checksum']==cache[f'registry/cache/index.crates.io-6f17d22bba15001f/{f.name}']['sha256'];t=tarfile.open(fileobj=io.BytesIO(b),mode='r:gz');files={m.name:t.extractfile(m).read()for m in t.getmembers()if m.isfile()};archives[name,version]=files
  for retained in(P/'source'/name/version).rglob('*'):
   if retained.is_file():assert retained.read_bytes()==files[name+'-'+version+'/'+str(retained.relative_to(P/'source'/name/version))]
 observed_manifest_edges=[]
 def scan(d,path,package):
  if not isinstance(d,dict):return
  for k,v in d.items():
   if k=='cc'and isinstance(v,dict)and any(x in path for x in['dependencies','build-dependencies','dev-dependencies']):observed_manifest_edges.append({'package':package,'table_path':path,'dependency':v})
   scan(v,path+[k],package)
 for root,r in a['observed_registry_packages'].items():
  b=(P/'unit/registry-manifests'/root/'Cargo.toml').read_bytes();assert H(b)==r['source_manifest_sha256'];scan(tomllib.loads(b.decode()),[],{'name':r['name'],'version':r['version']})
 assert observed_manifest_edges==[{'package':{'name':'blake3','version':'1.8.2'},'table_path':['build-dependencies'],'dependency':{'version':'1.1.12'}}]
 blake=next(u for u in a['units']if u['package_directory_label']=='blake3'and u['kind']=='build-script');assert blake['features']==['default','std','traits-preview']
 build_source=(P/'source/blake3/1.8.2/build.rs').read_bytes();blake_sourcepath=a['depinfo'][blake['source_depinfo_files'][0]]['source_paths'][0];capture=J('unit/capture.json');assert H(build_source)==capture['source_path_bindings'][blake_sourcepath]['sha256']
 for file in[cc['source_depinfo_files'][0],blake['source_depinfo_files'][0],next(u for u in a['units']if u['package_directory_label']=='blake3'and u['kind']=='library')['source_depinfo_files'][0]]:assert H((P/'unit/target-metadata'/file).read_bytes())==record['target-metadata/'+file]['sha256']
 run=J('unit/target-metadata/sbf-solana-solana/release/.fingerprint/blake3-d2167f6e743debda/run-build-script-build-script-build.json');env=[r['RerunIfEnvChanged']for r in run['local']if'RerunIfEnvChanged'in r];ccenv=next(r for r in env if r['var']=='CC');assert ccenv['val']==J('current-clang-path-observation.json')['requested_path']and next(r for r in env if r['var']=='CFLAGS')['val']is None
 outputs=[]
 for name,row in a['build_script_directives'].items():
  text=(P/'unit/target-metadata'/name).read_text();directives=[line for line in text.splitlines()if line.startswith(('cargo:','cargo::'))];assert directives==row['directives'];outputs.append({'path':name,'explicit_link_directives':[d for d in directives if d.startswith(('cargo:rustc-link-','cargo::rustc-link-'))]})
 assert not any(r['explicit_link_directives']for r in outputs)
 direct_blake=[]
 for u in a['units']:
  for dep in u['fingerprint_fields']['deps']:
   if dep[1]=='blake3':
    assert len(u['source_versions'])==1;s=u['source_versions'][0];md=tomllib.loads((P/'source'/s['name']/s['version']/'Cargo.toml').read_text());decl=[]
    def seek(d,path=[]):
     if not isinstance(d,dict):return
     for k,v in d.items():
      if k=='blake3'and isinstance(v,dict):decl.append({'table_path':path,'dependency':v})
      seek(v,path+[k])
    seek(md);direct_blake.append({'consumer_file':u['file'],'source_version':s,'features':u['features'],'fingerprint_edge':dep,'manifest_declarations':decl})
 assert len(direct_blake)==3
 return {'scope':'Current controlled build metadata and authenticated crate-source data only; not historical linked-code proof','unit_counts':{'fingerprints':239,'observed_registry_manifests':176,'build_outputs':26},'cc_unit':cc,'immediate_cc_consumers':consumers,'cc_dependency_name_edge_matches_current_fingerprint_LE_bytes':True,'cc_dep_edge_value_is_rustc_C_metadata_claim':False,'observed_manifest_cc_edges':observed_manifest_edges,'allowed_cc_version_constraint':'>=1.1.12,<2.0.0 under ordinary Cargo caret1.x semantics; older concrete published choice not selected or authenticated here','blake3_build_features':blake['features'],'blake3_direct_library_consumers':direct_blake,'recorded_CC_and_environment':env,'current_clang_resolution':J('current-clang-path-observation.json'),'build_output_link_census':outputs,'native_CC_invocation_proven':False,'native_CC_output_link_proven':False,'cc_is_host_layout_library_not_SBF_unit':True,'conditional_source_path_inference':'If TARGET=sbf-solana-solana and recorded PURE/NEON absent reflect actual run, blake3 main architecture branches for x86/arm/wasm do not call cc compile; source calls CC/CFLAGS rerun reporting unconditionally. This is static conditional inference, not execution trace.','current_registry_graph_temporal_exclusion':'Root owns independent176-registry/deploymentdate witness; this packet doesnotauthenticate temporalquery orruleoutprivate/vendor/prerelease sources.','whole_original_graph_or_binary_identity_proven':False,'new_compiler_VM_target_network_execution':0}
if __name__=='__main__':
 d=analyze();(P/'analysis.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'immediate_cc_consumers':len(d['immediate_cc_consumers']),'manifest_cc_edges':len(d['observed_manifest_cc_edges']),'direct_blake3_consumers':len(d['blake3_direct_library_consumers']),'CC_path':d['current_clang_resolution']['resolved_path'],'native_CC_invocation_proven':False},indent=2))

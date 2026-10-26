"""Passive artifact and Cargo/crate-source data replay; no tool, build or network invocation."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json
from analyze import analyze
P=Path(__file__).resolve().parent;H=lambda b:hashlib.sha256(b).hexdigest()
def verify(seal):
 assert __debug__,'Use Python without -O'
 raw=(P/'manifest.json').read_bytes();assert H(raw)==seal==(P/'manifest.sha256').read_text().strip();m=json.loads(raw)
 assert not any(f.is_symlink()for f in P.rglob('*'))
 assert set(m)|{'manifest.json','manifest.sha256'}=={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()}
 for n,r in m.items():
  path=PurePosixPath(n);assert not path.is_absolute()and'..'not in path.parts;b=(P/n).read_bytes();assert H(b)==r['sha256']and len(b)==r['bytes'],n
 d=analyze();assert d==json.loads((P/'analysis.json').read_text())
 assert d['unit_counts']=={'fingerprints':239,'observed_registry_manifests':176,'build_outputs':26}
 assert len(d['immediate_cc_consumers'])==len(d['observed_manifest_cc_edges'])==1 and len(d['blake3_direct_library_consumers'])==3
 assert d['immediate_cc_consumers'][0]['consumer_file']=='release/.fingerprint/blake3-6d23e45661a2bb6b/build-script-build-script-build.json'
 assert d['cc_unit']['source_versions']==[{'name':'cc','version':'1.10.0','archive_sha256':'86e055fa6e3e40ad6187ba25b6855eeb635d5271f8e0f0e1e9a5826b8d75bea0','source_manifest_sha256':'e8486afb97f4debf50ed5e80f8a5db3e36b3b4bd899db0051bb9fcbd9c5706d5'}]
 assert d['current_clang_resolution']['resolved_path']=='/Users/shawwalters/.cache/solana/v1.52/platform-tools/llvm/bin/clang-20'and d['current_clang_resolution']['sha256']=='3c5752d43548edbde66dcd61de941bfa30b4d175e32d3b301bd2de015de75b39'
 src=(P/'source/blake3/1.8.2/build.rs').read_text()
 for fragment in['fn new_build() -> cc::Build {','let mut build = cc::Build::new();','if is_x86_64() || is_x86_32() {','if (is_arm() && is_neon())','if is_wasm32() && is_wasm32_simd() {','println!("cargo:rerun-if-env-changed=CC");','println!("cargo:rerun-if-env-changed=CFLAGS");']:assert fragment in src
 assert d['cc_dep_edge_value_is_rustc_C_metadata_claim']is False and d['native_CC_invocation_proven']is False and d['native_CC_output_link_proven']is False and d['whole_original_graph_or_binary_identity_proven']is False and d['new_compiler_VM_target_network_execution']==0
 print('PASS:239fingerprints/176manifest census;onecc nameedge→hostblake3buildscript;cc>=1.1.12<2range;CCpathrecorded,currentclang20v1.52;26outputsnoexplicitlinkdirectives. No nativeinvocation/output/historicalgraph claim.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--expected-seal',required=True);a=p.parse_args();verify(a.expected_seal)

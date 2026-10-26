"""Passive official metadata/archive/source comparison replay. No network or native code."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,datetime
from analyze import analyze
P=Path(__file__).resolve().parent;H=lambda b:hashlib.sha256(b).hexdigest();J=lambda n:json.loads((P/n).read_text())
def verify(seal):
 assert __debug__,'Use Python without -O'
 raw=(P/'manifest.json').read_bytes();assert H(raw)==seal==(P/'manifest.sha256').read_text().strip();m=json.loads(raw)
 assert not any(f.is_symlink()for f in P.rglob('*'))
 assert set(m)|{'manifest.json','manifest.sha256'}=={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()}
 for n,r in m.items():
  rel=PurePosixPath(n);assert not rel.is_absolute()and'..'not in rel.parts
  b=(P/n).read_bytes();assert H(b)==r['sha256']and len(b)==r['bytes'],n
 d=analyze();assert d==J('analysis.json')
 assert(d['macro_package_pairs'],d['rust_source_files_per_macro_version'],d['rust_files_byte_identical'])==(10,66,65)
 assert not d['source_level_error_require_gte_ownership_or_serialization_fix_found']and d['transitive_resolutions_or_cargo_identity_can_still_differ']is True
 assert not d['historical_macro_graph_proved']and not d['BPF_output_or_macro_expansion_equivalence_proved']and d['native_compiler_VM_target_or_source_executions']==0
 rows=d['package_version_records'];macro=[r for r in rows if r['name']not in['anchor-lang','anchor-spl']];assert len(macro)==20
 for r in macro:
  if r['version']=='0.31.1':
   assert r['published_at'].startswith('2025-04-20T')and r['repository']=='https://github.com/coral-xyz/anchor'and r['published_by']['login']=='solana-foundation-tech'and r['trustpub_data']is None
   assert r['vcs']['git']['sha1']=='47284f8f0b9844c6b83234aa90f556bad00e12ed'
  else:
   assert r['version']=='0.31.2'and r['published_at'].startswith('2026-09-14T')and r['repository']=='https://github.com/otter-sec/anchor'and r['published_by']is None
   assert r['trustpub_data']=={'provider':'github','repository':'otter-sec/anchor','run_id':'34869152022','sha':'6f152a48f266eb187b2a3cc22f1cc7d1ae5bdbd3'}and r['vcs']['git']['sha1']==r['trustpub_data']['sha']
  assert r['yanked']is False
 inventories=J('source-inventory.json');by={(r['name'],r['version']):r for r in inventories}
 assert sum('anchor-syn'in by[(r['name'],'0.31.1')]['package_manifest'].get('dependencies',{})for r in J('comparisons.json'))==8
 for r in J('comparisons.json'):
  assert r['rust_added']==r['rust_removed']==[]
  if r['name']=='anchor-attribute-program':assert r['rust_changed']==['src/lib.rs']
  else:assert r['rust_changed']==[]
 for filename,needles in[
  ('source/anchor-attribute-error/0.31.1/src/lib.rs',['filename: file!(),','line: line!()','error_name: #error_code.name(),','error_code_number: #error_code.into(),','error_msg: #error_code.to_string(),','compared_values: None']),
  ('source/anchor-lang/0.31.1/src/lib.rs',['macro_rules! require_gte {','if $value1 < $value2 {','with_values(($value1, $value2))']),
  ('source/anchor-lang/0.31.1/src/error.rs',['pub fn with_values(mut self, values: (impl ToString, impl ToString))','values.0.to_string(),','values.1.to_string(),']),
  ('source/anchor-syn/0.31.1/src/codegen/accounts/constraints.rs',['pub fn generate_constraint_owner(','if my_owner != &owner_address {'])]:
  text=(P/filename).read_text()
  for needle in needles:assert needle in text
 prior=(P/'analyze.pre-completion.py').read_text();current=(P/'analyze.py').read_text();derivation=J('analyzer-completion-derivation.json');assert H(prior.encode())==derivation['original_sha256']and H(current.encode())==derivation['completed_sha256']
 for old,new in derivation['literal_replacements']:assert prior.count(old)==1;prior=prior.replace(old,new)
 assert prior==current
 timeline=J('publisher-timeline.json');assert timeline=={'scope':'Retained official version API and archive VCS fields, not independent GitHub-run or historical-deployment authentication','macro_versions':[{'version':v,'earliest_published':min(r['published_at']for r in macro if r['version']==v),'latest_published':max(r['published_at']for r in macro if r['version']==v),'repository':next(r['repository']for r in macro if r['version']==v),'vcs_sha':next(r['vcs']['git']['sha1']for r in macro if r['version']==v),'packages':10}for v in['0.31.1','0.31.2']]}
 print('PASS:10 macro/syn pairs;22 official-checksummed archives;65/66Rustfilesexact; only3program-version string changes;8macro->syn dependency bumps. Historical graph/Cargo metadata/compiled output equivalence remain unproved.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--expected-seal',required=True);a=p.parse_args();verify(a.expected_seal)

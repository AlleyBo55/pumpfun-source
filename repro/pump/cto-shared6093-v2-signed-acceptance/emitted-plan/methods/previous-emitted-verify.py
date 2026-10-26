"""Standard-library saved-artifact verification only; no target execution."""
from pathlib import Path
import argparse,json,hashlib
from analyze import P,H,analyze,Elf
from render import render
J=lambda p:json.loads(p.read_text())
def main():
 a=argparse.ArgumentParser();a.add_argument('--work-root',type=Path,default=P.parent);base=a.parse_args().work_root
 m=J(P/'manifest.json');assert set(m)=={str(q.relative_to(P))for q in P.rglob('*')if q.is_file()and q.name!='manifest.json'and '__pycache__'not in q.parts}
 for n,v in m.items():b=(P/n).read_bytes();assert H(b)==v['sha256']and len(b)==v['bytes'],n
 for n,v in J(P/'input-references.json').items():b=(base/n).read_bytes();assert H(b)==v['sha256']and len(b)==v['bytes'],n
 original=J(P/'original-copy-bindings.json');assert H((P/'original-control/manifest.json').read_bytes())==original['manifest_sha256']
 for n,v in original['files'].items():
  assert J(P/'original-control/manifest.json')[n]==v;b=(P/'original-control'/n).read_bytes();assert H(b)==v['sha256']and len(b)==v['bytes']
 assert len(list((P/'original-control').glob('*.asm')))==35
 proof=analyze(base);assert proof==J(P/'proof.json');b=(base/'pumpfun-source/work/cto-wallet-build-01/analysis/candidate.so').read_bytes()
 for f in proof['functions']:assert(P/(str(f['start'])+'.asm')).read_text()==render(b,f['start'],f['end'])
 assert all(x['normalized_equal']and x['callee_names_equal']for x in proof['selected71ec_comparisons'])
 r=J(P/'controller-result.json');assert r['state']=='requires-cache-review'and r['helper_exit']==r['build_sbf_aggregate_exit']==0
 assert r['compiler_child_exit']is None and r['strip_child_exit']is None and r['source_unchanged']and r['private_cache_existing_unchanged']
 assert not r['backend_error_lines']and not r['stack_llvm_diagnostics'];assert r['tool_sdk_before']==r['tool_sdk_after']
 assert r['source_after']==J(P/'source-control/source-proposed.json');assert len(r['source_after'])==37
 before=J(P/'source-control/source-baseline.json');after=J(P/'source-control/source-proposed.json');assert[n for n in before if before[n]!=after[n]]==['programs/pump/src/admin_cto.rs']
 assert after['programs/pump/src/admin_cto.rs']=='d6b4937f03a62c013baca8d93bf1be72f035681e17a6a86e19df204c57cce457'
 print('PASS: pinned terminal candidate+symbols;23complete candidate bodies/calls+anchors;35unchanged admitted original text controls;source37/receipts;parser+wrapper preservation;no new original decode/build/VM')
if __name__=='__main__':main()

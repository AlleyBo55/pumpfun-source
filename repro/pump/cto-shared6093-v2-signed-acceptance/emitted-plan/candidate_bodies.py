"""UNEXECUTED candidate-only named-body review; no recursive callee expansion."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,sys
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'methods'))
from reference_elf import Elf
from render import render
H=lambda b:hashlib.sha256(b).hexdigest()
def normalized_name(n):return re.sub(r'17h[0-9a-f]{16}E$','17h<HASH>E',n)
def main():
 a=argparse.ArgumentParser();a.add_argument('--expected-plan-seal',required=True);a.add_argument('--candidate',type=Path,required=True);a.add_argument('--symbols',type=Path,required=True);a.add_argument('--source-root',type=Path,required=True);a.add_argument('--output',type=Path,required=True);args=a.parse_args()
 assert H((P/'manifest.json').read_bytes())==args.expected_plan_seal and not args.output.exists()
 sources=json.loads((P/'build-plan-source-proposed.json').read_text());assert len(sources)==37
 for name,h in sources.items():assert H((args.source_root/name).read_bytes())==h
 cb=args.candidate.read_bytes();ub=args.symbols.read_bytes();c,u=Elf(cb),Elf(ub)
 assert c.by_name['.text']['address']==c.by_name['.text']['offset']
 prior=json.loads((P/'methods/previous-emitted-proof.json').read_text());names={normalized_name(n)for f in prior['functions']for n in f['names']};selected=[];allsyms={}
 for s in u.symbols:
  if s['type']==2 and s['size']:allsyms.setdefault(s['start'],[]).append(s)
 for start,ss in sorted(allsyms.items()):
  if not any(normalized_name(s['name'])in names or any(name in s['name']for name in ['collect_wallet_creator_fee','shared_token_raw_amount','shared_token_frozen'])for s in ss):continue
  assert len({s['size']for s in ss})==1;size=ss[0]['size'];assert c.at(start,size)==u.at(start,size)
  f=c.function(start,size,[s['name']for s in ss]);f['code_hex']=c.at(start,size).hex()
  for call in f['direct_calls']:call['actual_named_callee']=[s['name']for s in allsyms.get(call['target'],[])]
  selected.append(f)
 assert any('admin_cto7execute'in n for f in selected for n in f['names'])
 assert any('try_accounts'in n for f in selected for n in f['names'])
 assert any('__global9admin_cto'in n for f in selected for n in f['names'])
 seen={normalized_name(n)for f in selected for n in f['names']};missing=sorted(names-seen)
 args.output.mkdir(parents=True)
 for f in selected:(args.output/(str(f['start'])+'.asm')).write_text(render(cb,f['start'],f['end']))
 proof={'scope':'Existing23 logical-name allowlist plus collector and two shared-only helper names (if emitted);  candidate-only complete bodies/calls and existing bounded data previews. No recursive candidate/original callee expansion.','candidate_sha256':H(cb),'symbols_sha256':H(ub),'source37':sources,'functions':selected,'prior_function_names_absent_or_renamed':missing,'collector_named_body_present':any('collect_wallet_creator_fee'in n for f in selected for n in f['names']),'semantic_equivalence':None,'shared6093_composed':'PARTIAL_GUARDS_ZERO_GATES_ONLY_ABI_EFFECTS_UNPROVED','original_controls':'Only retained35 admitted text bodies, unchanged and hash-bound; not reparsed from original capture','manual_review_required':['Trace both independent shared empty-safe helper boundaries and actual sharedA/B call/branch order','A two caller empty reads, frozen then conditionalraw, owning6093 and frozenzero skipAMM','B raw then frozen, owning6093; empty/frozenzero/unfrozenzero skipATA/payout','No caller/helper presence-only proof; inspect actual successor CFG and data/control dependencies','Helper may inline or disappear; do not assume old addresses or force compiler attributes','Locate caller ATA/V/helper-return/SomeClock/event/AMM sequence and named callees','Check actual helper ownerFees6050→executablelogNone→fresh quote compare and native/token branches','Trace actual conditional branch destinations and owning error/drop calls, not a presence-only search','Verify zero/rent logs, source/postbalance saturation and source/destination rent data_len uses','Retain existing6019/6091/unique6092 proof only after emitted inspection','Compare parser/wrapper normalized hashes AND actual named callees against both71ec andd75 controls','Keep data-pointee extents, header/alias, natural source origins, ABI/cleanup, indirect calls, transitive behavior andshared6093 open']}
 (args.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print('CANDIDATE BODY RECORDS',len(selected),'manual review remains required')
if __name__=='__main__':main()

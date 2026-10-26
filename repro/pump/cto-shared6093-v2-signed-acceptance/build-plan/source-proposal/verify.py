"""Pure retained-source/proof verification; no compiler/VM/original decoder."""
from pathlib import Path,PurePosixPath
import hashlib,json,re
from compose import compose,REL
P=Path(__file__).resolve().parent;J=lambda p:json.loads(p.read_text());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 assert __debug__
 manifest=J(P/'manifest.json');assert set(manifest)=={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()}-{'manifest.json','manifest.sha256'}
 for n,r in manifest.items():
  rel=PurePosixPath(n);assert not rel.is_absolute()and'..'not in rel.parts;f=P/n;assert not f.is_symlink()and f.stat().st_size==r['bytes']and H(f)==r['sha256']
 assert H(P/'saved-oracle-review/manifest.json')=='4b250110db04a9cdf808286cacd45860df437bc183b882ccb2783122626b5a63'
 assert H(P/'admitted-fieldmap/manifest.json')=='c812166749cde8a0a41d2b67f69eb99ae735493949944ee9decab4664cb49370'
 for folder in ['saved-oracle-review','admitted-fieldmap']:
  for n,r in J(P/folder/'manifest.json').items():assert H(P/folder/n)==r['sha256']and(P/folder/n).stat().st_size==r['bytes']
 before=J(P/'source-before.json');after=J(P/'source-after.json');assert len(before)==len(after)==37 and set(before)==set(after)
 assert[n for n in before if before[n]!=after[n]]==[REL]and H(P/'baseline-admin_cto.rs')==before[REL]=='5499f2b14a7ad21ce1a4e5144882230d7bb668fce24fb735803fc78285f0f3a3'
 assert after[REL]=='950d6ec8c07072a3305c905509018f95b40d53e9ab25a4c1bda96b42c2a2fe58'
 assert{str(f.relative_to(P/'source')):H(f)for f in(P/'source').rglob('*')if f.is_file()}==after
 new,patch=compose();assert(P/'source'/REL).read_text()==new and(P/'proposal.patch').read_text()==patch
 old=(P/'baseline-admin_cto.rs').read_text();assert new[new.index("fn collect_wallet_creator_fee<'info>"):]==old[old.index("fn collect_wallet_creator_fee<'info>"):]
 assert new.count('PumpError::CtoSharedVaultFrozen')==2
 assert H(P/'superseded-proposal-manifest.json')=='3a231a46a6321b28c870de3c3318807a6d198fc36156bdde6098aca951a9582a'
 assert 'fn shared_token_raw_amount(a:&AccountInfo)->Result<u64>{if a.data_is_empty(){return Ok(0);}token_raw_amount(a)}'in new
 assert 'fn shared_token_frozen(a:&AccountInfo)->Result<bool>{if a.data_is_empty(){return Ok(false);}token_frozen(a)}'in new
 witness=J(P/'stable-6-counterexample.json')['row'];assert witness['case']['name']=='stable-6'and witness['original']['before']['creator_vault_quote_token_account']is None and witness['original']['error']is None and witness['candidate']['error']is None
 for filename,anchors in [('169712.asm',['169736:', 'CALL 1715000','169744:', '->169976','169976:', 'u64[r6+0]=2','169984:', 'u64[r6+8]=0']),('169240.asm',['169264:', 'CALL 1715000','169272:', '->169504','169504:', 'u64[r6+0]=2','169512:', 'u8[r6+8]=0'])]:
  text=(P/'admitted-fieldmap/admitted-original-control'/filename).read_text()
  for anchor in anchors:assert anchor in text
 first=new.index('let shared_amm_frozen_zero=');cpi=new.index('if shared&&holder&&!shared_amm_frozen_zero');second=new.index('let (rent,amount,shared_source_frozen)=')
 assert first<cpi<new.index('let wallet=')<second
 a=new[first:cpi];assert a.index('data_is_empty()')<a.index('token_frozen(')<a.index('token_raw_amount(')<a.index('PumpError::CtoSharedVaultFrozen')
 assert a.count('data_is_empty()')==1 and new[cpi:new.index('let wallet=')].count('data_is_empty()')==1
 b=new[second:new.index('if !shared_source_frozen&&amount>0')];assert b.index('let amount=shared_token_raw_amount(')<b.index('let frozen=shared_token_frozen(')<b.index('PumpError::CtoSharedVaultFrozen')
 assert b.index('Rent::get()?')<b.index('}else{')and b[b.index('}else{'):].count('Rent::get()?')==0
 assert new.count('error!(PumpError::CtoCreatorAccountNotWritable)')==old.count('error!(PumpError::CtoCreatorAccountNotWritable)')==1
 # Exact two substitutions preserve all unrelated text, owning errors, CPI/payout bodies and existing caller/helper sequence.
 stripped=re.sub(r'//[^\n]*|"(?:\\.|[^"\\])*"','',new);stack=[];close={')':'(',']':'[','}':'{'}
 for c in stripped:
  if c in'([{':stack.append(c)
  elif c in')]}':assert stack and stack.pop()==close[c]
 assert not stack
 status=J(P/'scope.json');assert status['built']is False and status['applied']is False and status['full_shared_composition_proven']is False and status['original_addressed_call_ABI_or_effect_closure']is False
 print('PASS PURE SOURCE PROPOSAL:37inputs,onlyCTOchanged;2orderedguards,zero-routegates;fullsharedABI/effects remainopen;no compiler/runtime/originaldecode.')
if __name__=='__main__':verify()

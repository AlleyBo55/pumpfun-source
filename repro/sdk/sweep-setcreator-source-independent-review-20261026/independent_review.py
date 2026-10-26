"""Independent stdlib data checks; does not import packet Python or SDK JS."""
from pathlib import Path
import argparse,hashlib,io,json,re,tarfile,base64
H=lambda b:hashlib.sha256(b).hexdigest()
def compact(s):return re.sub(r'\s+','',s)
def flatten(xs):
 out=[]
 for x in xs:
  if 'accounts'in x:out+=flatten(x['accounts'])
  else:out.append({'key':re.sub(r'_([a-z0-9])',lambda m:m[1].upper(),x['name']),'name':x['name'],'signer':x.get('signer',False),'writable':x.get('writable',False),'optional':x.get('optional',False),'address':x.get('address'),'pda':x.get('pda'),'relations':x.get('relations',[])})
 return out
def review(P,expected):
 J=lambda n:json.loads((P/n).read_bytes())
 assert H((P/'manifest.json').read_bytes())==expected
 manifest=J('manifest.json');actual={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()};assert actual==set(manifest)|{'manifest.json','manifest.sha256'};assert not any(f.is_symlink()for f in P.rglob('*'))
 for name,r in manifest.items():assert H((P/name).read_bytes())==r['sha256']and(P/name).stat().st_size==r['bytes']
 assert H((P/'controls/MANIFEST.json').read_bytes())=='a20815957ffd0f261737ee2ea20850f66d94b239d0379f2cc4caaf3e577376bb'
 original=J('controls/MANIFEST.json')['files']
 for n,path in [('sdk-matrix.json','controls/sdk-matrix.json'),('ts_static.py','ts_static.py')]:assert H((P/path).read_bytes())==original[n]['sha256']
 assert H((P/'controls/prior-record-manifest.json').read_bytes())=='33e756fc21ac913ba7455e3d1391900fbbe038180f8c593b7d542b8b0295ce7a'
 assert H((P/'archive-bindings.json').read_bytes())==J('controls/prior-record-manifest.json')['archive-bindings.json']['sha256']
 archives={}
 for row in J('archive-bindings.json'):
  b=(P/row['file']).read_bytes();assert H(b)==row['sha256']and hashlib.sha1(b).hexdigest()==row['sha1']and len(b)==row['bytes']and 'sha512-'+base64.b64encode(hashlib.sha512(b).digest()).decode()==row['integrity'];t=tarfile.open(fileobj=io.BytesIO(b));assert len({m.name for m in t})==len(t.getmembers());archives[row['file']]=t
 for n,r in J('source-bindings.json').items():
  m=archives[r['archive']].getmember(r['member']);assert m.isfile();b=archives[r['archive']].extractfile(m).read();assert b==(P/n).read_bytes()and H(b)==r['sha256']and len(b)==r['bytes']
 matrix=J('controls/sdk-matrix.json');prior={r['id']:r for r in matrix['routes']if r['unresolved_account_spreads_or_variables']};assert len(prior)==25
 analysis=J('analysis.json');rows=analysis['expanded_sites'];assert len(rows)==8;checked=[]
 for row in rows:
  r=prior[row['site_id']];s=(P/row['source_path']).read_text();assert H(s.encode())==r['source_sha256'];builder=r['source_builder_slice'];assert s.count(builder)==1
  if r['source_file']=='package/src/sdk.ts':key='pump:curve:'+r['method_name'];program='pump'
  else:key=r['package']+':'+r['method_name'];program='pump_amm'
  body=analysis['excerpts'][key]['source'];assert s.count(body)==1 and builder in body and H(body.encode())==row['method_sha256'];assert row['method_line']==analysis['excerpts'][key]['line']
  idl=J('sources/pump/package/src/idl/'+program+'.json');ix=next(x for x in idl['instructions']if program+':'+x['name']==row['instruction']);assert flatten(ix['accounts'])==row['idl_order']
  method=r['method_name'];mode='accountsStrict'if program=='pump_amm'and method!='setCoinCreator'else'accountsPartial';assert row['mode']==mode and r['builder_chain'][0]['method']==mode and '.'+mode+'('in compact(body);assert r['literal_anchor_method']==re.sub(r'_([a-z])',lambda m:m[1].upper(),ix['name'])
  assert len(r['unresolved_account_spreads_or_variables'])==1;assert compact(r['unresolved_account_spreads_or_variables'][0]).rstrip(',')in compact(body)
  if program=='pump_amm'and method!='setCoinCreator':
   recipient='getFeeRecipient(globalConfig,pool.isMayhemMode)'if method=='sweepProtocolFeeInstruction'else'coinCreatorVaultAuthorityPda(pool.coinCreator)';call='this.sweepFeeAccounts(payer,poolKey,pool,quoteTokenProgram,'+recipient+',)';assert compact(body).count(call)==1;assert len(row['branches'])==1 and len(row['branches'][0]['fields'])==12
  elif program=='pump':
   recipient='recipient'if method=='sweepProtocolFeeInstruction'else'recipient:creatorVaultPda(creator)';call='sweepBondingCurveFeeAccounts({payer,mint,'+recipient+',quoteMint,quoteTokenProgram,})';assert compact(body).count(call)==1
   assert len(row['branches'])==1 and len(row['branches'][0]['fields'])==9;assert {x['key']for x in row['branches'][0]['missing_idl_fields']}=={'global','associatedTokenProgram','systemProgram','bondingCurve'}
   prefix=s[:s.index(body)];assert 'quoteTokenProgram = TOKEN_PROGRAM_ID'in prefix[-600:]
  else:
   assert 'baseMint===undefined?{pool}:{pool,metadata:metadataPda(baseMint),bondingCurve:bondingCurvePda(baseMint),}'in compact(body)
   assert [len(b['fields'])for b in row['branches']]==[1,3];assert [len(b['missing_idl_fields'])for b in row['branches']]==[4,2]
  for branch in row['branches']:
   keys={x['key']for x in branch['fields']};assert len(keys)==len(branch['fields']);assert branch['missing_idl_fields']==[a for a in row['idl_order']if a['key']not in keys]
  checked.append(row['site_id'])
 assert len(set(checked))==8
 for label in ['pump','amm']:
  key=label+':sweepFeeAccounts';fields=analysis['helpers'][key];body=analysis['excerpts'][key]['source'];render='return{'+','.join(f['key']if compact(f['expression'])==f['key']else f['key']+':'+compact(f['expression'])for f in fields)+',};';assert render in compact(body)
  file='sources/'+label+('/package/src/swap/offlinePumpAmm.ts'if label=='pump'else'/package/src/sdk/offlinePumpAmm.ts');s=(P/file).read_text();assert s.count(body)==1;prefix=compact(s[:s.index(body)][-400:]);assert prefix.endswith('privatesweepFeeAccounts(payer:PublicKey,poolKey:PublicKey,pool:Pool,quoteTokenProgram:PublicKey,recipient:PublicKey,)')
 fields=analysis['helpers']['pump:sweepBondingCurveFeeAccounts'];body=analysis['excerpts']['pump:sweepBondingCurveFeeAccounts']['source'];render='return{'+','.join(f['key']if compact(f['expression'])==f['key']else f['key']+':'+compact(f['expression'])for f in fields)+',};';assert render in compact(body);assert 'constquote=normalizeQuoteMint(quoteMint);'in compact(body)
 for label in ['pump','amm']:
  online=compact(analysis['excerpts'][label+':onlineSetCoinCreatorInstructions']['source']);assert 'awaitthis.connection.getAccountInfo(poolKey)'in online and 'poolAccountInfo===null'in online
  assert online.index('decodePool(poolAccountInfo)')<online.index('poolAccountInfo.data.length<POOL_ACCOUNT_NEW_SIZE')<online.index('extendAccount(poolKey,payer)')<online.index('setCoinCreator(poolKey,pool.baseMint)')
  assert '=300;'in compact(analysis['excerpts'][label+':POOL_ACCOUNT_NEW_SIZE']['source']);assert '=287;'in compact(analysis['excerpts'][label+':POOL_SIZE']['source']);assert 'nullasanyasConnection'in compact(analysis['excerpts'][label+':OFFLINE_PUMP_AMM_PROGRAM']['source']);assert 'padTrailing(poolAccountInfo.data,this.offlineProgram.account.pool.size)'in compact(analysis['excerpts'][label+':decodePool']['source'])
 assert '!quoteMint||isLegacyQuoteMint(quoteMint)?NATIVE_MINT:quoteMint;'in compact(analysis['excerpts']['pump:normalizeQuoteMint']['source']);assert 'getAssociatedTokenAddressSync(quoteMint,owner,true,quoteTokenProgram)'in compact(analysis['excerpts']['pump:quoteAta']['source'])
 return {'state':'PASS_INDEPENDENT_EIGHT_STATIC_SITE_SOURCE_REVIEW_NOT_RUNTIME','packet_seal':expected,'payloads':len(manifest),'sources':len(J('source-bindings.json')),'expanded_sites':checked,'remaining_sites':analysis['remaining_sites'],'source_and_IDL_claims_confirmed':True,'actual_sdk_JS_RPC_VM_compiler_original_decoder_executions':0,'limitations':['No evaluated account resolution or numeric PDA/ATA proof','No full TypeScript call graph or on-chain compatibility proof','Replay cross-bindings and authenticated prior-eight controls should be strengthened in a successor as requested by root']}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--packet',type=Path,required=True);a.add_argument('--seal',required=True);a.add_argument('--output',type=Path,required=True);v=a.parse_args();result=review(v.packet,v.seal);v.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'state':result['state'],'expanded':len(result['expanded_sites'])}))

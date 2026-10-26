"""Static expansion of eight existing SDK object sites; no JavaScript execution."""
from pathlib import Path
import hashlib,json,re
from ts_static import tokens,pairs,class_methods,named_functions,object_fields,exported_const_declarations
P=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
J=lambda n:json.loads((P/n).read_text())
camel=lambda s:re.sub(r'_([a-z0-9])',lambda m:m.group(1).upper(),s)
def parse(name):
 source=(P/name).read_text();ts=tokens(source);ps,depth=pairs(ts)
 return source,ts,ps,class_methods(source,ts,ps,depth)
def method(parsed,name):
 s,t,p,ms=parsed;found=[m for m in ms if m['name']==name];assert len(found)==1,(name,len(found));m=found[0]
 return dict(name=name,line=m['line'],source=s[t[m['body_open']][1]:t[m['body_close']][2]],body_open=m['body_open'],body_close=m['body_close'])
def returned(parsed,m):
 s,t,ps,_=parsed;hits=[i+1 for i in range(m['body_open'],m['body_close'])if t[i][0]=='return'and t[i+1][0]=='{'];assert len(hits)==1
 fields,unknown=object_fields(s,t,ps,hits[0]);assert not unknown;return fields
def flat(accounts):
 out=[]
 for a in accounts:
  if 'accounts'in a:out+=flat(a['accounts'])
  else:out.append(dict(key=camel(a['name']),name=a['name'],signer=a.get('signer',False),writable=a.get('writable',False),optional=a.get('optional',False),address=a.get('address'),pda=a.get('pda'),relations=a.get('relations',[])))
 return out
def analyze():
 matrix=J('controls/sdk-matrix.json');prior=[r for r in matrix['routes']if r['unresolved_account_spreads_or_variables']];assert len(prior)==25
 pump=J('sources/pump/package/src/idl/pump.json');amm=J('sources/pump/package/src/idl/pump_amm.json');assert (P/'sources/pump/package/src/idl/pump_amm.json').read_bytes()==(P/'sources/amm/package/src/idl/pump_amm.json').read_bytes()
 idls={'pump':pump,'pump_amm':amm};rows=[];excerpts={};helpers={}
 for label,file in [('pump','package/src/swap/offlinePumpAmm.ts'),('amm','package/src/sdk/offlinePumpAmm.ts')]:
  path='sources/'+label+'/'+file;parsed=parse(path);helper=method(parsed,'sweepFeeAccounts');fields=returned(parsed,helper);assert len(fields)==12;helpers[label+':sweepFeeAccounts']=fields;excerpts[label+':sweepFeeAccounts']=helper
  for name,ix in [('sweepProtocolFeeInstruction','sweep_protocol_fee'),('sweepCreatorFeeInstruction','sweep_creator_fee'),('setCoinCreator','set_coin_creator')]:
   m=method(parsed,name);excerpts[label+':'+name]=m;r=next(x for x in prior if x['package']==label and x['source_file']==file and x['method_name']==name);assert r['passive_excluded']is None
   if name=='setCoinCreator':
    assert re.search(r'baseMint\s*===\s*undefined\s*\?\s*\{\s*pool\s*\}\s*:\s*\{',m['source']);op=[i for i in range(m['body_open'],m['body_close'])if parsed[1][i][0]=='{'and parsed[1][i-1][0]in ['?',':']];assert len(op)==2;branches=[object_fields(parsed[0],parsed[1],parsed[2],i)for i in op];assert all(not u for _,u in branches);expanded=[{'condition':'baseMint === undefined','fields':branches[0][0]},{'condition':'baseMint !== undefined','fields':branches[1][0]}];mode='accountsPartial'
   else:expanded=[{'condition':'unconditional helper object','fields':fields}];mode='accountsStrict';assert '.accountsStrict('in m['source']
   ordered=flat(next(x for x in amm['instructions']if x['name']==ix)['accounts']);keys={a['key']for a in ordered}
   for branch in expanded:
    supplied={f['key']for f in branch['fields']};assert len(supplied)==len(branch['fields'])and supplied<=keys;branch['missing_idl_fields']=[a for a in ordered if a['key']not in supplied]
    if mode=='accountsStrict':assert not branch['missing_idl_fields']
   rows.append(dict(site_id=r['id'],package=label,instruction='pump_amm:'+ix,mode=mode,source_path=path,method_line=m['line'],method_sha256=H(m['source'].encode()),branches=expanded,idl_order=ordered,helper_argument_expression=r['unresolved_account_spreads_or_variables']))
  excerpts[label+':decodePool']=method(parsed,'decodePool')
  for name in ['padTrailing']:
   matches=[f for f in named_functions(parsed[0],parsed[1],parsed[2])if f['name']==name];assert len(matches)==1;f=matches[0];excerpts[label+':'+name]={'name':name,'line':f['line'],'source':parsed[0][f['start']:f['end']]}
  constants={f['name']:f for f in exported_const_declarations(parsed[0],parsed[1])}
  for name in ['POOL_ACCOUNT_NEW_SIZE','POOL_SIZE','OFFLINE_PUMP_AMM_PROGRAM']:
   f=constants[name];excerpts[label+':'+name]={'name':name,'line':f['line'],'source':parsed[0][f['start']:f['end']]}
  online='sources/'+label+('/package/src/swap/onlinePumpAmm.ts'if label=='pump'else'/package/src/sdk/onlinePumpAmm.ts');excerpts[label+':onlineSetCoinCreatorInstructions']=method(parse(online),'setCoinCreatorInstructions')
 path='sources/pump/package/src/sdk.ts';parsed=parse(path);s,t,ps,_=parsed;fn=[x for x in named_functions(s,t,ps)if x['name']=='sweepBondingCurveFeeAccounts'];assert len(fn)==1;m=fn[0];fields=returned(parsed,m);assert len(fields)==9;helpers['pump:sweepBondingCurveFeeAccounts']=fields;excerpts['pump:sweepBondingCurveFeeAccounts']={'name':m['name'],'line':m['line'],'source':s[m['start']:m['end']]}
 for name,ix in [('sweepProtocolFeeInstruction','sweep_protocol_fee'),('sweepCreatorFeeInstruction','sweep_creator_fee')]:
  m=method(parsed,name);excerpts['pump:curve:'+name]=m;r=next(x for x in prior if x['package']=='pump'and x['source_file']=='package/src/sdk.ts'and x['method_name']==name);assert r['passive_excluded']is None
  ordered=flat(next(x for x in pump['instructions']if x['name']==ix)['accounts']);keys={a['key']for a in ordered};supplied={f['key']for f in fields};assert supplied<=keys
  rows.append(dict(site_id=r['id'],package='pump',instruction='pump:'+ix,mode='accountsPartial',source_path=path,method_line=m['line'],method_sha256=H(m['source'].encode()),branches=[{'condition':'unconditional helper object','fields':fields,'missing_idl_fields':[a for a in ordered if a['key']not in supplied]}],idl_order=ordered,helper_argument_expression=r['unresolved_account_spreads_or_variables']))
 assert len(rows)==8 and len({r['site_id']for r in rows})==8;assert helpers['pump:sweepFeeAccounts']==helpers['amm:sweepFeeAccounts']
 pda='sources/pump/package/src/pda.ts';text,pt,_,_=parse(pda);decl={f['name']:f for f in exported_const_declarations(text,pt)}
 for name in ['normalizeQuoteMint','quoteAta']:
  f=decl[name];excerpts['pump:'+name]={'name':name,'line':f['line'],'source':text[f['start']:f['end']]}
 for value in excerpts.values():
  value.pop('body_open',None);value.pop('body_close',None)
 return dict(scope='Eight existing account object sites expanded from authenticated archive source only; no SDK/runtime compatibility proof',expanded_sites=rows,helpers=helpers,excerpts=excerpts,original_dynamic_site_count=25,prior_closed_site_count=8,new_expanded_site_count=8,remaining_unexpanded_site_count=9,remaining_sites=[{'id':r['id'],'method':r['method_name'],'excluded':r['passive_excluded']}for r in prior if r['id']not in{q['site_id']for q in rows}and r['method_name']not in ['depositInstructionsInternal','withdrawInstructionsInternal','buyInstructionsNoPool','sellInstructionsNoPool']],new_JS_RPC_target_compiler_original_binary_executions=0)
if __name__=='__main__':
 d=analyze();(P/'analysis.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'expanded':len(d['expanded_sites']),'remaining':len(d['remaining_sites']),'account_counts':[(r['site_id'],len(r['idl_order']),[len(b['missing_idl_fields'])for b in r['branches']])for r in d['expanded_sites']]}))

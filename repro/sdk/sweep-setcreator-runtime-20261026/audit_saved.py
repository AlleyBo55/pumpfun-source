"""Saved-only SDK observation audit; no SDK, Node or Solders import/execution."""
from pathlib import Path
import argparse,hashlib,json,re
P=Path(__file__).resolve().parent
J=lambda n:json.loads((P/n).read_bytes())
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ALPHABET='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def encode(b):
 n=int.from_bytes(b,'big');s=''
 while n:n,r=divmod(n,58);s=ALPHABET[r]+s
 return '1'*(len(b)-len(b.lstrip(b'\0')))+s
def decode(s):
 n=0
 for c in s:n=n*58+ALPHABET.index(c)
 return b'\0'*(len(s)-len(s.lstrip('1')))+n.to_bytes((n.bit_length()+7)//8,'big')
def on_curve(b):
 q=2**255-19;v=int.from_bytes(b,'little');sign=v>>255;y=v&((1<<255)-1)
 if y>=q:return False
 d=(-121665*pow(121666,q-2,q))%q;den=(d*y*y+1)%q
 if den==0:return False
 x2=((y*y-1)*pow(den,q-2,q))%q;x=pow(x2,(q+3)//8,q)
 if x*x%q!=x2:x=x*pow(2,(q-1)//4,q)%q
 return x*x%q==x2 and not(x==0 and sign)
def instruction_rows(idl,instruction):
 ix=next(x for x in idl['instructions']if x['name']==instruction);assert ix['args']==[]
 assert all('accounts'not in x for x in ix['accounts'])
 return ix,ix['accounts']
def audit(live=False):
 # Authenticate all retained inputs, without following source_label strings.
 bindings=J('input-bindings.json')
 for n,r in bindings.items():assert H(P/n)==r['sha256']and(P/n).stat().st_size==r['bytes']
 assert H(P/'controls/plan-manifest.json')=='4ef3bda53234add99e88d7cc25f53e6275a2d5e52712dbfaa95b0bfb04ee528b';plan=J('controls/plan-manifest.json')
 for n in ['config.json','fixture.json','expected.json','offline-client.cjs','run_once.py','pda_math.py']:assert H(P/('controls/plan-'+n))==plan[n]['sha256']
 for n in ['all-module-files.json','graph-publication-manifest.json','source-proof-manifest.json','pump.json','pump_amm.json']:assert H(P/'controls'/n)==plan['controls/'+n]['sha256']
 assert H(P/'controls/graph-extra-files.json')==plan['graph-extra-files.json']['sha256']
 assert H(P/'controls/graph-publication-manifest.json')=='8a351ec761f71625466144d0c147e1aaa07267df2fbb73b7fd081fec40755ae3';publication=J('controls/graph-publication-manifest.json');assert H(P/'controls/all-module-files.json')==publication['all-module-files.json']['sha256']
 assert H(P/'controls/source-proof-manifest.json')=='ee143e26fcf33efee56fb421e6a2e604baa029ae4e51b07c7b170d1c74f19052'
 assert H(P/'controls/root-admission.json')=='744669e4cea68f52e727064257f9ca0aad2d405cd6baf291814e62742b411c21';assert H(P/'controls/root-plan-review.json')=='d194bebe40545dba9bbe348f77562b376ba01492f362a4b566200dd6f2bd192e'
 admission=J('controls/root-admission.json');claim=J('saved/consumed-claim.json');config=J('controls/plan-config.json');oracle=J('controls/plan-expected.json');fixture=J('controls/plan-fixture.json');observed=J('saved/observations.json');terminal=J('saved/terminal.json');controller=J('saved/controller-result.json');root_terminal=J('controls/root-terminal-observation.json')
 assert admission['root_accepted']is True and admission['state']=='ROOT_ACCEPTED_OFFLINE_PUBLIC_SDK_WRAPPER_OBSERVATION';assert admission['review_sha256']==H(P/'controls/root-plan-review.json');assert claim['admission_sha256']==H(P/'controls/root-admission.json')and claim['attempt']==1
 assert claim['bindings']==admission['bindings'];b=claim['bindings'];assert b['plan_manifest_sha256']==H(P/'controls/plan-manifest.json');assert b['script_sha256']==H(P/'controls/plan-offline-client.cjs')and b['fixture_sha256']==H(P/'controls/plan-fixture.json')and b['oracle_sha256']==H(P/'controls/plan-expected.json')
 assert (b['observation_count'],b['fully_compared_construction_cases'],b['omitted_baseMint_observation_cases'])==(10,8,2)
 before=J('saved/before.json');after=J('saved/after.json');assert before==after
 modules=J('controls/all-module-files.json');full=dict(modules);full.update({n:r['sha256']for n,r in J('controls/graph-extra-files.json').items()});assert len(modules)==4747 and len(full)==4749 and before['graph_files']==full
 assert before['node_sha256']==b['node_sha256']==config['node_sha256']=='3cc715fde633656eb0e08c0eb0dbe3ae534b4621147ee491b4781c4775124ba1';assert before['python_sha256']==b['python_sha256']==config['python_sha256']
 launch=J('saved/launch.json');started=J('saved/child-started.json');assert launch['command']==started['command']and started['attempt']==1;assert launch['command']==[config['node_resolved_path'],str(Path(b['output']).parent/'sdk-sweep-offline-client-plan-v2/offline-client.cjs'),config['graph_root'],str(Path(b['output']).parent/'sdk-sweep-offline-client-plan-v2/fixture.json'),str(Path(b['output']).parent/'sdk-sweep-offline-client-plan-v2/expected.json'),str(Path(b['output']).parent/'sdk-sweep-offline-client-plan-v2/controls/all-module-files.json'),b['output']+'/observations.json']
 assert launch['environment']['NODE_OPTIONS']==launch['environment']['NODE_PATH']=='';assert launch['observation_timeout_seconds']==120
 assert terminal['actual_child_exit']==controller['actual_child_exit']==root_terminal['actual_Node_child_exit']==0;assert root_terminal['actual_controller_terminal_exit']==0 and root_terminal['session_id']==7332;assert root_terminal['controller_result_sha256']==H(P/'saved/controller-result.json');assert terminal['observation_timeout_count']==controller['observation_timeout_count']==0 and terminal['termination_performed']is False and terminal['no_retry_performed']is True
 assert controller['observations']==root_terminal['observations']==10 and controller['fully_compared_constructed_instructions']==root_terminal['fully_compared_constructed']==8
 assert terminal['stdout_sha256']==H(P/'saved/stdout.log')and terminal['stderr_sha256']==H(P/'saved/stderr.log');assert controller['state']=='COMPLETE_OFFLINE_OBSERVATION_NOT_CONTRACT_ACCEPTANCE'and controller['inputs_unchanged']is True
 assert observed['state']=='OBSERVATION_COMPLETE'and observed['phase']=='finalize'and observed['error']is None;assert observed['node']==config['node_recorded_version']=='v24.5.0'and observed['platform']=='darwin'and observed['arch']=='arm64';assert observed['graphRoot']==b['graph_root']
 assert observed['fixtureSha256']==b['fixture_sha256']and observed['expectedSha256']==b['oracle_sha256'];assert observed['blocked']==[]and observed['randomOverride']is False and observed['targetVMs']==observed['compilers']==observed['installations']==0
 assert [r['id']for r in observed['rows']]==[r['id']for r in oracle['rows']]and len(observed['rows'])==10
 keys={n:encode(bytes([r['byte']])*32)for n,r in fixture['keys'].items()};assert keys==oracle['key_values']
 compiled=J('compiled-bindings.json');entry_files={'@pump-fun/pump-sdk':'pump-main.js','@pump-fun/pump-sdk/swap':'pump-swap.js','@pump-fun/pump-swap-sdk':'swap-main.js'}
 for name,graph_path in compiled.items():assert H(P/'compiled'/name)==modules[graph_path]
 pump_pkg=J('controls/pump-package.json');swap_pkg=J('controls/swap-package.json');assert H(P/'controls/pump-package.json')==modules['node_modules/@pump-fun/pump-sdk/package.json']and H(P/'controls/swap-package.json')==modules['node_modules/@pump-fun/pump-swap-sdk/package.json'];assert pump_pkg['version']=='4.3.1'and swap_pkg['version']=='2.2.0';assert pump_pkg['exports']['.']['require']=='./dist/index.js'and pump_pkg['exports']['./*']['require']=='./dist/*/index.js'and swap_pkg['exports']['.']['require']=='./dist/index.js'
 loaded=observed['loadedModules'];assert len(loaded)==len({r['file']for r in loaded})==316;assert all(r['sha256']==modules[r['file']]==full[r['file']]for r in loaded)
 for entry,name in entry_files.items():assert any(r['request']==entry and r['resolved']==compiled[name]for r in observed['moduleAttempts']);assert any(r['file']==compiled[name]for r in loaded)
 instruction_count=meta_count=0;errors=[];validated=[]
 for row,spec in zip(observed['rows'],oracle['rows']):
  assert row['publicEntry']==spec['public_entry']and row['method']==spec['method'];assert row['ownerClass']==('PumpSdk'if spec['public_entry']=='@pump-fun/pump-sdk'else'PumpAmmSdk');assert row['blockedBefore']==row['blockedAfter']==0
  source=(P/'compiled'/entry_files[row['publicEntry']]).read_text();function=row['compiledFunctionSource'];assert source.count(function)==1 and hashlib.sha256(function.encode()).hexdigest()==row['compiledFunctionSha256'];assert function.startswith('async '+row['method']+'(')
  if row['method']=='setCoinCreator':args=[keys['pool']]+([keys['baseMint']]if row['id'].endswith('-supplied')else[])
  elif '-curve-'in row['id']:
   args={'payer':keys['payer'],'mint':keys['baseMint'],'quoteMint':fixture['curveQuoteMint']};args['creator'if row['method']=='sweepCreatorFeeInstruction'else'recipient']=keys['coinCreator'if row['method']=='sweepCreatorFeeInstruction'else'protocolRecipient'];assert 'quoteTokenProgram'not in row['actualArguments']
  else:
   args={'payer':keys['payer'],'poolKey':keys['pool'],'quoteTokenProgram':fixture['quoteTokenProgram'],'pool':{'quoteMint':keys['ammQuoteMint'],'poolQuoteTokenAccount':keys['poolQuoteTokenAccount'],'coinCreator':keys['coinCreator'],'isMayhemMode':False}}
   if row['method']=='sweepProtocolFeeInstruction':args['globalConfig']={'protocolFeeRecipients':[keys['protocolRecipient']],'reservedFeeRecipient':keys['reservedRecipient'],'reservedFeeRecipients':[]}
  assert row['actualArguments']==args
  if spec['fully_compared_if_constructed']:
   assert row['state']=='CONSTRUCTED'and row['fullyCompared']is True and row['differences']==[];actual=row['instruction'];expected=spec['expected'];assert actual==expected
   idl=J('controls/pump.json'if row['publicEntry']=='@pump-fun/pump-sdk'else'controls/pump_amm.json');ix,accounts=instruction_rows(idl,spec['instruction']);assert actual['programId']==idl['address']and actual['dataHex']==bytes(ix['discriminator']).hex();assert len(actual['keys'])==len(accounts)
   assert len({m['key']for m in actual['keys']})==len(actual['keys'])
   for i,(a,m)in enumerate(zip(accounts,actual['keys'])):assert m['index']==i and m['idlName']==a['name']and m['isSigner']==a.get('signer',False)and m['isWritable']==a.get('writable',False)
   instruction_count+=1;meta_count+=len(actual['keys']);validated.append(row['id'])
  else:
   assert row['state']=='ERROR_OBSERVED'and'instruction'not in row and'fullyCompared'not in row;assert row['error']['message']=='Reached maximum depth for account resolution. Unresolved accounts: `metadata`, `bondingCurve`';assert row['error']['name']=='Error'and row['error']['code']is None;assert '/node_modules/@coral-xyz/anchor/dist/cjs/program/accounts-resolver.js:68:'in row['error']['stack'];errors.append({'id':row['id'],'message':row['error']['message']})
 assert instruction_count==8 and meta_count==84 and len(errors)==2;assert controller['omitted_baseMint_rows']==[r for r in observed['rows']if r['state']=='ERROR_OBSERVED']
 root_oracle=J('controls/root-independent-oracle.json');assert root_oracle['state']=='PASS_INDEPENDENT_SOLDERS_PDA_AND_SAVED_INSTRUCTION_COMPARISON'and root_oracle['native_crypto_utility_imported']is True and root_oracle['SDK_or_target_VM_reruns']==0;assert(root_oracle['derivation_records'],root_oracle['unique_addresses'],root_oracle['fully_compared_instructions'],root_oracle['account_metas_compared'])==(16,13,8,84)
 assert len(oracle['derivations'])==len(root_oracle['derivations'])==16
 for want,got in zip(oracle['derivations'],root_oracle['derivations']):
  assert(want['label'],want['address'])==(got['label'],got['address']);seeds=[bytes.fromhex(x)for x in want['seed_hex']];program=decode(want['program']);address=decode(want['address']);assert len(address)==len(program)==32;assert hashlib.sha256(b''.join(seeds)+bytes([got['bump']])+program+b'ProgramDerivedAddress').digest()==address and not on_curve(address)
  for bump in range(255,got['bump'],-1):assert on_curve(hashlib.sha256(b''.join(seeds)+bytes([bump])+program+b'ProgramDerivedAddress').digest())
 assert len({r['address']for r in oracle['derivations']})==13
 addons=observed['addonAttempts'];assert addons==[{'phase':'load-genuine-web3','file':'node_modules/bufferutil/prebuilds/darwin-arm64/bufferutil.node','sha256':'688f957f5a989f6406e5caa26382e213c8b7316eb600303307dc95be60c287c0','state':'LOADED'}];assert[r['file']for r in loaded if r['nativeAddon']]==[addons[0]['file']];assert controller['native_addon_observations']==addons
 failures=[r for r in observed['moduleAttempts']if r['resolved']is None];assert len(failures)==14 and all(r['code']=='MODULE_NOT_FOUND'for r in failures);assert sum(r['request']=='encoding'for r in failures)==1 and sum(r['request'].endswith('bigint_buffer.node')for r in failures)==13
 assert(P/'saved/stderr.log').read_text()=='bigint: Failed to load bindings, pure JS will be used (try npm run rebuild?)\n';assert not(P/'saved/stdout.log').read_bytes()
 live_count=None
 if live:
  root=Path(config['graph_root']);assert not any(f.is_symlink()for f in root.rglob('*'));current={str(f.relative_to(root)):H(f)for f in root.rglob('*')if f.is_file()};assert current==full;live_count=len(current)
 return {'state':'PASS_SAVED_PUBLIC_COMPILED_SDK_OBSERVATION_NOT_ONCHAIN_ACCEPTANCE','plan_seal':H(P/'controls/plan-manifest.json'),'root_admission_sha256':H(P/'controls/root-admission.json'),'actual_child_and_controller_exit':0,'observations':10,'fully_compared_constructed_instructions':8,'account_metas':84,'omitted_baseMint_errors':errors,'recorded_blocked_API_events':0,'loaded_graph_modules':316,'module_load_attempt_records':len(observed['moduleAttempts']),'missing_bigint_native_resolution_candidates':13,'missing_optional_encoding_resolution':1,'genuine_native_addon_loads':addons,'before_after_graph_files':4749,'current_graph_files_rehashed':live_count,'root_Solders_derivation_records':16,'unique_PDA_ATA_addresses':13,'this_review_SDK_Node_Solders_imports_or_reruns':0,'target_VM_compiler_signing_deployment_execution_by_this_review':0,'historical_native_loader_identity_or_valid_target_state_or_whole_identity_proven':False,'IDL_names_are_index_annotations_not_observed_Instruction_properties':True}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--live-graph',action='store_true');a.add_argument('--output',type=Path,required=True);v=a.parse_args();result=audit(v.live_graph);v.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['state','observations','fully_compared_constructed_instructions','account_metas','loaded_graph_modules','current_graph_files_rehashed']}))

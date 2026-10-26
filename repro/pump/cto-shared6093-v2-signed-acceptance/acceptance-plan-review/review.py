"""Read-only frozen acceptance plan audit and mock subprocess tests only."""
from pathlib import Path,PurePosixPath
import ast,difflib,hashlib,json,subprocess,sys
P=Path(__file__).resolve().parent;W=P.parent;R=W/'cto-shared6093-v2-acceptance-plan';J=lambda p:json.loads(p.read_text());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SEAL='7e779eec39bdc076b11961a54cfc484422e3a776c973cf76e5d25b9d3786449a';LANES={'ordinary':'9c8121167c3a755c6c4acec3151fdb79507eacd597f65e485af858fb020b4feb','six-case':'028a7f9500c2846d360c479825006ff2ea01d3f50e4149a84ad3cc780bc7ce60'}
def snap(root):return{str(f.relative_to(root)):H(f)for f in root.rglob('*')if f.is_file()}
before=snap(R);assert H(R/'manifest.json')==SEAL
for root,seal in[(R,SEAL),*[(R/n,s)for n,s in LANES.items()]]:
 assert H(root/'manifest.json')==seal==(root/'manifest.sha256').read_text().strip();m=J(root/'manifest.json');assert set(m)==set(snap(root))-{'manifest.json','manifest.sha256'}
 for n,row in m.items():
  q=PurePosixPath(n);assert not q.is_absolute()and'..'not in q.parts;f=root/n;assert not f.is_symlink();assert H(f)==(row if isinstance(row,str)else row['sha256'])
  if isinstance(row,dict):assert f.stat().st_size==row['bytes']
assert J(R/'lane-seals.json')==LANES
schema=J(R/'admission-schema.json');assert schema['plan_seals']==LANES and schema['SCHEMA_ONLY_NOT_ACTUAL_ADMISSION']is True and not(W/'cto-shared6093-v2-root-runtime-admission.json').exists()
configs={};inputmaps={}
for lane in LANES:
 root=R/lane;cfg=J(root/'plan.json');configs[lane]=cfg;inputs=J(root/'inputs.json');inputmaps[lane]=inputs;assert len(inputs)==15
 assert cfg['candidate_sha256']=='fdfdb5f27af9b8c22effd48ea523c06bd037ceedf49df0da8178cad19eed38f5'and cfg['candidate_source_CTO']=='950d6ec8c07072a3305c905509018f95b40d53e9ab25a4c1bda96b42c2a2fe58'
 assert cfg['source37_sha256']==H(root/'current-controls/source37.json')=='80165bb94946ecc9486a4740e6c284ce4a75a3f7d6d01d38d4956306893978fc'
 assert cfg['build_plan_seal']==H(root/'current-controls/build-plan-manifest.json')=='29069875549ea325beeafc10059c6893218211c327d08a6f90bce70df10e5ae2'
 for n,h in inputs.items():assert H(root/'repo'/n)==h
 for k in['out','claim','gate_output']:assert not Path(cfg[k]).exists()
 deriv=J(root/'derivation.json');prior=J(root/'predecessor-controls/manifest.json');assert H(root/'predecessor-controls/manifest.json')==deriv['prior_manifest_sha256']==cfg['prior_plan_seal']
 for n,h in deriv['retained_predecessor_controls'].items():assert H(root/'predecessor-controls'/n)==h==prior[n]
 for row in deriv['changed_same_path_payloads']:
  old=root/'predecessor-controls'/row['path'];new=root/row['path'];assert H(old)==row['old_sha256']and H(new)==row['new_sha256']
  expected=''.join(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile='predecessor/'+row['path'],tofile='successor/'+row['path']));assert(root/'changes'/(row['path']+'.diff')).read_text()==expected
 assert all(prior['repo/'+n]==h for n,h in inputs.items())
 for f in root.glob('*.py'):ast.parse(f.read_text())
assert inputmaps['ordinary']==inputmaps['six-case']
old=(R/'ordinary/predecessor-controls/controller.py').read_text();expected=old.replace("E=P.parent/'cto-wallet-collector-build-01'","E=P.parents[1]/'cto-shared6093-v2-build-01'").replace("OUT=P.parent/'cto-wallet-collector-preservation-01'","OUT=P.parents[1]/'cto-shared6093-v2-ordinary-preservation-01'").replace('6e0c9002d09e0cee6cc738b3a9e0983a8d0cd89374fa2cc7c41fa45910515b9e','fdfdb5f27af9b8c22effd48ea523c06bd037ceedf49df0da8178cad19eed38f5');assert expected==(R/'ordinary/controller.py').read_text()
assert H(R/'six-case/cases.json')==H(R/'six-case/predecessor-controls/cases.json')=='9ae6408a962aad2234664bf0eb09b263a3d47f2b1abefa2a4dfc2e70d9b74e58'
a=(R/'ordinary/admission.py').read_text();g=(R/'ordinary/gate.py').read_text();assert a==(R/'six-case/admission.py').read_text()and g==(R/'six-case/gate.py').read_text()
assert g.index('binding=check_admission(')<g.index('gateout.mkdir(')<g.index("durable(gateout/'claim.json'")<g.index('child=launch_child(')
assert "plan_check(seal,False);check_admission(cfg,emitted_seal,root_admission_sha,seal)"in g
assert "len(data['cases'])==363"in(R/'ordinary/verify_results.py').read_text()and'original_successes==169 and txs==726 and signatures==1448'in(R/'ordinary/verify_results.py').read_text()
assert "'all_six_effects_equal':all(not x['different_effect_fields']for x in comparison)"in(R/'six-case/saved_checks.py').read_text()
assert "durable(out/f'side-{index:02d}-{side}.json',item)"in(R/'six-case/driver.py').read_text()
receipts=[]
for lane,seal in LANES.items():
 for name,cmd in [('readonly',[sys.executable,'-B','gate.py','--expected-seal',seal]),('gate-mocks',[sys.executable,'-B','test_gate.py'])]+([('case-mocks',[sys.executable,'-B','test_plan.py'])]if lane=='six-case'else[]):
  child=subprocess.run(cmd,cwd=R/lane,capture_output=True);(P/(lane+'-'+name+'.stdout')).write_bytes(child.stdout);(P/(lane+'-'+name+'.stderr')).write_bytes(child.stderr);assert child.returncode==0;receipts.append({'lane':lane,'check':name,'exit':child.returncode})
for cfg in configs.values():
 for k in['out','claim','gate_output']:assert not Path(cfg[k]).exists()
assert snap(R)==before and not(W/'cto-shared6093-v2-root-runtime-admission.json').exists()
(P/'input-hashes.json').write_text(json.dumps(before,indent=2)+'\n');(P/'review.json').write_text(json.dumps({'state':'PASS_FROZEN_FINITE_V2_ACCEPTANCE_PLAN_REVIEW_PENDING_ROOT_ADMISSION','parent_seal':SEAL,'lane_seals':LANES,'source15_inputs_unchanged':True,'ordinary_controller_exact3substitutions':True,'six113b_cases_exact':True,'before_after_gate_admission_checks_present':True,'gate_claim_precedes_child_native_import':True,'ordinary_strict363_169_726_1448':True,'six_all6effectfields_required_logs_separate':True,'source37_candidate_build_cache_emitted_bindings_checked':True,'root_admission_not_created':True,'outputs_claims_absent':True,'mock_and_readonly_receipts':receipts,'packet_unchanged':True,'realhelper_Solders_VM_native_compiler_original_decoder_network_imports_executions':0,'limits':['Onlygateis authorizedentry; retainedlowercontrollerscannotbeexecuteddirectly','Suppliedsixcase test_gateconfig usesordinarylane mock; independentactualsixgate-pathmockaddedseparately','No universalsharedABI/header/transitive/historical/fullidentity proof','Actualruntime requires root-authoredadmission hash+emittedseal CLI pins']},indent=2)+'\n');print('PASS frozen acceptance plan passive+supplied mock checks')

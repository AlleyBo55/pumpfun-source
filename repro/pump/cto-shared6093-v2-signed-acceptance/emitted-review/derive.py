"""Saved candidate-body/metadata audit; no original read or new callee decode."""
from pathlib import Path
import gzip,hashlib,json,struct
P=Path(__file__).resolve().parent;W=P.parent;R=W/'cto-shared6093-v2-emitted-review';PLAN=W/'cto-shared6093-v2-emitted-plan';J=lambda p:json.loads(p.read_text());H=lambda b:hashlib.sha256(b).hexdigest();G=lambda p:json.loads(gzip.decompress(p.read_bytes()))
def snap(root):return{str(f.relative_to(root)):H(f.read_bytes())for f in root.rglob('*')if f.is_file()}
rb=snap(R);pb=snap(PLAN);assert H((PLAN/'manifest.json').read_bytes())=='970784c402bc690704309e0621b84885bbe455f5abe6844600304228288af870'
for n,r in J(PLAN/'manifest.json').items():assert H((PLAN/n).read_bytes())==r['sha256']
launch=J(R/'launch-results.json');assert launch['plan_seal']=='970784c402bc690704309e0621b84885bbe455f5abe6844600304228288af870'and len(launch['runs'])==7
for index,run in enumerate(launch['runs']):
 assert run['returncode']==0
 for stream in['stdout','stderr']:assert H((R/f'run-{index}.{stream}').read_bytes())==run[stream+'_sha256']
p=J(R/'candidate-bodies/proof.json');fs={f['start']:f for f in p['functions']};assert len(fs)==24 and p['candidate_sha256']=='fdfdb5f27af9b8c22effd48ea523c06bd037ceedf49df0da8178cad19eed38f5'and p['symbols_sha256']=='1e088e9add0218ebf6745a7f7557a4dc55dc68e86ec97790584db7f169c14bc3'
for n,h in p['source37'].items():assert H((W/'cto-shared6093-v2-build-01/repo'/n).read_bytes())==h
assert len(p['source37'])==37 and p['source37']['programs/pump/src/admin_cto.rs']=='950d6ec8c07072a3305c905509018f95b40d53e9ab25a4c1bda96b42c2a2fe58'
ex,raw,frozen,collector=[fs[n]for n in[441928,471104,471544,471640]]
def ins(f,pc):
 b=bytes.fromhex(f['code_hex']);o=pc-f['start'];d=b[o:o+8];assert len(d)==8;op,reg,off,imm=struct.unpack('<BBhi',d);v={'pc':pc,'hex':d.hex(),'opcode':op,'reg':reg,'offset':off,'immediate':imm}
 if op==133:v['target']=pc+8+imm*8
 elif op&7 in(5,6)and op not in(149,141):v['branch_target']=pc+8+off*8
 return v
def at(pc):return ins(raw if raw['start']<=pc<raw['end']else frozen if frozen['start']<=pc<frozen['end']else ex,pc)
branches={471136:471360,471304:471320,471576:471616,449328:450152,449424:456776,449576:450152,449664:449680,449824:450184,450168:450184,450176:453328,450576:451336,450672:450688,450912:450928,451088:452032,451120:457792,451424:451776,452016:452080,452024:457792,452072:457792,456400:456920,456464:450216,459112:465600,459136:459152,459144:465744,459224:447384,459280:459296,459288:465744}
for pc,target in branches.items():assert at(pc)['branch_target']==target
calls={471128:1387344,471168:1387712,471288:1317464,471568:1387344,471600:476680,449320:1387344,449408:471544,449648:471104,450008:1361816,450160:1387344,450656:471104,450896:471544,451304:1361816,451360:1380600,451856:1380800,451880:1387016,452624:477080,456368:1379456,456424:52360,459096:1292560,459192:471640,459312:1380368,459648:1270552,459816:1270552}
for pc,target in calls.items():assert at(pc)['target']==target
assert at(471360)['immediate']==2 and at(471368)['immediate']==0 and at(471616)['immediate']==2 and at(471624)['immediate']==0
stores=[ins(ex,ex['start']+i)for i in range(0,ex['bytes'],8)if ins(ex,ex['start']+i)['opcode']==98 and ins(ex,ex['start']+i)['immediate']in[6019,6091,6092,6093]]
assert[(r['pc'],r['immediate'])for r in stores]==[(444352,6091),(446352,6019),(449112,6092),(449968,6093),(451264,6093)]
assert at(449944)['immediate']==116 and at(451240)['immediate']==131
(P/'cfg-anchors.json').write_text(json.dumps({'branches':[at(pc)for pc in branches],'calls':[at(pc)for pc in calls],'code_stores':stores,'shared_raw_complete_body':raw,'shared_frozen_complete_body':frozen},indent=2)+'\n')
def choose(proof,n):return next(f for f in proof['functions']if any(n in name for name in f['names']))
def seq(f,inv):
 names={r['start']:r['names']for r in inv['candidate_symbol_windows']};return[x.get('actual_named_callee',names.get(x['target'],[]))for x in f['direct_calls']]
ni=G(R/'new-inventory.json.gz');base=[('71ec',Path('/Users/shawwalters/Documents/Codex/2026-10-25/go/work/pr12-selected-cto-emitted-review/proof.json'),G(R/'baseline-before.json.gz')),('d75',Path('/Users/shawwalters/Documents/Codex/2026-10-25/go/work/cto-wallet-emitted-review/proof.json'),G(R/'baseline-after.json.gz')),('6e',PLAN/'retained-6e-candidate-proof.json',G(PLAN/'retained-6e-inventory.json.gz'))];comparisons=[]
for tag,path,inv in base:
 old=J(path)
 for name in['12try_accounts','__global9admin_cto']:
  a,b=choose(old,name),choose(p,name);assert a['bytes']==b['bytes']and a['normalized_sha256']==b['normalized_sha256']and seq(a,inv)==seq(b,ni)
  comparisons.append({'baseline':tag,'name':name,'bytes':b['bytes'],'normalized_sha256':b['normalized_sha256'],'all_named_callees':seq(b,ni),'calls':len(b['direct_calls']),'equal':True})
def norm(f):
 b=bytearray.fromhex(f['code_hex'])
 for r in f['direct_calls']+f['external_calls']:b[r['offset']+4:r['offset']+8]=bytes(4)
 for r in f['data_references']:b[r['offset']+4:r['offset']+8]=bytes(4);b[r['offset']+12:r['offset']+16]=bytes(4)
 return bytes(b)
prior=choose(J(PLAN/'retained-6e-candidate-proof.json'),'collect_wallet_creator_fee');a,b=norm(prior),norm(collector);assert len(a)==len(b)==5040 and seq(prior,base[-1][2])==seq(collector,ni)
assert[i for i in range(0,len(a),8)if a[i:i+8]!=b[i:i+8]]==[568]and struct.unpack('<BBhi',a[568:576])==(98,10,-280,174)and struct.unpack('<BBhi',b[568:576])==(98,10,-280,191)
comparisons.append({'baseline':'6e','name':'collect_wallet_creator_fee','bytes':5040,'normalized_equal':False,'only_normalized_difference':{'offset':568,'before_source_line':174,'after_source_line':191},'all22named_callees_equal':True})
(P/'preserved-controls.json').write_text(json.dumps(comparisons,indent=2)+'\n')
t=J(R/'6e-to-shared-v2-transitions.json');assert not t['changed_strongest_rows']and len(t['all1035_rows'])==1035 and t['summary_after']==ni['summary']
assert ni['summary']=={'original_windows':1035,'candidate_symbol_windows':782,'candidate_inferred_windows':782,'candidate_with_pattern':493,'candidate_with_call_consistent_pattern':427,'original_with_call_consistent_pattern':454,'pattern_pairs':1462,'call_consistent_pairs':1080,'raw_equal_pairs':617,'ambiguous_candidate_rows':99}
assert J(R/'baseline-6e-replay-check.json')['baseline6e_replay_equal']and G(R/'baseline-6e-replay.json.gz')==G(PLAN/'retained-6e-inventory.json.gz')
cb=(W/'cto-shared6093-v2-build-01/build-01/artifacts/pump_recovered.so').read_bytes();assert H(cb)==p['candidate_sha256'];assert cb[1473448:1473464]==b'src/admin_cto.rs'
(P/'candidate-origin.json').write_text(json.dumps({'own_candidate_path':'src/admin_cto.rs','address':1473448,'bytes':16,'shared_A_line':116,'shared_B_line':131,'collector6050_line':191,'original_shared_lines':[660,719],'original_collector_line':198,'natural_origin_equality':False},indent=2)+'\n')
assert snap(R)==rb and snap(PLAN)==pb
(P/'input-hashes.json').write_text(json.dumps({'raw_outputs':rb,'plan_manifest':H((PLAN/'manifest.json').read_bytes()),'baseline_proof_hashes':{tag:H(path.read_bytes())for tag,path,_ in base}},indent=2)+'\n')
result={'state':'PASS_BOUNDED_SHARED_V2_EMITTED_SEQUENCE_REVIEW_NOT_SEMANTIC_CERTIFICATION','candidate_sha256':p['candidate_sha256'],'symbols_sha256':p['symbols_sha256'],'candidate_bodies':24,'sharedraw440B_empty0':True,'sharedfrozen96B_emptyfalse':True,'sharedA_two_caller_empty_reads_frozen_raw_positive6093_zero_skipAMM':True,'sharedB_raw_frozen_positive6093_zero_skipATA_payout':True,'nativeRent_path_preserved_locally':True,'owning_errors_source_lines':[116,131,191],'parser_wrapper_vs3baselines_normalized_and_named_callees_equal':True,'ordinary_collector_6e_only_normalized_delta':'line174->191 atoffset568;22namedcalls equal','original1035_strongest_changes_vs6e':0,'summary':ni['summary'],'raw_outputs_plan_unchanged':True,'VM_native_compiler_network_original_read_or_new_callee_decode':0,'unclosed':['shared1108280/1565736/604312/native157128 ABIeffects correspondence','header/alias/transitive/drop/OOM and runtime preservation','pay_token emitted4776B vs6e4848B; sourceunchanged noemittedidentityclaim','token_amount/token_raw_amount standalone symbolsabsent, notsemanticfailureproof','naturalorigins differ original660/719/198','wholeoriginalbyteidentity']}
(P/'review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

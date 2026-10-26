"""UNEXECUTED controller. Requires a separately root-accepted review admission."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
from verify_plan import P,H,J,verify_plan,snapshot_graph
def write_sync(path,data,exclusive=False):
 flags=os.O_WRONLY|os.O_CREAT|(os.O_EXCL if exclusive else os.O_TRUNC)
 fd=os.open(path,flags,0o600)
 with os.fdopen(fd,'w')as f:f.write(json.dumps(data,indent=2)+'\n');f.flush();os.fsync(f.fileno())
def main():
 a=argparse.ArgumentParser();a.add_argument('--expected-seal',required=True);a.add_argument('--admission',type=Path,required=True);v=a.parse_args();verified=verify_plan(v.expected_seal);config=J('config.json');admission=json.loads(v.admission.read_bytes())
 assert admission['state']=='ROOT_ACCEPTED_OFFLINE_PUBLIC_SDK_WRAPPER_OBSERVATION'and admission['root_accepted']is True
 expected={'plan_manifest_sha256':v.expected_seal,'node_sha256':config['node_sha256'],'python_sha256':config['python_sha256'],'script_sha256':H(P/'offline-client.cjs'),'fixture_sha256':H(P/'fixture.json'),'oracle_sha256':H(P/'expected.json'),'graph_root':config['graph_root'],'output':config['future_output'],'observation_count':10,'fully_compared_construction_cases':8,'omitted_baseMint_observation_cases':2}
 assert admission['bindings']==expected and admission['no_VM_compiler_signing_deployment']is True and admission['reviewed_genuine_loader_observer_and_network_RPC_denial']is True
 assert len(admission['review_sha256'])==64 and all(c in'0123456789abcdef'for c in admission['review_sha256'])
 before=snapshot_graph();out=Path(config['future_output']);out.mkdir(exist_ok=False)
 write_sync(out/'consumed-claim.json',{'state':'CONSUMED_BEFORE_NODE_OR_SDK_IMPORT','admission_sha256':H(v.admission),'bindings':expected,'attempt':1},True);write_sync(out/'before.json',before,True)
 command=[config['node_resolved_path'],str(P/'offline-client.cjs'),config['graph_root'],str(P/'fixture.json'),str(P/'expected.json'),str(P/'controls/all-module-files.json'),str(out/'observations.json')]
 env={'HOME':str(Path.home()),'PATH':'/opt/homebrew/bin:/usr/bin:/bin','LANG':'C.UTF-8','HTTP_PROXY':'http://127.0.0.1:1','HTTPS_PROXY':'http://127.0.0.1:1','NO_PROXY':'','NODE_OPTIONS':'','NODE_PATH':''};write_sync(out/'launch.json',{'command':command,'environment':env,'observation_timeout_seconds':config['observation_timeout_seconds'],'observation_timeout_behavior':config['observation_timeout_policy']},True)
 observation_timeout_count=0
 with(out/'stdout.log').open('xb')as stdout,(out/'stderr.log').open('xb')as stderr:
  child=subprocess.Popen(command,cwd=P,env=env,stdout=stdout,stderr=stderr)
  write_sync(out/'child-started.json',{'pid':child.pid,'command':command,'attempt':1},True)
  while True:
   try:
    code=child.wait(timeout=config['observation_timeout_seconds']);break
   except subprocess.TimeoutExpired:
    observation_timeout_count+=1
    write_sync(out/f'observation-timeout-{observation_timeout_count:04d}.json',{'state':'OBSERVATION_TIMEOUT_NOT_TERMINAL','pid':child.pid,'observation_timeout_count':observation_timeout_count,'terminal_status_observed':False,'same_child_handle_preserved':True,'termination_performed':False,'restart_performed':False,'next_action':'Continue waiting on this same child; preserve all partial and raw output'},True)
 write_sync(out/'terminal.json',{'actual_child_exit':code,'observation_timeout_count':observation_timeout_count,'termination_performed':False,'same_child_handle_preserved':True,'stdout_sha256':H(out/'stdout.log'),'stderr_sha256':H(out/'stderr.log'),'attempt':1,'no_retry_performed':True},True)
 try:
  after=snapshot_graph();write_sync(out/'after.json',after,True);assert before==after;verify_plan(v.expected_seal)
  observation=json.loads((out/'observations.json').read_bytes());assert observation['node']==config['node_recorded_version'];assert len(observation['rows'])==10
  assert [r['id']for r in observation['rows']]==[r['id']for r in J('expected.json')['rows']]
  loaded=observation['loadedModules'];files=J('controls/all-module-files.json');assert all(files[r['file']]==r['sha256']for r in loaded)
  positives=[r for r,spec in zip(observation['rows'],J('expected.json')['rows'])if spec['fully_compared_if_constructed']];assert len(positives)==8;assert all(r['state']=='CONSTRUCTED'and r['differences']==[]and r['blockedBefore']==r['blockedAfter']for r in positives)
  assert code==0
  write_sync(out/'controller-result.json',{'state':'COMPLETE_OFFLINE_OBSERVATION_NOT_CONTRACT_ACCEPTANCE','actual_child_exit':code,'observation_timeout_count':observation_timeout_count,'termination_performed':False,'inputs_unchanged':True,'observations':10,'fully_compared_constructed_instructions':8,'omitted_baseMint_rows':[r for r,spec in zip(observation['rows'],J('expected.json')['rows'])if not spec['fully_compared_if_constructed']],'native_addon_observations':observation['addonAttempts'],'limits':'Synthetic inputs only; denied transport/API guards and genuine loader observer declared. No valid pool/mint/account state, full historical host/loader, target contract behavior or byte identity proof.'},True)
 except BaseException as error:
  write_sync(out/'controller-failure.json',{'state':'RETAINED_FAILURE_NO_RETRY','actual_child_exit':code,'observation_timeout_count':observation_timeout_count,'termination_performed':False,'error_type':type(error).__name__,'message':str(error)},True);raise
if __name__=='__main__':main()

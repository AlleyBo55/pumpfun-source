"""Future fixed twelve-side diagnostic; never invoke frozen harness main()."""
from pathlib import Path
import argparse,copy,hashlib,importlib.metadata,importlib.util,json,sys,traceback
sys.dont_write_bytecode=True
from common import P,J,H,durable,check_plan,supported_running_python
from saved_checks import validate_item,audit_transaction,analyze_observations
def run_all(helper,data,candidate,out,transaction_auditor=audit_transaction):
 rows=[];attempts=[];signature_rows=[];failure=None
 try:
  for index,spec in enumerate(data['rows']):
   row={'family':spec['family'],'variant':spec['variant'],'case':spec['case']}
   for side,binary in[('original',None),('candidate',candidate)]:
    marker={'case_index':index,'case':spec['case']['name'],'side':side,'target_call_count_in_this_side':1}
    durable(out/f'attempt-{index:02d}-{side}.json',marker);attempts.append(marker)
    item=helper.run(copy.deepcopy(spec['case']),binary)
    # Persist every returned field and full logs/transaction before interpretation.
    durable(out/f'side-{index:02d}-{side}.json',item)
    validate_item(item,spec['case']);signature_rows.append({**marker,**transaction_auditor(item)})
    row[side]=item
   rows.append(row)
  analysis=analyze_observations(rows,data)
 except BaseException:failure=traceback.format_exc();analysis=None
 finally:
  observation={'rows':rows,'attempts':attempts,'signature_audits':signature_rows,'analysis':analysis,'failure':failure,'partial_side_files_preserved':True,'vm_calls_attempted':len(attempts),'retry_attempts':0}
  durable(out/'observations.json',observation)
 return observation
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--execute',action='store_true');ap.add_argument('--expected-seal',required=True);ap.add_argument('--claim-sha256');args=ap.parse_args();cfg,data=check_plan(args.expected_seal,True)
 if not args.execute:print('READONLY driver preflight; helper/VM not imported');return 0
 supported_running_python(cfg);out=Path(cfg['out']);claim=Path(cfg['claim']);assert claim.is_file()and out.is_dir()and H(claim)==args.claim_sha256
 claim_data=J(claim);assert claim_data['plan_seal']==args.expected_seal and claim_data['controller_sha256']==H(P/'controller.py')and claim_data['driver_sha256']==H(Path(__file__))
 launch=J(out/'launch.json');assert launch['claim_sha256']==args.claim_sha256 and launch['plan_seal']==args.expected_seal
 assert importlib.metadata.version('solders')==cfg['solders']
 # Exactly the frozen five-module import graph, loaded only after durable claim.
 path=P/'repo/scripts/pump_admin_cto_differential.py';sys.path.insert(0,str(path.parent));spec=importlib.util.spec_from_file_location('frozen_admin_cto_helper',path);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
 observation=run_all(helper,data,Path(cfg['candidate_path']),out)
 check_plan(args.expected_seal,True)
 if observation['failure']:state='FAILED_PARTIAL_RAW_OBSERVATIONS_PRESERVED';code=2
 elif observation['analysis']['all_original_hypotheses_observed']:state='DIAGNOSTIC_OBSERVATIONS_RECORDED';code=0
 else:state='COUNTEREVIDENCE_PRESERVED';code=2
 durable(out/'driver-result.json',{'state':state,'returncode':code,'vm_calls_attempted':observation['vm_calls_attempted'],'target_sides_limit':12,'preservation_pass_claimed':False,'field_mapping_proven':False,'analysis':observation['analysis'],'failure':observation['failure']});print(state);return code
if __name__=='__main__':raise SystemExit(main())

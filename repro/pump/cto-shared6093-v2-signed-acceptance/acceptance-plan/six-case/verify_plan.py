"""Read-only source/seal preflight; no harness or native runtime imports."""
import argparse,json
from common import check_plan,fresh
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--expected-seal',required=True);p.add_argument('--offline',action='store_true');a=p.parse_args();cfg,data=check_plan(a.expected_seal,not a.offline);fresh(cfg)
 print(json.dumps({'state':'VERIFIED_UNEXECUTED_SIGNED_ORACLE_PLAN','cases':6,'sides':12,'helper_api':cfg['helper_api'],'input_files':15,'only_changes':'Target token amount/state108 plus case name','root_and_independent_review_still_required':True,'plan_preparation_VM_executions':0,'field_mapping_proven':False,'preservation_pass_claimed':False},indent=2))

"""Run a publication's passive verifier with exact directory-entry case checks.
Audit-hook `open` covers builtins.open, io.open/Path.open, and importlib reads.
Only opens beneath the declared publication (casefold scope) are constrained;
trusted Python/runtime/crypto module reads elsewhere are outside this guard.
No archive/controller/VM/build code is invoked by this wrapper.
"""
from pathlib import Path
import argparse,json,os,runpy,sys,traceback
sys.dont_write_bytecode=True
ap=argparse.ArgumentParser();ap.add_argument('--publication-root',required=True);ap.add_argument('--expected-seal',required=True);ap.add_argument('--crypto',action='store_true');ap.add_argument('--observation',required=True);args=ap.parse_args()
root=os.path.abspath(args.publication_root);prefix=root.rstrip(os.sep)+os.sep;reads=[];violations=[]
def exact_components(path):
 # Do not resolve(), exists(), or case-normalize: compare requested names with
 # actual directory entry strings. Missing/miscased components fail closed.
 absolute=os.path.abspath(path);current=os.path.sep
 for component in Path(absolute).parts[1:]:
  entries=os.listdir(current)
  if component not in entries:
   alternatives=[n for n in entries if n.casefold()==component.casefold()]
   return {'requested_path':absolute,'parent':current,'requested_component':component,'casefold_matching_actual_entries':alternatives,'reason':'Component spelling is absent from actual directory entries'}
  current=os.path.join(current,component)
 return None
problem=exact_components(root)
if problem:raise FileNotFoundError(json.dumps(problem,sort_keys=True))
def audit(event,arguments):
 if event!='open'or not isinstance(arguments[0],(str,bytes,os.PathLike)):return
 path=os.path.abspath(os.fsdecode(arguments[0]));in_scope=path.casefold()==root.casefold()or path.casefold().startswith(prefix.casefold())
 if not in_scope:return
 violation=exact_components(path)
 if violation:
  violations.append(violation);raise FileNotFoundError('EXACT_CASE_READ_REJECTED '+json.dumps(violation,sort_keys=True))
 reads.append({'requested_path':path,'mode':arguments[1],'flags':arguments[2],'exact_entry_spelling':True})
sys.addaudithook(audit);status='FAILED';failure=None;returncode=1
try:
 sys.path.insert(0,root);sys.argv=[os.path.join(root,'verify.py'),'--expected-seal',args.expected_seal]+(['--crypto']if args.crypto else[])
 runpy.run_path(sys.argv[0],run_name='__main__')
 if violations:raise AssertionError('Verifier caught a rejected alias read; case violations remain failures')
 status='PASS_EXACT_CASE_PORTABLE_VERIFIER';returncode=0
except BaseException:
 failure=traceback.format_exc();sys.stderr.write(failure)
finally:
 observation={'state':status,'publication_root':root,'expected_seal':args.expected_seal,'crypto_requested':args.crypto,'returncode':returncode,'exact_case_publication_open_count':len(reads),'violations':violations,'publication_opens':reads,'failure':failure,'guard_scope':'Every publication-scoped open checks every requested path component against actual directory-entry strings; no exists/resolve/casealias workaround','runtime_reads_elsewhere':'Trusted Python/stdcrypto runtime paths excluded; this guard is not a network/VM sandbox','target_VM_compiler_original_decoder_invocations_by_wrapper':0}
 Path(args.observation).write_text(json.dumps(observation,indent=2)+'\n')
raise SystemExit(returncode)

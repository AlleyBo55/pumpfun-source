"""Exact bundled path case + deny stale external user-workspace reads.
Run only the documented passive verifier; optional crypto verifies saved records.
This observes Python-level opens/stat/listing/readlink, not full native loader IO.
"""
from pathlib import Path
import argparse,hashlib,importlib.metadata,json,os,runpy,site,sys,sysconfig,traceback
sys.dont_write_bytecode=True
ap=argparse.ArgumentParser();ap.add_argument('--publication-root',required=True);ap.add_argument('--expected-seal',required=True);ap.add_argument('--crypto',action='store_true');ap.add_argument('--observation',required=True);a=ap.parse_args()
root=os.path.abspath(a.publication_root);observation_path=os.path.abspath(a.observation);guard_file=os.path.abspath(__file__)
def under(path,base):return path==base or path.startswith(base.rstrip(os.sep)+os.sep)
trusted=set()
for value in[sys.prefix,sys.base_prefix,*site.getsitepackages(),sysconfig.get_path('stdlib'),sysconfig.get_path('platstdlib'),sysconfig.get_path('purelib'),sysconfig.get_path('platlib')]:
 if value:
  trusted.add(os.path.abspath(value));trusted.add(str(Path(value).resolve()))
# Reject accidental broad allowlist entries; no generic home/workspace root.
for base in trusted:assert base not in['/','/Users','/Users/shawwalters','/Users/shawwalters/Documents','/Users/shawwalters/Documents/Codex']
trusted=sorted(trusted);ancestors={str(p)for p in Path(root).parents};opens=[];runtime_reads=[];metadata=[];violations=[];internal_case_lookup=False
original_stat,original_lstat,original_readlink=os.stat,os.lstat,os.readlink

def pathvalue(value):
 if isinstance(value,int):return None
 if not isinstance(value,(str,bytes,os.PathLike)):return None
 return os.path.abspath(os.fsdecode(value))
def exact(path):
 global internal_case_lookup
 internal_case_lookup=True
 try:
  current=os.path.sep
  for component in Path(path).parts[1:]:
   names=os.listdir(current)
   if component not in names:
    alternatives=[n for n in names if n.casefold()==component.casefold()]
    return {'kind':'CASE_MISMATCH'if alternatives else'MISSING_COMPONENT','requested_path':path,'parent':current,'component':component,'actual_casefold_matches':alternatives}
   current=os.path.join(current,component)
 finally:internal_case_lookup=False
 return None

def classify(path,operation,write=False):
 if path is None:return
 bundled=under(path.casefold(),root.casefold())
 if write:
  if path==observation_path:return
  violation={'kind':'UNAUTHORIZED_WRITE','path':path,'operation':operation};violations.append(violation);raise PermissionError(str(violation))
 if bundled:
  problem=exact(path)
  if problem:
   if problem['kind']=='MISSING_COMPONENT':return # Ordinary failed import/stat probe; no file read occurs.
   violations.append(problem);raise FileNotFoundError('EXACT_CASE_READ_REJECTED '+json.dumps(problem,sort_keys=True))
  (opens if operation=='open'else metadata).append({'path':path,'operation':operation,'exact_entry_spelling':True});return
 if any(under(path,base)for base in trusted)or path==guard_file:
  runtime_reads.append({'path':path,'operation':operation});return
 # Ancestors are allowed for directory navigation only, never file opens.
 if operation in['listdir','scandir','stat','lstat','readlink']and path in ancestors:return
 if under(path,'/Users'):
  violation={'kind':'EXTERNAL_USER_WORKSPACE_READ','path':path,'operation':operation};violations.append(violation);raise PermissionError('STALE_WORKSPACE_READ_REJECTED '+json.dumps(violation,sort_keys=True))
 # Non-user OS/runtime paths are outside workspace denial; record rather than
 # claiming complete OS/native-loader identity.
 runtime_reads.append({'path':path,'operation':operation,'outside_user_tree':True})

def audit(event,args):
 if event=='open':
  flags=args[2];write=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND));classify(pathvalue(args[0]),'open',write)
 elif event in['os.listdir','os.scandir']and not internal_case_lookup:classify(pathvalue(args[0]),event[3:])
def checked_stat(path,*args,**kwargs):classify(pathvalue(path),'stat');return original_stat(path,*args,**kwargs)
def checked_lstat(path,*args,**kwargs):classify(pathvalue(path),'lstat');return original_lstat(path,*args,**kwargs)
def checked_readlink(path,*args,**kwargs):classify(pathvalue(path),'readlink');return original_readlink(path,*args,**kwargs)
problem=exact(root)
if problem:raise FileNotFoundError(json.dumps(problem))
sys.addaudithook(audit);os.stat=checked_stat;os.lstat=checked_lstat;os.readlink=checked_readlink
state='FAILED';failure=None;code=1
try:
 sys.path.insert(0,root);sys.argv=[root+'/verify.py','--expected-seal',a.expected_seal]+(['--crypto']if a.crypto else[])
 runpy.run_path(sys.argv[0],run_name='__main__')
 if violations:raise AssertionError('Caught access violations still fail the guard')
 state='PASS_CASE_CORRECT_BUNDLED_READS_NO_STALE_USER_WORKSPACE_ACCESS';code=0
except BaseException:
 failure=traceback.format_exc();sys.stderr.write(failure)
finally:
 result={'state':state,'publication_root':root,'expected_seal':a.expected_seal,'crypto_requested':a.crypto,'returncode':code,'trusted_python_runtime_roots':trusted,'trusted_guard_source_file':guard_file,'bundled_open_count':len(opens),'bundled_metadata_operation_count':len(metadata),'trusted_runtime_operation_count':len(runtime_reads),'violations':violations,'bundled_opens':opens,'bundled_metadata':metadata,'runtime_reads':runtime_reads,'failure':failure,'limitations':'Python-level filesystem observations only; not universal native-loader/system-library identity or security sandbox','VM_compiler_original_decoder_invocations_by_wrapper':0}
 Path(observation_path).write_text(json.dumps(result,indent=2)+'\n')
raise SystemExit(code)

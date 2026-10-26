"""Guard passive verifier's user-file reads to its own publication."""
from pathlib import Path
import os,runpy,sys
R=Path(__file__).resolve().parent.parent/'anchor031-macro-version-audit';seen=[]
def guard(event,args):
 if event!='open'or not isinstance(args[0],(str,bytes,os.PathLike)):return
 q=Path(os.path.abspath(os.fsdecode(args[0])))
 if str(q).startswith('/Users/shawwalters/'):
  if not q.is_relative_to(R):raise PermissionError('External private root forbidden: '+str(q))
  seen.append(str(q.relative_to(R)))
sys.addaudithook(guard);sys.argv=[str(R/'verify.py'),'--expected-seal','d88372caef6c64996b49e5063af87dd52bd16f18d2575ec35c19d2b1cc6f11df'];runpy.run_path(str(R/'verify.py'),run_name='__main__');print('GUARDED PASS',len(seen),'user-file reads confined to publication')

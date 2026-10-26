"""Stdlib-only plan checks/writes. No helper, solders or VM import."""
from pathlib import Path,PurePosixPath
import ast,copy,hashlib,json,os,stat,sys
P=Path(__file__).resolve().parent
J=lambda p:json.loads(p.read_text())
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def durable(path,obj):
 data=(json.dumps(obj,indent=2)+'\n').encode()
 with path.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
 fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def no_symlink_path(path):
 for q in[path,*path.parents]:assert not q.is_symlink(),str(q)
def check_plan(seal,live=True):
 assert __debug__,'Use Python without -O'
 assert H(P/'manifest.json')==seal
 m=J(P/'manifest.json');assert not any(q.is_symlink()for q in P.rglob('*'))
 assert set(m)|{'manifest.json','manifest.sha256'}=={str(q.relative_to(P))for q in P.rglob('*')if q.is_file()}
 assert(P/'manifest.sha256').read_text().strip()==seal
 for n,h in m.items():
  rel=PurePosixPath(n);assert not rel.is_absolute()and'..'not in rel.parts;assert H(P/n)==h,n
 cfg=J(P/'plan.json');prior=J(P/'controls/preservation-manifest.json');assert H(P/'controls/preservation-manifest.json')==cfg['prior_plan_seal']=='58b09002d2f1562b702db7e09ca2b905fae305157448b9e6a1eaf8fd540da2b6'
 for n in['inputs.json','source37.json','build-controller-result.json','build-plan-manifest.json','python-environment.json','python-preflight.stdout','python-preflight.stderr']:assert H(P/'controls'/('preservation-'+n))==prior[n]
 inputs=J(P/'controls/preservation-inputs.json');assert len(inputs)==15 and set(inputs)=={str(q.relative_to(P/'repo'))for q in(P/'repo').rglob('*')if q.is_file()}
 for n,h in inputs.items():assert H(P/'repo'/n)==h==prior['repo/'+n],n
 assert H(P/'prior/receipt.json')==cfg['prior_receipt_sha256']=='ec1c1e658a98d7dae949c02f0c9648beaa17f7eea820d4d2f401f512a71e4cba'
 old=J(P/'prior/receipt.json');old_exit=J(P/'prior/exit.json');assert old['case_count']==len(old['cases'])==363 and old['candidate_sha256']==cfg['candidate_sha256']and old_exit['passed']is True and old_exit['receipt_json_sha256']==H(P/'prior/receipt.json')
 for n in['stdout.log','stderr.log']:assert H(P/'prior'/n)==old_exit[n.replace('.','_')+'_sha256']
 data=J(P/'cases.json');assert cfg['cases']==len(data['rows'])==6 and cfg['sides']==12 and cfg['retries_permitted']==0
 assert set(data['families'])=={'A','B'}and data['families']['A']['baseline_case_name']=='shared-amm-True-1000000'and data['families']['B']['baseline_case_name']=='stable-7'
 assert[(r['family'],r['variant'])for r in data['rows']]==[(f,v)for f in['A','B']for v in['baseline','frozen-positive','frozen-zero']]
 for row in data['rows']:
  family=data['families'][row['family']];base=next(x['case']for x in old['cases']if x['case']['name']==family['baseline_case_name']);expected=copy.deepcopy(base)
  if row['variant']!='baseline':
   expected['name']+='-'+row['variant'];expected['accounts'][family['target_field']]['patches']=[[108,'02']]
   if row['variant']=='frozen-zero':expected['accounts'][family['target_field']]['tokens']=0
  assert row['case']==expected and base['holder']is True and base['new_none']is True
 assert data['families']['A']['target_field']=='coin_creator_vault_ata'and data['families']['A']['positive_origin_hypothesis']==660
 assert data['families']['B']['target_field']=='creator_vault_quote_token_account'and data['families']['B']['positive_origin_hypothesis']==719
 tree=ast.parse((P/'repo/scripts/pump_admin_cto_differential.py').read_text());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='run');assert[a.arg for a in fn.args.args]==['c','binary']and isinstance(fn.args.defaults[0],ast.Constant)and fn.args.defaults[0].value is None
 for q in P.glob('*.py'):ast.parse(q.read_text())
 build=J(P/'controls/preservation-build-controller-result.json');assert build['source_after']==J(P/'controls/preservation-source37.json')and len(build['source_after'])==37
 assert build['proposal_manifest']==H(P/'controls/preservation-build-plan-manifest.json')=='ff7a857b5394b57c61eebb19cf6265fa001b18b2d0f3db4936fd00c48cbb2fa0'
 py=J(P/'controls/preservation-python-environment.json');assert cfg['python']==py['python_path']and cfg['python_binary_sha256']==py['binary_sha256']and py['observed']['version'].startswith(cfg['python_version_prefix'])and py['observed']['solders']==cfg['solders']
 probe=J(P/'metadata/python-preflight.json');assert probe['returncode']==0 and probe['observed']['version'].startswith(cfg['python_version_prefix'])and probe['observed']['solders']==cfg['solders']and probe['observed']['solders_imported']is False
 for key in['stdout','stderr']:assert H(P/'metadata'/('python-preflight.'+key))==probe[key+'_sha256']
 if live:
  for name in['candidate_path','build_source_root','out','claim']:no_symlink_path(Path(cfg[name]))
  assert H(Path(cfg['candidate_path']))==cfg['candidate_sha256']
  assert H(Path(cfg['python']).resolve())==cfg['python_binary_sha256']and str(Path(cfg['python']).resolve())==py['resolved_python_path']
  for n,h in build['source_after'].items():assert H(Path(cfg['build_source_root'])/n)==h
 return cfg,data
def fresh(cfg):
 for key in['out','claim']:assert not Path(cfg[key]).exists(),'Existing attempt; never retry'
def supported_running_python(cfg):
 assert sys.version.startswith(cfg['python_version_prefix'])and Path(sys.executable).resolve()==Path(cfg['python']).resolve()and H(Path(sys.executable).resolve())==cfg['python_binary_sha256'],'Execute only through the pinned existing Python3.12 interpreter'

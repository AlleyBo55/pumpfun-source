"""Supplemental gate for exact emitted/root admission; stdlib checks only."""
from pathlib import Path,PurePosixPath
import hashlib,json,os
P=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
J=lambda p:json.loads(p.read_text())
def no_links(path):
 for q in[path,*path.parents]:assert not q.is_symlink(),str(q)
def check_members(root,filename,seal):
 assert __debug__
 assert H(root/filename)==seal
 m=J(root/filename);m=m.get('files',m)
 assert not any(f.is_symlink()for f in root.rglob('*'))
 actual={str(f.relative_to(root))for f in root.rglob('*')if f.is_file()}
 extras={filename}
 if(root/'manifest.sha256').exists():extras.add('manifest.sha256');assert(root/'manifest.sha256').read_text().split()[0]==seal
 assert actual==set(m)|extras
 for name,row in m.items():
  rel=PurePosixPath(name);assert not rel.is_absolute()and'..'not in rel.parts;f=root/name
  assert H(f)==(row if isinstance(row,str)else row['sha256'])
  if isinstance(row,dict)and'bytes'in row:assert f.stat().st_size==row['bytes']
 return m
def plan_check(seal,fresh=True):
 check_members(P,'manifest.json',seal);cfg=J(P/'plan.json');inputs=J(P/'inputs.json');assert len(inputs)==15
 assert set(inputs)=={str(f.relative_to(P/'repo'))for f in(P/'repo').rglob('*')if f.is_file()}
 for name,h in inputs.items():assert H(P/'repo'/name)==h
 old=J(P/'predecessor-controls/manifest.json');assert H(P/'predecessor-controls/manifest.json')==cfg['prior_plan_seal']
 for n,h in inputs.items():assert old['repo/'+n]==h
 build=J(P/'current-controls/controller-result.json');source=J(P/'current-controls/source37.json');assert build['state']=='requires-cache-review'and build['helper_exit']==build['build_sbf_aggregate_exit']==0 and build['compiler_child_exit']is None and build['strip_child_exit']is None
 assert build['source_unchanged']and source==build['source_after']and len(source)==37 and source['programs/pump/src/admin_cto.rs']==cfg['candidate_source_CTO']
 assert H(P/'current-controls/build-plan-manifest.json')==build['proposal_manifest']==cfg['build_plan_seal']=='29069875549ea325beeafc10059c6893218211c327d08a6f90bce70df10e5ae2'
 assert H(P/'current-controls/source37.json')==cfg['source37_sha256']
 assert H(Path(cfg['build_path'])/'controller-result.json')==H(P/'current-controls/controller-result.json')
 if cfg['lane']=='six-case':
  oracle=J(P/'oracle-plan.json')
  for key in ['candidate_path','candidate_sha256','build_source_root','out','claim','python','python_binary_sha256','prior_candidate_sha256']:assert cfg[key]==oracle[key],key
 no_links(Path(cfg['candidate_path']));no_links(Path(cfg['build_source_root']))
 for n,h in source.items():
  no_links(Path(cfg['build_source_root'])/n);assert H(Path(cfg['build_source_root'])/n)==h
 assert H(Path(cfg['candidate_path']))==cfg['candidate_sha256']=='fdfdb5f27af9b8c22effd48ea523c06bd037ceedf49df0da8178cad19eed38f5'
 assert H(Path(cfg['python']).resolve())==cfg['python_binary_sha256']
 for name in['out','claim','gate_output']:
  path=Path(cfg[name]);no_links(path)
  if fresh:assert not path.exists(),'Existing attempt; never retry'
 return cfg
def check_admission(cfg,emitted_seal,root_admission_sha,plan_seal):
 work=P.parents[1];review=work/'cto-shared6093-v2-emitted-independent-review';root=work/'cto-shared6093-v2-root-runtime-admission.json'
 no_links(review);no_links(root);check_members(review,'manifest.json',emitted_seal);assert H(root)==root_admission_sha
 emitted=J(review/'review.json');assert emitted['state']=='PASS_BOUNDED_SHARED_V2_EMITTED_SEQUENCE_REVIEW_NOT_SEMANTIC_CERTIFICATION' and emitted['candidate_sha256']==cfg['candidate_sha256'] and emitted['symbols_sha256']=='1e088e9add0218ebf6745a7f7557a4dc55dc68e86ec97790584db7f169c14bc3' and emitted['raw_outputs_plan_unchanged']is True
 assert H(Path(cfg['build_path'])/'build-01/target/sbf-solana-solana/release/pump_recovered.so')==emitted['symbols_sha256']
 cache=work/'cto-shared6093-v2-cache-review';no_links(cache);check_members(cache,'manifest.json','4d0b0e35067703be30a3945d7a1f9db12870e7525fb61f283754449c698de9fe')
 doc=J(root);assert doc['state']=='ROOT_APPROVED_FINITE_V2_RUNTIME_AFTER_EMITTED_REVIEW'
 for key,value in{'candidate_sha256':cfg['candidate_sha256'],'source_CTO_sha256':cfg['candidate_source_CTO'],'source37_sha256':cfg['source37_sha256'],'build_plan_seal':cfg['build_plan_seal'],'cache_review_seal':'4d0b0e35067703be30a3945d7a1f9db12870e7525fb61f283754449c698de9fe','emitted_review_seal':emitted_seal}.items():assert doc[key]==value,key
 assert cfg['lane']in doc['approved_lanes']and doc['plan_seals'][cfg['lane']]==plan_seal and doc['whole_byte_identity_claimed']is False
 return {'root_admission_sha256':root_admission_sha,'emitted_review_seal':emitted_seal,'root_admission_path':str(root),'emitted_review_path':str(review)}
def durable(path,obj):
 with path.open('x')as f:json.dump(obj,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)

from pathlib import Path
import tempfile,json,hashlib,os,shutil,subprocess,sys
from common import *
import package,verify_stream
passed=[]
def reject(name,fn):
 try:fn()
 except (ValueError,AssertionError,OSError):passed.append(name);return
 raise AssertionError('accepted '+name)
with tempfile.TemporaryDirectory(prefix='p29-synthetic-')as td:
 d=Path(td).resolve();root=d/'group';root.mkdir();(root/'empty').mkdir();(root/'run.py').write_bytes(b'opaque not executed\n');(root/'run.py').chmod(0o751);(root/'raw').write_bytes(bytes(range(256))*12);(root/'deep').mkdir();(root/'deep/data.txt').write_bytes(b'bytes\x00\xff')
 m={str(p.relative_to(root)):digest_file(p)for p in root.rglob('*')if p.is_file()};(root/'manifest.json').write_text(json.dumps({'files':m},indent=2)+'\n');seal=H((root/'manifest.json').read_bytes());(root/'manifest.sha256').write_text(seal+'  manifest.json\n');rows=[{'group':'synthetic','path':str(root),'manifest_sha256':seal}]
 a=package.package(rows,d/'a',limit=128);b=package.package(rows,d/'b',limit=128);assert a==b;assert len(a['archive']['parts'])>1;assert verify_stream.stream(d/'a',a,rows)['groups']==1;passed.extend(['rawmodes_emptydirectories_stream','deterministic_repeat_and_multipart'])
 bad=json.loads(json.dumps(a));bad['groups'][0]['members']['run.py']['mode']=0o644;reject('wrongmode',lambda:verify_stream.stream(d/'a',bad,rows))
 bad=json.loads(json.dumps(a));bad['groups'][0]['manifest_sha256']='0'*64;reject('wrongknowninnerseal',lambda:verify_stream.stream(d/'a',bad,rows))
 part=d/'a'/a['archive']['parts'][0]['path'];raw=part.read_bytes();part.write_bytes(bytes([raw[0]^1])+raw[1:]);reject('partcorruption',lambda:verify_stream.stream(d/'a',a,rows));part.write_bytes(raw)
 (root/'extra').write_text('x');reject('unmanifested',lambda:authenticate_group(rows[0]));(root/'extra').unlink()
 (root/'__pycache__').mkdir();reject('cache_directory',lambda:authenticate_group(rows[0]));(root/'__pycache__').rmdir()
 (root/'link').symlink_to('raw');reject('symlink',lambda:authenticate_group(rows[0]));(root/'link').unlink()
 reject('missinggroup',lambda:authenticate_group(dict(rows[0],path=str(d/'missing'))))
 # CLI pre-existing refusal must never write failure logs into an unowned directory.
 cli=d/'synthetic-plan';cli.mkdir()
 for name in['package.py','common.py','verify_stream.py']:shutil.copyfile(Path(__file__).parent/name,cli/name)
 (cli/'groups.json').write_text(json.dumps(rows))
 pm={f.name:H(f.read_bytes())for f in cli.iterdir()if f.is_file()};(cli/'manifest.json').write_text(json.dumps(pm));ph=H((cli/'manifest.json').read_bytes());(cli/'manifest.sha256').write_text(ph+'  manifest.json\n')
 sentinel=d/'preexisting';sentinel.mkdir();(sentinel/'keep').write_bytes(b'unrelated immutable bytes');before={f.name:f.read_bytes()for f in sentinel.iterdir()};r=subprocess.run([sys.executable,'-B',str(cli/'package.py'),'--reviewed-plan-sha256',ph,'--output',str(sentinel),'--execute'],capture_output=True);assert r.returncode!=0 and {f.name:f.read_bytes()for f in sentinel.iterdir()}==before;passed.append('CLI preexisting output sentinel unchanged')
 reject('unsafe group name',lambda:package.package([dict(rows[0],group='../escape')],d/'unsafe'))
 reject('source output overlap',lambda:package.package(rows,root/'nestedoutput'))
 print(json.dumps({'status':'PASS_SYNTHETIC_ONLY','cases':passed,'real_group_packager_runs':0,'archived_code_executions':0,'decoder_build_VM_calls':0}))

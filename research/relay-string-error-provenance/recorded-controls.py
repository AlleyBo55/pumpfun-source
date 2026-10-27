from pathlib import Path
import subprocess,json,re
p=Path.cwd()/'work/relay-typeid-20261026';rust=Path.home()/'.cache/solana/v1.48/platform-tools/rust/bin/rustc';rows=[]
for name,flags in [('cargo-name',['--crate-name','donation_relay_source_proposal']),('cargo-remap',['--crate-name','donation_relay_source_proposal','-Zremap-cwd-prefix=']),('metadata',['--crate-name','donation_relay_source_proposal','-C','metadata=1234','-Zremap-cwd-prefix=']),('abort',['-C','panic=abort']),('overflow',['-C','panic=abort','-C','overflow-checks=on']),('legacy-target',[])]:
 target='sbf-solana-solana' if name=='legacy-target' else 'sbpf-solana-solana'
 cmd=[str(rust),'--crate-type','lib','--edition','2021','-C','opt-level=3','--target',target,'--emit','asm',str(p/'probe.rs'),'-o',str(p/(name+'.s'))]+flags
 r=subprocess.run(cmd,capture_output=True,text=True);a=(p/(name+'.s')).read_text() if r.returncode==0 else '';x=re.search(r'(_ZN\w+Error7type_id[^:\n]*):\n(.*?)\.Lfunc_end',a,re.S);vals=re.findall(r'lddw r\d+, (-?\d+)',x[2]) if x else []
 rows.append(dict(name=name,command=cmd,returncode=r.returncode,stderr=r.stderr,halves=[hex(int(v)%(1<<64)) for v in vals]));print(name,rows[-1]['halves'])
(p/'controls.json').write_text(json.dumps(rows,indent=2)+'\n')

from pathlib import Path
import subprocess,json,re,hashlib,os
out=Path.cwd()/'work/relay-typeid-20261026/matrix';out.mkdir(exist_ok=True);source=out.parent/'probe.rs';records=[]
for sdk in sorted((Path.home()/'.cache/solana').glob('*/platform-tools')):
    rustc=sdk/'rust/bin/rustc'
    if not rustc.exists():continue
    version=subprocess.run([str(rustc),'-vV'],capture_output=True,text=True).stdout
    targets=subprocess.run([str(rustc),'--print','target-list'],capture_output=True,text=True).stdout.splitlines()
    for target in ['sbf-solana-solana','sbpf-solana-solana']:
        if target not in targets:continue
        d=out/(sdk.parent.name+'-'+target);d.mkdir(exist_ok=True)
        cmd=[str(rustc),'--crate-name','relay_typeid_probe','--crate-type','lib','--edition','2021','-C','opt-level=3','-C','panic=abort','-C','overflow-checks=on','-Zremap-cwd-prefix=','--target',target,'--emit','asm',str(source),'-o',str(d/'probe.s')]
        env=dict(os.environ)
        for k in ['RUSTFLAGS','RUSTUP_TOOLCHAIN','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER']:env.pop(k,None)
        p=subprocess.run(cmd,capture_output=True,text=True,env=env);(d/'build.log').write_text(p.stdout+p.stderr);(d/'rustc-version.txt').write_text(version)
        asm=(d/'probe.s').read_text() if p.returncode==0 else ''
        x=re.search(r'(_ZN\w+Error7type_id[^:\n]*):\n(.*?)\.Lfunc_end',asm,re.S)
        vals=re.findall(r'lddw r\d+, (-?\d+)',x[2]) if x else []
        libs=sdk/'rust/lib/rustlib'/target/'lib'
        hashes={str(q.relative_to(sdk)):hashlib.sha256(q.read_bytes()).hexdigest() for pat in ['libstd-*.rlib','liballoc-*.rlib','libcore-*.rlib'] for q in sorted(libs.glob(pat))}
        rec=dict(sdk=sdk.parent.name,target=target,command=cmd,returncode=p.returncode,rustc_sha256=hashlib.sha256(rustc.read_bytes()).hexdigest(),sysroot_hashes=hashes,typeid_halves=[hex(int(v)%(1<<64)) for v in vals],directory=d.name)
        records.append(rec);print(d.name,rec['typeid_halves'],flush=True)
(out/'results.json').write_text(json.dumps(records,indent=2)+'\n')

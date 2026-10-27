from pathlib import Path
import shutil,subprocess,json,importlib.util
p=Path('work/relay-residual-20261026').resolve();source=p/'source-shared-direct';shutil.copytree(p/'source-482',source,dirs_exist_ok=True);original=(source/'src/shared_donation.rs').read_text()
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-shared-direct'").replace("mode.startswith('jupiter-')","mode.startswith('shared-direct-')");(p/'build_shared_direct.py').write_text(driver)
s=importlib.util.spec_from_file_location('sd','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
variants=[('mint',True,False,False),('from',False,True,False),('program',False,False,True),('mint-from',True,True,False),('mint-program',True,False,True),('from-program',False,True,True),('all',True,True,True)];rows=[]
for name,mint,from_account,program in variants:
 mode='shared-direct-'+name;d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 text=original
 if mint:text=text.replace('mint:ctx.mint.clone()','mint:ctx.mint')
 if from_account:text=text.replace('from:ctx.from_token_account.clone()','from:ctx.from_token_account')
 if program:text=text.replace('CpiContext::new(ctx.token_program.clone(),','CpiContext::new(ctx.token_program,')
 (source/'src/shared_donation.rs').write_text(text);(d/'shared_donation.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_shared_direct.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode)
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text();target=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes()).function(131136,10248,[]);elf=a.Elf((d/'symbols.so').read_bytes());v=next(x for x in elf.symbols if '13donate_shared17h'in x['name']);f=elf.function(v['start'],v['size'],[]);row.update(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'shared-direct-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

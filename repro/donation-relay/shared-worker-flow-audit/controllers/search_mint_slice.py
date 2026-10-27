from pathlib import Path
import shutil,subprocess,json,importlib.util
p=Path('work/relay-residual-20261026').resolve();source=p/'source-mint-slice';shutil.copytree(p/'source-482',source,dirs_exist_ok=True);original=(source/'src/shared_donation.rs').read_text()
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-mint-slice'").replace("mode.startswith('jupiter-')","mode.startswith('mint-slice-')");(p/'build_mint_slice.py').write_text(driver)
s=importlib.util.spec_from_file_location('ms','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);rows=[]
start=original.index(' {\n  let info=ctx.mint.clone();');end=original.index('\n let tracker=',start);block=original[start:end]
body=block.replace(' {\n  let info=ctx.mint.clone();let owner=*info.owner;','\n  let mint=*info.key;let owner=*info.owner;').replace('ctx.mint_whitelist.mints.contains(&mint)','mints.contains(&mint)')[:-2]+'\n Ok(())\n}'
variants={}
for attr,name in [('', 'helper-auto'),('#[inline(always)]\n','helper-inline')]:
 helper=attr+'fn check_donation_mint(info:AccountInfo,mints:&[Pubkey])->Result<()> {'+body+'\n'
 variants[name]=original[:start]+'\n check_donation_mint(ctx.mint.clone(),&ctx.mint_whitelist.mints)?;'+original[end:]+'\n'+helper
for shadow in (False,True):
 newblock=block.replace('let info=ctx.mint.clone();let owner=*info.owner;','let info=ctx.mint.clone();let mints:&[Pubkey]=&ctx.mint_whitelist.mints;let owner=*info.owner;'+('let mint=*info.key;'if shadow else '')).replace('ctx.mint_whitelist.mints.contains(&mint)','mints.contains(&mint)')
 variants['local-'+str(int(shadow))]=original[:start]+newblock+original[end:]
for name,text in variants.items():
 mode='mint-slice-'+name;d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 (source/'src/shared_donation.rs').write_text(text);(d/'shared_donation.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_mint_slice.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode)
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text();target=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes()).function(131136,10248,[]);e=a.Elf((d/'symbols.so').read_bytes());v=next(x for x in e.symbols if '13donate_shared17h'in x['name']);f=e.function(v['start'],v['size'],[]);row.update(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'mint-slice-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

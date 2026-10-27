from pathlib import Path
import shutil,subprocess,json,importlib.util
p=Path('work/relay-residual-20261026').resolve();source=p/'source-jupiter-option';shutil.copytree(p/'source-location-combined',source,dirs_exist_ok=True);base=(source/'src/settlement_handlers.rs').read_text().replace('let infos=remaining.to_vec();','let infos=remaining.iter().cloned().collect::<Vec<_>>();')
base=base.replace('invoke_jupiter(program.key(),authority,remaining,data,seeds)?','invoke_jupiter(program.key(),authority,remaining,data,Some(seeds))?')
base=base.replace("pub fn invoke_jupiter<'info>(program:Pubkey,authority:Pubkey,remaining:&[AccountInfo<'info>],data:Vec<u8>,seeds:&[&[&[u8]]])", "pub fn invoke_jupiter<'info>(program:Pubkey,authority:Pubkey,remaining:&[AccountInfo<'info>],data:Vec<u8>,seeds:Option<&[&[&[u8]]]>)")
old='if seeds.is_empty() {anchor_lang::solana_program::program::invoke(&ix,&infos)?;} else {anchor_lang::solana_program::program::invoke_signed(&ix,&infos,seeds)?;}Ok(())'
variants={'if-some':'if let Some(seeds)=seeds {anchor_lang::solana_program::program::invoke_signed(&ix,&infos,seeds)?;} else {anchor_lang::solana_program::program::invoke(&ix,&infos)?;}Ok(())','match':'match seeds {Some(seeds)=>anchor_lang::solana_program::program::invoke_signed(&ix,&infos,seeds)?,None=>anchor_lang::solana_program::program::invoke(&ix,&infos)?};Ok(())'}
s=importlib.util.spec_from_file_location('joa','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-jupiter-option'");(p/'build_jupiter_option.py').write_text(driver);rows=[]
for name,branch in variants.items():
 mode='jupiter-option-'+name;d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 assert base.count(old)==1;text=base.replace(old,branch);(source/'src/settlement_handlers.rs').write_text(text);(d/'settlement_handlers.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_jupiter_option.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode)
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text()
  target=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes()).function(64824,2496,[]);elf=a.Elf((d/'symbols.so').read_bytes());v=next(x for x in elf.symbols if '14invoke_jupiter17h'in x['name']);f=elf.function(v['start'],v['size'],[]);row.update(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'jupiter-option-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

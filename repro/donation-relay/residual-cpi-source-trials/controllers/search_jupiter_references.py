from pathlib import Path
import shutil,subprocess,json,importlib.util
p=Path('work/relay-residual-20261026').resolve();source=p/'source-jupiter-references';shutil.copytree(p/'source-location-combined',source,dirs_exist_ok=True);base=(source/'src/settlement_handlers.rs').read_text().replace('let infos=remaining.to_vec();','let infos=remaining.iter().cloned().collect::<Vec<_>>();')
s=importlib.util.spec_from_file_location('ja','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);target=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes()).function(64824,2496,[])
driver=(p/'build_burn_close.py').read_text().replace("source-burn-close'","source-jupiter-references'").replace("mode.startswith('burn-close-')","mode.startswith('jupiter-references-')");(p/'build_jupiter_references.py').write_text(driver);rows=[]
for name,program_ref,authority_ref in [('authority',False,True),('program',True,False),('both',True,True)]:
 mode='jupiter-references-'+name;d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 text=base
 if authority_ref:
  text=text.replace("invoke_jupiter<'info>(program:Pubkey,authority:Pubkey,", "invoke_jupiter<'info>(program:Pubkey,authority:&Pubkey,").replace('invoke_jupiter(program.key(),authority,','invoke_jupiter(program.key(),&authority,').replace('a.key==&authority','a.key==authority')
 if program_ref:
  text=text.replace("invoke_jupiter<'info>(program:Pubkey,", "invoke_jupiter<'info>(program:&Pubkey,").replace('invoke_jupiter(program.key(),','invoke_jupiter(&program.key(),').replace('Instruction {program_id:program,','Instruction {program_id:*program,')
 (source/'src/settlement_handlers.rs').write_text(text);(d/'settlement_handlers.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_jupiter_references.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode)
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text()
  elf=a.Elf((d/'symbols.so').read_bytes());v=next(x for x in elf.symbols if '14invoke_jupiter17h'in x['name']);f=elf.function(v['start'],v['size'],[]);row.update(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'jupiter-references-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

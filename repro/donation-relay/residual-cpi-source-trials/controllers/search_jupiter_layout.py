from pathlib import Path
import shutil,subprocess,json,importlib.util,itertools,struct
p=Path('work/relay-residual-20261026').resolve();source=p/'source-jupiter-layout';shutil.copytree(p/'source-location-combined',source,dirs_exist_ok=True);original=(source/'src/settlement_handlers.rs').read_text().replace('let infos=remaining.to_vec();','let infos=remaining.iter().cloned().collect::<Vec<_>>();')
s=importlib.util.spec_from_file_location('jupiter_analysis','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);elf_o=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes());target=elf_o.function(64824,2496,[])
def norm(elf,f):
 b=bytearray(elf.at(f['start'],f['bytes']))
 for q in f['direct_calls']:b[q['offset']+4:q['offset']+8]=b'\0'*4
 for q in f['data_references']:b[q['offset']+4:q['offset']+8]=b[q['offset']+12:q['offset']+16]=b'\0'*4
 return b
original_norm=norm(elf_o,target)
driver=(p/'build_burn_close.py').read_text().replace("source-burn-close'","source-jupiter-layout'").replace("mode.startswith('burn-close-')","mode.startswith('jupiter-layout-')");(p/'build_jupiter_layout.py').write_text(driver)
oldbranch='if seeds.is_empty() {anchor_lang::solana_program::program::invoke(&ix,&infos)?;} else {anchor_lang::solana_program::program::invoke_signed(&ix,&infos,seeds)?;}Ok(())'
branches={'base':oldbranch,'inverse':'if !seeds.is_empty() {anchor_lang::solana_program::program::invoke_signed(&ix,&infos,seeds)?;} else {anchor_lang::solana_program::program::invoke(&ix,&infos)?;}Ok(())','return':'if seeds.is_empty() {anchor_lang::solana_program::program::invoke(&ix,&infos).map_err(Into::into)} else {anchor_lang::solana_program::program::invoke_signed(&ix,&infos,seeds).map_err(Into::into)}','reborrow':oldbranch.replace('&infos,seeds','&infos,&seeds[..]')}
fields={'p':'program_id:program','a':'accounts:metas','d':'data'};variants=[]
for order in itertools.permutations('pad'):
 for branch in ['base','inverse']:
  variants.append((''.join(order)+'-'+branch,order,branch))
variants += [('pad-return',tuple('pad'),'return'),('pad-reborrow',tuple('pad'),'reborrow')]
rows=[]
for name,order,branch in variants:
 mode='jupiter-layout-'+name;d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 text=original.replace('Instruction {program_id:program,accounts:metas,data}','Instruction {'+','.join(fields[k]for k in order)+'}').replace(oldbranch,branches[branch]);(source/'src/settlement_handlers.rs').write_text(text);(d/'settlement_handlers.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_jupiter_layout.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode)
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text()
  elf=a.Elf((d/'symbols.so').read_bytes());v=next(x for x in elf.symbols if '14invoke_jupiter17h'in x['name']);f=elf.function(v['start'],v['size'],[]);b=norm(elf,f)
  row.update(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'],equal_slots=sum(original_norm[i:i+8]==b[i:i+8]for i in range(0,min(len(original_norm),len(b)),8)))
 rows.append(row);print(json.dumps(row),flush=True);(p/'jupiter-layout-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

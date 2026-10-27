from pathlib import Path
import shutil,subprocess,json,importlib.util,itertools
p=Path('work/relay-residual-20261026').resolve();source=p/'source-jupiter-meta';shutil.copytree(p/'source-location-combined',source,dirs_exist_ok=True);base=(source/'src/settlement_handlers.rs').read_text().replace('let infos=remaining.to_vec();','let infos=remaining.iter().cloned().collect::<Vec<_>>();')
s=importlib.util.spec_from_file_location('jma','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-jupiter-meta'");(p/'build_jupiter_meta.py').write_text(driver)
old='let metas=remaining.iter().map(|a|if a.is_writable {anchor_lang::solana_program::instruction::AccountMeta::new(*a.key,a.key==&authority)} else {anchor_lang::solana_program::instruction::AccountMeta::new_readonly(*a.key,a.key==&authority)}).collect();'
fields={'p':'pubkey:*a.key','s':'is_signer:a.key==&authority','w':'is_writable:a.is_writable'}
variants=[]
for order in itertools.permutations('psw'):
 for move in [False,True]:
  body='anchor_lang::solana_program::instruction::AccountMeta {'+','.join(fields[x]for x in order)+'}'
  variants.append((''.join(order)+('-move'if move else ''),'let metas=remaining.iter().map('+('move 'if move else '')+'|a|'+body+').collect();'))
for name,body in [('signer-first','{let signer=a.key==&authority;if a.is_writable {anchor_lang::solana_program::instruction::AccountMeta::new(*a.key,signer)} else {anchor_lang::solana_program::instruction::AccountMeta::new_readonly(*a.key,signer)}}'),('mutable-readonly','{let mut meta=anchor_lang::solana_program::instruction::AccountMeta::new_readonly(*a.key,a.key==&authority);meta.is_writable=a.is_writable;meta}'),('key-method','anchor_lang::solana_program::instruction::AccountMeta {pubkey:a.key(),is_signer:a.key()==authority,is_writable:a.is_writable}')]:
 for move in [False,True]:variants.append((name+('-move'if move else ''),'let metas=remaining.iter().map('+('move 'if move else '')+'|a|'+body+').collect();'))
variants.append(('constructor-move',old.replace('.map(|a|','.map(move |a|')))
rows=[]
for name,new in variants:
 mode='jupiter-meta-'+name;d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 assert base.count(old)==1;text=base.replace(old,new);(source/'src/settlement_handlers.rs').write_text(text);(d/'settlement_handlers.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_jupiter_meta.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode)
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text()
  elf_o=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes());target=elf_o.function(64824,2496,[])
  elf=a.Elf((d/'symbols.so').read_bytes());v=next(x for x in elf.symbols if '14invoke_jupiter17h'in x['name']);f=elf.function(v['start'],v['size'],[]);row.update(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'jupiter-meta-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

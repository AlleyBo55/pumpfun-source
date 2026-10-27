from pathlib import Path
import shutil,subprocess,json,importlib.util,itertools
p=Path('work/relay-residual-20261026').resolve();source=p/'source-donation-context';shutil.copytree(p/'source-482',source,dirs_exist_ok=True);original=(source/'src/donation_handlers.rs').read_text()
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-donation-context'").replace("mode.startswith('jupiter-')","mode.startswith('donation-context-')");(p/'build_donation_context.py').write_text(driver)
s=importlib.util.spec_from_file_location('dc','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
fields={'d':'debouncer_token_account:accounts.debouncer_token_account.to_account_info()','m':'mint:accounts.mint.to_account_info()','f':'from_token_account:accounts.from_token_account.to_account_info()','p':'token_program:accounts.token_program.to_account_info()'}
regular=','.join(fields[k]for k in 'dmfp')+',';native=regular.replace('from_token_account:accounts.from_token_account','from_token_account:accounts.temp_wsol_token_account');assert original.count(regular)==3 and original.count(native)==2
names={92:'donation_handlers24donate_native_v1_handler',93:'donation_handlers41donate_native_pubkey_config_id_v1_handler',94:'donation_handlers17donate_v1_handler',95:'donation_handlers45donate_pubkey_config_id_with_payer_v1_handler'}
coords={92:(70200,6272),93:(76472,6272),94:(82744,2568),95:(85312,2568)};rows=[]
for order in itertools.permutations('dmfp'):
 name=''.join(order);mode='donation-context-'+name;d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 block=','.join(fields[k]for k in order)+',';text=original.replace(regular,block).replace(native,block.replace('from_token_account:accounts.from_token_account','from_token_account:accounts.temp_wsol_token_account'));(source/'src/donation_handlers.rs').write_text(text);(d/'donation_handlers.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_donation_context.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode,targets={})
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text();o=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes());elf=a.Elf((d/'symbols.so').read_bytes())
  for ordinal,term in names.items():
   target=o.function(*coords[ordinal],[]);v=next(x for x in elf.symbols if term in x['name']);f=elf.function(v['start'],v['size'],[]);row['targets'][ordinal]=dict(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'donation-context-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if any(v['matched']for v in row['targets'].values()):break

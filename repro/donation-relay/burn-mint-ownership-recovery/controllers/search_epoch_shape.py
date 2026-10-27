from pathlib import Path
import shutil,subprocess,json,importlib.util
p=Path('work/relay-residual-20261026').resolve();source=p/'source-epoch-shape';shutil.copytree(p/'source-481',source,dirs_exist_ok=True);original=(source/'src/settlement_handlers.rs').read_text();head,tail=original.split('macro_rules! just_error',1)
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-epoch-shape'").replace("mode.startswith('jupiter-')","mode.startswith('epoch-shape-')");(p/'build_epoch_shape.py').write_text(driver)
s=importlib.util.spec_from_file_location('esa','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
call_start=head.index(' anchor_spl::token_interface::transfer_checked(');call_stop=head.index(' accounts.debouncer.total_amount=0;');call=head[call_start:call_stop]
accounts='anchor_spl::token_interface::TransferChecked {\n  from:accounts.debouncer_token_account.to_account_info(),mint:accounts.mint.to_account_info(),to:accounts.distribution_token_account.to_account_info(),authority:accounts.debouncer.to_account_info(),\n }'
assert accounts in call
variants={
 'control':head,
 'distribution-argument':head.replace('mint:accounts.debouncer.mint,epoch,total_amount:gross','mint:accounts.debouncer.mint,epoch:args.epoch,total_amount:gross'),
 'event-argument':head.replace('mint:accounts.debouncer.mint,epoch,gross_epoch_amount:gross','mint:accounts.debouncer.mint,epoch:args.epoch,gross_epoch_amount:gross'),
 'both-argument':head.replace('mint:accounts.debouncer.mint,epoch,','mint:accounts.debouncer.mint,epoch:args.epoch,'),
 'seed-local':head.replace(call,' let signer_seeds:&[&[&[u8]]]=&[seeds];\n'+call.replace('&[seeds]','signer_seeds')),
 'with-signer':head.replace('CpiContext::new_with_signer(accounts.token_program.to_account_info(),'+accounts+',&[seeds])','CpiContext::new(accounts.token_program.to_account_info(),'+accounts+').with_signer(&[seeds])'),
 'accounts-first':head.replace(call,' let cpi_accounts='+accounts+';\n'+call.replace(accounts,'cpi_accounts')),
 'program-local':head.replace(call,' let cpi_program=accounts.token_program.to_account_info();\n'+call.replace('accounts.token_program.to_account_info()','cpi_program')),
}
rows=[]
for name,body in variants.items():
 mode='epoch-shape-'+name;d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 text=body+'macro_rules! just_error'+tail;(source/'src/settlement_handlers.rs').write_text(text);(d/'settlement_handlers.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_epoch_shape.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode)
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text();target=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes()).function(87880,4000,[]);elf=a.Elf((d/'symbols.so').read_bytes());v=next(x for x in elf.symbols if '11close_epoch17h'in x['name']);f=elf.function(v['start'],v['size'],[]);row.update(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'epoch-shape-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

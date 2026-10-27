from pathlib import Path
import shutil,subprocess,json,importlib.util,itertools
p=Path('work/relay-residual-20261026').resolve();source=p/'source-epoch-init';shutil.copytree(p/'source-481',source,dirs_exist_ok=True);original=(source/'src/settlement_handlers.rs').read_text();head,tail=original.split('macro_rules! just_error',1)
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-epoch-init'").replace("mode.startswith('jupiter-')","mode.startswith('epoch-init-')");(p/'build_epoch_init.py').write_text(driver)
s=importlib.util.spec_from_file_location('eia','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
state='accounts.distribution.set_inner(DistributionV1 {bump:distribution_bump,state:DistributionV1State::Initialized,config_id:accounts.debouncer.config_id,mint:accounts.debouncer.mint,epoch,total_amount:gross});'
overflow='accounts.epoch_tracker.current_epoch=accounts.epoch_tracker.current_epoch.checked_add(1).ok_or(Code::ArithmeticOverflow)?;'
states={'inner':state,'deref':state.replace('accounts.distribution.set_inner(', '*accounts.distribution=').replace('});','};'),'fields':'accounts.distribution.bump=distribution_bump;accounts.distribution.state=DistributionV1State::Initialized;accounts.distribution.config_id=accounts.debouncer.config_id;accounts.distribution.mint=accounts.debouncer.mint;accounts.distribution.epoch=epoch;accounts.distribution.total_amount=gross;'}
overflows={'inline':overflow,'match':'match accounts.epoch_tracker.current_epoch.checked_add(1) {Some(next)=>accounts.epoch_tracker.current_epoch=next,None=>return Err(Code::ArithmeticOverflow.into())};','temporary':'let next=accounts.epoch_tracker.current_epoch.checked_add(1).ok_or(Code::ArithmeticOverflow)?;accounts.epoch_tracker.current_epoch=next;'}
rows=[]
for (sn,st),(on,ov),seedlocal in itertools.product(states.items(),overflows.items(),[False,True]):
 if sn=='inner'and on=='inline':continue
 name=f'{sn}-{on}-{int(seedlocal)}';mode='epoch-init-'+name;d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 text=head.replace(state,st).replace(overflow,ov)
 if seedlocal:text=text.replace(' anchor_spl::token_interface::transfer_checked(', ' let signer_seeds:&[&[&[u8]]]=&[seeds];\n anchor_spl::token_interface::transfer_checked(').replace('},&[seeds]),gross','},signer_seeds),gross')
 text+='macro_rules! just_error'+tail;(source/'src/settlement_handlers.rs').write_text(text);(d/'settlement_handlers.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_epoch_init.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode)
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text();target=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes()).function(87880,4000,[]);elf=a.Elf((d/'symbols.so').read_bytes());v=next(x for x in elf.symbols if '11close_epoch17h'in x['name']);f=elf.function(v['start'],v['size'],[]);row.update(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'epoch-init-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

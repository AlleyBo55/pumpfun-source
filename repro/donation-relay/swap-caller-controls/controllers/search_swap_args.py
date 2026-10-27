from pathlib import Path
import shutil,subprocess,json,importlib.util
p=Path('work/relay-residual-20261026').resolve();source=p/'source-swap-args';shutil.copytree(p/'source-burn-caller-order',source,dirs_exist_ok=True);base=(source/'src/settlement_handlers.rs').read_text();lib=(source/'src/lib.rs').read_text();lib=lib.replace('just_swap(ctx.accounts,swap_data,ctx.remaining_accounts','just_swap(ctx.accounts,crate::codec::wire::JustSwapV1 {jupiter_swap_ix_data:swap_data},ctx.remaining_accounts')
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-swap-args'").replace("mode.startswith('jupiter-')","mode.startswith('swap-args-')");(p/'build_swap_args.py').write_text(driver)
s=importlib.util.spec_from_file_location('sa','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);rows=[]
for name in ['destructure','field']:
 label='swap-args-'+name;d=p/label;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 text=base.replace("accounts:&mut JustSwapV1<'info>,data:Vec<u8>,remaining:","accounts:&mut JustSwapV1<'info>,args:crate::codec::wire::JustSwapV1,remaining:")
 if name=='destructure':text=text.replace(' if !(accounts.distribution.epoch<accounts.epoch_tracker.current_epoch)', ' let crate::codec::wire::JustSwapV1 {jupiter_swap_ix_data:data}=args; if !(accounts.distribution.epoch<accounts.epoch_tracker.current_epoch)',1)
 else:text=text.replace('remaining,data,&[seeds],accounts.distribution.total_amount','remaining,args.jupiter_swap_ix_data,&[seeds],accounts.distribution.total_amount',1)
 for n,v in [('settlement_handlers.rs',text),('lib.rs',lib)]:(source/'src'/n).write_text(v);(d/n).write_text(v)
 r=subprocess.run(['python3','-B',str(p/'build_swap_args.py'),label],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode)
 if r.returncode==0:
  e=a.Elf((d/'symbols.so').read_bytes());o=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes());v=next(s for s in e.symbols if 'settlement_handlers9just_swap17h'in s['name']);f=e.function(v['start'],v['size'],[]);row.update(bytes=f['bytes'],matched=f['normalized_sha256']==o.function(102792,4448,[])['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'swap-args-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

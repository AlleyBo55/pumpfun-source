from pathlib import Path
import shutil,subprocess,json,importlib.util,itertools
p=Path('work/relay-residual-20261026').resolve();source=p/'source-shared-late';shutil.copytree(p/'source-482',source,dirs_exist_ok=True);original=(source/'src/shared_donation.rs').read_text();mark='check_message(&args.message)?;check_bps(args.tip_bps)?;';prefix,rest=original.split(mark,1)
pre='\n let DonationContext {epoch_tracker,debouncer,from,mint_whitelist,debouncer_token_account,mint:mint_info,from_token_account,token_program}=ctx;'
for field in ['epoch_tracker','debouncer','from','mint_whitelist','debouncer_token_account','mint','from_token_account','token_program']:rest=rest.replace('ctx.'+field,'mint_info'if field=='mint'else field)
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-shared-late'").replace("mode.startswith('jupiter-')","mode.startswith('shared-late-')");(p/'build_shared_late.py').write_text(driver)
s=importlib.util.spec_from_file_location('sl','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);rows=[]
for mint,from_account,program in itertools.product([False,True],repeat=3):
 name=''.join(str(int(v))for v in [mint,from_account,program]);mode='shared-late-'+name;d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 b=rest
 if mint:b=b.replace('mint:mint_info.clone()','mint:mint_info')
 if from_account:b=b.replace('from:from_token_account.clone()','from:from_token_account')
 if program:b=b.replace('CpiContext::new(token_program.clone(),','CpiContext::new(token_program,')
 text=prefix+mark+pre+b;(source/'src/shared_donation.rs').write_text(text);(d/'shared_donation.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_shared_late.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode)
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text();target=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes()).function(131136,10248,[]);e=a.Elf((d/'symbols.so').read_bytes());v=next(x for x in e.symbols if '13donate_shared17h'in x['name']);f=e.function(v['start'],v['size'],[]);row.update(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'shared-late-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

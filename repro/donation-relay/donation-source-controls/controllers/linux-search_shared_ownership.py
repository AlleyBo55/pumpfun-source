from pathlib import Path
import shutil,subprocess,json,importlib.util,itertools
root=Path.cwd();p=root/'work/relay-linux-canonical-20261026';source=p/'source-shared-ownership';shutil.copytree(root/'work/relay-residual-20261026/source-482',source,dirs_exist_ok=True);original=(source/'src/shared_donation.rs').read_text();head,body=original.split('pub fn donate_shared(ctx:DonationContext,args:DonationArgs)->Result<DonationAmounts> {',1)
driver=(p/'build_locations.py').read_text().replace('locations-output','shared-ownership-output').replace('source-locations','source-shared-ownership');(p/'build_shared_ownership.py').write_text(driver)
s=importlib.util.spec_from_file_location('lsa',root/'repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);rows=[]
for ctx_pattern,args_pattern in itertools.product([False,True],repeat=2):
 name=f'{int(ctx_pattern)}{int(args_pattern)}';d=p/('shared-ownership-'+name);d.mkdir(exist_ok=True);b=body;pre=''
 if ctx_pattern:
  pre+='\n let DonationContext {epoch_tracker,debouncer,from,mint_whitelist,debouncer_token_account,mint:mint_info,from_token_account,token_program}=ctx;'
  for field in ['epoch_tracker','debouncer','from','mint_whitelist','debouncer_token_account','mint','from_token_account','token_program']:b=b.replace('ctx.'+field,'mint_info'if field=='mint'else field)
 if args_pattern:
  pre+='\n let DonationArgs {config_id,amount,message,tip_bps,epoch_tracker_bump,debouncer_bump}=args;'
  for field in ['config_id','amount','message','tip_bps','epoch_tracker_bump','debouncer_bump']:b=b.replace('args.'+field,field)
 text=head+'pub fn donate_shared(ctx:DonationContext,args:DonationArgs)->Result<DonationAmounts> {'+pre+b;(source/'src/shared_donation.rs').write_text(text);(d/'shared_donation.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_shared_ownership.py')],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode)
 for f in (p/'shared-ownership-output').iterdir():
  if f.is_file():shutil.copyfile(f,d/f.name)
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text();target=a.Elf((root/'evidence/dependencies/donation_relay/deployed.so').read_bytes()).function(131136,10248,[]);elf=a.Elf((d/'symbols.so').read_bytes());v=next(x for x in elf.symbols if '13donate_shared17h'in x['name']);f=elf.function(v['start'],v['size'],[]);row.update(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'shared-ownership-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

from pathlib import Path
import shutil,subprocess,json,importlib.util,re
p=Path('work/relay-residual-20261026').resolve();source=p/'source-donation-args';shutil.copytree(p/'source-482',source,dirs_exist_ok=True);base=(source/'src/donation_handlers.rs').read_text();driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-donation-args'").replace("mode.startswith('jupiter-')","mode.startswith('donation-args-')");(p/'build_donation_args.py').write_text(driver)
s=importlib.util.spec_from_file_location('da','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
pattern=r' let crate::codec::wire::\w+ \{amount,config_id,tip_bps,message,credited_to\}=args;'
plain=re.sub(pattern,'',base);assert plain!=base
for name in ['amount','config_id','tip_bps','message','credited_to']:plain=re.sub(r'(?<![\w.])'+name+r'\b(?!\s*:)', 'args.'+name,plain)
def inline_events(text):
 # Non-native bodies alone; native bodies close an account between event creation and return.
 chunks=text.split('pub fn ')
 for i,c in enumerate(chunks):
  if i and not c.startswith('donate_native'):
   c=c.replace('let event=DonationMadeV1Event','let event=DonationMadeV1Event')
   match=re.search(r'let event=(DonationMadeV1Event \{[^\n]+\});',c)
   assert match
   c=c.replace(match.group(), '').replace('Ok(event)','Ok('+match.group(1)+')')
   chunks[i]=c
 return 'pub fn '.join(chunks)
def split_shared_call(text,context_local,args_local):
 pattern=r'let result=crate::shared_donation::donate_shared\((crate::shared_donation::DonationContext \{[^}]+\}),(crate::shared_donation::DonationArgs \{[^}]+\})\)\?;'
 def replace(m):
  ctx,arg=m.groups();prefix=''
  if context_local:prefix+='let shared_context='+ctx+';';ctx='shared_context'
  if args_local:prefix+='let shared_args='+arg+';';arg='shared_args'
  return prefix+'let result=crate::shared_donation::donate_shared('+ctx+','+arg+')?;'
 result,n=re.subn(pattern,replace,text,flags=re.S);assert n==5;return result
variants={'args-fields':plain,'inline-events':inline_events(base),'args-fields-inline':inline_events(plain),'context-local':split_shared_call(base,True,False),'arguments-local':split_shared_call(base,False,True),'both-locals':split_shared_call(base,True,True)};rows=[]
names={92:'donation_handlers24donate_native_v1_handler',93:'donation_handlers41donate_native_pubkey_config_id_v1_handler',94:'donation_handlers17donate_v1_handler',95:'donation_handlers45donate_pubkey_config_id_with_payer_v1_handler'};coords={92:(70200,6272),93:(76472,6272),94:(82744,2568),95:(85312,2568)}
for name,text in variants.items():
 mode='donation-args-'+name;d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 (source/'src/donation_handlers.rs').write_text(text);(d/'donation_handlers.rs').write_text(text);r=subprocess.run(['python3','-B',str(p/'build_donation_args.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode,targets={})
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text();o=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes());e=a.Elf((d/'symbols.so').read_bytes())
  for i,term in names.items():
   target=o.function(*coords[i],[]);v=next(x for x in e.symbols if term in x['name']);f=e.function(v['start'],v['size'],[]);row['targets'][i]=dict(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'donation-args-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if any(v['matched']for v in row['targets'].values()):break

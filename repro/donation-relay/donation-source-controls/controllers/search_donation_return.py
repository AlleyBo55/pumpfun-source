from pathlib import Path
import shutil,subprocess,json,importlib.util,itertools
p=Path('work/relay-residual-20261026').resolve();source=p/'source-donation-return';shutil.copytree(p/'source-482',source,dirs_exist_ok=True);worker=(source/'src/shared_donation.rs').read_text();handlers=(source/'src/donation_handlers.rs').read_text()
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-donation-return'").replace("mode.startswith('jupiter-')","mode.startswith('donation-return-')");(p/'build_donation_return.py').write_text(driver)
s=importlib.util.spec_from_file_location('dr','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
fields={'e':('u128','tracker.current_epoch','epoch'),'g':('u64','delta','gross_amount'),'t':('u64','product/10000','tip')};rows=[]
names={92:'donation_handlers24donate_native_v1_handler',93:'donation_handlers41donate_native_pubkey_config_id_v1_handler',94:'donation_handlers17donate_v1_handler',95:'donation_handlers45donate_pubkey_config_id_with_payer_v1_handler',112:'shared_donation13donate_shared'};coords={92:(70200,6272),93:(76472,6272),94:(82744,2568),95:(85312,2568),112:(131136,10248)}
for order in itertools.permutations('egt'):
 name=''.join(order);mode='donation-return-'+name;d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 w=worker.replace('pub struct DonationAmounts {pub epoch:u128,pub gross_amount:u64,pub tip:u64}','pub type DonationAmounts=('+','.join(fields[x][0]for x in order)+');').replace('Ok(DonationAmounts {epoch:tracker.current_epoch,gross_amount:delta,tip:product/10000})','Ok(('+','.join(fields[x][1]for x in order)+'))');h=handlers
 for i,x in enumerate(order):h=h.replace('result.'+fields[x][2],'result.'+str(i))
 for filename,text in [('shared_donation.rs',w),('donation_handlers.rs',h)]:
  (source/'src'/filename).write_text(text);(d/filename).write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_donation_return.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode,targets={})
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text();o=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes());e=a.Elf((d/'symbols.so').read_bytes())
  for i,term in names.items():
   target=o.function(*coords[i],[]);v=next(x for x in e.symbols if term in x['name']);f=e.function(v['start'],v['size'],[]);row['targets'][i]=dict(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'donation-return-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if any(x['matched']for x in row['targets'].values()):break

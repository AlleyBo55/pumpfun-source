from pathlib import Path
import shutil,subprocess,json,importlib.util
p=Path('work/relay-residual-20261026').resolve();source=p/'source-unit-increment';shutil.copytree(p/'source-482',source,dirs_exist_ok=True);base={n:(source/'src'/n).read_text()for n in ['settlement_handlers.rs','business_error_codes.rs']}
code=(p/'unit-error-helper-epoch/business_error_codes.rs').read_text()
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-unit-increment'").replace("mode.startswith('jupiter-')","mode.startswith('unit-increment-')");(p/'build_unit_increment.py').write_text(driver)
s=importlib.util.spec_from_file_location('ui','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);rows=[]
old='accounts.epoch_tracker.current_epoch=accounts.epoch_tracker.current_epoch.checked_add(1).ok_or(Code::ArithmeticOverflow)?;'
variants={
 'inline-fn':('increment_epoch(&mut accounts.epoch_tracker.current_epoch)?;', '#[inline(always)] fn increment_epoch(epoch:&mut u128)->Result<()> {match epoch.checked_add(1) {Some(next)=>{*epoch=next;Ok(())},None=>crate::business_error_codes::failure(Code::ArithmeticOverflow)}}'),
 'map-or':('accounts.epoch_tracker.current_epoch.checked_add(1).map_or_else(|| crate::business_error_codes::failure(Code::ArithmeticOverflow), |next| {accounts.epoch_tracker.current_epoch=next;Ok(())})?;', ''),
 'if-let':('if let Some(next)=accounts.epoch_tracker.current_epoch.checked_add(1) {accounts.epoch_tracker.current_epoch=next;} else {crate::business_error_codes::failure(Code::ArithmeticOverflow)?;}', ''),
}
for name,(statement,helper) in variants.items():
 label='unit-increment-'+name;d=p/label;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 text=base['settlement_handlers.rs'].replace(old,statement);text=text.replace('macro_rules! just_error',helper+'macro_rules! just_error',1)
 for n,body in [('settlement_handlers.rs',text),('business_error_codes.rs',code)]:(source/'src'/n).write_text(body);(d/n).write_text(body)
 r=subprocess.run(['python3','-B',str(p/'build_unit_increment.py'),label],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode)
 if r.returncode==0:
  e=a.Elf((d/'symbols.so').read_bytes());o=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes());v=next(x for x in e.symbols if '11close_epoch17h'in x['name']);f=e.function(v['start'],v['size'],[]);row.update(bytes=f['bytes'],matched=f['normalized_sha256']==o.function(87880,4000,[])['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'unit-increment-results.json').write_text(json.dumps(rows,indent=2)+'\n')

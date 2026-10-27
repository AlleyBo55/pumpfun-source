from pathlib import Path
import shutil,subprocess,json,importlib.util
p=Path('work/relay-residual-20261026').resolve();source=p/'source-epoch-result-shape';shutil.copytree(p/'source-482',source,dirs_exist_ok=True);original=(source/'src/settlement_handlers.rs').read_text();head,tail=original.split('macro_rules! just_error',1)
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-epoch-result-shape'").replace("mode.startswith('jupiter-')","mode.startswith('epoch-result-shape-')");(p/'build_epoch_result_shape.py').write_text(driver)
s=importlib.util.spec_from_file_location('ers','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);rows=[]
expr='accounts.epoch_tracker.current_epoch.checked_add(1).ok_or(Code::ArithmeticOverflow)?'
helper='fn increment_epoch(value:u128)->Result<u128> {match value.checked_add(1) {Some(next)=>Ok(next),None=>Err(Code::ArithmeticOverflow.into())}}'
variants={
 'map-error':(expr.replace('.ok_or(Code::ArithmeticOverflow)?','.ok_or(Code::ArithmeticOverflow).map_err(anchor_lang::error::Error::from)?'),''),
 'map-ok-default':('accounts.epoch_tracker.current_epoch.checked_add(1).map(Ok).unwrap_or_else(|| Err(anchor_lang::error::Error::from(Code::ArithmeticOverflow)))?',''),
 'result-local':('next_epoch?', ''),
 'helper-auto':('increment_epoch(accounts.epoch_tracker.current_epoch)?',helper),
 'helper-inline':('increment_epoch(accounts.epoch_tracker.current_epoch)?','#[inline(always)] '+helper),
}
for name,(replacement,helper) in variants.items():
 label='epoch-result-shape-'+name;d=p/label;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 body=head
 if name=='result-local':body=body.replace(' accounts.epoch_tracker.current_epoch=', ' let next_epoch:Result<u128>=accounts.epoch_tracker.current_epoch.checked_add(1).ok_or_else(|| Code::ArithmeticOverflow.into());accounts.epoch_tracker.current_epoch=')
 body=body.replace(expr,replacement)
 text=body+helper+'macro_rules! just_error'+tail;(source/'src/settlement_handlers.rs').write_text(text);(d/'settlement_handlers.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_epoch_result_shape.py'),label],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode)
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text();target=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes()).function(87880,4000,[]);e=a.Elf((d/'symbols.so').read_bytes());v=next(x for x in e.symbols if '11close_epoch17h'in x['name']);f=e.function(v['start'],v['size'],[]);row.update(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'epoch-result-shape-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

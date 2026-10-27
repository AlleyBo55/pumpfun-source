from pathlib import Path
import shutil,subprocess,json,importlib.util
p=Path('work/relay-residual-20261026').resolve();source=p/'source-unit-error-helper';shutil.copytree(p/'source-482',source,dirs_exist_ok=True);base={n:(source/'src'/n).read_text()for n in ['settlement_handlers.rs','business_error_codes.rs']}
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-unit-error-helper'").replace("mode.startswith('jupiter-')","mode.startswith('unit-error-helper-')");(p/'build_unit_error_helper.py').write_text(driver)
s=importlib.util.spec_from_file_location('ueh','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
helper='\n#[inline(never)]\npub fn failure(code:ErrorCode)->anchor_lang::Result<()> { Err(anchor_lang::error::AnchorError {error_name:code.name(),error_code_number:code.into(),error_msg:code.to_string(),error_origin:None,compared_values:None}.into()) }\n'
old='accounts.epoch_tracker.current_epoch=accounts.epoch_tracker.current_epoch.checked_add(1).ok_or(Code::ArithmeticOverflow)?;'
new='match accounts.epoch_tracker.current_epoch.checked_add(1) {Some(next)=>{accounts.epoch_tracker.current_epoch=next;Ok(())},None=>crate::business_error_codes::failure(Code::ArithmeticOverflow)}?;'
label='unit-error-helper-epoch';d=p/label;d.mkdir(exist_ok=True)
if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
texts=dict(base);texts['business_error_codes.rs']+=helper;assert old in texts['settlement_handlers.rs'];texts['settlement_handlers.rs']=texts['settlement_handlers.rs'].replace(old,new)
for n,text in texts.items():(source/'src'/n).write_text(text);(d/n).write_text(text)
r=subprocess.run(['python3','-B',str(p/'build_unit_error_helper.py'),label],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(exit_code=r.returncode)
if r.returncode==0:
 e=a.Elf((d/'symbols.so').read_bytes());o=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes());v=next(x for x in e.symbols if '11close_epoch17h'in x['name']);f=e.function(v['start'],v['size'],[]);row.update(bytes=f['bytes'],matched=f['normalized_sha256']==o.function(87880,4000,[])['normalized_sha256'],normalized_sha256=f['normalized_sha256']);row['helpers']=[dict(name=x['name'],bytes=x['size'],matched=e.function(x['start'],x['size'],[])['normalized_sha256']==o.function(152048,504,[])['normalized_sha256'])for x in e.symbols if 'failure17h'in x['name']]
(d/'target-result.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row))

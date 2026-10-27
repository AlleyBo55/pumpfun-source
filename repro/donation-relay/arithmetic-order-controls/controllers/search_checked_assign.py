from pathlib import Path
import shutil,subprocess,json,importlib.util
p=Path('work/relay-residual-20261026').resolve();source=p/'source-checked-assign';shutil.copytree(p/'source-482',source,dirs_exist_ok=True);base=(source/'src/shared_donation.rs').read_text();code=(p/'unit-error-helper-epoch/business_error_codes.rs').read_text()
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-checked-assign'").replace("mode.startswith('jupiter-')","mode.startswith('checked-assign-')");(p/'build_checked_assign.py').write_text(driver)
s=importlib.util.spec_from_file_location('ca','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);rows=[]
for name,kinds in [('add',('add',)),('sub-mul',('sub','mul')),('all',('sub','mul','add'))]:
 label='checked-assign-'+name;d=p/label;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 text=base
 if 'sub'in kinds:text=text.replace('let delta=after.checked_sub(before).ok_or(Code::ArithmeticOverflow)?;','let mut delta=after;checked_sub_assign(&mut delta,before)?;')
 if 'mul'in kinds:text=text.replace('let product=delta.checked_mul(u64::from(args.tip_bps)).ok_or(Code::ArithmeticOverflow)?;','let mut product=delta;checked_mul_assign(&mut product,u64::from(args.tip_bps))?;')
 if 'add'in kinds:text=text.replace('debouncer.total_amount=debouncer.total_amount.checked_add(delta).ok_or(Code::ArithmeticOverflow)?;','checked_add_assign(&mut debouncer.total_amount,delta)?;')
 for kind in kinds:text+='\n#[inline(always)] fn checked_'+kind+'_assign(target:&mut u64,rhs:u64)->Result<()> {match target.checked_'+kind+'(rhs) {Some(value)=>{*target=value;Ok(())},None=>crate::business_error_codes::failure(Code::ArithmeticOverflow)}}\n'
 for n,v in [('shared_donation.rs',text),('business_error_codes.rs',code)]:(source/'src'/n).write_text(v);(d/n).write_text(v)
 r=subprocess.run(['python3','-B',str(p/'build_checked_assign.py'),label],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode)
 if r.returncode==0:
  e=a.Elf((d/'symbols.so').read_bytes());o=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes());v=next(s for s in e.symbols if '13donate_shared17h'in s['name']);f=e.function(v['start'],v['size'],[]);row.update(bytes=f['bytes'],matched=f['normalized_sha256']==o.function(131136,10248,[])['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'checked-assign-results.json').write_text(json.dumps(rows,indent=2)+'\n')

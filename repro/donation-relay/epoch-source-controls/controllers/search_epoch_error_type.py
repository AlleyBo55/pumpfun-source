from pathlib import Path
import shutil,subprocess,json,importlib.util
p=Path('work/relay-residual-20261026').resolve();source=p/'source-epoch-error-type';shutil.copytree(p/'source-482',source,dirs_exist_ok=True);original=(source/'src/settlement_handlers.rs').read_text();head,tail=original.split('macro_rules! just_error',1)
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-epoch-error-type'").replace("mode.startswith('jupiter-')","mode.startswith('epoch-error-type-')");(p/'build_epoch_error_type.py').write_text(driver)
s=importlib.util.spec_from_file_location('eet','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);rows=[]
variants={'lazy-anchor-error':'.ok_or_else(|| anchor_lang::error::Error::from(Code::ArithmeticOverflow))?', 'eager-anchor-error':'.ok_or::<anchor_lang::error::Error>(Code::ArithmeticOverflow.into())?', 'lazy-code':'.ok_or_else(|| Code::ArithmeticOverflow)?'}
for name,replacement in variants.items():
 label='epoch-error-type-'+name;d=p/label;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 assert head.count('.ok_or(Code::ArithmeticOverflow)?')==1
 text=head.replace('.ok_or(Code::ArithmeticOverflow)?',replacement)+'macro_rules! just_error'+tail;(source/'src/settlement_handlers.rs').write_text(text);(d/'settlement_handlers.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_epoch_error_type.py'),label],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode)
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text();target=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes()).function(87880,4000,[]);e=a.Elf((d/'symbols.so').read_bytes());v=next(x for x in e.symbols if '11close_epoch17h'in x['name']);f=e.function(v['start'],v['size'],[]);row.update(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'epoch-error-type-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

from pathlib import Path
import shutil,subprocess,json,importlib.util,itertools
p=Path('work/relay-residual-20261026').resolve();source=p/'source-epoch-seedtypes';shutil.copytree(p/'source-481',source,dirs_exist_ok=True);original=(source/'src/settlement_handlers.rs').read_text();head,tail=original.split('macro_rules! just_error',1)
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-epoch-seedtypes'").replace("mode.startswith('jupiter-')","mode.startswith('epoch-seedtypes-')");(p/'build_epoch_seedtypes.py').write_text(driver)
s=importlib.util.spec_from_file_location('est','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
old='let seeds:&[&[u8]]=&[b"debouncer_v1",accounts.debouncer.config_id.as_ref(),accounts.debouncer.mint.as_ref(),&bump];'
parts='b"debouncer_v1".as_ref(),accounts.debouncer.config_id.as_ref(),accounts.debouncer.mint.as_ref(),&bump'
forms={
 'inferred-array':('let seeds=&['+parts+'];','&[&seeds[..]]'),
 'explicit-array':('let seeds:&[&[u8];4]=&['+parts+'];','&[seeds]'),
 'owned-array':('let seeds:[&[u8];4]=['+parts+'];','&[&seeds]'),
 'outer-inferred':(old+'let signer_seeds=&[seeds];','signer_seeds'),
 'outer-array':(old+'let signer_seeds:&[&[&[u8]];1]=&[seeds];','signer_seeds'),
 'nested-inline':('','&[&['+parts+']]'),
}
rows=[]
for (name,(definition,use)),reverse in itertools.product(forms.items(),[False,True]):
 mode='epoch-seedtypes-'+name+('-reverse'if reverse else '');d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 text=head.replace(old,definition).replace('},&[seeds]),gross','},'+use+'),gross')
 if reverse:text=text.replace('if args.epoch!=epoch','if epoch!=args.epoch')
 text+='macro_rules! just_error'+tail;(source/'src/settlement_handlers.rs').write_text(text);(d/'settlement_handlers.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_epoch_seedtypes.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=mode,exit_code=r.returncode)
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text();target=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes()).function(87880,4000,[]);elf=a.Elf((d/'symbols.so').read_bytes());v=next(x for x in elf.symbols if '11close_epoch17h'in x['name']);f=elf.function(v['start'],v['size'],[]);row.update(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'epoch-seedtypes-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

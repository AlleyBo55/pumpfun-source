from pathlib import Path
import shutil,subprocess,json,importlib.util,itertools
p=Path('work/relay-residual-20261026').resolve();source=p/'source-burn-close';shutil.copytree(p/'source-location-combined',source,dirs_exist_ok=True)
original=(source/'src/settlement_handlers.rs').read_text();start=original.index("pub fn burn_and_close<'info>");stop=original.index('\nmacro_rules! distribution_error',start)
s=importlib.util.spec_from_file_location('burn_analysis','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
original_elf=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes());target=original_elf.function(127704,2856,[])
driver=(p/'build_close_literals.py').read_text().replace("source-close-literals'","source-burn-close'").replace("mode.startswith('close-literal-')","mode.startswith('burn-close-')");driver=driver.replace("'rustc','--release'", "'rustc','-v','--release'");(p/'build_burn_close.py').write_text(driver)
rows=[]
for destructure,burn_order,close_order,tail in itertools.product([False,True],repeat=4):
 name=''.join(str(int(v))for v in [destructure,burn_order,close_order,tail]);mode='burn-close-'+name;d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 pre='let BurnCloseContext {token,mint,authority,destination,program}=ctx;' if destructure else 'let (mint,authority,destination,program)=(ctx.mint,ctx.authority,ctx.destination,ctx.program);';token='token' if destructure else 'ctx.token'
 burnfields=[f'mint:mint.clone()',f'from:{token}.clone()',f'authority:authority.clone()']
 if burn_order:burnfields[0],burnfields[1]=burnfields[1],burnfields[0]
 closefields=[f'account:{token}','destination:destination','authority:authority']
 if close_order:closefields[1],closefields[2]=closefields[2],closefields[1]
 replacement="pub fn burn_and_close<'info>(ctx:BurnCloseContext<'info>,amount:u64,seeds:&[&[&[u8]]])->Result<()> {\n "+pre+'\n if amount!=0 {anchor_spl::token_interface::burn(CpiContext::new_with_signer(program.clone(),anchor_spl::token_interface::Burn {'+','.join(burnfields)+'},seeds),amount)?;}\n anchor_spl::token_interface::close_account(CpiContext::new_with_signer(program,anchor_spl::token_interface::CloseAccount {'+','.join(closefields)+'},seeds))'+(''if tail else '?;Ok(())')+'\n}\n'
 text=original[:start]+replacement+original[stop:];(source/'src/settlement_handlers.rs').write_text(text);(d/'settlement_handlers.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_burn_close.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr)
 row=dict(name=name,destructure=destructure,burn_field_order=burn_order,close_field_order=close_order,tail_return=tail,exit_code=r.returncode)
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text()
  elf=a.Elf((d/'symbols.so').read_bytes());v=next(x for x in elf.symbols if '14burn_and_close17h'in x['name']);f=elf.function(v['start'],v['size'],[])
  row.update(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'burn-close-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

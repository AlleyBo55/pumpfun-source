from pathlib import Path
import shutil,subprocess,json,importlib.util,itertools
p=Path('work/relay-residual-20261026').resolve();source=p/'source-burn-ownership';shutil.copytree(p/'source-location-combined',source,dirs_exist_ok=True)
original=(source/'src/settlement_handlers.rs').read_text();start=original.index("pub fn burn_and_close<'info>");stop=original.index('\nmacro_rules! distribution_error',start)
s=importlib.util.spec_from_file_location('burn_analysis','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);target=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes()).function(127704,2856,[])
driver=(p/'build_burn_close.py').read_text().replace("source-burn-close'","source-burn-ownership'").replace("mode.startswith('burn-close-')","mode.startswith('burn-ownership-')");(p/'build_burn_ownership.py').write_text(driver)
styles={
 'direct':('',dict(token='ctx.token',mint='ctx.mint',authority='ctx.authority',destination='ctx.destination',program='ctx.program')),
 'mint-context':('let (authority,destination,program)=(ctx.authority,ctx.destination,ctx.program);',dict(token='ctx.token',mint='ctx.mint',authority='authority',destination='destination',program='program')),
 'mint-borrow':('let mint=&ctx.mint;let (authority,destination,program)=(ctx.authority,ctx.destination,ctx.program);',dict(token='ctx.token',mint='(*mint)',authority='authority',destination='destination',program='program')),
 'individual':('let mint=ctx.mint;let authority=ctx.authority;let destination=ctx.destination;let program=ctx.program;',dict(token='ctx.token',mint='mint',authority='authority',destination='destination',program='program')),
}
rows=[]
for (style,(pre,v)),burn_order,tail in itertools.product(styles.items(),[False,True],[False,True]):
 mode=f'burn-ownership-{style}-{int(burn_order)}{int(tail)}';d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 burnfields=[f'mint:{v["mint"]}.clone()',f'from:{v["token"]}.clone()',f'authority:{v["authority"]}.clone()']
 if burn_order:burnfields[0],burnfields[1]=burnfields[1],burnfields[0]
 closefields=[f'account:{v["token"]}',f'destination:{v["destination"]}',f'authority:{v["authority"]}']
 replacement="pub fn burn_and_close<'info>(ctx:BurnCloseContext<'info>,amount:u64,seeds:&[&[&[u8]]])->Result<()> {\n "+pre+'\n if amount!=0 {anchor_spl::token_interface::burn(CpiContext::new_with_signer('+v['program']+'.clone(),anchor_spl::token_interface::Burn {'+','.join(burnfields)+'},seeds),amount)?;}\n anchor_spl::token_interface::close_account(CpiContext::new_with_signer('+v['program']+',anchor_spl::token_interface::CloseAccount {'+','.join(closefields)+'},seeds))'+(''if tail else '?;Ok(())')+'\n}\n'
 text=original[:start]+replacement+original[stop:];(source/'src/settlement_handlers.rs').write_text(text);(d/'settlement_handlers.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_burn_ownership.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=mode,exit_code=r.returncode)
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text()
  elf=a.Elf((d/'symbols.so').read_bytes());v=next(x for x in elf.symbols if '14burn_and_close17h'in x['name']);f=elf.function(v['start'],v['size'],[])
  row.update(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'burn-ownership-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

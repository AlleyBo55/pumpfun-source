from pathlib import Path
import shutil,subprocess,json,importlib.util
p=Path('work/relay-residual-20261026').resolve();source=p/'source-jupiter';shutil.copytree(p/'source-location-combined',source,dirs_exist_ok=True);original=(source/'src/settlement_handlers.rs').read_text()
s=importlib.util.spec_from_file_location('jupiter_analysis','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);target=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes()).function(64824,2496,[])
driver=(p/'build_burn_close.py').read_text().replace("source-burn-close'","source-jupiter'").replace("mode.startswith('burn-close-')","mode.startswith('jupiter-')");(p/'build_jupiter.py').write_text(driver)
variants={'iter-cloned':'remaining.iter().cloned().collect::<Vec<_>>()','iter-map-clone':'remaining.iter().map(Clone::clone).collect::<Vec<_>>()','to-owned':'remaining.to_owned()','vec-from':'Vec::from(remaining)'};rows=[]
for name,expr in variants.items():
 mode='jupiter-'+name;d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 assert original.count('let infos=remaining.to_vec();')==1
 text=original.replace('let infos=remaining.to_vec();','let infos='+expr+';');(source/'src/settlement_handlers.rs').write_text(text);(d/'settlement_handlers.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_jupiter.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,expression=expr,exit_code=r.returncode)
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text()
  elf=a.Elf((d/'symbols.so').read_bytes());v=next(x for x in elf.symbols if '14invoke_jupiter17h'in x['name']);f=elf.function(v['start'],v['size'],[]);row.update(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'jupiter-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

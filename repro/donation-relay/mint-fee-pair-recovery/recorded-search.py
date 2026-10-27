from pathlib import Path
import shutil,subprocess,json,importlib.util
p=Path('work/relay-residual-20261026').resolve();source=p/'source-mint-search';shutil.copytree(p/'source-share-values',source,dirs_exist_ok=True)
base=(source/'src/mint_policy.rs').read_text();old='let fee_basis_points=u16::from(fee.older_transfer_fee.transfer_fee_basis_points) | u16::from(fee.newer_transfer_fee.transfer_fee_basis_points);\n   if fee_basis_points!=0 {return Ok(false);}'
assert old in base
a='u16::from(fee.older_transfer_fee.transfer_fee_basis_points)';b='u16::from(fee.newer_transfer_fee.transfer_fee_basis_points)'
variants={
 'tuple-old':f'if ({a},{b}) != (0,0) {{return Ok(false);}}',
 'tuple-new':f'if ({b},{a}) != (0,0) {{return Ok(false);}}',
 'array-old':f'if [{a},{b}] != [0,0] {{return Ok(false);}}',
 'array-new':f'if [{b},{a}] != [0,0] {{return Ok(false);}}',
 'match-old':f'match ({a},{b}) {{(0,0)=>(),_=>return Ok(false)}}',
 'zero-and':f'if !({a}==0 && {b}==0) {{return Ok(false);}}',
 'any-old':f'if [{a},{b}].iter().any(|x| *x!=0) {{return Ok(false);}}',
 'any-new':f'if [{b},{a}].iter().any(|x| *x!=0) {{return Ok(false);}}',
}
driver=(p/'build_mint_serial.py').read_text().replace("source-mint-serial'","source-mint-search'").replace("mode=='mint-serial'","mode.startswith('mint-search-')");(p/'build_mint_search.py').write_text(driver)
s=importlib.util.spec_from_file_location('mint_analyzer',Path('repro/donation-relay/distribution-worker-source-recovery/analyze.py'));ana=importlib.util.module_from_spec(s);s.loader.exec_module(ana)
target=json.loads((p/'share-values/original-function-ledger.json').read_text())[106];rows=[]
for name,body in variants.items():
 mode='mint-search-'+name;d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 text=base.replace(old,body);(source/'src/mint_policy.rs').write_text(text);(d/'mint_policy.rs').write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_mint_search.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr)
 row={'variant':name,'exit_code':r.returncode}
 if r.returncode==0:
  elf=ana.Elf((d/'symbols.so').read_bytes());symbol=next(x for x in elf.symbols if 'typed_mint_safe' in x['name']);record=elf.function(symbol['start'],symbol['size'],[symbol['name']]);row.update(bytes=record['bytes'],normalized_sha256=record['normalized_sha256'],matched=record['normalized_sha256']==target['normalized_sha256']);(d/'mint-record.json').write_text(json.dumps(record,indent=2)+'\n')
 rows.append(row);print(json.dumps(row),flush=True)
 (p/'mint-search-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if row.get('matched'):break

from pathlib import Path
import shutil,subprocess,json,importlib.util,re,itertools,hashlib
p=Path('work/relay-residual-20261026').resolve();source=p/'source-partial-args';shutil.copytree(p/'source-482',source,dirs_exist_ok=True);base=(source/'src/donation_handlers.rs').read_text();driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-partial-args'").replace("mode.startswith('jupiter-')","mode.startswith('partial-args-')");(p/'build_partial_args.py').write_text(driver)
s=importlib.util.spec_from_file_location('pa','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
allfields=['amount','config_id','tip_bps','message','credited_to'];sets=[['message'],['amount','message'],['amount','tip_bps','message'],['config_id','message'],['message','credited_to'],['amount','config_id','tip_bps','message'],['amount','tip_bps','message','credited_to']];rows=json.loads((p/'partial-args-results.json').read_text())
sets=[list(v) for n in range(6) for v in itertools.combinations(allfields,n)]
for row in rows:
 d=p/('partial-args-'+row['name']);launch=json.loads((d/'launch.json').read_text());assert hashlib.sha256((d/'donation_handlers.rs').read_bytes()).hexdigest()==launch['inputs']['src/donation_handlers.rs'];assert row['exit_code']==0
finished={tuple(row['fields']) for row in rows}
names={92:'donation_handlers24donate_native_v1_handler',93:'donation_handlers41donate_native_pubkey_config_id_v1_handler',94:'donation_handlers17donate_v1_handler',95:'donation_handlers45donate_pubkey_config_id_with_payer_v1_handler'};coords={92:(70200,6272),93:(76472,6272),94:(82744,2568),95:(85312,2568)}
for fields in sets:
 if tuple(fields) in finished:continue
 name='-'.join(fields) or 'none';mode='partial-args-'+name;d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 text=base.replace('{amount,config_id,tip_bps,message,credited_to}=args;','{'+(','.join(fields)+',' if fields else '')+'..}=args;')
 for field in set(allfields)-set(fields):text=re.sub(r'(?<![\w.])'+field+r'\b(?!\s*:)', 'args.'+field,text)
 (source/'src/donation_handlers.rs').write_text(text);(d/'donation_handlers.rs').write_text(text);r=subprocess.run(['python3','-B',str(p/'build_partial_args.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,fields=fields,exit_code=r.returncode,targets={})
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text();o=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes());e=a.Elf((d/'symbols.so').read_bytes())
  for i,term in names.items():
   target=o.function(*coords[i],[]);v=next(x for x in e.symbols if term in x['name']);f=e.function(v['start'],v['size'],[]);row['targets'][i]=dict(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
 rows.append(row);print(json.dumps(row),flush=True);(p/'partial-args-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 if any(v['matched']for v in row['targets'].values()):break

from pathlib import Path
import shutil,subprocess,json,importlib.util
p=Path('work/relay-residual-20261026').resolve();source=p/'source-root-profiles';shutil.copytree(p/'source-482',source,dirs_exist_ok=True)
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-root-profiles'").replace("mode.startswith('jupiter-')","mode.startswith('root-profile-')")
driver=driver.replace("(out/'launch.json').write_text", "flags={'root-profile-control':['-C','opt-level=3'],'root-profile-opt2':['-C','opt-level=2'],'root-profile-size':['-C','opt-level=s'],'root-profile-minsize':['-C','opt-level=z'],'root-profile-cgu2':['-C','codegen-units=2']}[mode];cmd+=flags\n(out/'launch.json').write_text")
(p/'build_root_profile.py').write_text(driver)
s=importlib.util.spec_from_file_location('rp','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);rows=[]
for name in ['control','opt2','size','minsize','cgu2']:
 mode='root-profile-'+name;d=p/mode;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 r=subprocess.run(['python3','-B',str(p/'build_root_profile.py'),mode],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode)
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text()
  for dest,origin in [('original.so',Path('evidence/dependencies/donation_relay/deployed.so')),('unstripped.so',d/'symbols.so'),('original-windows.json',Path('repro/donation-relay/swap-receipt-coordinate-recovery/original-windows.json'))]:shutil.copyfile(origin,d/dest)
  results=a.analyze(d);before=json.loads(Path('repro/donation-relay/burn-mint-ownership-recovery/builds/recovered/match-ledger.json').read_text());bm={x['ordinal']for x in before if x['normalized_candidate_indices']};am={x['ordinal']for x in results['match-ledger.json']if x['normalized_candidate_indices']};row.update(summary=results['comparison-summary.json'],gained=sorted(am-bm),lost=sorted(bm-am));(d/'comparison.json').write_text(json.dumps(row,indent=2)+'\n')
 rows.append(row);(p/'root-profile-results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)

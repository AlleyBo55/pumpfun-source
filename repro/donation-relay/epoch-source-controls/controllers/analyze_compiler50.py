from pathlib import Path
import importlib.util,shutil,json
root=Path.cwd();p=root/'work/relay-residual-20261026/compiler50-oldlibs';assert json.loads((p/'result.json').read_text())['exit_code']==0
s=importlib.util.spec_from_file_location('a',root/'repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
shutil.copyfile(root/'evidence/dependencies/donation_relay/deployed.so',p/'original.so');shutil.copyfile(p/'symbols.so',p/'unstripped.so');shutil.copyfile(root/'repro/donation-relay/swap-receipt-coordinate-recovery/original-windows.json',p/'original-windows.json');a.write(p)
before=json.loads((root/'repro/donation-relay/burn-mint-ownership-recovery/builds/recovered/match-ledger.json').read_text());after=json.loads((p/'match-ledger.json').read_text());bm={r['ordinal']for r in before if r['normalized_candidate_indices']};am={r['ordinal']for r in after if r['normalized_candidate_indices']};d=dict(gained=sorted(am-bm),lost=sorted(bm-am),summary=json.loads((p/'comparison-summary.json').read_text()));(p/'frontier-change.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))

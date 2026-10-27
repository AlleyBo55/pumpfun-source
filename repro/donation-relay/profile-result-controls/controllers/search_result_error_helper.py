from pathlib import Path
import shutil,subprocess,json,importlib.util
p=Path('work/relay-residual-20261026').resolve();source=p/'source-result-error-helper';shutil.copytree(p/'source-482',source,dirs_exist_ok=True);base={n:(source/'src'/n).read_text()for n in ['settlement_handlers.rs','shared_donation.rs','business_error_codes.rs']}
driver=(p/'build_jupiter_confirmation.py').read_text().replace("source-jupiter-confirmation'","source-result-error-helper'").replace("mode.startswith('jupiter-')","mode.startswith('result-error-helper-')");(p/'build_result_error_helper.py').write_text(driver)
s=importlib.util.spec_from_file_location('reh','repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);rows=[]
helper='\n#[inline(never)]\npub fn failure<T>(code:ErrorCode)->anchor_lang::Result<T> { Err(anchor_lang::error::AnchorError {error_name:code.name(),error_code_number:code.into(),error_msg:code.to_string(),error_origin:None,compared_values:None}.into()) }\n'
for name in ['epoch','shared','both']:
 label='result-error-helper-'+name;d=p/label;d.mkdir(exist_ok=True)
 if not(d/'target').exists():(d/'target').symlink_to('../anchor-v8/target')
 texts=dict(base);texts['business_error_codes.rs']+=helper
 if name in('epoch','both'):
  head,tail=texts['settlement_handlers.rs'].split('macro_rules! just_error',1);assert head.count('.ok_or(Code::ArithmeticOverflow)?')==1;head=head.replace('.ok_or(Code::ArithmeticOverflow)?','.map(Ok).unwrap_or_else(||crate::business_error_codes::failure(Code::ArithmeticOverflow))?');texts['settlement_handlers.rs']=head+'macro_rules! just_error'+tail
 if name in('shared','both'):
  assert texts['shared_donation.rs'].count('.ok_or(Code::ArithmeticOverflow)?')==3;texts['shared_donation.rs']=texts['shared_donation.rs'].replace('.ok_or(Code::ArithmeticOverflow)?','.map(Ok).unwrap_or_else(||crate::business_error_codes::failure(Code::ArithmeticOverflow))?')
 for n,text in texts.items():(source/'src'/n).write_text(text);(d/n).write_text(text)
 r=subprocess.run(['python3','-B',str(p/'build_result_error_helper.py'),label],capture_output=True,text=True);(d/'driver.log').write_text(r.stdout+r.stderr);row=dict(name=name,exit_code=r.returncode,targets={})
 if r.returncode==0:
  assert '--crate-name donation_relay_source_proposal' in(d/'build.log').read_text();o=a.Elf(Path('evidence/dependencies/donation_relay/deployed.so').read_bytes());e=a.Elf((d/'symbols.so').read_bytes())
  for ordinal,term,st,z in [(96,'11close_epoch17h',87880,4000),(112,'13donate_shared17h',131136,10248)]:
   target=o.function(st,z,[]);v=next(x for x in e.symbols if term in x['name']);f=e.function(v['start'],v['size'],[]);row['targets'][ordinal]=dict(bytes=f['bytes'],matched=f['normalized_sha256']==target['normalized_sha256'],normalized_sha256=f['normalized_sha256'])
  row['helpers']=[dict(name=x['name'],bytes=x['size'],normalized_sha256=e.function(x['start'],x['size'],[])['normalized_sha256'])for x in e.symbols if 'failure17h'in x['name']]
 rows.append(row);print(json.dumps(row),flush=True);(p/'result-error-helper-results.json').write_text(json.dumps(rows,indent=2)+'\n')

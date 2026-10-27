from pathlib import Path
import json,re,shutil,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[1];base=ROOT/'work/relay-full-errors-v148';source=P/'source';f=source/'src/idl.rs';s=(base/'source/src/idl.rs').read_text();lo=s.index('pub type ProgramFailure');hi=s.index('\n#[derive(Clone, Copy, Debug)]',lo)
s=s[:lo]+'''pub type ProgramFailure = solana_program::program_error::ProgramError;
pub type IdlError = crate::generated_exit::exit_error::Error;
use crate::generated_exit::exit_error::ErrorCode;
pub type I<T> = Result<T, IdlError>;
fn code(n: ErrorCode) -> IdlError { n.into() }
pub fn program_error(error: ProgramFailure) -> IdlError { error.into() }
fn named<T>(r: I<T>, name: &'static str) -> I<T> {
    r.map_err(|error| error.with_account_name(name))
}
fn require(ok: bool, n: ErrorCode, name: &'static str) -> I<()> {
    named(if ok { Ok(()) } else { Err(code(n)) }, name)
}
fn require_keys(left: Key, right: Key, n: ErrorCode, name: &'static str) -> I<()> {
    if left == right { return Ok(()); }
    let error = code(n).with_pubkeys((
        solana_program::pubkey::Pubkey::new_from_array(left),
        solana_program::pubkey::Pubkey::new_from_array(right),
    ));
    named(Err(error), name)
}
'''+s[hi:]
s=s.replace('IdlError { cause: Cause::Owned(owned), account: None, keys: None, values: None, origin: None }','owned')
s=s.replace('''        return Err(IdlError {
            cause: Cause::Owned(crate::generated_exit::exit_error::account_discriminator_not_found()),
            account: None, keys: None, values: None, origin: None,
        });''','''        return Err(crate::generated_exit::exit_error::account_discriminator_not_found());''')
s=s.replace('''        return Err(IdlError {
            cause: Cause::Owned(owned),
            account: None, keys: None, values: None, origin: None,
        }); // enclosing generated parser replaces and drops the owned account name.''','''        return Err(owned); // enclosing generated parser replaces and drops the owned account name.''')
s=s.replace('''if owner != RELAY { let mut e = code(3007); e.keys = Some((owner, RELAY)); return Err(e); }''','''if owner != RELAY {
        return Err(code(ErrorCode::AccountOwnedByWrongProgram).with_pubkeys((
            solana_program::pubkey::Pubkey::new_from_array(owner),
            solana_program::pubkey::Pubkey::new_from_array(RELAY),
        )));
    }''')
s=s.replace('''        IdlError {
            cause: Cause::Owned(crate::generated_exit::exit_error::account_did_not_serialize()),
            account: None, keys: None, values: None, origin: None,
        }''','''        crate::generated_exit::exit_error::account_did_not_serialize()''')
s=s.replace('''        let mut e = code(2506);
        e.values = Some((dst.len() as u64, src.len() as u64)); Err(e)''','''        Err(code(ErrorCode::RequireGteViolated).with_values((dst.len() as u64, src.len() as u64)))''')
for r in json.loads((base/'framework-codes.json').read_text()):
 n,name=r['code'],r['name'];s=re.sub(r'code\('+str(n)+r'\)',f'code(ErrorCode::{name})',s);s=re.sub(r', '+str(n)+r',',', ErrorCode::'+name+',',s)
assert 'Cause::' not in s and 'e.keys' not in s and 'e.values' not in s
f.write_text(s)
f=source/'src/error_report.rs';s=(base/'source/src/error_report.rs').read_text().replace(',idl::Cause as IdlCause','');lo=s.index('        Failure::Idl(e)=>{');hi=s.index('        Failure::Unrecovered',lo);s=s[:lo]+'        Failure::Idl(error)=>error.log(),\n'+s[hi:];lo=s.index('        Failure::Idl(e)=>match');hi=s.index('        Failure::Unrecovered',lo);s=s[:lo]+'        Failure::Idl(error)=>error.into(),\n'+s[hi:];f.write_text(s)
for n in ['build.py','runtime.py','analyze.py','disasm.py','original-windows.json','run-header-cases.py','original-evidence.json','original-217.asm','framework-codes.json','business-codes.json','check-selectors.py','check-program-data.py']:shutil.copyfile(base/n,P/n)
shutil.copytree(base/'upstream',P/'upstream',dirs_exist_ok=True);H=lambda b:hashlib.sha256(b).hexdigest();(P/'baseline-source-manifest.json').write_text((base/'source-manifest.json').read_text());(P/'source-manifest.json').write_text(json.dumps({str(q.relative_to(source)):H(q.read_bytes()) for q in sorted(source.rglob('*')) if q.is_file()},indent=2)+'\n')
print('Prepared two-file IDL owned error ABI reconstruction')

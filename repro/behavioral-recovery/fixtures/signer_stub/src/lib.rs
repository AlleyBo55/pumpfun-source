// Minimal CPI signer-forwarder for differential testing.
// Instruction data layout: [n_ix_data:u16 LE][ix_data bytes][seed_count:u8]{[seed_len:u8][seed bytes]}...
// Accounts: [0]=target program account, [1..]=accounts to forward to the target (in order).
// Account [1] (first forwarded) is marked as the signer (the PDA this program signs).
use solana_program::{account_info::AccountInfo, entrypoint, entrypoint::ProgramResult,
  instruction::{AccountMeta, Instruction}, program::invoke_signed, pubkey::Pubkey};
entrypoint!(process);
fn process(_pid:&Pubkey, accounts:&[AccountInfo], data:&[u8]) -> ProgramResult {
    let mut o=0usize;
    let n=u16::from_le_bytes([data[o],data[o+1]]) as usize; o+=2;
    let ix_data=data[o..o+n].to_vec(); o+=n;
    let seed_count=data[o] as usize; o+=1;
    let mut seeds:Vec<Vec<u8>>=Vec::new();
    for _ in 0..seed_count { let l=data[o] as usize; o+=1; seeds.push(data[o..o+l].to_vec()); o+=1*0; o+=l; }
    let target=accounts[0].key;
    let fwd=&accounts[1..];
    let metas:Vec<AccountMeta>=fwd.iter().enumerate().map(|(i,ai)|{
        let signer = i==0; // first forwarded account is the PDA signer
        if ai.is_writable { AccountMeta::new(*ai.key, signer) } else { AccountMeta::new_readonly(*ai.key, signer) }
    }).collect();
    let ix=Instruction{program_id:*target, accounts:metas, data:ix_data};
    let seed_refs:Vec<&[u8]>=seeds.iter().map(|s|s.as_slice()).collect();
    invoke_signed(&ix, fwd, &[seed_refs.as_slice()])
}

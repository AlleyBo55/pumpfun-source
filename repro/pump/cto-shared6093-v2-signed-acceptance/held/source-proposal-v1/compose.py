"""Unapplied partial shared guard/route composition; original call ABI remains open."""
from pathlib import Path
import difflib
P=Path(__file__).resolve().parent;REL='programs/pump/src/admin_cto.rs'
def compose():
 old=(P/'baseline-admin_cto.rs').read_text();new=old
 marker=' if shared&&holder&&!a.coin_creator_vault_ata.data_is_empty(){invoke_signed('
 replacement=''' let shared_amm_frozen_zero=if shared&&holder&&!a.coin_creator_vault_ata.data_is_empty(){
  if token_frozen(&a.coin_creator_vault_ata.to_account_info())?{
   if token_raw_amount(&a.coin_creator_vault_ata.to_account_info())?>0{return Err(error!(PumpError::CtoSharedVaultFrozen));}
   true
  }else{false}
 }else{false};
 if shared&&holder&&!shared_amm_frozen_zero&&!a.coin_creator_vault_ata.data_is_empty(){invoke_signed('''
 assert new.count(marker)==1;new=new.replace(marker,replacement)
 marker='''  let rent=Rent::get()?.minimum_balance(0);let amount=if native{a.creator_vault.lamports().saturating_sub(rent)}else{token_amount(&a.creator_vault_quote_token_account.to_account_info())?};
  if amount>0||(!native&&!a.creator_vault_quote_token_account.data_is_empty()){'''
 replacement='''  let (rent,amount,shared_source_frozen)=if native{
   let rent=Rent::get()?.minimum_balance(0);
   (rent,a.creator_vault.lamports().saturating_sub(rent),false)
  }else{
   let amount=token_raw_amount(&a.creator_vault_quote_token_account.to_account_info())?;
   let frozen=token_frozen(&a.creator_vault_quote_token_account.to_account_info())?;
   if frozen&&amount>0{return Err(error!(PumpError::CtoSharedVaultFrozen));}
   (0,amount,frozen)
  };
  if !shared_source_frozen&&amount>0{'''
 assert new.count(marker)==1;new=new.replace(marker,replacement)
 return new,''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='baseline/'+REL,tofile='proposal/'+REL))
if __name__=='__main__':
 new,patch=compose();(P/'source'/REL).write_text(new);(P/'proposal.patch').write_text(patch)

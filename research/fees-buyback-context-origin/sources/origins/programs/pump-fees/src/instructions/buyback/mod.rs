use anchor_lang::prelude::*;
use crate::FeeError;
use crate::buyback::BuybackVault;








#[derive(Accounts)]
#[instruction(index:u8)]
pub struct InitializeBuyback<'info>{
 #[account(mut)]pub payer:Signer<'info>,
 #[account(init,payer=payer,space=208,seeds=[b"buyback-vault".as_ref(),&[index]],bump)]pub buyback_vault:Box<Account<'info,BuybackVault>>,
 #[account(init_if_needed,payer=payer,associated_token::mint=mint,associated_token::authority=buyback_vault,associated_token::token_program=token_program)]pub buyback_vault_ata:Box<InterfaceAccount<'info,anchor_spl::token_interface::TokenAccount>>,
 pub system_program:Program<'info,System>,pub associated_token_program:Program<'info,anchor_spl::associated_token::AssociatedToken>,
 pub mint:InterfaceAccount<'info,anchor_spl::token_interface::Mint>,pub token_program:Interface<'info,anchor_spl::token_interface::TokenInterface>,
 /// CHECK: event PDA.
 #[account(seeds=[b"__event_authority"],bump)]pub event_authority:AccountInfo<'info>,
 /// CHECK: event target.
 pub program:AccountInfo<'info>,
}





































































 pub fn initialize_buyback(_ctx:Context<InitializeBuyback>,index:u8)->Result<()>{require_gt!(8u8,index,FeeError::InvalidBuybackIndex);Ok(())}

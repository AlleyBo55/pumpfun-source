//! Partial social-fee behavior integrated from the independently validated draft.
use anchor_lang::prelude::*;
use crate::FeeError;
use crate::types::FeeProgramGlobal;
#[derive(Accounts)]
#[instruction(user_id:String,platform:u8)]
pub struct CreateSocialFeePda<'info>{
 #[account(mut)]pub payer:Signer<'info>,
 #[account(init_if_needed,payer=payer,space=179,seeds=[b"social-fee-pda",user_id.as_bytes(),&[platform]],bump)]pub social_fee_pda:Account<'info,SocialFeePda>,
 pub system_program:Program<'info,System>,
 #[account(seeds=[b"fee-program-global"],bump=fee_program_global.bump)]pub fee_program_global:Account<'info,FeeProgramGlobal>,
 /// CHECK: event authority PDA validated.
 #[account(seeds=[b"__event_authority"],bump)]pub event_authority:UncheckedAccount<'info>,
 /// CHECK: event-CPI program account; original imposes no typed-program constraint.
 pub program:UncheckedAccount<'info>,
}
pub use crate::state::SocialFeePda;
#[event]
pub struct SocialFeePdaCreated{pub timestamp:i64,pub user_id:String,pub platform:u8,pub social_fee_pda:Pubkey,pub created_by:Pubkey}

#[derive(Accounts)]
#[instruction(user_id:String,platform:u8)]
pub struct ClaimSocialFeePda<'info>{
 /// CHECK: arbitrary recipient validated in handler.
 #[account(mut)]pub recipient:UncheckedAccount<'info>,
 #[account(mut,seeds=[b"social-fee-pda",user_id.as_bytes(),&[platform]],bump=social_fee_pda.bump)]pub social_fee_pda:Account<'info,SocialFeePda>,
 #[account(seeds=[b"fee-program-global"],bump=fee_program_global.bump,has_one=social_claim_authority @ FeeError::NotAuthorized)]pub fee_program_global:Account<'info,FeeProgramGlobal>,
 pub social_claim_authority:Signer<'info>,
 /// CHECK: event PDA.
 #[account(seeds=[b"__event_authority"],bump)]pub event_authority:UncheckedAccount<'info>,
 /// CHECK: event CPI target.
 pub program:UncheckedAccount<'info>,
}
#[event]
#[derive(Clone)]
pub struct SocialFeePdaClaimed{pub timestamp:i64,pub user_id:String,pub platform:u8,pub social_fee_pda:Pubkey,pub recipient:Pubkey,pub social_claim_authority:Pubkey,pub amount_claimed:u64,pub claimable_before:u64,pub lifetime_claimed:u64,pub recipient_balance_before:u64,pub recipient_balance_after:u64,pub quote_mint:Pubkey,pub lifetime_stable_claimed:u64}

#[derive(Accounts)]
#[instruction(user_id:String,platform:u8)]
pub struct ClaimSocialFeePdaV2<'info>{
 /// CHECK: recipient.
 #[account(mut)]pub recipient:UncheckedAccount<'info>,
 #[account(mut,seeds=[b"social-fee-pda",user_id.as_bytes(),&[platform]],bump=social_fee_pda.bump)]pub social_fee_pda:Account<'info,SocialFeePda>,
 #[account(mut)]pub quote_mint:Box<InterfaceAccount<'info,anchor_spl::token_interface::Mint>>,
 /// CHECK: canonical ATA; data validated on token branch.
 #[account(mut,seeds=[social_fee_pda.key().as_ref(),quote_token_program.key().as_ref(),quote_mint.key().as_ref()],bump,seeds::program=associated_token_program.key())]pub associated_social_fee_pda:UncheckedAccount<'info>,
 /// CHECK: canonical ATA; data validated on token branch.
 #[account(mut,seeds=[recipient.key().as_ref(),quote_token_program.key().as_ref(),quote_mint.key().as_ref()],bump,seeds::program=associated_token_program.key())]pub associated_recipient:UncheckedAccount<'info>,
 pub quote_token_program:Interface<'info,anchor_spl::token_interface::TokenInterface>,
 pub associated_token_program:Program<'info,anchor_spl::associated_token::AssociatedToken>,
 #[account(seeds=[b"fee-program-global"],bump=fee_program_global.bump,has_one=social_claim_authority @ FeeError::NotAuthorized)]pub fee_program_global:Account<'info,FeeProgramGlobal>,
 pub social_claim_authority:Signer<'info>,
 pub system_program:Program<'info,System>,
 /// CHECK: event PDA.
 #[account(seeds=[b"__event_authority"],bump)]pub event_authority:AccountInfo<'info>,
 /// CHECK: event CPI target.
 pub program:AccountInfo<'info>,
}

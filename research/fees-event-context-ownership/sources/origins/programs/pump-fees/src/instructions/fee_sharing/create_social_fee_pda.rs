use anchor_lang::prelude::*;
use crate::types::FeeProgramGlobal;
use crate::state::SocialFeePda;







#[derive(Accounts)]
#[instruction(user_id:String,platform:u8)]
pub struct CreateSocialFeePda<'info>{
 #[account(mut)]pub payer:Signer<'info>,
 #[account(init_if_needed,payer=payer,space=179,seeds=[b"social-fee-pda",user_id.as_bytes(),&[platform]],bump)]pub social_fee_pda:Account<'info,SocialFeePda>,
 pub system_program:Program<'info,System>,
 #[account(seeds=[b"fee-program-global"],bump=fee_program_global.bump)]pub fee_program_global:Account<'info,FeeProgramGlobal>,
 /// CHECK: event authority PDA validated.
 #[account(seeds=[b"__event_authority"],bump)]pub event_authority:AccountInfo<'info>,
 /// CHECK: event-CPI program account; original imposes no typed-program constraint.
 pub program:AccountInfo<'info>,
}

use anchor_lang::prelude::*;
use crate::FeeError;
use crate::social::{CreateSocialFeePda, SocialFeePdaCreated};

 pub fn create_social(ctx:Context<CreateSocialFeePda>,user_id:String,platform:u8)->Result<()> {
  require!(ctx.accounts.fee_program_global.disable_flags & 1 == 0,FeeError::FeatureDeactivated);
  require!(user_id.len()<=20,FeeError::UserIdTooLong);
  if ctx.accounts.social_fee_pda.version!=0{return Ok(());}
  let state=&mut ctx.accounts.social_fee_pda;
  state.bump=ctx.bumps.social_fee_pda;state.version=1;state.user_id=user_id.clone();state.platform=platform;
  state.total_claimed=0;state.last_claimed=0;state.total_stable_claimed=0;state._reserved=[0;120];
  let event=SocialFeePdaCreated{timestamp:Clock::get()?.unix_timestamp,user_id,platform,social_fee_pda:state.key(),created_by:ctx.accounts.payer.key()};
  emit!(event);emit_cpi!(event);Ok(())
 }

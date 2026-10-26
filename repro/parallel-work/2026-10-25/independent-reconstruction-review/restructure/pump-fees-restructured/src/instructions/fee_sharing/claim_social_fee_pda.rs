use anchor_lang::prelude::*;
use crate::FeeError;
use crate::social::{ClaimSocialFeePda, ClaimSocialFeePdaV2, SocialFeePdaClaimed};

 pub fn claim_v2(ctx:Context<ClaimSocialFeePdaV2>,_user_id:String,_platform:u8)->Result<Option<SocialFeePdaClaimed>> {
  require!(ctx.accounts.fee_program_global.disable_flags&2==0,FeeError::FeatureDeactivated);
  let timestamp=Clock::get()?.unix_timestamp;let now=timestamp as u64;
  let state=&mut ctx.accounts.social_fee_pda;
  if state.last_claimed!=0 && now.saturating_sub(state.last_claimed)<ctx.accounts.fee_program_global.claim_rate_limit{return Ok(None);}
  let native=ctx.accounts.quote_mint.key()==anchor_spl::token::spl_token::native_mint::ID;
  let amount;let before;let after;
  if native {
   amount=state.to_account_info().lamports().saturating_sub(Rent::get()?.minimum_balance(179));
   if amount==0 || ctx.accounts.recipient.executable{return Ok(None);}
   before=ctx.accounts.recipient.lamports();
   {let info=state.to_account_info();let mut from=info.try_borrow_mut_lamports()?;let mut to=ctx.accounts.recipient.try_borrow_mut_lamports()?;**from-=amount;**to+=amount;}
   after=ctx.accounts.recipient.lamports();state.total_claimed=state.total_claimed.saturating_add(amount);
  }else{
   crate::instructions::fee_sharing::admit_associated_token_account(
    &ctx.accounts.associated_social_fee_pda,&state.to_account_info(),&ctx.accounts.quote_mint.key(),
    &ctx.accounts.quote_token_program.key(),&ctx.accounts.quote_mint.to_account_info(),&ctx.accounts.quote_token_program,
    false,&ctx.accounts.social_claim_authority,&ctx.accounts.system_program)?;
   crate::instructions::fee_sharing::admit_associated_token_account(
    &ctx.accounts.associated_recipient,&ctx.accounts.recipient.to_account_info(),&ctx.accounts.quote_mint.key(),
    &ctx.accounts.quote_token_program.key(),&ctx.accounts.quote_mint.to_account_info(),&ctx.accounts.quote_token_program,
    true,&ctx.accounts.social_claim_authority,&ctx.accounts.system_program)?;
   amount={
    let data=ctx.accounts.associated_social_fee_pda.try_borrow_data()?;
    anchor_spl::token_interface::TokenAccount::try_deserialize(&mut &data[..])?.amount
   };
   if amount==0{return Ok(None);}
   before={
    let data=ctx.accounts.associated_recipient.try_borrow_data()?;
    anchor_spl::token_interface::TokenAccount::try_deserialize(&mut &data[..]).map(|account|account.amount).unwrap_or_default()
   };
   let platform=[state.platform];let bump=[state.bump];let seeds:&[&[u8]]=&[b"social-fee-pda",state.user_id.as_bytes(),&platform,&bump];
   anchor_spl::token_interface::transfer_checked(CpiContext::new_with_signer(ctx.accounts.quote_token_program.to_account_info(),anchor_spl::token_interface::TransferChecked{from:ctx.accounts.associated_social_fee_pda.to_account_info(),mint:ctx.accounts.quote_mint.to_account_info(),to:ctx.accounts.associated_recipient.to_account_info(),authority:state.to_account_info()},&[seeds]),amount,ctx.accounts.quote_mint.decimals)?;
   after=before.saturating_add(amount);
   state.total_stable_claimed=state.total_stable_claimed.saturating_add(amount);
  }
  state.last_claimed=now;
  let event=SocialFeePdaClaimed{timestamp,user_id:state.user_id.clone(),platform:state.platform,social_fee_pda:state.key(),recipient:ctx.accounts.recipient.key(),social_claim_authority:ctx.accounts.social_claim_authority.key(),amount_claimed:amount,claimable_before:amount,lifetime_claimed:state.total_claimed,recipient_balance_before:before,recipient_balance_after:after,quote_mint:if native{Pubkey::default()}else{ctx.accounts.quote_mint.key()},lifetime_stable_claimed:state.total_stable_claimed};
  emit!(event);emit_cpi!(event.clone());Ok(Some(event))
 }

pub fn claim(ctx:Context<ClaimSocialFeePda>,user_id:String,platform:u8)->Result<Option<SocialFeePdaClaimed>> {
  require!(ctx.accounts.fee_program_global.disable_flags&2==0,FeeError::FeatureDeactivated);
  let state=&mut ctx.accounts.social_fee_pda;
  let timestamp=Clock::get()?.unix_timestamp;let now=timestamp as u64;
  if state.last_claimed!=0 && now.saturating_sub(state.last_claimed)<ctx.accounts.fee_program_global.claim_rate_limit {return Ok(None);}
  let amount=state.to_account_info().lamports().saturating_sub(Rent::get()?.minimum_balance(179));
  if amount==0 || ctx.accounts.recipient.executable{return Ok(None);}
  let before=ctx.accounts.recipient.lamports();
  {let info=state.to_account_info();let mut from=info.try_borrow_mut_lamports()?;let mut to=ctx.accounts.recipient.try_borrow_mut_lamports()?;**from-=amount;**to+=amount;}
  state.total_claimed=state.total_claimed.saturating_add(amount);state.last_claimed=now;
  let event=SocialFeePdaClaimed {timestamp,user_id:state.user_id.clone(),platform:state.platform,social_fee_pda:state.key(),recipient:ctx.accounts.recipient.key(),social_claim_authority:ctx.accounts.social_claim_authority.key(),amount_claimed:amount,claimable_before:amount,lifetime_claimed:state.total_claimed,recipient_balance_before:before,recipient_balance_after:ctx.accounts.recipient.lamports(),quote_mint:Pubkey::default(),lifetime_stable_claimed:state.total_stable_claimed};
  emit!(event);emit_cpi!(event.clone());Ok(Some(event))
 }

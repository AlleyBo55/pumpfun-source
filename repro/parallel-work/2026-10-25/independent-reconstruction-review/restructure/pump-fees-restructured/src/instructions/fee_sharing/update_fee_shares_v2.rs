//! Recovered sharing updates; captured Pump/AMM dependencies execute their own CPIs.
use anchor_lang::prelude::*;
use anchor_lang::solana_program::{instruction::{Instruction,AccountMeta},program::invoke};
use crate::{FeeError, pump_global};
use crate::types::Shareholder;
use crate::instructions::fee_sharing::create_donation_fee_pda::{PUMP, AMM, BondingCurve, ConfigStatus, SharingConfig};
use crate::sharing::{Pump, Amm};
use crate::sharing_update::*;

 pub fn update_fee_shares_v2<'info>(mut ctx:Context<'_, '_, '_, 'info,UpdateFeeSharesV2<'info>>,shareholders:Vec<Shareholder>)->Result<()> {
  require!(ctx.accounts.sharing_config.version!=1,FeeError::FeeSharesAlreadyUpdated);
  // Same complete authorization target [234096,235304) as legacy.
  legacy_authorize(&ctx.accounts.sharing_config,ctx.accounts.authority.key())?;
  let quote = ctx.accounts.quote_mint.key();
  let expected = v2_expected_quote(&ctx.accounts.bonding_curve.to_account_info());
  if quote != expected {
      return Err(error!(FeeError::InvalidQuoteMint).with_pubkeys((quote, expected)));
  }
  ctx.remaining_accounts = preprocess_remaining(
      ctx.remaining_accounts, &ctx.accounts.bonding_curve,
      &ctx.accounts.mint.key(), &expected,
  )?;
  v2_transfer_creator_fees_to_pump(
      &ctx.accounts.bonding_curve,
      crate::pump_amm::cpi::accounts::TransferCreatorFeesToPumpV2 {
          payer: ctx.accounts.authority.to_account_info(),
          quote_mint: ctx.accounts.quote_mint.to_account_info(),
          token_program: ctx.accounts.token_program.to_account_info(),
          system_program: ctx.accounts.system_program.to_account_info(),
          associated_token_program: ctx.accounts.associated_token_program.to_account_info(),
          coin_creator: ctx.accounts.sharing_config.to_account_info(),
          coin_creator_vault_authority: ctx.accounts.coin_creator_vault_authority.to_account_info(),
          coin_creator_vault_ata: ctx.accounts.coin_creator_vault_ata.to_account_info(),
          pump_creator_vault: ctx.accounts.pump_creator_vault.to_account_info(),
          pump_creator_vault_ata: ctx.accounts.pump_creator_vault_ata.to_account_info(),
          event_authority: ctx.accounts.amm_event_authority.to_account_info(),
          program: ctx.accounts.pump_amm_program.to_account_info(),
      },
  )?;
  // The cloned AccountInfo/borrow die before payout preparation.
  let zero_quote = legacy_curve_quote_is_zero(&ctx.accounts.bonding_curve.to_account_info())?;
  let prepared = if zero_quote {
      prepare_v2_zero_payout(ctx.remaining_accounts, &ctx.accounts.sharing_config.shareholders)?
  } else {
      prepare_v2_quote_payout(ctx.remaining_accounts, &ctx.accounts.sharing_config.shareholders)?
  };
  if prepared.changed {
      ctx.accounts.sharing_config.shareholders = prepared.shareholders;
      ctx.accounts.sharing_config.exit(&crate::ID)?;
  }
  if !prepared.accounts.is_empty() {
      v2_distribute_creator_fees(
          crate::pump::cpi::accounts::DistributeCreatorFeesV2 {
              payer: ctx.accounts.authority.to_account_info(),
              mint: ctx.accounts.mint.to_account_info(),
              bonding_curve: ctx.accounts.bonding_curve.to_account_info(),
              sharing_config: ctx.accounts.sharing_config.to_account_info(),
              creator_vault: ctx.accounts.pump_creator_vault.to_account_info(),
              system_program: ctx.accounts.system_program.to_account_info(),
              event_authority: ctx.accounts.pump_event_authority.to_account_info(),
              program: ctx.accounts.pump_program.to_account_info(),
              creator_vault_quote_token_account: ctx.accounts.pump_creator_vault_ata.to_account_info(),
              quote_mint: ctx.accounts.quote_mint.to_account_info(),
              quote_token_program: ctx.accounts.token_program.to_account_info(),
              associated_token_program: ctx.accounts.associated_token_program.to_account_info(),
          },
          prepared.accounts,
      )?;
  }
  v2_validate_shares(&shareholders)?;
  let state=&mut ctx.accounts.sharing_config;state.shareholders=shareholders.clone();state.admin_revoked=true;
  let event=UpdateFeeSharesEvent{timestamp:Clock::get()?.unix_timestamp,mint:ctx.accounts.mint.key(),sharing_config:state.key(),admin:state.admin,new_shareholders:shareholders,version:state.version};emit!(event);emit_cpi!(event);Ok(())
 }


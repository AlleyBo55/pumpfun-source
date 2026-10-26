//! Recovered sharing updates; captured Pump/AMM dependencies execute their own CPIs.
use anchor_lang::prelude::*;
use anchor_lang::solana_program::{instruction::{Instruction,AccountMeta},program::invoke};
use crate::{FeeError, pump_global};
use crate::types::Shareholder;
use crate::instructions::fee_sharing::create_donation_fee_pda::{PUMP, AMM, BondingCurve, ConfigStatus, SharingConfig};
use crate::sharing::{Pump, Amm};
use crate::sharing_update::*;

pub fn update_fee_shares<'info>(mut ctx:Context<'_, '_, '_, 'info,UpdateFeeShares<'info>>,shareholders:Vec<Shareholder>)->Result<()> {
  // The temporary AccountInfo and its data borrow end before version/auth checks.
  let quote_is_zero = legacy_curve_quote_is_zero(&ctx.accounts.bonding_curve.to_account_info())?;
  require!(quote_is_zero,FeeError::UnsupportedQuoteMint);
  require!(ctx.accounts.sharing_config.version!=1,FeeError::FeeSharesAlreadyUpdated);
  legacy_authorize(&ctx.accounts.sharing_config,ctx.accounts.authority.key())?;
  ctx.remaining_accounts = preprocess_remaining(
      ctx.remaining_accounts, &ctx.accounts.bonding_curve,
      &ctx.accounts.mint.key(), &anchor_spl::token::spl_token::native_mint::ID,
  )?;
  // Own the fixed accounts before the adapter's reserve/owner guard.
  legacy_transfer_creator_fees_to_pump(
      &ctx.accounts.bonding_curve,
      crate::pump_amm::cpi::accounts::TransferCreatorFeesToPump {
          program: ctx.accounts.pump_amm_program.to_account_info(),
          wsol_mint: ctx.accounts.wsol_mint.to_account_info(),
          token_program: ctx.accounts.token_program.to_account_info(),
          system_program: ctx.accounts.system_program.to_account_info(),
          associated_token_program: ctx.accounts.associated_token_program.to_account_info(),
          coin_creator: ctx.accounts.sharing_config.to_account_info(),
          coin_creator_vault_authority: ctx.accounts.coin_creator_vault_authority.to_account_info(),
          coin_creator_vault_ata: ctx.accounts.coin_creator_vault_ata.to_account_info(),
          pump_creator_vault: ctx.accounts.pump_creator_vault.to_account_info(),
          event_authority: ctx.accounts.amm_event_authority.to_account_info(),
      },
  )?;
  // Existing shareholder validation belongs here, after the AMM call.
  let payout_accounts = legacy_payout_accounts(
      &mut ctx.accounts.sharing_config, ctx.remaining_accounts,
  )?;
  if !payout_accounts.is_empty() {
  legacy_distribute_creator_fees(
      crate::pump::cpi::accounts::DistributeCreatorFees {
          program: ctx.accounts.pump_program.to_account_info(),
          mint: ctx.accounts.mint.to_account_info(),
          bonding_curve: ctx.accounts.bonding_curve.to_account_info(),
          sharing_config: ctx.accounts.sharing_config.to_account_info(),
          creator_vault: ctx.accounts.pump_creator_vault.to_account_info(),
          system_program: ctx.accounts.system_program.to_account_info(),
          event_authority: ctx.accounts.pump_event_authority.to_account_info(),
      },
      payout_accounts,
  )?;
  }
  legacy_validate_shares(&shareholders)?;
  let state=&mut ctx.accounts.sharing_config;state.shareholders=shareholders.clone();state.admin_revoked=true;
  let event=UpdateFeeSharesEvent{timestamp:Clock::get()?.unix_timestamp,mint:ctx.accounts.mint.key(),sharing_config:state.key(),admin:state.admin,new_shareholders:shareholders,version:state.version};emit!(event);emit_cpi!(event);Ok(())
 }

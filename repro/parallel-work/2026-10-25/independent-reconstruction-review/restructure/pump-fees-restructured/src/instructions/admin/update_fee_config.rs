use anchor_lang::prelude::*;
use crate::contexts::*;
use crate::types::*;
use crate::FeeError;
use crate::instructions::common::*;

pub fn update_fee_config(ctx: Context<UpdateFeeConfig>, fee_tiers: Vec<FeeTier>, flat_fees: Fees) -> Result<()> {
        validate_fees(&flat_fees)?;
        validate_tiers(&fee_tiers)?;
        ctx.accounts.fee_config.fee_tiers = fee_tiers.clone();
        ctx.accounts.fee_config.flat_fees = flat_fees.clone();
        let event = UpdateFeeConfigEvent { timestamp: Clock::get()?.unix_timestamp,
            admin: ctx.accounts.admin.key(), fee_config: ctx.accounts.fee_config.key(), fee_tiers, flat_fees };
        emit!(event.clone()); emit_cpi!(event); Ok(())
    }

pub fn update_stable_fee_config(ctx: Context<UpdateStableFeeConfig>, fee_tiers: Vec<FeeTier>) -> Result<()> {
        validate_tiers(&fee_tiers)?;
        ctx.accounts.fee_config.stable_fee_tiers = fee_tiers.clone();
        let event = UpdateStableFeeConfigEvent { timestamp: Clock::get()?.unix_timestamp,
            admin: ctx.accounts.admin.key(), fee_config: ctx.accounts.fee_config.key(),
            stable_fee_tiers: fee_tiers, flat_fees: ctx.accounts.fee_config.flat_fees.clone() };
        emit!(event.clone()); emit_cpi!(event); Ok(())
    }

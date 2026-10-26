use anchor_lang::prelude::*;
use crate::contexts::*;
use crate::types::*;
use crate::FeeError;
use crate::instructions::common::*;

pub fn upsert_fee_tiers(ctx: Context<UpsertFeeTiers>, fee_tiers: Vec<FeeTier>, offset: u8) -> Result<()> {
        upsert_tiers(&mut ctx.accounts.fee_config.fee_tiers, &fee_tiers, offset)?;
        let event = UpsertFeeTiersEvent { timestamp: Clock::get()?.unix_timestamp,
            admin: ctx.accounts.admin.key(), fee_config: ctx.accounts.fee_config.key(), fee_tiers, offset };
        emit!(event.clone()); emit_cpi!(event); Ok(())
    }

pub fn upsert_stable_fee_tiers(ctx: Context<UpsertStableFeeTiers>, fee_tiers: Vec<FeeTier>, offset: u8) -> Result<()> {
        upsert_tiers(&mut ctx.accounts.fee_config.stable_fee_tiers, &fee_tiers, offset)?;
        let event = UpsertStableFeeTiersEvent { timestamp: Clock::get()?.unix_timestamp,
            admin: ctx.accounts.admin.key(), fee_config: ctx.accounts.fee_config.key(), stable_fee_tiers: fee_tiers, offset };
        emit!(event.clone()); emit_cpi!(event); Ok(())
    }

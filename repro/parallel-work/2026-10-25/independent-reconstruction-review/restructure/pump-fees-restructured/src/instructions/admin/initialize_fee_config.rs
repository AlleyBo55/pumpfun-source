use anchor_lang::prelude::*;
use crate::contexts::*;
use crate::types::*;
use crate::FeeError;
use crate::instructions::common::*;

pub fn initialize_fee_config(ctx: Context<InitializeFeeConfig>) -> Result<()> {
        ctx.accounts.fee_config.bump = ctx.bumps.fee_config;
        ctx.accounts.fee_config.admin = ctx.accounts.admin.key();
        let event = InitializeFeeConfigEvent {
            timestamp: Clock::get()?.unix_timestamp,
            admin: ctx.accounts.admin.key(),
            fee_config: ctx.accounts.fee_config.key(),
        };
        emit!(event);
        emit_cpi!(event);
        Ok(())
    }

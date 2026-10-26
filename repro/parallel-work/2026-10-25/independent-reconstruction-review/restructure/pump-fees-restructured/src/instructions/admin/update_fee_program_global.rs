use anchor_lang::prelude::*;
use crate::contexts::*;
use crate::types::*;
use crate::FeeError;
use crate::instructions::common::*;

pub fn set_authority(ctx: Context<SetAuthority>, new_authority: Pubkey) -> Result<()> {
        require!(new_authority != Pubkey::default(), FeeError::InvalidAdmin);
        let old_authority = ctx.accounts.fee_program_global.authority;
        ctx.accounts.fee_program_global.authority = new_authority;
        let event = SetAuthorityEvent { timestamp: Clock::get()?.unix_timestamp, old_authority, new_authority };
        emit!(event);
        emit_cpi!(event);
        Ok(())
    }

pub fn set_claim_rate_limit(ctx: Context<SetClaimRateLimit>, claim_rate_limit: u64) -> Result<()> {
        ctx.accounts.fee_program_global.claim_rate_limit = claim_rate_limit;
        let event = SetClaimRateLimitEvent { timestamp: Clock::get()?.unix_timestamp, claim_rate_limit };
        emit!(event);
        emit_cpi!(event);
        Ok(())
    }

pub fn set_disable_flags(ctx: Context<SetDisableFlags>, disable_flags: u8) -> Result<()> {
        ctx.accounts.fee_program_global.disable_flags = disable_flags;
        let event = SetDisableFlagsEvent { timestamp: Clock::get()?.unix_timestamp, disable_flags };
        emit!(event);
        emit_cpi!(event);
        Ok(())
    }

pub fn set_social_claim_authority(ctx: Context<SetSocialClaimAuthority>, social_claim_authority: Pubkey) -> Result<()> {
        ctx.accounts.fee_program_global.social_claim_authority = social_claim_authority;
        let event = SetSocialClaimAuthorityEvent { timestamp: Clock::get()?.unix_timestamp, social_claim_authority };
        emit!(event);
        emit_cpi!(event);
        Ok(())
    }

pub fn update_admin(ctx: Context<UpdateAdmin>) -> Result<()> {
        let old_admin = ctx.accounts.fee_config.admin;
        ctx.accounts.fee_config.admin = ctx.accounts.new_admin.key();
        let event = UpdateAdminEvent { timestamp: Clock::get()?.unix_timestamp, old_admin, new_admin: ctx.accounts.fee_config.admin };
        emit!(event); emit_cpi!(event); Ok(())
    }

pub fn set_exotic_flat_fees(ctx: Context<SetExoticFlatFees>, exotic_flat_fees: Fees) -> Result<()> {
        validate_fees(&exotic_flat_fees)?;
        let info = ctx.accounts.fee_config.to_account_info();
        if info.data_len() < 4097 {
            let rent = Rent::get()?.minimum_balance(4097);
            let extra = rent.saturating_sub(info.lamports());
            if extra > 0 {
                anchor_lang::system_program::transfer(CpiContext::new(
                    ctx.accounts.system_program.to_account_info(), anchor_lang::system_program::Transfer {
                        from: ctx.accounts.admin.to_account_info(), to: info.clone(),
                    }), extra)?;
            }
            info.realloc(4097, true)?;
        }
        ctx.accounts.fee_config.exotic_flat_fees = exotic_flat_fees.clone();
        let event = SetExoticFlatFeesEvent { timestamp: Clock::get()?.unix_timestamp,
            admin: ctx.accounts.admin.key(), fee_config: ctx.accounts.fee_config.key(), exotic_flat_fees };
        emit!(event.clone()); emit_cpi!(event); Ok(())
    }

use anchor_lang::prelude::*;
use crate::contexts::*;
use crate::types::*;
use crate::FeeError;
use crate::instructions::common::*;

pub fn initialize_fee_program_global(ctx: Context<InitializeFeeProgramGlobal>, social_claim_authority: Pubkey, disable_flags: u8, claim_rate_limit: u64) -> Result<()> {
        let state = &mut ctx.accounts.fee_program_global;
        state.bump = ctx.bumps.fee_program_global;
        state.authority = ctx.accounts.authority.key();
        state.social_claim_authority = social_claim_authority;
        state.disable_flags = disable_flags;
        state.claim_rate_limit = claim_rate_limit;
        let event = InitializeFeeProgramGlobalEvent {
            timestamp: Clock::get()?.unix_timestamp, authority: ctx.accounts.authority.key(),
            social_claim_authority, disable_flags, claim_rate_limit,
        };
        emit!(event);
        emit_cpi!(event);
        Ok(())
    }

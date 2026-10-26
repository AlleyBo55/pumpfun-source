use anchor_lang::prelude::*;
use crate::*;
use crate::state::*;
use crate::checked_program::*;
use anchor_spl::{associated_token::AssociatedToken, token_interface::{Mint, TokenAccount, TokenInterface}};

pub fn initialize_global_params(ctx: Context<InitializeGlobalParams>) -> Result<()> {
        ctx.accounts.global_params.admin = ctx.accounts.admin.key();
        Ok(())
    }

pub fn update_global_params(ctx: Context<Admin>, args: UpdateGlobalParamsArgs) -> Result<()> {
        let state = &mut ctx.accounts.global_params;
        if let Some(v) = args.field_0 { state.reset_prefix[0..4].copy_from_slice(&v.to_le_bytes()); }
        if let Some(v) = args.field_1 { state.reset_prefix[4..8].copy_from_slice(&v.to_le_bytes()); }
        for (value, offset) in [(args.field_2, 8), (args.field_3, 16), (args.field_4, 24), (args.field_5, 32)] {
            if let Some(v) = value { state.reset_prefix[offset..offset+8].copy_from_slice(&v.to_le_bytes()); }
        }
        if let Some(v) = args.field_6 { state.reset_middle[0] = v; }
        if let Some(v) = args.field_7 { state.reset_middle[9..17].copy_from_slice(&v.to_le_bytes()); }
        if let Some(v) = args.field_8 { state.reset_middle[17..25].copy_from_slice(&v.to_le_bytes()); }
        if let Some(v) = args.field_9 { state.preserved_middle_a.copy_from_slice(&v.to_le_bytes()); }
        if let Some(v) = args.field_10 { state.field_10 = v; }
        for (value, offset) in [(args.field_11, 0), (args.field_12, 8), (args.field_13, 16)] {
            if let Some(v) = value { state.reset_stable_prefix[offset..offset+8].copy_from_slice(&v.to_le_bytes()); }
        }
        if let Some(v) = args.field_14 { state.reset_stable_suffix[0..8].copy_from_slice(&v.to_le_bytes()); }
        if let Some(v) = args.field_15 { state.reset_stable_suffix[8..16].copy_from_slice(&v.to_le_bytes()); }
        let old_version = state.version;
        state.version = state.version.checked_add(1).ok_or(MayhemError::MathOverflow)?;
        let event = GlobalParamsUpdateEvent {
            old_version, new_version: state.version,
            field_0: u32::from_le_bytes(state.reset_prefix[0..4].try_into().unwrap()),
            field_1: u32::from_le_bytes(state.reset_prefix[4..8].try_into().unwrap()),
            field_2: u64::from_le_bytes(state.reset_prefix[8..16].try_into().unwrap()),
            field_3: u64::from_le_bytes(state.reset_prefix[16..24].try_into().unwrap()),
            field_4: u64::from_le_bytes(state.reset_prefix[24..32].try_into().unwrap()),
            field_5: u64::from_le_bytes(state.reset_prefix[32..40].try_into().unwrap()),
            field_6: state.reset_middle[0],
            field_7: u64::from_le_bytes(state.reset_middle[9..17].try_into().unwrap()),
            field_8: u64::from_le_bytes(state.reset_middle[17..25].try_into().unwrap()),
            field_9: u64::from_le_bytes(state.preserved_middle_a),
            field_10: state.field_10,
            field_11: u64::from_le_bytes(state.reset_stable_prefix[0..8].try_into().unwrap()),
            field_12: u64::from_le_bytes(state.reset_stable_prefix[8..16].try_into().unwrap()),
            field_13: u64::from_le_bytes(state.reset_stable_prefix[16..24].try_into().unwrap()),
            field_14: u64::from_le_bytes(state.reset_stable_suffix[0..8].try_into().unwrap()),
            field_15: u64::from_le_bytes(state.reset_stable_suffix[8..16].try_into().unwrap()),
        };
        emit!(event);
        emit_cpi!(event);
        Ok(())
    }

pub fn update_admin(ctx: Context<Admin>, new_admin: Pubkey) -> Result<()> {
        ctx.accounts.global_params.admin = new_admin;
        Ok(())
    }

pub fn update_trader(ctx: Context<Admin>, new_trader: Pubkey) -> Result<()> {
        ctx.accounts.global_params.trader = new_trader;
        Ok(())
    }

pub fn update_max_sol_per_sweep(ctx: Context<Admin>, value: u64) -> Result<()> {
        ctx.accounts.global_params.max_sol_per_sweep = value;
        Ok(())
    }

pub fn update_max_stable_per_sweep(ctx: Context<Admin>, value: u64) -> Result<()> {
        ctx.accounts.global_params.max_stable_per_sweep = value;
        Ok(())
    }

pub fn reset_sol_deployed(ctx: Context<Admin>) -> Result<()> {
        ctx.accounts.global_params.sol_deployed = 0;
        Ok(())
    }

pub fn reset_stable_deployed(ctx: Context<Admin>) -> Result<()> {
        ctx.accounts.global_params.stable_deployed = 0;
        Ok(())
    }

pub fn reset_state(ctx: Context<Admin>) -> Result<()> {
        let state = &mut ctx.accounts.global_params;
        state.reset_prefix = [0; 40];
        state.paused = false;
        state.sol_deployed = 0;
        state.reset_middle = [0; 25];
        state.reset_stable_prefix = [0; 24];
        state.stable_deployed = 0;
        state.reset_stable_suffix = [0; 24];
        Ok(())
    }

pub fn stop_trading(ctx: Context<Admin>) -> Result<()> {
        require_eq!(ctx.accounts.global_params.paused, false, MayhemError::TradingPaused);
        ctx.accounts.global_params.paused = true;
        Ok(())
    }

pub fn resume_trading(ctx: Context<Admin>) -> Result<()> {
        // The original also uses 6000/TradingPaused when already active.
        require_eq!(ctx.accounts.global_params.paused, true, MayhemError::TradingPaused);
        ctx.accounts.global_params.paused = false;
        Ok(())
    }

use anchor_lang::prelude::*;
use anchor_spl::token_interface::{Mint, TokenAccount, TokenInterface};
use crate::create_v2::MAYHEM_ID;
use crate::trade_types::BondingCurve;
use crate::{Global, PumpError, UpdateMayhemVirtualParamsEvent};

// Mayhem resyncs a bonding curve's virtual quote (SOL-side) reserve against the mayhem
// sol-vault token balance. Account #0 (`sol_vault_authority`) is mayhem's ["sol-vault"] PDA
// and must sign, so this instruction is reachable only through a mayhem `invoke_signed` CPI.
#[event_cpi]
#[derive(Accounts)]
pub struct SetMayhemVirtualParams<'info> {
    #[account(mut, seeds = [b"sol-vault"], bump, seeds::program = MAYHEM_ID)]
    pub sol_vault_authority: Signer<'info>,
    #[account(mut, associated_token::mint = mint, associated_token::authority = sol_vault_authority, associated_token::token_program = token_program)]
    pub mayhem_token_vault: InterfaceAccount<'info, TokenAccount>,
    pub mint: InterfaceAccount<'info, Mint>,
    #[account(seeds = [b"global"], bump)]
    pub global: Box<Account<'info, Global>>,
    #[account(mut, seeds = [b"bonding-curve", mint.key().as_ref()], bump)]
    pub bonding_curve: Account<'info, BondingCurve>,
    #[account(address = anchor_spl::token_2022::ID)]
    pub token_program: Interface<'info, TokenInterface>,
}

pub fn execute(ctx: Context<SetMayhemVirtualParams>) -> Result<()> {
    let vault_amount = ctx.accounts.mayhem_token_vault.amount;
    let initial_real_token_reserves = ctx.accounts.global.initial_real_token_reserves;
    let mint = ctx.accounts.mint.key();
    let bc = &mut ctx.accounts.bonding_curve;
    let virtual_token_reserves = bc.virtual_token_reserves;
    let virtual_sol_reserves = bc.virtual_quote_reserves;

    if bc.is_mayhem_mode {
        // den = 2 * token_total_supply - global.initial_real_token_reserves - mayhem_token_vault.amount
        let denominator = bc
            .token_total_supply
            .checked_mul(2)
            .ok_or(PumpError::Overflow)?
            .checked_sub(initial_real_token_reserves)
            .ok_or(PumpError::Overflow)?
            .checked_sub(vault_amount)
            .ok_or(PumpError::Overflow)?;
        if bc.real_quote_reserves >= 10_000_000 && denominator >= 1_000_000_000_000 {
            let scaled = (bc.real_quote_reserves as u128)
                .checked_mul(bc.virtual_token_reserves as u128)
                .ok_or(PumpError::Overflow)?
                .checked_div(denominator as u128)
                .ok_or(PumpError::DivisionByZero)? as u64;
            let computed = bc
                .real_quote_reserves
                .checked_add(scaled)
                .ok_or(PumpError::Overflow)?;
            let cap = if bc.quote_mint == Pubkey::default() {
                2_000_000_000_000
            } else {
                160_000_000_000
            };
            bc.virtual_quote_reserves = computed.min(cap);
        }
    }

    let event = UpdateMayhemVirtualParamsEvent {
        timestamp: Clock::get()?.unix_timestamp,
        mint,
        virtual_token_reserves,
        virtual_sol_reserves,
        new_virtual_token_reserves: bc.virtual_token_reserves,
        new_virtual_sol_reserves: bc.virtual_quote_reserves,
        real_token_reserves: bc.real_token_reserves,
        real_sol_reserves: bc.real_quote_reserves,
    };
    emit!(event.clone());
    emit_cpi!(event);
    Ok(())
}

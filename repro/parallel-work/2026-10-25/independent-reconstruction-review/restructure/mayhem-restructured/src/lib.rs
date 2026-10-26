//! Partial independently compiled Mayhem implementation: 24 recovered administration, sweep,
//! burn and recovered trade handlers. Unknown fields are preserved as byte arrays, not guessed names.
//! This is not a complete or byte-identical program reconstruction.
use anchor_lang::prelude::*;
mod checked_program;
use checked_program::{CheckedSystemProgram, CheckedSystemProgramBumps, __client_accounts_checked_system_program, __cpi_client_accounts_checked_system_program};
use anchor_spl::{associated_token::AssociatedToken, token_interface::{Mint, TokenAccount, TokenInterface}};

pub mod state;
pub mod instructions;
pub use instructions::burn::*;
pub use instructions::pump_interface::*;
pub use instructions::pump_interface_v2::*;
pub use instructions::pump_amm_interface::*;

declare_id!("MAyhSmzXzV1pTf7LsNkrNwkWKTo4ougAJ1PPg47MD4e");

#[program]
pub mod mayhem_recovered {
    use super::*;
    pub fn buy_pump_swap(ctx: Context<BuyPumpSwap>, reference: u128, tolerance_bps: u16, retained_reserve_bps: u16) -> Result<()> { instructions::pump_amm_interface::buy_pump_swap(ctx, reference, tolerance_bps, retained_reserve_bps) }
    pub fn sell_pump_swap(ctx: Context<SellPumpSwap>, reference: u128, tolerance_bps: u16, retained_reserve_bps: u16) -> Result<()> { instructions::pump_amm_interface::sell_pump_swap(ctx, reference, tolerance_bps, retained_reserve_bps) }
    pub fn buy_v2(ctx: Context<BuyV2>, reference: u128, tolerance_bps: u16, retained_reserve_bps: u16) -> Result<()> { instructions::pump_interface_v2::buy_v2(ctx, reference, tolerance_bps, retained_reserve_bps) }
    pub fn sell_v2(ctx: Context<SellV2>, reference: u128, tolerance_bps: u16, retained_reserve_bps: u16) -> Result<()> { instructions::pump_interface_v2::sell_v2(ctx, reference, tolerance_bps, retained_reserve_bps) }
    pub fn buy(ctx: Context<LegacyBuy>, reference: u128, tolerance_bps: u16, retained_reserve_bps: u16) -> Result<()> { instructions::pump_interface::buy(ctx, reference, tolerance_bps, retained_reserve_bps) }
    pub fn sell(ctx: Context<LegacySell>, reference: u128, tolerance_bps: u16, retained_reserve_bps: u16) -> Result<()> {
        instructions::pump_interface::sell(ctx, reference, tolerance_bps, retained_reserve_bps)
    }
    pub fn burn_tokens(ctx: Context<BurnTokens>) -> Result<()> {
        instructions::burn::handler(ctx)
    }
    pub fn sweep_fees<'info>(ctx: Context<'info, SweepFees<'info>>) -> Result<()> { crate::instructions::fee_recipients::sweep_fees(ctx) }
    pub fn sweep_fees_admin<'info>(ctx: Context<'info, SweepFeesAdmin<'info>>) -> Result<()> { crate::instructions::fee_recipients::sweep_fees_admin(ctx) }
    pub fn withdraw_quote_admin(ctx: Context<WithdrawQuoteAdmin>, amount: u64) -> Result<()> { crate::instructions::fee_recipients::withdraw_quote_admin(ctx, amount) }
    pub fn withdraw_admin(ctx: Context<WithdrawAdmin>, amount: u64) -> Result<()> { crate::instructions::fee_recipients::withdraw_admin(ctx, amount) }
    pub fn extend_account(ctx: Context<ExtendAccount>) -> Result<()> { crate::instructions::extend_account::extend_account(ctx) }
    pub fn initialize_fee_recipient(ctx: Context<InitializeFeeRecipient>, index: u8) -> Result<()> { crate::instructions::fee_recipients::initialize_fee_recipient(ctx, index) }
    pub fn initialize_global_params(ctx: Context<InitializeGlobalParams>) -> Result<()> { crate::instructions::admin::initialize_global_params(ctx) }
    pub fn update_global_params(ctx: Context<Admin>, args: UpdateGlobalParamsArgs) -> Result<()> { crate::instructions::admin::update_global_params(ctx, args) }
    pub fn update_admin(ctx: Context<Admin>, new_admin: Pubkey) -> Result<()> { crate::instructions::admin::update_admin(ctx, new_admin) }
    pub fn update_trader(ctx: Context<Admin>, new_trader: Pubkey) -> Result<()> { crate::instructions::admin::update_trader(ctx, new_trader) }
    pub fn update_max_sol_per_sweep(ctx: Context<Admin>, value: u64) -> Result<()> { crate::instructions::admin::update_max_sol_per_sweep(ctx, value) }
    pub fn update_max_stable_per_sweep(ctx: Context<Admin>, value: u64) -> Result<()> { crate::instructions::admin::update_max_stable_per_sweep(ctx, value) }
    pub fn reset_sol_deployed(ctx: Context<Admin>) -> Result<()> { crate::instructions::admin::reset_sol_deployed(ctx) }
    pub fn reset_stable_deployed(ctx: Context<Admin>) -> Result<()> { crate::instructions::admin::reset_stable_deployed(ctx) }
    pub fn reset_state(ctx: Context<Admin>) -> Result<()> { crate::instructions::admin::reset_state(ctx) }
    pub fn stop_trading(ctx: Context<Admin>) -> Result<()> { crate::instructions::admin::stop_trading(ctx) }
    pub fn resume_trading(ctx: Context<Admin>) -> Result<()> { crate::instructions::admin::resume_trading(ctx) }
}

#[derive(Accounts)]
pub struct Admin<'info> {
    #[account(mut)]
    pub admin: Signer<'info>,
    #[account(mut, seeds = [b"global-params"], bump, has_one = admin)]
    pub global_params: Account<'info, GlobalParams>,
    pub system_program: CheckedSystemProgram<'info>,
    /// CHECK: Preserve the captured runtime PDA derivation and ConstraintSeeds error.
    #[account(seeds = [b"__event_authority"], bump)]
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Captured parser consumes this account without an address constraint.
    pub program: UncheckedAccount<'info>,
}

/// Exact observed Borsh positions; opaque bytes remain named by behavior.
/// This is not an assertion of historical field names or Rust memory layout.
#[account]
pub struct GlobalParams {
    pub reset_prefix: [u8; 40], // serialized offset 8
    pub paused: bool, // 48
    pub admin: Pubkey, // 49
    pub trader: Pubkey, // 81
    pub sol_deployed: i128, // 113
    pub preserved_middle_a: [u8; 8], // 129
    pub reset_middle: [u8; 25], // 137
    pub version: u32, // 162, incremented by update_global_params
    pub field_10: u64, // 166
    pub max_sol_per_sweep: u64, // 174
    pub reset_stable_prefix: [u8; 24], // 182
    pub stable_deployed: i128, // 206
    pub reset_stable_suffix: [u8; 24], // 222
    pub max_stable_per_sweep: u64, // 246
}

#[error_code]
pub enum MayhemError {
    #[msg("Trading is paused")]
    TradingPaused,
    #[msg("Trading is active")]
    TradingActive,
    #[msg("Math overflow")]
    MathOverflow,
    #[msg("Withdraw Rate limit")]
    WithdrawRateLimit = 14,
    #[msg("Account type not supported")]
    AccountTypeNotSupported = 16,
    #[msg("Only 8 fee recipients supported")]
    MaxFeeRecipientsExceeded = 17,
}

/// Recovered serialized widths/order. Semantic names remain unresolved.
#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct UpdateGlobalParamsArgs {
    pub field_0: Option<u32>,
    pub field_1: Option<u32>,
    pub field_2: Option<u64>,
    pub field_3: Option<u64>,
    pub field_4: Option<u64>,
    pub field_5: Option<u64>,
    pub field_6: Option<u8>,
    pub field_7: Option<u64>,
    pub field_8: Option<u64>,
    pub field_9: Option<u64>,
    pub field_10: Option<u64>,
    pub field_11: Option<u64>,
    pub field_12: Option<u64>,
    pub field_13: Option<u64>,
    pub field_14: Option<u64>,
    pub field_15: Option<u64>,
}

// The discriminator is observed from original emitted data. Historical event
// type name remains unresolved; overriding it avoids pretending to know it.
#[event(discriminator = [0x63,0xa7,0x5c,0x98,0x98,0xe3,0x26,0x29])]
pub struct GlobalParamsUpdateEvent {
    pub old_version: u32,
    pub new_version: u32,
    pub field_0: u32,
    pub field_1: u32,
    pub field_2: u64,
    pub field_3: u64,
    pub field_4: u64,
    pub field_5: u64,
    pub field_6: u8,
    pub field_7: u64,
    pub field_8: u64,
    pub field_9: u64,
    pub field_10: u64,
    pub field_11: u64,
    pub field_12: u64,
    pub field_13: u64,
    pub field_14: u64,
    pub field_15: u64,
}

#[derive(Accounts)]
pub struct InitializeGlobalParams<'info> {
    #[account(mut)]
    pub admin: Signer<'info>,
    #[account(init, payer = admin, space = 254, seeds = [b"global-params"], bump)]
    pub global_params: Account<'info, GlobalParams>,
    pub system_program: CheckedSystemProgram<'info>,
}

#[account]
pub struct FeeRecipient {
    pub bump: u8,
    pub index: u8,
    pub opaque: [u8; 32],
}

#[derive(Accounts)]
#[instruction(index: u8)]
pub struct InitializeFeeRecipient<'info> {
    #[account(mut)]
    pub admin: Signer<'info>,
    #[account(address = anchor_spl::token::spl_token::native_mint::ID)]
    pub wsol_mint: InterfaceAccount<'info, Mint>,
    #[account(init, payer = admin, space = 42, seeds = [b"fee-recipient".as_ref(), &[index]], bump)]
    pub fee_recipient: Account<'info, FeeRecipient>,
    #[account(init, payer = admin, associated_token::mint = wsol_mint, associated_token::authority = fee_recipient, associated_token::token_program = token_program)]
    pub fee_recipient_ata: InterfaceAccount<'info, TokenAccount>,
    #[account(mut, seeds = [b"global-params"], bump)]
    pub global_params: Account<'info, GlobalParams>,
    pub system_program: CheckedSystemProgram<'info>,
    #[account(address = anchor_spl::token::ID)]
    pub token_program: Interface<'info, TokenInterface>,
    pub associated_token_program: Program<'info, AssociatedToken>,
}

#[derive(Accounts)]
pub struct ExtendAccount<'info> {
    /// CHECK: Owner/mut checked here; recognized discriminator checked in handler.
    #[account(mut, owner = ID)]
    pub account: UncheckedAccount<'info>,
    pub user: Signer<'info>,
    pub system_program: CheckedSystemProgram<'info>,
    /// CHECK: Preserve the captured runtime PDA derivation and ConstraintSeeds error.
    #[account(seeds = [b"__event_authority"], bump)]
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Captured parser consumes this account without an address constraint.
    pub program: UncheckedAccount<'info>,
}

#[event(discriminator = [0x61,0x61,0xd7,0x90,0x5d,0x92,0x16,0x7c])]
pub struct ExtendAccountEvent {
    pub account: Pubkey,
    pub user: Pubkey,
    pub old_size: u64,
    pub new_size: u64,
    pub timestamp: i64,
}

#[derive(Accounts)]
pub struct WithdrawAdmin<'info> {
    #[account(mut)]
    pub admin: Signer<'info>,
    #[account(mut, seeds = [b"global-params"], bump, has_one = admin)]
    pub global_params: Account<'info, GlobalParams>,
    /// CHECK: PDA/writability enforced here; System CPI enforces spending owner.
    #[account(mut, seeds = [b"sol-vault"], bump)]
    pub sol_vault: UncheckedAccount<'info>,
    pub system_program: CheckedSystemProgram<'info>,
}

#[derive(Accounts)]
pub struct WithdrawQuoteAdmin<'info> {
    #[account(mut)] pub admin: Signer<'info>,
    #[account(mut, seeds = [b"global-params"], bump, has_one = admin)]
    pub global_params: Account<'info, GlobalParams>,
    /// CHECK: PDA authorizes its token accounts.
    #[account(mut, seeds = [b"sol-vault"], bump)] pub sol_vault: UncheckedAccount<'info>,
    pub quote_mint: InterfaceAccount<'info, Mint>,
    #[account(mut, associated_token::mint = quote_mint, associated_token::authority = sol_vault, associated_token::token_program = token_program)]
    pub vault_quote_ata: InterfaceAccount<'info, TokenAccount>,
    #[account(init_if_needed, payer = admin, associated_token::mint = quote_mint, associated_token::authority = admin, associated_token::token_program = token_program)]
    pub admin_quote_ata: InterfaceAccount<'info, TokenAccount>,
    pub token_program: Interface<'info, TokenInterface>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub system_program: CheckedSystemProgram<'info>,
}

#[event(discriminator = [218,130,134,253,101,109,149,152])]
pub struct SweepEvent { pub amount: u64, pub timestamp: i64 }
pub(crate) fn sweep_remaining<'info>(remaining: &'info [AccountInfo<'info>], destination: &AccountInfo<'info>, destination_ata: &AccountInfo<'info>, token: &AccountInfo<'info>, mint: Pubkey, limit: u64, admin: bool) -> Result<u64> {
    require_eq!(remaining.len(),16,MayhemError::AccountTypeNotSupported);
    let rent = Rent::get()?;
    let mut total = 0u64;
    for pair in remaining.chunks_exact(2) {
        let mut recipient=Account::<FeeRecipient>::try_from(&pair[0])?;
        let ata=InterfaceAccount::<TokenAccount>::try_from(&pair[1])?;
        let before_total=total;
        let available = limit - total;
        let token_amount = ata.amount.min(available);
        if token_amount > 0 {
            let index=[recipient.index];let bump=[recipient.bump];let seeds: &[&[u8]]=&[b"fee-recipient", &index, &bump];
            anchor_spl::token::transfer(CpiContext::new_with_signer(*token.key, anchor_spl::token::Transfer { from: ata.to_account_info(), to: destination_ata.clone(), authority: recipient.to_account_info() }, &[seeds]),token_amount)?;
            total += token_amount;
        }
        if mint == anchor_spl::token::spl_token::native_mint::ID {
            let account = recipient.to_account_info();
            let amount = (account.lamports() - rent.minimum_balance(account.data_len())).min(limit-total);
            **account.try_borrow_mut_lamports()? -= amount;
            **destination.try_borrow_mut_lamports()? += amount;
            total += amount;
        }
        let (counter, timestamp) = if mint == anchor_spl::token::spl_token::native_mint::ID { (8, 0) } else { (16, 24) };
        let previous=u64::from_le_bytes(recipient.opaque[counter..counter+8].try_into().unwrap());
        recipient.opaque[counter..counter+8].copy_from_slice(&(previous + total-before_total).to_le_bytes());
        if !admin { recipient.opaque[timestamp..timestamp+8].copy_from_slice(&Clock::get()?.unix_timestamp.to_le_bytes()); }
        recipient.exit(&ID)?;
    }
    Ok(total)
}

#[derive(Accounts)]
pub struct SweepFees<'info> {
    #[account(mut)] pub trader: Signer<'info>,
    #[account(mut, seeds=[b"global-params"], bump, has_one=trader)] pub global_params: Account<'info, GlobalParams>,
    pub quote_mint: InterfaceAccount<'info, Mint>,
    #[account(mut, associated_token::mint=quote_mint, associated_token::authority=trader, associated_token::token_program=token_program)] pub trader_quote_ata: InterfaceAccount<'info, TokenAccount>,
    pub system_program: CheckedSystemProgram<'info>,
    #[account(address=anchor_spl::token::ID)] pub token_program: Interface<'info,TokenInterface>,
    pub associated_token_program: Program<'info,AssociatedToken>,
    /// CHECK: Preserve the captured runtime PDA derivation and ConstraintSeeds error.
    #[account(seeds = [b"__event_authority"], bump)]
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Captured parser consumes this account without an address constraint.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct SweepFeesAdmin<'info> {
    #[account(mut)] pub admin: Signer<'info>,
    #[account(mut, seeds=[b"global-params"], bump, has_one=admin)] pub global_params: Account<'info, GlobalParams>,
    pub quote_mint: InterfaceAccount<'info, Mint>,
    #[account(mut, associated_token::mint=quote_mint, associated_token::authority=admin, associated_token::token_program=token_program)] pub admin_quote_ata: InterfaceAccount<'info, TokenAccount>,
    pub system_program: CheckedSystemProgram<'info>,
    #[account(address=anchor_spl::token::ID)] pub token_program: Interface<'info,TokenInterface>,
    pub associated_token_program: Program<'info,AssociatedToken>,
    /// CHECK: Preserve the captured runtime PDA derivation and ConstraintSeeds error.
    #[account(seeds = [b"__event_authority"], bump)]
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Captured parser consumes this account without an address constraint.
    pub program: UncheckedAccount<'info>,
}
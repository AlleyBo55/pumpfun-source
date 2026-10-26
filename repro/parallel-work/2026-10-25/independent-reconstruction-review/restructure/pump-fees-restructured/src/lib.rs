//! Partial reconstruction: all thirty-one instruction bodies implemented with bounded validation.
//! It is not the deployed program source.
use anchor_lang::prelude::*;

mod contexts;
mod social;
mod sharing;
mod sharing_update;
use sharing_update::*;
use instructions::fee_sharing::admin_cto_sharing_config::*;
use instructions::buyback::*;
use sharing::*;
use instructions::withdraw::*;
use social::*;
use instructions::fee_sharing::create_donation_fee_pda::*;
mod pump_global;
mod types;
mod state;
mod instructions;

use contexts::*;
use types::*;
use instructions::common::*;

declare_id!("pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ");

declare_program!(pump);
declare_program!(pump_amm);

#[program]
pub mod pump_fees_candidate {
    use super::*;

    #[allow(unused_variables)]
    pub fn admin_cto_sharing_config(ctx: Context<AdminCtoSharingConfig>, new_admin: Option<Pubkey>) -> Result<()> {
        instructions::fee_sharing::admin_cto_sharing_config::admin_cto_sharing_config(ctx, new_admin)
    }

    #[allow(unused_variables)]
    pub fn claim_social_fee_pda(ctx: Context<ClaimSocialFeePda>, user_id: String, platform: u8) -> Result<Option<SocialFeePdaClaimed>> {
        instructions::fee_sharing::claim_social_fee_pda::claim(ctx, user_id, platform)
    }

    #[allow(unused_variables)]
    pub fn claim_social_fee_pda_v2(ctx: Context<ClaimSocialFeePdaV2>, user_id: String, platform: u8) -> Result<Option<SocialFeePdaClaimed>> {
        instructions::fee_sharing::claim_social_fee_pda::claim_v2(ctx, user_id, platform)
    }

    #[allow(unused_variables)]
    pub fn crank_donation_fee_pda(ctx: Context<CrankDonationFeePda>) -> Result<()> {
        instructions::fee_sharing::create_donation_fee_pda::crank(ctx)
    }

    #[allow(unused_variables)]
    pub fn create_donation_fee_pda(ctx: Context<CreateDonationFeePda>) -> Result<()> {
        instructions::fee_sharing::create_donation_fee_pda::create(ctx)
    }

    #[allow(unused_variables)]
    pub fn create_fee_sharing_config(ctx: Context<CreateFeeSharingConfig>) -> Result<()> {
        sharing::create_sharing(ctx)
    }

    #[allow(unused_variables)]
    pub fn create_social_fee_pda(ctx: Context<CreateSocialFeePda>, user_id: String, platform: u8) -> Result<()> {
        instructions::fee_sharing::create_social_fee_pda::create_social(ctx, user_id, platform)
    }

    #[allow(unused_variables)]
    pub fn extend_fee_config(ctx: Context<ExtendFeeConfig>) -> Result<()> {
        let info = ctx.accounts.fee_config.to_account_info();
        let data = info.try_borrow_data()?;
        require!(info.owner == &ID && data.len() >= 9 && data[..8] == [143,52,146,187,219,123,76,155], FeeError::InvalidFeeConfigAccount);
        let bump = [data[8]];
        let config_program = ctx.accounts.config_program_id.key();
        let expected = Pubkey::create_program_address(&[b"fee_config", config_program.as_ref(), &bump], &ID)
            .map_err(|_| error!(FeeError::InvalidFeeConfigAccount))?;
        require_keys_eq!(expected, info.key(), FeeError::InvalidFeeConfigAccount);
        let current_size = data.len();
        drop(data);
        if current_size >= 4097 { return Ok(()); }
        let rent = Rent::get()?;
        let amount = rent.minimum_balance(4097) - rent.minimum_balance(current_size);
        anchor_lang::system_program::transfer(CpiContext::new(
            ctx.accounts.system_program.to_account_info(), anchor_lang::system_program::Transfer {
                from: ctx.accounts.user.to_account_info(), to: info.clone(),
            }), amount)?;
        info.realloc(4097, true)?;
        let event = ExtendFeeConfigEvent { fee_config: info.key(), user: ctx.accounts.user.key(),
            current_size: current_size as u64, new_size: 4097, timestamp: Clock::get()?.unix_timestamp };
        emit!(event); emit_cpi!(event); Ok(())
    }

    #[allow(unused_variables)]
    pub fn get_fees(ctx: Context<GetFees>, is_pump_pool: bool, market_cap_lamports: u128, trade_size_lamports: u64, is_new_quote_mint: OptionBool) -> Result<Fees> {
        let config = &ctx.accounts.fee_config;
        if !is_pump_pool { return Ok(config.flat_fees.clone()); }
        Ok(select_fee_tier(if is_new_quote_mint.0 { &config.stable_fee_tiers } else { &config.fee_tiers }, market_cap_lamports))
    }

    #[allow(unused_variables)]
    pub fn get_fees_with_quote_mint(ctx: Context<GetFeesWithQuoteMint>, is_pump_pool: bool, market_cap_lamports: u128, quote_mint: Pubkey) -> Result<Fees> {
        let config = &ctx.accounts.fee_config;
        if !is_pump_pool { return Ok(config.flat_fees.clone()); }
        let quote = quote_mint.to_bytes();
        if quote == [0; 32] || quote == WRAPPED_SOL || quote == OTHER_NORMAL_QUOTE {
            Ok(select_fee_tier(&config.fee_tiers, market_cap_lamports))
        } else if quote == USDC {
            Ok(select_fee_tier(&config.stable_fee_tiers, market_cap_lamports))
        } else if config.exotic_flat_fees.lp_fee_bps == 0 && config.exotic_flat_fees.protocol_fee_bps == 0 && config.exotic_flat_fees.creator_fee_bps == 0 {
            Ok(config.flat_fees.clone())
        } else { Ok(config.exotic_flat_fees.clone()) }
    }

    #[allow(unused_variables)]
    pub fn initialize_buyback(ctx: Context<InitializeBuyback>, index: u8) -> Result<()> {
        instructions::buyback::initialize_buyback(ctx,index)
    }

    #[allow(unused_variables)]
    pub fn initialize_fee_config(ctx: Context<InitializeFeeConfig>) -> Result<()> { crate::instructions::admin::initialize_fee_config::initialize_fee_config(ctx) }

    #[allow(unused_variables)]
    pub fn initialize_fee_program_global(ctx: Context<InitializeFeeProgramGlobal>, social_claim_authority: Pubkey, disable_flags: u8, claim_rate_limit: u64) -> Result<()> { crate::instructions::admin::initialize_fee_program_global::initialize_fee_program_global(ctx, social_claim_authority, disable_flags, claim_rate_limit) }

    #[allow(unused_variables)]
    pub fn revoke_fee_sharing_authority(_ctx: Context<RevokeFeeSharingAuthority>) -> Result<()> {
        Err(error!(FeeError::DeprecatedInstruction))
    }

    #[allow(unused_variables)]
    pub fn set_authority(ctx: Context<SetAuthority>, new_authority: Pubkey) -> Result<()> { crate::instructions::admin::update_fee_program_global::set_authority(ctx, new_authority) }

    #[allow(unused_variables)]
    pub fn set_claim_rate_limit(ctx: Context<SetClaimRateLimit>, claim_rate_limit: u64) -> Result<()> { crate::instructions::admin::update_fee_program_global::set_claim_rate_limit(ctx, claim_rate_limit) }

    #[allow(unused_variables)]
    pub fn set_disable_flags(ctx: Context<SetDisableFlags>, disable_flags: u8) -> Result<()> { crate::instructions::admin::update_fee_program_global::set_disable_flags(ctx, disable_flags) }

    #[allow(unused_variables)]
    pub fn set_exotic_flat_fees(ctx: Context<SetExoticFlatFees>, exotic_flat_fees: Fees) -> Result<()> { crate::instructions::admin::update_fee_program_global::set_exotic_flat_fees(ctx, exotic_flat_fees) }

    #[allow(unused_variables)]
    pub fn set_social_claim_authority(ctx: Context<SetSocialClaimAuthority>, social_claim_authority: Pubkey) -> Result<()> { crate::instructions::admin::update_fee_program_global::set_social_claim_authority(ctx, social_claim_authority) }

    #[allow(unused_variables)]
    pub fn sweep_buyback(ctx: Context<SweepBuyback>, index: u8) -> Result<()> {
        instructions::buyback::sweep_buyback(ctx,index)
    }

    #[allow(unused_variables)]
    pub fn transfer_fee_sharing_authority(_ctx: Context<TransferFeeSharingAuthority>) -> Result<()> {
        Err(error!(FeeError::DeprecatedInstruction))
    }

    #[allow(unused_variables)]
    pub fn update_admin(ctx: Context<UpdateAdmin>) -> Result<()> { crate::instructions::admin::update_fee_program_global::update_admin(ctx) }

    #[allow(unused_variables)]
    pub fn update_buyback_authority(ctx: Context<UpdateBuyback>, index: u8, new_authority: Pubkey) -> Result<()> {
        instructions::buyback::update_buyback_authority(ctx,index,new_authority)
    }

    #[allow(unused_variables)]
    pub fn update_buyback_claim_rate_limit(ctx: Context<UpdateBuyback>, index: u8, claim_rate_limit: i64) -> Result<()> {
        instructions::buyback::update_buyback_claim_rate_limit(ctx,index,claim_rate_limit)
    }

    #[allow(unused_variables)]
    pub fn update_fee_config(ctx: Context<UpdateFeeConfig>, fee_tiers: Vec<FeeTier>, flat_fees: Fees) -> Result<()> { crate::instructions::admin::update_fee_config::update_fee_config(ctx, fee_tiers, flat_fees) }

    #[allow(unused_variables)]
    pub fn update_fee_shares<'info>(ctx: Context<'_, '_, '_, 'info, UpdateFeeShares<'info>>, shareholders: Vec<Shareholder>) -> Result<()> {
        instructions::fee_sharing::update_fee_shares::update_fee_shares(ctx, shareholders)
    }

    #[allow(unused_variables)]
    pub fn update_fee_shares_v2<'info>(ctx: Context<'_, '_, '_, 'info, UpdateFeeSharesV2<'info>>, shareholders: Vec<Shareholder>) -> Result<()> {
        instructions::fee_sharing::update_fee_shares_v2::update_fee_shares_v2(ctx, shareholders)
    }

    #[allow(unused_variables)]
    pub fn update_stable_fee_config(ctx: Context<UpdateStableFeeConfig>, fee_tiers: Vec<FeeTier>) -> Result<()> { crate::instructions::admin::update_fee_config::update_stable_fee_config(ctx, fee_tiers) }

    #[allow(unused_variables)]
    pub fn upsert_fee_tiers(ctx: Context<UpsertFeeTiers>, fee_tiers: Vec<FeeTier>, offset: u8) -> Result<()> { crate::instructions::admin::upsert_fee_tiers::upsert_fee_tiers(ctx, fee_tiers, offset) }

    #[allow(unused_variables)]
    pub fn upsert_stable_fee_tiers(ctx: Context<UpsertStableFeeTiers>, fee_tiers: Vec<FeeTier>, offset: u8) -> Result<()> { crate::instructions::admin::upsert_fee_tiers::upsert_stable_fee_tiers(ctx, fee_tiers, offset) }

    #[allow(unused_variables)]
    pub fn withdraw(ctx: Context<Withdraw>) -> Result<()> {
        instructions::withdraw::execute(ctx)
    }

}

#[error_code]
pub enum CandidateError {
    #[msg("Research candidate handler not reconstructed")]
    Unsupported,
}

pub const WRAPPED_SOL: [u8; 32] = [6,155,136,87,254,171,129,132,251,104,127,99,70,24,192,53,218,196,57,220,26,235,59,85,152,160,240,0,0,0,0,1];
pub const OTHER_NORMAL_QUOTE: [u8; 32] = [131,13,252,159,222,95,230,184,170,124,4,164,118,233,30,138,198,187,38,74,173,144,250,25,201,223,73,216,92,62,91,94];
pub const USDC: [u8; 32] = [198,250,122,243,190,219,173,58,61,101,243,106,171,201,116,49,177,187,228,194,210,246,224,228,124,166,2,3,69,47,93,97];

#[error_code]
pub enum FeeError {
    #[msg("Only Pump and PumpSwap programs can call this instruction")]
    UnauthorizedProgram = 0,
    #[msg("Invalid admin")]
    InvalidAdmin = 1,
    #[msg("No fee tiers provided")]
    NoFeeTiers = 2,
    #[msg("format")]
    TooManyFeeTiers = 3,
    #[msg("The offset should be <= fee_config.fee_tiers.len()")]
    OffsetNotContinuous = 4,
    #[msg("Fee tiers must be sorted by market cap threshold (ascending)")]
    FeeTiersNotSorted = 5,
    #[msg("Fee total must not exceed 10_000bps")]
    InvalidFeeTotal = 6,
    #[msg("Invalid Sharing Config")]
    InvalidSharingConfig = 7,
    #[msg("Invalid Pool")]
    InvalidPool = 8,
    #[msg("Sharing config authority has been revoked - sharing config can only be updated once")]
    SharingConfigAdminRevoked = 9,
    #[msg("No shareholders provided")]
    NoShareholders = 10,
    #[msg("format")]
    TooManyShareholders = 11,
    #[msg("Duplicate shareholder address")]
    DuplicateShareholder = 12,
    #[msg("Not enough remaining accounts")]
    NotEnoughRemainingAccounts = 13,
    #[msg("Invalid share total - must equal 10_000 basis points")]
    InvalidShareTotal = 14,
    #[msg("Share calculation overflow")]
    ShareCalculationOverflow = 15,
    #[msg("The given account is not authorized to execute this instruction.")]
    NotAuthorized = 16,
    #[msg("Shareholder cannot have zero share")]
    ZeroShareNotAllowed = 17,
    #[msg("Fee sharing config is not active")]
    SharingConfigNotActive = 18,
    #[msg("AMM accounts are required for graduated coins")]
    AmmAccountsRequiredForGraduatedCoin = 19,
    #[msg("Remaining account key doesn't match shareholder address")]
    ShareholderAccountMismatch = 20,
    #[msg("Feature is currently deactivated")]
    FeatureDeactivated = 21,
    #[msg("User ID exceeds maximum length")]
    UserIdTooLong = 22,
    #[msg("Instruction is deprecated")]
    DeprecatedInstruction = 23,
    #[msg("Reward split can only be updated once")]
    FeeSharesAlreadyUpdated = 24,
    #[msg("Math overflow")]
    MathOverflow = 25,
    #[msg("Invalid buybackindex")]
    InvalidBuybackIndex = 26,
    #[msg("Claim rate limit exceeded")]
    ClaimRateLimitExceeded = 27,
    #[msg("Account is not a valid FeeConfig for this instruction")]
    InvalidFeeConfigAccount = 28,
    #[msg("Account type not supported")]
    AccountTypeNotSupported = 29,
    #[msg("Mint does not match quote mint")]
    InvalidMint = 30,
    #[msg("Unsupported quote mint")]
    UnsupportedQuoteMint = 31,
    #[msg("Invalid remaining accounts")]
    InvalidRemainingAccounts = 32,
    #[msg("Pool creator_fees must be swept before the shares change")]
    PoolCreatorFeesNotSwept = 33,
    #[msg("quote_mint is not the bonding curve's quote mint")]
    InvalidQuoteMint = 34,
    #[msg("Token withdrawals need quote_mint, vault_ata, user_ata and token_program")]
    IncompleteTokenAccounts = 35,
    #[msg("Nothing to withdraw")]
    NothingToWithdraw = 36,
}


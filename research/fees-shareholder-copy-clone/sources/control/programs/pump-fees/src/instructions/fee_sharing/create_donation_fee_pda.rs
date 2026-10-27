use anchor_lang::prelude::*;
use anchor_spl::token_interface::Mint;
use crate::types::FeeProgramGlobal;
use crate::state::DonationFeePda;
use crate::donation::{BondingCurve, PUMP};















#[derive(Accounts)]
pub struct CreateDonationFeePda<'info> {
    /// CHECK: event PDA validated.
    #[account(seeds=[b"__event_authority"],bump)] pub event_authority: AccountInfo<'info>,
    pub program: Program<'info, crate::program::PumpFeesCandidate>,
    #[account(mut)] pub payer: Signer<'info>,
    pub system_program: Program<'info,System>,
    #[account(seeds=[b"fee-program-global"],bump=fee_program_global.bump)] pub fee_program_global: Account<'info,FeeProgramGlobal>,
    #[account(init_if_needed,payer=payer,space=218,seeds=[b"donation-fee-pda",base_mint.key().as_ref(),config_id.key().as_ref()],bump)] pub donation_fee_pda: Account<'info,DonationFeePda>,
    /// CHECK: identifier only.
    pub config_id: UncheckedAccount<'info>,
    pub base_mint: InterfaceAccount<'info,Mint>,
    #[account(seeds=[b"bonding-curve",base_mint.key().as_ref()],bump,seeds::program=PUMP)] pub bonding_curve: Account<'info,BondingCurve>,
    /// CHECK: validated in handler.
    pub pool: UncheckedAccount<'info>,
    /// CHECK: derived identifier; state rules under recovery.
    #[account(seeds=[b"sharing-config",base_mint.key().as_ref()],bump)] pub sharing_config: UncheckedAccount<'info>,
}

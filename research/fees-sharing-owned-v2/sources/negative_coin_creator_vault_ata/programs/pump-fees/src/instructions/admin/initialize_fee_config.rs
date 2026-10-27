use anchor_lang::prelude::*;
use crate::types::{FeeConfig, FeeProgramGlobal};
use crate::FeeError;

#[event_cpi]
#[derive(Accounts)]
pub struct InitializeFeeConfig<'info> {
    #[account(mut, address = anchor_lang::solana_program::pubkey!("8LWu7QM2dGR1G8nKDHthckea57bkCzXyBTAKPJUBDHo8") @ FeeError::InvalidAdmin)]
    pub admin: Signer<'info>,
    #[account(init, payer = admin, space = 2512,
              seeds = [b"fee_config", config_program_id.key().as_ref()], bump)]
    pub fee_config: Account<'info, FeeConfig>,
    pub system_program: Program<'info, System>,
    /// CHECK: Key is the FeeConfig PDA namespace.
    pub config_program_id: UncheckedAccount<'info>,
}

use anchor_lang::prelude::*;
use crate::donation::ConfigStatus;
use crate::types::Shareholder;
use crate::{FeeError, pump_global};
use crate::sharing::{Pump, Amm, SharingPool};
use crate::donation::{BondingCurve, PUMP, AMM};






























#[account]
pub struct SharingConfig {pub bump:u8,pub version:u8,pub status:ConfigStatus,pub mint:Pubkey,pub admin:Pubkey,pub admin_revoked:bool,pub shareholders:Vec<Shareholder>}















#[derive(Accounts)]
pub struct CreateFeeSharingConfig<'info>{
 /// CHECK: event PDA.
 #[account(seeds=[b"__event_authority"],bump)]pub event_authority:UncheckedAccount<'info>,
 pub program:Program<'info,crate::program::PumpFeesCandidate>,
 #[account(mut)]pub payer:Signer<'info>,
 #[account(seeds=[b"global"],bump,seeds::program=PUMP)]pub global:Box<Account<'info,pump_global::Global>>,
 pub mint:InterfaceAccount<'info,anchor_spl::token_interface::Mint>,
 #[account(init_if_needed,payer=payer,space=1024,seeds=[b"sharing-config",mint.key().as_ref()],bump)]pub sharing_config:Account<'info,SharingConfig>,
 pub system_program:Program<'info,System>,
 #[account(mut,seeds=[b"bonding-curve",mint.key().as_ref()],bump,seeds::program=PUMP)]pub bonding_curve:Account<'info,BondingCurve>,
 pub pump_program:Program<'info,Pump>,
 /// CHECK: external event PDA.
 #[account(seeds=[b"__event_authority"],bump,seeds::program=PUMP)]pub pump_event_authority:UncheckedAccount<'info>,
 /// CHECK: optional pool validated in handler.
 #[account(mut)]pub pool:Option<Account<'info,SharingPool>>,
 pub pump_amm_program:Option<Program<'info,Amm>>,
 /// CHECK: external event PDA.
 #[account(seeds=[b"__event_authority"],bump,seeds::program=AMM)]pub pump_amm_event_authority:Option<AccountInfo<'info>>,
}

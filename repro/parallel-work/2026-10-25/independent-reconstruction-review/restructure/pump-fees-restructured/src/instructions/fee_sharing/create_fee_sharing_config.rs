use anchor_lang::prelude::*;
use crate::instructions::fee_sharing::create_donation_fee_pda::ConfigStatus;
use crate::types::Shareholder;

#[account]
pub struct SharingConfig {pub bump:u8,pub version:u8,pub status:ConfigStatus,pub mint:Pubkey,pub admin:Pubkey,pub admin_revoked:bool,pub shareholders:Vec<Shareholder>}

use anchor_lang::prelude::*;
use crate::types::*;
use crate::FeeError;

pub(crate) fn select_fee_tier(tiers: &[FeeTier], cap: u128) -> Fees {
    if cap < tiers[0].market_cap_lamports_threshold { return tiers[0].fees.clone(); }
    for tier in tiers.iter().rev() {
        if cap >= tier.market_cap_lamports_threshold { return tier.fees.clone(); }
    }
    tiers[0].fees.clone()
}

pub(crate) fn validate_fees(fees: &Fees) -> Result<()> {
    // The original aborts on addition overflow before comparing the total.
    let total = fees.lp_fee_bps.checked_add(fees.protocol_fee_bps).unwrap()
        .checked_add(fees.creator_fee_bps).unwrap();
    require!(total <= 10_000, FeeError::InvalidFeeTotal);
    Ok(())
}
pub(crate) fn validate_tiers(tiers: &[FeeTier]) -> Result<()> {
    require!(!tiers.is_empty(), FeeError::NoFeeTiers);
    require!(tiers.len() <= 50, FeeError::TooManyFeeTiers);
    for tier in tiers { validate_fees(&tier.fees)?; }
    require!(tiers.windows(2).all(|pair| pair[0].market_cap_lamports_threshold < pair[1].market_cap_lamports_threshold), FeeError::FeeTiersNotSorted);
    Ok(())
}

pub(crate) fn upsert_tiers(current: &mut Vec<FeeTier>, incoming: &[FeeTier], offset: u8) -> Result<()> {
    require!(!incoming.is_empty(), FeeError::NoFeeTiers);
    let offset = offset as usize;
    require!(offset <= current.len(), FeeError::OffsetNotContinuous);
    require!(current.len().max(offset + incoming.len()) <= 50, FeeError::TooManyFeeTiers);
    for (index, tier) in incoming.iter().enumerate() {
        if offset + index < current.len() { current[offset + index] = tier.clone(); }
        else { current.push(tier.clone()); }
    }
    validate_tiers(current)
}

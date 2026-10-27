use anchor_lang::prelude::*;















#[inline(never)]
pub fn legacy_curve_quote_is_zero(bonding_curve: &AccountInfo<'_>) -> Result<bool> {
    if bonding_curve.data_len() < 115 { return Ok(true); }

  Ok(Pubkey::new_from_array(bonding_curve.data.borrow()[83..115].try_into().unwrap()) == Pubkey::default())
}

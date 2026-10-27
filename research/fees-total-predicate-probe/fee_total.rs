#![no_std]
#[repr(C)]
pub struct Fees { pub lp_fee_bps: u64, pub protocol_fee_bps: u64, pub creator_fee_bps: u64 }
#[no_mangle]
#[inline(never)]
pub fn fee_total_is_valid(fees: &Fees) -> bool {
    fees.lp_fee_bps + fees.protocol_fee_bps + fees.creator_fee_bps <= 10_000
}

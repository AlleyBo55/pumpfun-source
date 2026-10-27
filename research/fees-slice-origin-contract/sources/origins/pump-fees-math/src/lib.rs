use crate::types::Fees;






















impl Fees {
    #[inline(never)]
    pub fn is_valid(&self) -> bool {

        self.lp_fee_bps + self.protocol_fee_bps + self.creator_fee_bps <= 10_000
    }
}

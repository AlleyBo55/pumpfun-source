use crate::types::{FeeConfig, FeeTier, Fees};
use anchor_lang::{AccountDeserialize, AnchorSerialize, Discriminator, prelude::Pubkey};

fn value() -> FeeConfig {
    FeeConfig { bump: 17, admin: Pubkey::new_from_array([3;32]),
        flat_fees: Fees { lp_fee_bps:0, protocol_fee_bps:0, creator_fee_bps:0 },
        fee_tiers: vec![], stable_fee_tiers: vec![],
        exotic_flat_fees: Fees { lp_fee_bps:0, protocol_fee_bps:0, creator_fee_bps:0 } }
}
fn account(v:&FeeConfig, size:usize, prefix:&[u8;8]) -> Vec<u8> {
    let mut data=prefix.to_vec(); v.serialize(&mut data).unwrap(); data.resize(size,0); data
}
#[test]
fn full_buffer_prefix_is_skipped() {
    let v=value(); let mut cases=0;
    for size in [2512,4072,4073,4096,4097,5000] {
        for prefix in [[0;8], [85;8], <[u8;8]>::try_from(FeeConfig::DISCRIMINATOR).unwrap()] {
            let data=account(&v,size,&prefix); let mut bytes=data.as_slice();
            let decoded=FeeConfig::try_deserialize_unchecked(&mut bytes).unwrap();
            assert_eq!(decoded.bump,17); assert_eq!(decoded.admin,v.admin);
            assert_eq!(decoded.flat_fees.lp_fee_bps,0); assert!(decoded.fee_tiers.is_empty());
            assert_eq!(bytes.len(),size-if size<4073{69}else if size<4097{73}else{97});
            cases+=1;
        }
    }
    println!("PREFIX_CASES={cases}");
}
#[test]
fn checked_and_short_input_contracts() {
    let v=value(); let mut cases=0;
    for size in [0,1,7,8,9,2503,2504,2511] {
        let data=vec![0;size]; let mut bytes=data.as_slice();
        assert!(FeeConfig::try_deserialize_unchecked(&mut bytes).is_err());
        assert_eq!(bytes.len(),if size<8{size}else{size-8}); cases+=1;
    }
    for prefix in [[0;8],[85;8]] {
        let data=account(&v,2512,&prefix);let mut bytes=data.as_slice();
        assert!(FeeConfig::try_deserialize(&mut bytes).is_err()); assert_eq!(bytes.len(),2512);cases+=1;
    }
    let data=account(&v,2512,&<[u8;8]>::try_from(FeeConfig::DISCRIMINATOR).unwrap());
    let mut bytes=data.as_slice();assert_eq!(FeeConfig::try_deserialize(&mut bytes).unwrap().admin,v.admin);cases+=1;
    println!("BOUNDARY_CASES={cases}");
}
#[test]
fn version_boundaries_use_payload_length() {
    let mut v=value();v.fee_tiers=vec![FeeTier {market_cap_lamports_threshold:23,fees:Fees {lp_fee_bps:1,protocol_fee_bps:2,creator_fee_bps:3}}];
    v.stable_fee_tiers=vec![FeeTier {market_cap_lamports_threshold:47,fees:Fees {lp_fee_bps:4,protocol_fee_bps:5,creator_fee_bps:6}}];
    v.exotic_flat_fees=Fees {lp_fee_bps:7,protocol_fee_bps:8,creator_fee_bps:9};
    for size in [2512,4072,4073,4096,4097,5000] {
        let data=account(&v,size,&[0;8]);let mut bytes=data.as_slice();let d=FeeConfig::try_deserialize_unchecked(&mut bytes).unwrap();
        assert_eq!(d.bump,17);assert_eq!(d.fee_tiers.len(),1);assert_eq!(d.fee_tiers[0].market_cap_lamports_threshold,23);
        assert_eq!(d.stable_fee_tiers.len(),if size>=4073{1}else{0});
        assert_eq!(d.exotic_flat_fees.creator_fee_bps,if size>=4097{9}else{0});
    }
    println!("VERSION_CASES=6");
}

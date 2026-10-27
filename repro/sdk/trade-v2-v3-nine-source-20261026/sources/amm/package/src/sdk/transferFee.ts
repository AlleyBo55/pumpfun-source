import BN from "bn.js";
import { AccountInfo, PublicKey } from "@solana/web3.js";
import {
  getEpochFee,
  getTransferFeeConfig,
  TOKEN_2022_PROGRAM_ID,
  TransferFeeConfig,
  unpackMint,
} from "@solana/spl-token";
import { ceilDiv } from "./util";

/**
 * The Token-2022 transfer fee a quote mint charges this epoch. `null` is no fee: a legacy SPL
 * Token mint (WSOL, USDC) or a Token-2022 mint without `TransferFeeConfig`.
 *
 * Token-2022 withholds the fee from the *receiver* of every transfer. The programs gross up what
 * must land in a pool's quote vault (so the pool books exactly its share) and send every payout
 * as it is (so the receiver bears the fee); the schedule's fees stay basis points of the pool
 * amounts. Buy caps bind on the taxed debit, sell / withdraw floors on what lands.
 *
 * rust reference: pump-amm utils/transfer_fee.rs QuoteTransferFee, pump-mint-extensions TransferFee
 */
export interface QuoteTransferFee {
  basisPoints: number;
  maximumFee: BN;
}

const ONE_IN_BASIS_POINTS = new BN(10_000);

/** `quoteMint`'s `TransferFeeConfig`, or `null` when the mint is not Token-2022 or has none. */
export function parseTransferFeeConfig(
  quoteMint: PublicKey,
  quoteMintAccountInfo: AccountInfo<Buffer>,
): TransferFeeConfig | null {
  if (!quoteMintAccountInfo.owner.equals(TOKEN_2022_PROGRAM_ID)) {
    return null;
  }
  return getTransferFeeConfig(
    unpackMint(quoteMint, quoteMintAccountInfo, TOKEN_2022_PROGRAM_ID),
  );
}

/** The schedule entry in force at `epoch` (the newer one once its epoch has arrived). */
export function transferFeeAt(
  config: TransferFeeConfig,
  epoch: number | bigint,
): QuoteTransferFee {
  const fee = getEpochFee(config, BigInt(epoch));
  return {
    basisPoints: fee.transferFeeBasisPoints,
    maximumFee: new BN(fee.maximumFee.toString()),
  };
}

/** What Token-2022 keeps back from the receiver when `amount` is sent (spl `calculate_fee`). */
export function transferFeeOn(
  fee: QuoteTransferFee | null | undefined,
  amount: BN,
): BN {
  if (!fee || fee.basisPoints === 0 || amount.isZero()) {
    return new BN(0);
  }
  return BN.min(
    ceilDiv(amount.muln(fee.basisPoints), ONE_IN_BASIS_POINTS),
    fee.maximumFee,
  );
}

/** What lands when `amount` is sent. */
export function netOfTransferFee(
  fee: QuoteTransferFee | null | undefined,
  amount: BN,
): BN {
  return amount.sub(transferFeeOn(fee, amount));
}

/**
 * The amount to send so that at least `net` lands (spl `calculate_pre_fee_amount`; at most one
 * unit more than needed, which stays in the receiving account).
 */
export function grossForTransferFee(
  fee: QuoteTransferFee | null | undefined,
  net: BN,
): BN {
  if (!fee || fee.basisPoints === 0 || net.isZero()) {
    return net;
  }
  if (fee.basisPoints === 10_000) {
    return net.add(fee.maximumFee);
  }
  const raw = ceilDiv(
    net.mul(ONE_IN_BASIS_POINTS),
    ONE_IN_BASIS_POINTS.subn(fee.basisPoints),
  );
  return raw.sub(net).gte(fee.maximumFee) ? net.add(fee.maximumFee) : raw;
}

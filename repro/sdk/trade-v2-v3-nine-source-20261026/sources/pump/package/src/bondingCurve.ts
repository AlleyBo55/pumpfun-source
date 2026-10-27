import { NATIVE_MINT_2022 } from "@solana/spl-token";
import { PublicKey } from "@solana/web3.js";
import BN from "bn.js";

import {
  CurveDepthExceededError,
  QuoteBondingCurveNotEligibleError,
  QuoteCurveAwaitingMigrationError,
  QuoteReservesOutOfRangeError,
  UnsupportedQuoteMintError,
} from "./errors";
import { computeFeesBps, getFee, ONE_BILLION_SUPPLY } from "./fees";
import { isLegacyQuoteMint } from "./pda";
import { BondingCurve, FeeConfig, Global, QuoteControl } from "./state";
import {
  QuoteTransferFee,
  transferFeeGrossFor,
  transferFeeNetOf,
} from "./transferFee";

/**
 * The `virtualQuoteReserves` a new curve quoted in `quoteMint` starts from,
 * the way `create_v2` seeds it: SOL (WSOL or the zero key) from
 * `Global.initialVirtualSolReserves`, a mint whitelisted on `Global` from
 * `Global.initialVirtualQuoteReserves` (even when quote control lists it too),
 * and a mint admitted through quote control from its entry. The Token-2022
 * native mint always throws `UnsupportedQuoteMintError`: `create_v2` rejects
 * it before consulting either list.
 *
 * @param quoteControl - The decoded `QuoteControl` PDA, or `null` when the
 * account does not exist yet (an empty list). Pass it whenever the mint may
 * be a quote-control mint: a mint in neither list then throws
 * `UnsupportedQuoteMintError`, as `create_v2` would reject it. When omitted,
 * an unlisted mint falls back to `Global.initialVirtualQuoteReserves` — what
 * callers that predate quote control always got — and quote-control mints
 * are seeded wrong.
 * @param pumpQuote - When `quoteMint` is a pump coin listed nowhere: its
 * curve (and pool once migrated), from which `create_v2` derives the seed
 * (`pumpQuoteReserves`).
 */
export function initialVirtualQuoteReservesFor(
  global: Global,
  quoteMint: PublicKey,
  quoteControl?: QuoteControl | null,
  pumpQuote?: PumpQuoteCurve,
): BN {
  if (isLegacyQuoteMint(quoteMint)) {
    return global.initialVirtualSolReserves;
  }
  // Without a caller-supplied list, the one fetched with the pump coin
  // decides whether the coin itself is listed (a listed coin is never priced
  // through the pump-quote path).
  if (quoteControl === undefined && pumpQuote?.quoteControl !== undefined) {
    quoteControl = pumpQuote.quoteControl;
  }

  // Checked before either list, as `create_v2` does: pump-fees treats this
  // key as SOL, but it cannot quote a curve whichever list admits it.
  if (quoteMint.equals(NATIVE_MINT_2022)) {
    throw new UnsupportedQuoteMintError(quoteMint);
  }

  // `quoteMint` is non-zero here, so an empty (zero-key) whitelist slot can
  // never match.
  if (global.whitelistedQuoteMints.some((mint) => mint.equals(quoteMint))) {
    return global.initialVirtualQuoteReserves;
  }

  const entry = quoteControl?.mints.find((candidate) =>
    candidate.mint.equals(quoteMint),
  );
  if (entry) {
    return entry.initialVirtualQuoteReserves;
  }

  if (pumpQuote) {
    if (!pumpQuote.mint.equals(quoteMint)) {
      throw new Error(
        `pumpQuote is for ${pumpQuote.mint.toBase58()}, not the quote mint ${quoteMint.toBase58()}`,
      );
    }
    return pumpQuoteReserves(global, pumpQuote, quoteControl)
      .virtualQuoteReserves;
  }

  if (quoteControl !== undefined) {
    throw new UnsupportedQuoteMintError(quoteMint);
  }

  return global.initialVirtualQuoteReserves;
}

/**
 * `pump_quote::MAX_CURVE_DEPTH`: the deepest coin `create_v2` admits, whatever
 * `Global.maxCurveDepth` is set to.
 */
export const MAX_CURVE_DEPTH = 5;

/** One pump coin on a quote chain, as `create_v2` prices it. */
export interface PumpQuoteChainCoin {
  /** The coin's mint. */
  mint: PublicKey;
  /** The coin's decoded bonding curve. */
  bondingCurve: BondingCurve;
  /**
   * Once the coin's curve has migrated: its canonical pool's base vault
   * balance, quote vault balance and `Pool.virtualQuoteReserves` (may be
   * negative).
   */
  pool?: { baseReserves: BN; quoteReserves: BN; virtualQuoteReserves: BN };
}

/**
 * A pump coin Q offered as a `create_v2` quote mint (listed neither on
 * `Global` nor in quote control): what the program reads to admit it and
 * seed the new curve.
 */
export interface PumpQuoteCurve extends PumpQuoteChainCoin {
  /**
   * The `QuoteControl` PDA as fetched with Q (`null` when it does not exist):
   * a chain whose depth-0 root is quoted in a quote-control mint seeds from
   * its entry. Used when the caller passes no `quoteControl` of its own.
   */
  quoteControl?: QuoteControl | null;
  /**
   * The rest of Q's quote chain: the coin Q is quoted in, the coin that one
   * is quoted in, and so on down to the depth-0 root (`Q.depth` coins,
   * nearest first). Empty or omitted for a depth-0 Q. `create_v2` prices
   * every coin on it at its live reserves.
   */
  chain?: PumpQuoteChainCoin[];
}

/** pump `BondingCurve::is_migrated`: every reserve zeroed by the migration. */
export function isBondingCurveMigrated(bondingCurve: BondingCurve): boolean {
  return (
    bondingCurve.realQuoteReserves.isZero() &&
    bondingCurve.virtualQuoteReserves.isZero() &&
    bondingCurve.realTokenReserves.isZero() &&
    bondingCurve.virtualTokenReserves.isZero()
  );
}

/**
 * The first checks `create_v2` runs on pump coin Q, before reading anything
 * below it: the depth gate (`CurveDepthExceededError`, against
 * `min(global.maxCurveDepth, MAX_CURVE_DEPTH)`), then mayhem
 * (`QuoteBondingCurveNotEligibleError`). Returns the new coin's depth.
 */
export function pumpQuoteGate(
  global: Global,
  quote: Pick<PumpQuoteCurve, "mint" | "bondingCurve">,
): number {
  const depth = quote.bondingCurve.depth + 1;
  const max = Math.min(global.maxCurveDepth, MAX_CURVE_DEPTH);
  if (depth > max) {
    throw new CurveDepthExceededError(depth, max);
  }
  if (quote.bondingCurve.isMayhemMode) {
    throw new QuoteBondingCurveNotEligibleError(quote.mint);
  }
  return depth;
}

// `create_v2`'s walk: Q, then the curve of each coin's `quoteMint`, `Q.depth
// + 1` coins in all, ending on the depth-0 root. Trailing coins are ignored,
// as the program ignores trailing accounts.
function pumpQuoteChain(
  quote: Pick<PumpQuoteCurve, "mint" | "bondingCurve" | "chain">,
): PumpQuoteChainCoin[] {
  const coins: PumpQuoteChainCoin[] = [quote];
  for (let i = 0; i < quote.bondingCurve.depth; i++) {
    const expected = coins[i].bondingCurve.quoteMint;
    const coin = quote.chain?.[i];
    if (!coin) {
      throw new Error(
        `Pump coin ${quote.mint.toBase58()} is nested: the curve of ${expected.toBase58()} is required (QuoteChainAccountsRequired)`,
      );
    }
    if (!coin.mint.equals(expected)) {
      throw new Error(
        `Quote chain of ${quote.mint.toBase58()}: coin ${i + 1} is ${coin.mint.toBase58()}, expected ${expected.toBase58()}`,
      );
    }
    coins.push(coin);
  }
  return coins;
}

// What a fresh curve quoted in the root's own quote would be seeded with.
function rootTarget(
  global: Global,
  root: PumpQuoteChainCoin,
  quoteControl: QuoteControl | null,
): BN {
  const curve = root.bondingCurve;
  if (curve.quoteMint.equals(PublicKey.default)) {
    return global.initialVirtualSolReserves;
  }
  if (global.whitelistedQuoteMints.some((m) => m.equals(curve.quoteMint))) {
    return global.initialVirtualQuoteReserves;
  }
  const entry = quoteControl?.mints.find((candidate) =>
    candidate.mint.equals(curve.quoteMint),
  );
  if (!entry) {
    throw new QuoteBondingCurveNotEligibleError(root.mint);
  }
  return entry.initialVirtualQuoteReserves;
}

/**
 * The checks `create_v2` runs on pump coin Q and its quote chain before it
 * reads any price, in its order: `pumpQuoteGate`, then per coin, Q first, the
 * root's eligibility (`QuoteBondingCurveNotEligibleError`: the root's own
 * quote no list admits) and a complete but unmigrated curve
 * (`QuoteCurveAwaitingMigrationError`). Returns the new coin's depth and the
 * reference seed whose raise is bought up the chain. Needs only the curves
 * (no pools), so it can run before any pool is fetched.
 */
export function pumpQuoteAdmission(
  global: Global,
  quote: Pick<
    PumpQuoteCurve,
    "mint" | "bondingCurve" | "quoteControl" | "chain"
  >,
  quoteControl?: QuoteControl | null,
): { depth: number; target: BN } {
  const depth = pumpQuoteGate(global, quote);
  const coins = pumpQuoteChain(quote);
  let target = new BN(0);
  coins.forEach((coin, i) => {
    if (i === coins.length - 1) {
      target = rootTarget(
        global,
        coin,
        quoteControl !== undefined
          ? quoteControl
          : (quote.quoteControl ?? null),
      );
    }
    if (
      !isBondingCurveMigrated(coin.bondingCurve) &&
      coin.bondingCurve.complete
    ) {
      throw new QuoteCurveAwaitingMigrationError(coin.mint);
    }
  });
  return { depth, target };
}

// pump `quote_tokens_out`: a constant-product buy; an emptied quote side
// prices nothing rather than handing out the whole base.
function chainBuy(mint: PublicKey, base: BN, quoteSide: BN, quoteIn: BN): BN {
  if (quoteSide.lten(0)) {
    throw new Error(
      `Pump coin ${mint.toBase58()}: zero quote reserves (DivisionByZero)`,
    );
  }
  return getBuyTokenAmountFromSolAmountQuote({
    inputAmount: quoteIn,
    virtualTokenReserves: base,
    virtualQuoteReserves: quoteSide,
  });
}

// pump `hop_tokens_out`: the tokens a buy of `quoteIn` returns at one chain
// coin, before fees. A migrated coin is its pool's constant product. A trading
// curve is its virtual constant product up to its real token reserves; a buy
// past them takes the remainder at `buy_quote`'s price, completes the curve
// and spends the rest exact-in in the pool-to-be (the migration deposit,
// `tokenTotalSupply - initialRealTokenReserves`, against the whole raise less
// `poolMigrationFee` on a SOL curve), as `buy_v3` and a multi-hop curve hop
// do. So no hop ever returns more than the coin can sell.
function chainCoinHop(
  global: Global,
  coin: PumpQuoteChainCoin,
): (quoteIn: BN) => BN {
  const curve = coin.bondingCurve;
  if (isBondingCurveMigrated(curve)) {
    if (!coin.pool) {
      throw new Error(
        `Pump coin ${coin.mint.toBase58()} has migrated: its pool reserves are required`,
      );
    }
    const { baseReserves } = coin.pool;
    const quoteSide = coin.pool.quoteReserves.add(
      coin.pool.virtualQuoteReserves,
    );
    // The program refuses this with Overflow.
    if (quoteSide.isNeg()) {
      throw new Error(
        `Pump coin ${coin.mint.toBase58()}: negative effective pool quote reserves (Overflow)`,
      );
    }
    return (quoteIn) => chainBuy(coin.mint, baseReserves, quoteSide, quoteIn);
  }

  const {
    virtualTokenReserves,
    virtualQuoteReserves,
    realTokenReserves: remaining,
  } = curve;
  return (quoteIn) => {
    const onCurve = chainBuy(
      coin.mint,
      virtualTokenReserves,
      virtualQuoteReserves,
      quoteIn,
    );
    if (onCurve.lte(remaining)) {
      return onCurve;
    }
    const remainderPrice = getBuySolAmountFromTokenAmountQuote({
      minAmount: remaining,
      virtualTokenReserves,
      virtualQuoteReserves,
    });
    const budget = quoteIn.sub(remainderPrice);
    if (budget.ltn(2)) {
      return remaining;
    }
    const poolQuote = curve.realQuoteReserves
      .add(remainderPrice)
      .sub(
        curve.quoteMint.equals(PublicKey.default)
          ? global.poolMigrationFee
          : new BN(0),
      );
    if (poolQuote.isNeg()) {
      throw new Error(
        `Pump coin ${coin.mint.toBase58()}: the pool-to-be's raise is below the migration fee (Overflow)`,
      );
    }
    const poolBase = curve.tokenTotalSupply.sub(
      global.initialRealTokenReserves,
    );
    return remaining.add(
      chainBuy(coin.mint, poolBase, poolQuote, budget.subn(1)),
    );
  };
}

/**
 * The `virtualQuoteReserves` and `depth` `create_v2` gives a coin quoted in
 * pump coin Q, with the program's admission checks (`pumpQuoteAdmission`).
 * Every coin on Q's quote chain is priced live: the reference seed's
 * graduation raise is bought on the root (its pool's constant product once
 * migrated; its curve while trading, completing it and buying on from the
 * pool-to-be past the remaining supply, as `buy_v3` would), what that returns
 * is bought on the next coin up, and so on to Q; the Q bought is the new
 * curve's raise, scaled back by the raise ratio. A Q deeper than 0 needs `quote.chain`. Throws the typed
 * error the program's refusal maps to (`CurveDepthExceededError`,
 * `QuoteBondingCurveNotEligibleError`, `QuoteCurveAwaitingMigrationError`,
 * `QuoteReservesOutOfRangeError`).
 *
 * @param quoteControl - The decoded `QuoteControl` PDA, or `null` when it
 *   does not exist; consulted for the chain root's own quote. Omitted, the
 *   one fetched with Q (`quote.quoteControl`) is used.
 */
export function pumpQuoteReserves(
  global: Global,
  quote: PumpQuoteCurve,
  quoteControl?: QuoteControl | null,
): { virtualQuoteReserves: BN; depth: number } {
  const { depth, target } = pumpQuoteAdmission(global, quote, quoteControl);
  // Read Q first, as the program does, then buy root first. Each hop returns
  // at most what that coin can sell, so there is no supply bound.
  const hops = pumpQuoteChain(quote).map((coin) => chainCoinHop(global, coin));
  const tradable = global.initialVirtualTokenReserves.sub(
    global.initialRealTokenReserves,
  );
  const raise = hops.reduceRight(
    (quoteIn, hop) => hop(quoteIn),
    target.mul(global.initialRealTokenReserves).div(tradable),
  );
  const derived = raise.mul(tradable).div(global.initialRealTokenReserves);
  if (derived.ltn(1)) {
    throw new QuoteReservesOutOfRangeError(quote.mint, derived);
  }
  return { virtualQuoteReserves: derived, depth };
}

/**
 * The curve `create_v2` would initialize for `quoteMint`.
 *
 * @param quoteControl - See `initialVirtualQuoteReservesFor`; required for a
 * quote-control mint to be seeded correctly.
 * @param creatorFeeBps - The `creator_fee_bps` the create is sent with
 * (`createV2Instruction`'s `creatorFeeBps`); omitted or zero means the
 * schedule rate. `create_v2` always stores `canEditCreatorFee = false`.
 * @param isHolderReward - Whether the create is sent with `holderReward`
 * (`createV2Instruction`'s `holderReward`): the curve's creator is then the
 * coin's `holderRewardsPda(mint)`, which this function cannot derive without
 * the mint, so `creator` stays the zero key either way.
 * @param pumpQuote - When `quoteMint` is a pump coin listed nowhere; sets
 * the derived seed and `depth` (see `pumpQuoteReserves`).
 */
export function newBondingCurve(
  global: Global,
  quoteMint: PublicKey = PublicKey.default,
  quoteControl?: QuoteControl | null,
  creatorFeeBps?: BN,
  isHolderReward = false,
  pumpQuote?: PumpQuoteCurve,
): BondingCurve {
  // The type never admitted `null`, but the pre-quote-control code treated any
  // falsy quote as SOL at runtime and untyped callers rely on it.
  const quote = quoteMint ?? PublicKey.default;
  const virtualQuoteReserves = initialVirtualQuoteReservesFor(
    global,
    quote,
    quoteControl,
    pumpQuote ?? undefined,
  );
  // A listed quote wins over the pump-quote path, as in `create_v2`.
  const listedIn =
    quoteControl !== undefined ? quoteControl : pumpQuote?.quoteControl;
  const isPumpQuoted =
    pumpQuote != null &&
    !isLegacyQuoteMint(quote) &&
    !global.whitelistedQuoteMints.some((mint) => mint.equals(quote)) &&
    !listedIn?.mints.some((entry) => entry.mint.equals(quote));

  return {
    virtualTokenReserves: global.initialVirtualTokenReserves,
    virtualQuoteReserves,
    realTokenReserves: global.initialRealTokenReserves,
    realQuoteReserves: new BN(0),
    tokenTotalSupply: global.tokenTotalSupply,
    complete: false,
    creator: PublicKey.default,
    isMayhemMode: global.mayhemModeEnabled,
    isCashbackCoin: false,
    // Stored the way the program stores it: the zero key for SOL curves.
    quoteMint: isLegacyQuoteMint(quote) ? PublicKey.default : quote,
    creatorFeeBps: creatorFeeBps ?? new BN(0),
    canEditCreatorFee: false,
    isHolderReward,
    creatorFee: new BN(0),
    protocolFees: new BN(0),
    depth: isPumpQuoted ? pumpQuote.bondingCurve.depth + 1 : 0,
    initialVirtualQuoteReserves: virtualQuoteReserves,
    postCompleteBaseOut: new BN(0),
    postCompleteQuoteIn: new BN(0),
  };
}

function getBuySolAmountFromTokenAmountQuote({
  minAmount,
  virtualTokenReserves,
  virtualQuoteReserves,
}: {
  minAmount: BN;
  virtualTokenReserves: BN;
  virtualQuoteReserves: BN;
}): BN {
  return minAmount
    .mul(virtualQuoteReserves)
    .div(virtualTokenReserves.sub(minAmount))
    .add(new BN(1));
}

function getBuyTokenAmountFromSolAmountQuote({
  inputAmount,
  virtualTokenReserves,
  virtualQuoteReserves,
}: {
  inputAmount: BN;
  virtualTokenReserves: BN;
  virtualQuoteReserves: BN;
}): BN {
  return inputAmount
    .mul(virtualTokenReserves)
    .div(virtualQuoteReserves.add(inputAmount));
}

function getSellSolAmountFromTokenAmountQuote({
  inputAmount,
  virtualTokenReserves,
  virtualQuoteReserves,
}: {
  inputAmount: BN;
  virtualTokenReserves: BN;
  virtualQuoteReserves: BN;
}): BN {
  return inputAmount
    .mul(virtualQuoteReserves)
    .div(virtualTokenReserves.add(inputAmount));
}

/**
 * @param params.quoteMint - Selects the quote when `bondingCurve` is `null`
 * (a curve about to be created); an existing curve's own `quoteMint` is
 * authoritative for fee selection.
 * @param params.quoteControl - The decoded `QuoteControl` PDA (or `null` when
 * it does not exist), needed to seed a new curve quoted in a quote-control
 * mint; see `initialVirtualQuoteReservesFor`.
 * @param params.creatorFeeBps - Used only when `bondingCurve` is `null`: the
 * `creator_fee_bps` the create is sent with, so the first buy is quoted at
 * the rate the program will charge. An existing curve's own `creatorFeeBps`
 * is authoritative.
 * @param params.quoteTransferFee - The quote's Token-2022 transfer fee in
 * force (`OnlinePumpSdk.fetchBuyState` / `fetchQuoteTransferFee`), if any:
 * `amount` is then what leaves the wallet, fee included, and only what lands
 * on the curve buys tokens.
 */
export function getBuyTokenAmountFromSolAmount({
  global,
  feeConfig,
  mintSupply,
  bondingCurve,
  amount: budget,
  quoteMint,
  quoteControl,
  creatorFeeBps,
  pumpQuote,
  quoteTransferFee,
}: {
  global: Global;
  feeConfig: FeeConfig | null;
  mintSupply: BN | null;
  bondingCurve: BondingCurve | null;
  amount: BN;
  quoteMint: PublicKey;
  quoteControl?: QuoteControl | null;
  creatorFeeBps?: BN;
  /** Used only when `bondingCurve` is `null` and the quote is a pump coin. */
  pumpQuote?: PumpQuoteCurve;
  quoteTransferFee?: QuoteTransferFee | null;
}): BN {
  // The program derives the buy from what the budget lands on the curve.
  const amount = transferFeeNetOf(quoteTransferFee, budget);
  if (amount.lten(0)) {
    return new BN(0);
  }

  let isNewBondingCurve = false;

  if (bondingCurve === null || mintSupply === null) {
    bondingCurve = newBondingCurve(
      global,
      quoteMint,
      quoteControl,
      creatorFeeBps,
      false,
      pumpQuote ?? undefined,
    );
    mintSupply = global.tokenTotalSupply;
    isNewBondingCurve = true;
  }

  // migrated bonding curve
  if (bondingCurve.virtualTokenReserves.eq(new BN(0))) {
    return new BN(0);
  }

  const { virtualQuoteReserves, virtualTokenReserves } = bondingCurve;
  const { protocolFeeBps, creatorFeeBps: chargedCreatorFeeBps } =
    computeFeesBps({
      global,
      feeConfig,
      mintSupply,
      virtualQuoteReserves,
      virtualTokenReserves,
      quoteMint: bondingCurve.quoteMint,
      creatorFeeBps: bondingCurve.creatorFeeBps,
    });

  const totalFeeBasisPoints = protocolFeeBps.add(
    isNewBondingCurve || !PublicKey.default.equals(bondingCurve.creator)
      ? chargedCreatorFeeBps
      : new BN(0),
  );

  const inputAmount = amount
    .subn(1)
    .muln(10_000)
    .div(totalFeeBasisPoints.addn(10_000));

  const tokensReceived = getBuyTokenAmountFromSolAmountQuote({
    inputAmount,
    virtualTokenReserves: bondingCurve.virtualTokenReserves,
    virtualQuoteReserves: bondingCurve.virtualQuoteReserves,
  });

  return BN.min(tokensReceived, bondingCurve.realTokenReserves);
}

/**
 * @param params.quoteMint - Selects the quote when `bondingCurve` is `null`
 * (a curve about to be created); an existing curve's own `quoteMint` is
 * authoritative for fee selection.
 * @param params.quoteControl - The decoded `QuoteControl` PDA (or `null` when
 * it does not exist), needed to seed a new curve quoted in a quote-control
 * mint; see `initialVirtualQuoteReservesFor`.
 * @param params.creatorFeeBps - Used only when `bondingCurve` is `null`; see
 * `getBuyTokenAmountFromSolAmount`.
 * @param params.quoteTransferFee - The quote's Token-2022 transfer fee in
 * force, if any: the cost is then what leaves the wallet, the curve's share
 * grossed up so the curve books the full amount (the fees go as they are).
 */
export function getBuySolAmountFromTokenAmount({
  global,
  feeConfig,
  mintSupply,
  bondingCurve,
  amount,
  quoteMint,
  quoteControl,
  creatorFeeBps,
  pumpQuote,
  quoteTransferFee,
}: {
  global: Global;
  feeConfig: FeeConfig | null;
  mintSupply: BN | null;
  bondingCurve: BondingCurve | null;
  amount: BN;
  quoteMint: PublicKey;
  quoteControl?: QuoteControl | null;
  creatorFeeBps?: BN;
  /** Used only when `bondingCurve` is `null` and the quote is a pump coin. */
  pumpQuote?: PumpQuoteCurve;
  quoteTransferFee?: QuoteTransferFee | null;
}): BN {
  if (amount.eq(new BN(0))) {
    return new BN(0);
  }

  let isNewBondingCurve = false;

  if (bondingCurve === null || mintSupply === null) {
    bondingCurve = newBondingCurve(
      global,
      quoteMint,
      quoteControl,
      creatorFeeBps,
      false,
      pumpQuote ?? undefined,
    );
    mintSupply = global.tokenTotalSupply;
    isNewBondingCurve = true;
  }

  // migrated bonding curve
  if (bondingCurve.virtualTokenReserves.eq(new BN(0))) {
    return new BN(0);
  }

  const minAmount = BN.min(amount, bondingCurve.realTokenReserves);

  const solCost = getBuySolAmountFromTokenAmountQuote({
    minAmount,
    virtualTokenReserves: bondingCurve.virtualTokenReserves,
    virtualQuoteReserves: bondingCurve.virtualQuoteReserves,
  });

  return transferFeeGrossFor(quoteTransferFee, solCost).add(
    getFee({
      global,
      feeConfig,
      mintSupply,
      bondingCurve,
      amount: solCost,
      isNewBondingCurve,
    }),
  );
}

/**
 * @param params.quoteTransferFee - The quote's Token-2022 transfer fee in
 * force, if any: the proceeds are then what lands in the wallet, the payout
 * less the fee (the slippage floor binds on it).
 */
export function getSellSolAmountFromTokenAmount({
  global,
  feeConfig,
  mintSupply,
  bondingCurve,
  amount,
  quoteTransferFee,
}: {
  global: Global;
  feeConfig: FeeConfig | null;
  mintSupply: BN;
  bondingCurve: BondingCurve;
  amount: BN;
  quoteTransferFee?: QuoteTransferFee | null;
}): BN {
  if (amount.eq(new BN(0))) {
    return new BN(0);
  }

  // migrated bonding curve
  if (bondingCurve.virtualTokenReserves.eq(new BN(0))) {
    return new BN(0);
  }

  const solCost = getSellSolAmountFromTokenAmountQuote({
    inputAmount: amount,
    virtualTokenReserves: bondingCurve.virtualTokenReserves,
    virtualQuoteReserves: bondingCurve.virtualQuoteReserves,
  });

  return transferFeeNetOf(
    quoteTransferFee,
    solCost.sub(
      getFee({
        global,
        feeConfig,
        mintSupply,
        bondingCurve,
        amount: solCost,
        isNewBondingCurve: false,
      }),
    ),
  );
}

export function getStaticRandomFeeRecipient(): PublicKey {
  const randomIndex = Math.floor(Math.random() * CURRENT_FEE_RECIPIENTS.length);
  return new PublicKey(CURRENT_FEE_RECIPIENTS[randomIndex]);
}

const CURRENT_FEE_RECIPIENTS = [
  "62qc2CNXwrYqQScmEdiZFFAnJR262PxWEuNQtxfafNgV",
  "7VtfL8fvgNfhz17qKRMjzQEXgbdpnHHHQRh54R9jP2RJ",
  "7hTckgnGnLQR6sdH7YkqFTAA7VwTfYFaZ6EhEsU3saCX",
  "9rPYyANsfQZw3DnDmKE3YCQF5E8oD89UXoHn9JFEhJUz",
  "AVmoTthdrX6tKt4nDjco2D775W2YK3sDhxPcMmzUAmTY",
  "CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM",
  "FWsW1xNtWscwNmKv6wVsU1iTzRN6wmmk3MjxRP5tT7hz",
  "G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP",
];

export function getStaticRandomFeeRecipientForBuyback(): PublicKey {
  const randomIndex = Math.floor(
    Math.random() * CURRENT_FEE_RECIPIENTS_FOR_BUYBACK.length,
  );
  return new PublicKey(CURRENT_FEE_RECIPIENTS_FOR_BUYBACK[randomIndex]);
}

/**
 * The buyback recipient whose quote ATA the v3 trades pay on a token quote:
 * always the first listed entry (`Global.buybackFeeRecipients[0]`), so a
 * single ATA per quote mint must exist (the trade never creates it). SOL
 * curves pay any listed wallet (`getStaticRandomFeeRecipientForBuyback`).
 */
export function getBuybackFeeRecipientForTokenQuote(): PublicKey {
  return new PublicKey(CURRENT_FEE_RECIPIENTS_FOR_BUYBACK[0]);
}

// Same keys, same order as `Global.buybackFeeRecipients` on mainnet and devnet.
const CURRENT_FEE_RECIPIENTS_FOR_BUYBACK = [
  "5YxQFdt3Tr9zJLvkFccqXVUwhdTWJQc1fFg2YPbxvxeD",
  "9M4giFFMxmFGXtc3feFzRai56WbBqehoSeRE5GK7gf7",
  "GXPFM2caqTtQYC2cJ5yJRi9VDkpsYZXzYdwYpGnLmtDL",
  "3BpXnfJaUTiwXnJNe7Ej1rcbzqTTQUvLShZaWazebsVR",
  "5cjcW9wExnJJiqgLjq7DEG75Pm6JBgE1hNv4B2vHXUW6",
  "EHAAiTxcdDwQ3U4bU6YcMsQGaekdzLS3B5SmYo46kJtL",
  "5eHhjP8JaYkz83CWwvGU2uMUXefd3AazWGx4gpcuEEYD",
  "A7hAgCzFw14fejgCp387JUJRMNyz4j89JKnhtKU8piqW",
];

export function bondingCurveMarketCap({
  mintSupply,
  virtualQuoteReserves,
  virtualTokenReserves,
}: {
  mintSupply: BN;
  virtualQuoteReserves: BN;
  virtualTokenReserves: BN;
}): BN {
  if (virtualTokenReserves.isZero()) {
    throw new Error("Division by zero: virtual token reserves cannot be zero");
  }
  return virtualQuoteReserves.mul(mintSupply).div(virtualTokenReserves);
}

// ---- v3 buys: the post-completion leg ----
//
// A `buy_v3` / `buy_exact_quote_in_v3` past the remaining supply sells the
// remainder at the curve's price, completes the curve and buys the rest from
// the pool the migration will create (not on mayhem curves). These mirror the
// program's arithmetic, fees included.

interface V3Rates {
  protocolFeeBps: BN;
  // Zero on a curve without a creator, as the program charges.
  creatorFeeBps: BN;
}

function v3Rates(
  global: Global,
  feeConfig: FeeConfig,
  mintSupply: BN,
  bondingCurve: BondingCurve,
): V3Rates {
  const { protocolFeeBps, creatorFeeBps } = computeFeesBps({
    global,
    feeConfig,
    mintSupply: bondingCurve.isMayhemMode ? mintSupply : ONE_BILLION_SUPPLY,
    virtualQuoteReserves: bondingCurve.virtualQuoteReserves,
    virtualTokenReserves: bondingCurve.virtualTokenReserves,
    quoteMint: bondingCurve.quoteMint,
    creatorFeeBps: bondingCurve.creatorFeeBps,
  });
  return {
    protocolFeeBps,
    creatorFeeBps: bondingCurve.creator.equals(PublicKey.default)
      ? new BN(0)
      : creatorFeeBps,
  };
}

function ceilFee(amount: BN, bps: BN): BN {
  return amount.mul(bps).addn(9_999).divn(10_000);
}

function v3Fees(amount: BN, rates: V3Rates): BN {
  return ceilFee(amount, rates.protocolFeeBps).add(
    ceilFee(amount, rates.creatorFeeBps),
  );
}

// pump `Global::buyback_fee_from_protocol_fee`: the slice of a leg's protocol
// fee paid out in the trade, floor; none on a mayhem curve.
function v3BuybackSlice(
  global: Global,
  bondingCurve: BondingCurve,
  net: BN,
  rates: V3Rates,
): BN {
  if (bondingCurve.isMayhemMode) {
    return new BN(0);
  }
  return ceilFee(net, rates.protocolFeeBps)
    .mul(global.buybackBasisPoints)
    .divn(10_000);
}

// pump `BuyDebit::total`: what a v3 buy takes from the buyer's quote account
// for a curve leg of `net` (and a post-completion leg of `legNet`): everything
// that lands on the curve, grossed up for the quote's transfer fee, plus the
// buyback slices of both legs, sent as they are. The plain total without a fee.
function v3BuyDebit(
  global: Global,
  bondingCurve: BondingCurve,
  rates: V3Rates,
  quoteTransferFee: QuoteTransferFee | null | undefined,
  net: BN,
  legNet: BN | null,
): BN {
  const buyback = v3BuybackSlice(global, bondingCurve, net, rates).add(
    legNet ? v3BuybackSlice(global, bondingCurve, legNet, rates) : new BN(0),
  );
  const curveBound = net
    .add(v3Fees(net, rates))
    .add(legNet ? legNet.add(v3Fees(legNet, rates)) : new BN(0))
    .sub(buyback);
  return transferFeeGrossFor(quoteTransferFee, curveBound).add(buyback);
}

// pump `exact_quote_in_fees`: the net quote a budget leaves after fees.
function v3ExactQuoteInNet(budget: BN, rates: V3Rates): BN {
  const totalBps = rates.protocolFeeBps.add(rates.creatorFeeBps);
  let net = totalBps.isZero()
    ? budget
    : budget.muln(10_000).div(totalBps.addn(10_000));
  const cost = net.add(v3Fees(net, rates));
  if (cost.gt(budget)) {
    net = net.sub(cost.sub(budget));
  }
  return net;
}

// The reserves `migrate_v2` would deposit once the curve leg completes it.
function poolToBe(
  global: Global,
  bondingCurve: BondingCurve,
  curveBaseTokenBalance: BN,
  curveTokens: BN,
  curveNetQuote: BN,
): { base: BN; quote: BN } {
  const raised = bondingCurve.realQuoteReserves.add(curveNetQuote);
  const base = curveBaseTokenBalance.sub(curveTokens);
  const quote = isLegacyQuoteMint(bondingCurve.quoteMint)
    ? raised.sub(global.poolMigrationFee)
    : raised;
  // The program refuses an empty pool-to-be; here it almost always means a
  // wrong `curveBaseTokenBalance` (say, read under the other token program).
  if (base.lten(0) || quote.lten(0)) {
    throw new Error(
      `Empty pool-to-be (base ${base.toString()}, quote ${quote.toString()}): check curveBaseTokenBalance`,
    );
  }
  return { base, quote };
}

/**
 * What `buy_v3` charges for `amount` tokens, fees included: the cap to send
 * as `max_sol_cost` before slippage. Past the remaining supply the cost
 * includes the post-completion leg; on a mayhem curve it stops at the
 * remaining supply (send `partialFill` then). Zero on a complete curve
 * (every trade is refused until the migration).
 *
 * @param params.curveBaseTokenBalance - The curve's base ATA balance
 *   (`OnlinePumpSdk.fetchBuyState` returns it); prices the pool-to-be.
 * @param params.quoteTransferFee - The quote's Token-2022 transfer fee in
 *   force (`fetchBuyState` returns it), if any: the cost is then what leaves
 *   the wallet, what must land on the curve grossed up and the buyback slice
 *   sent as it is, which is what `max_sol_cost` is checked against.
 * @throws when `amount` would take the whole pool-to-be (6021
 *   `NotEnoughTokensToBuy` on chain), or when the pool-to-be is empty.
 */
export function getBuyV3QuoteAmountFromTokenAmount({
  global,
  feeConfig,
  mintSupply,
  bondingCurve,
  amount,
  curveBaseTokenBalance,
  quoteTransferFee,
}: {
  global: Global;
  /** Required: v3 always charges the `FeeConfig` schedule. */
  feeConfig: FeeConfig;
  mintSupply: BN;
  bondingCurve: BondingCurve;
  amount: BN;
  curveBaseTokenBalance: BN;
  quoteTransferFee?: QuoteTransferFee | null;
}): BN {
  const remaining = bondingCurve.realTokenReserves;
  if (
    amount.isZero() ||
    bondingCurve.complete ||
    bondingCurve.virtualTokenReserves.isZero()
  ) {
    return new BN(0);
  }
  const rates = v3Rates(global, feeConfig, mintSupply, bondingCurve);
  const curveTokens = BN.min(amount, remaining);
  const curveNet = getBuySolAmountFromTokenAmountQuote({
    minAmount: curveTokens,
    virtualTokenReserves: bondingCurve.virtualTokenReserves,
    virtualQuoteReserves: bondingCurve.virtualQuoteReserves,
  });
  const debit = (legNet: BN | null) =>
    v3BuyDebit(global, bondingCurve, rates, quoteTransferFee, curveNet, legNet);
  if (amount.lte(remaining) || bondingCurve.isMayhemMode) {
    return debit(null);
  }

  const pastCurve = amount.sub(remaining);
  const pool = poolToBe(
    global,
    bondingCurve,
    curveBaseTokenBalance,
    remaining,
    curveNet,
  );
  if (pool.base.lte(pastCurve)) {
    throw new Error(
      `buy_v3 of ${amount.toString()} tokens takes the whole pool-to-be (NotEnoughTokensToBuy)`,
    );
  }
  // pump-amm `buy_quote`: ceil(Q * out / (B - out)).
  const legNet = pool.quote
    .mul(pastCurve)
    .add(pool.base.sub(pastCurve))
    .subn(1)
    .div(pool.base.sub(pastCurve));
  return debit(legNet);
}

/**
 * The tokens `buy_exact_quote_in_v3` buys for `amount` quote, fees included;
 * apply slippage to it for `min_tokens_out`. Past the remaining supply the
 * leftover budget buys from the pool-to-be; on a mayhem curve it stops at the
 * remaining supply (send `partialFill` then). Zero on a complete curve.
 *
 * @param params.curveBaseTokenBalance - As in
 *   `getBuyV3QuoteAmountFromTokenAmount`.
 * @param params.quoteTransferFee - The quote's Token-2022 transfer fee in
 *   force, if any: `amount` is then what leaves the wallet, fee included; the
 *   buy is derived from what it lands on the curve and shaved until the
 *   actual debit fits, as the program does.
 * @throws when a crossing budget meets an empty pool-to-be.
 */
export function getBuyV3TokenAmountFromQuoteAmount({
  global,
  feeConfig,
  mintSupply,
  bondingCurve,
  amount,
  curveBaseTokenBalance,
  quoteTransferFee,
}: {
  global: Global;
  /** Required: v3 always charges the `FeeConfig` schedule. */
  feeConfig: FeeConfig;
  mintSupply: BN;
  bondingCurve: BondingCurve;
  amount: BN;
  curveBaseTokenBalance: BN;
  quoteTransferFee?: QuoteTransferFee | null;
}): BN {
  if (
    amount.isZero() ||
    bondingCurve.complete ||
    bondingCurve.virtualTokenReserves.isZero()
  ) {
    return new BN(0);
  }
  const rates = v3Rates(global, feeConfig, mintSupply, bondingCurve);
  const debit = (net: BN, legNet: BN | null) =>
    v3BuyDebit(global, bondingCurve, rates, quoteTransferFee, net, legNet);
  const tokensFor = (net: BN) =>
    getBuyTokenAmountFromSolAmountQuote({
      inputAmount: net.subn(1),
      virtualTokenReserves: bondingCurve.virtualTokenReserves,
      virtualQuoteReserves: bondingCurve.virtualQuoteReserves,
    });
  // The derivation runs on what the budget lands on the curve.
  const spendable = transferFeeNetOf(quoteTransferFee, amount);
  let net = v3ExactQuoteInNet(spendable, rates);
  if (net.lten(1)) {
    return new BN(0);
  }
  let tokens = tokensFor(net);
  const remaining = bondingCurve.realTokenReserves;
  if (tokens.lte(remaining) || bondingCurve.isMayhemMode) {
    // The debit may exceed the budget by the transfer fee's rounding: the
    // program shaves the net until it fits.
    const excess = debit(net, null).sub(amount);
    if (excess.gtn(0)) {
      net = net.sub(excess);
      if (net.lten(1)) {
        return new BN(0);
      }
      tokens = tokensFor(net);
    }
    return BN.min(tokens, remaining);
  }

  const curveNet = getBuySolAmountFromTokenAmountQuote({
    minAmount: remaining,
    virtualTokenReserves: bondingCurve.virtualTokenReserves,
    virtualQuoteReserves: bondingCurve.virtualQuoteReserves,
  });
  // A budget past the remaining supply takes the crossing branch whatever the
  // minimum, and the program first requires the remainder's own debit (the
  // transfer fee included) to fit it; the fallbacks below that stop at the
  // remainder all settle on that debit.
  if (debit(curveNet, null).gt(amount)) {
    throw new Error(
      `A budget of ${amount.toString()} crosses the remaining supply but does not cover the remainder's debit with the quote's transfer fee (TooMuchSolRequired)`,
    );
  }
  const budgetLeft = spendable.sub(curveNet.add(v3Fees(curveNet, rates)));
  if (budgetLeft.lten(0)) {
    return remaining;
  }
  const totalBps = rates.protocolFeeBps.add(rates.creatorFeeBps);
  const afterFees = totalBps.isZero()
    ? budgetLeft
    : budgetLeft.muln(10_000).div(totalBps.addn(10_000));
  if (afterFees.ltn(2)) {
    return remaining;
  }
  let legNet = v3ExactQuoteInNet(budgetLeft, rates);
  const pool = poolToBe(
    global,
    bondingCurve,
    curveBaseTokenBalance,
    remaining,
    curveNet,
  );
  // pump-amm `buy_exact_quote_in`: floor((in - 1) * B / (Q + in - 1)).
  const legTokensFor = (quoteIn: BN) =>
    quoteIn
      .subn(1)
      .mul(pool.base)
      .div(pool.quote.add(quoteIn.subn(1)));
  let legTokens = legTokensFor(legNet);
  // pump `fit_leg_to_budget`: the leg was priced on what lands; shave its
  // quote until the actual debit fits the budget, and drop it when nothing is
  // left for it (the buy then stops at the completed curve).
  for (;;) {
    const excess = debit(curveNet, legNet).sub(amount);
    if (excess.lten(0)) {
      break;
    }
    legNet = legNet.sub(excess);
    if (legNet.lten(1)) {
      return remaining;
    }
    legTokens = legTokensFor(legNet);
    if (legTokens.isZero()) {
      return remaining;
    }
  }
  return remaining.add(legTokens);
}

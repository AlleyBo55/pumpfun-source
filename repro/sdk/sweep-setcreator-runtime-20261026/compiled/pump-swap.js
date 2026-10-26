"use strict";
var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// src/swap/index.ts
var swap_exports = {};
__export(swap_exports, {
  CANONICAL_POOL_INDEX: () => CANONICAL_POOL_INDEX,
  FEE_CONFIG_SIZE_POST_EXOTIC: () => FEE_CONFIG_SIZE_POST_EXOTIC,
  FEE_CONFIG_SIZE_POST_STABLE: () => FEE_CONFIG_SIZE_POST_STABLE,
  FEE_CONFIG_SIZE_PRE_STABLE: () => FEE_CONFIG_SIZE_PRE_STABLE,
  GLOBAL_CONFIG_PDA: () => GLOBAL_CONFIG_PDA,
  GLOBAL_CONFIG_SIZE: () => GLOBAL_CONFIG_SIZE,
  GLOBAL_VOLUME_ACCUMULATOR_PDA: () => GLOBAL_VOLUME_ACCUMULATOR_PDA,
  MPL_TOKEN_METADATA_PROGRAM_ID: () => MPL_TOKEN_METADATA_PROGRAM_ID,
  MULTI_HOP_MAX_HOPS: () => MULTI_HOP_MAX_HOPS,
  OFFLINE_PUMP_AMM_PROGRAM: () => OFFLINE_PUMP_AMM_PROGRAM,
  OnlinePumpAmmSdk: () => OnlinePumpAmmSdk,
  POOL_ACCOUNT_NEW_SIZE: () => POOL_ACCOUNT_NEW_SIZE,
  POOL_SIZE: () => POOL_SIZE,
  PUMP_AMM_EVENT_AUTHORITY_PDA: () => PUMP_AMM_EVENT_AUTHORITY_PDA,
  PUMP_AMM_FEE_CONFIG_PDA: () => PUMP_AMM_FEE_CONFIG_PDA,
  PUMP_AMM_PROGRAM_ID: () => PUMP_AMM_PROGRAM_ID,
  PUMP_AMM_SDK: () => PUMP_AMM_SDK,
  PUMP_AMM_TOTAL_TOKEN_SUPPLY: () => PUMP_AMM_TOTAL_TOKEN_SUPPLY,
  PUMP_EVENT_AUTHORITY_PDA: () => PUMP_EVENT_AUTHORITY_PDA,
  PUMP_FEE_CONFIG_PDA: () => PUMP_FEE_CONFIG_PDA,
  PUMP_FEE_PROGRAM_ID: () => PUMP_FEE_PROGRAM_ID,
  PUMP_GLOBAL_PDA: () => PUMP_GLOBAL_PDA,
  PUMP_MINT: () => PUMP_MINT,
  PUMP_PROGRAM_ID: () => PUMP_PROGRAM_ID,
  PumpAmmAdminSdk: () => PumpAmmAdminSdk,
  PumpAmmSdk: () => PumpAmmSdk,
  SOL_LIKE_QUOTE_MINTS: () => SOL_LIKE_QUOTE_MINTS,
  STABLE_QUOTE_MINTS: () => STABLE_QUOTE_MINTS,
  USDC_MINT: () => USDC_MINT,
  bondingCurvePda: () => bondingCurvePda,
  boostVaultAta: () => boostVaultAta,
  boostVaultAuthorityPda: () => boostVaultAuthorityPda,
  buyBaseInput: () => buyBaseInput,
  buyDebit: () => buyDebit,
  buyQuoteInput: () => buyQuoteInput,
  calculateFeeTier: () => calculateFeeTier,
  canonicalPoolQuoteMint: () => canonicalPoolQuoteMint,
  canonicalPumpPoolPda: () => canonicalPumpPoolPda,
  coinCreatorVaultAtaPda: () => coinCreatorVaultAtaPda,
  coinCreatorVaultAuthorityPda: () => coinCreatorVaultAuthorityPda,
  computeFeesBps: () => computeFeesBps,
  currentDayTokens: () => currentDayTokens,
  depositLpToken: () => depositLpToken,
  feeSharingConfigPda: () => feeSharingConfigPda,
  feesForQuoteMint: () => feesForQuoteMint,
  getBuybackFeeRecipient: () => getBuybackFeeRecipient,
  getFeeRecipient: () => getFeeRecipient,
  getPumpAmmProgram: () => getPumpAmmProgram,
  grossForTransferFee: () => grossForTransferFee,
  holderRewardsPda: () => holderRewardsPda,
  isPumpPool: () => isPumpPool,
  isSolLikeQuoteMint: () => isSolLikeQuoteMint,
  isStableQuoteMint: () => isStableQuoteMint,
  isZeroFees: () => isZeroFees,
  lpMintAta: () => lpMintAta,
  lpMintPda: () => lpMintPda,
  metadataPda: () => metadataPda,
  multiHopSwapQuote: () => multiHopSwapQuote,
  netOfTransferFee: () => netOfTransferFee,
  parseTransferFeeConfig: () => parseTransferFeeConfig,
  poolMarketCap: () => poolMarketCap,
  poolPda: () => poolPda,
  poolV2Pda: () => poolV2Pda,
  pumpAmmJson: () => pump_amm_default,
  pumpAmmPda: () => pumpAmmPda,
  pumpFeePda: () => pumpFeePda,
  pumpPda: () => pumpPda,
  pumpPoolAuthorityPda: () => pumpPoolAuthorityPda,
  resolveMultiHopRoute: () => resolveMultiHopRoute,
  sellBaseInput: () => sellBaseInput,
  sellQuoteInput: () => sellQuoteInput,
  supportsTradeV2: () => supportsTradeV2,
  totalUnclaimedTokens: () => totalUnclaimedTokens,
  transferFeeAt: () => transferFeeAt,
  transferFeeOn: () => transferFeeOn,
  userVolumeAccumulatorPda: () => userVolumeAccumulatorPda,
  withdraw: () => withdraw
});
module.exports = __toCommonJS(swap_exports);

// src/swap/pda.ts
var import_spl_token = require("@solana/spl-token");
var import_web3 = require("@solana/web3.js");
var import_bn = __toESM(require("bn.js"));
var import_buffer = require("buffer");
var PUMP_PROGRAM_ID = new import_web3.PublicKey(
  "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
);
var PUMP_AMM_PROGRAM_ID = new import_web3.PublicKey(
  "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
);
var PUMP_FEE_PROGRAM_ID = new import_web3.PublicKey(
  "pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ"
);
var PUMP_MINT = new import_web3.PublicKey(
  "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn"
);
var CANONICAL_POOL_INDEX = 0;
function pumpPda(seeds) {
  return import_web3.PublicKey.findProgramAddressSync(seeds, PUMP_PROGRAM_ID)[0];
}
function pumpAmmPda(seeds) {
  return import_web3.PublicKey.findProgramAddressSync(seeds, PUMP_AMM_PROGRAM_ID)[0];
}
function pumpFeePda(seeds) {
  return import_web3.PublicKey.findProgramAddressSync(seeds, PUMP_FEE_PROGRAM_ID)[0];
}
var GLOBAL_CONFIG_PDA = pumpAmmPda([import_buffer.Buffer.from("global_config")]);
var PUMP_AMM_EVENT_AUTHORITY_PDA = pumpAmmPda([
  import_buffer.Buffer.from("__event_authority")
]);
var GLOBAL_VOLUME_ACCUMULATOR_PDA = pumpAmmPda([
  import_buffer.Buffer.from("global_volume_accumulator")
]);
var PUMP_AMM_FEE_CONFIG_PDA = pumpFeePda([
  import_buffer.Buffer.from("fee_config"),
  PUMP_AMM_PROGRAM_ID.toBuffer()
]);
var PUMP_GLOBAL_PDA = pumpPda([import_buffer.Buffer.from("global")]);
var PUMP_EVENT_AUTHORITY_PDA = pumpPda([
  import_buffer.Buffer.from("__event_authority")
]);
var PUMP_FEE_CONFIG_PDA = pumpFeePda([
  import_buffer.Buffer.from("fee_config"),
  PUMP_PROGRAM_ID.toBuffer()
]);
function poolPda(index, owner, baseMint, quoteMint) {
  return pumpAmmPda([
    import_buffer.Buffer.from("pool"),
    new import_bn.default(index).toArrayLike(import_buffer.Buffer, "le", 2),
    owner.toBuffer(),
    baseMint.toBuffer(),
    quoteMint.toBuffer()
  ]);
}
function lpMintPda(pool) {
  return pumpAmmPda([import_buffer.Buffer.from("pool_lp_mint"), pool.toBuffer()]);
}
function lpMintAta(lpMint, owner) {
  return (0, import_spl_token.getAssociatedTokenAddressSync)(
    lpMint,
    owner,
    true,
    import_spl_token.TOKEN_2022_PROGRAM_ID
  );
}
function pumpPoolAuthorityPda(mint) {
  return pumpPda([import_buffer.Buffer.from("pool-authority"), mint.toBuffer()]);
}
function holderRewardsPda(mint) {
  return pumpPda([import_buffer.Buffer.from("holder-rewards"), mint.toBuffer()]);
}
var MPL_TOKEN_METADATA_PROGRAM_ID = new import_web3.PublicKey(
  "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s"
);
function bondingCurvePda(mint) {
  return pumpPda([import_buffer.Buffer.from("bonding-curve"), mint.toBuffer()]);
}
function metadataPda(mint) {
  return import_web3.PublicKey.findProgramAddressSync(
    [
      import_buffer.Buffer.from("metadata"),
      MPL_TOKEN_METADATA_PROGRAM_ID.toBuffer(),
      mint.toBuffer()
    ],
    MPL_TOKEN_METADATA_PROGRAM_ID
  )[0];
}
function canonicalPoolQuoteMint(bondingCurveQuoteMint) {
  return bondingCurveQuoteMint.equals(import_web3.PublicKey.default) ? import_spl_token.NATIVE_MINT : bondingCurveQuoteMint;
}
function canonicalPumpPoolPda(mint, quoteMint = import_spl_token.NATIVE_MINT) {
  return poolPda(
    CANONICAL_POOL_INDEX,
    pumpPoolAuthorityPda(mint),
    mint,
    canonicalPoolQuoteMint(quoteMint)
  );
}
function userVolumeAccumulatorPda(user) {
  return pumpAmmPda([import_buffer.Buffer.from("user_volume_accumulator"), user.toBuffer()]);
}
function coinCreatorVaultAuthorityPda(coinCreator) {
  return pumpAmmPda([import_buffer.Buffer.from("creator_vault"), coinCreator.toBuffer()]);
}
function coinCreatorVaultAtaPda(coinCreatorVaultAuthority, quoteMint, quoteTokenProgram) {
  return (0, import_spl_token.getAssociatedTokenAddressSync)(
    quoteMint,
    coinCreatorVaultAuthority,
    true,
    quoteTokenProgram
  );
}
function feeSharingConfigPda(mint) {
  return pumpFeePda([import_buffer.Buffer.from("sharing-config"), mint.toBuffer()]);
}
function poolV2Pda(baseMint) {
  return pumpAmmPda([import_buffer.Buffer.from("pool-v2"), baseMint.toBuffer()]);
}
function boostVaultAuthorityPda(pool) {
  return pumpAmmPda([import_buffer.Buffer.from("boost_vault"), pool.toBuffer()]);
}
function boostVaultAta(boostVaultAuthority, quoteMint, quoteTokenProgram) {
  return (0, import_spl_token.getAssociatedTokenAddressSync)(
    quoteMint,
    boostVaultAuthority,
    true,
    quoteTokenProgram
  );
}

// src/swap/pumpAmmAdmin.ts
var import_spl_token6 = require("@solana/spl-token");
var import_bn10 = __toESM(require("bn.js"));

// src/swap/offlinePumpAmm.ts
var import_spl_token5 = require("@solana/spl-token");
var import_web36 = require("@solana/web3.js");
var import_bn9 = __toESM(require("bn.js"));

// src/swap/buy.ts
var import_web33 = require("@solana/web3.js");
var import_bn4 = __toESM(require("bn.js"));

// src/swap/fees.ts
var import_spl_token2 = require("@solana/spl-token");
var import_web32 = require("@solana/web3.js");

// src/swap/util.ts
var import_anchor = require("@coral-xyz/anchor");
var import_bn2 = __toESM(require("bn.js"));

// src/idl/pump_amm.json
var pump_amm_default = {
  address: "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA",
  metadata: {
    name: "pump_amm",
    version: "0.1.0",
    spec: "0.1.0",
    description: "Created with Anchor"
  },
  instructions: [
    {
      name: "admin_cto_pool",
      discriminator: [
        45,
        61,
        165,
        151,
        104,
        0,
        49,
        189
      ],
      accounts: [
        {
          name: "payer",
          writable: true,
          signer: true
        },
        {
          name: "global_config"
        },
        {
          name: "pool",
          writable: true
        },
        {
          name: "pool_authority",
          signer: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  112,
                  111,
                  111,
                  108,
                  45,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              },
              {
                kind: "account",
                path: "pool.base_mint",
                account: "Pool"
              }
            ],
            program: {
              kind: "const",
              value: [
                1,
                86,
                224,
                246,
                147,
                102,
                90,
                207,
                68,
                219,
                21,
                104,
                191,
                23,
                91,
                170,
                81,
                137,
                203,
                151,
                245,
                210,
                255,
                59,
                101,
                93,
                43,
                182,
                253,
                109,
                24,
                176
              ]
            }
          }
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: [
        {
          name: "coin_creator",
          type: "pubkey"
        },
        {
          name: "is_holder_reward",
          type: "bool"
        },
        {
          name: "creator_fee_bps",
          type: {
            option: "u64"
          }
        }
      ]
    },
    {
      name: "admin_update_token_incentives",
      discriminator: [
        209,
        11,
        115,
        87,
        213,
        23,
        124,
        204
      ],
      accounts: [
        {
          name: "admin",
          writable: true,
          signer: true,
          relations: [
            "global_config"
          ]
        },
        {
          name: "global_config",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  103,
                  108,
                  111,
                  98,
                  97,
                  108,
                  95,
                  99,
                  111,
                  110,
                  102,
                  105,
                  103
                ]
              }
            ]
          }
        },
        {
          name: "global_volume_accumulator",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  103,
                  108,
                  111,
                  98,
                  97,
                  108,
                  95,
                  118,
                  111,
                  108,
                  117,
                  109,
                  101,
                  95,
                  97,
                  99,
                  99,
                  117,
                  109,
                  117,
                  108,
                  97,
                  116,
                  111,
                  114
                ]
              }
            ]
          }
        },
        {
          name: "mint"
        },
        {
          name: "global_incentive_token_account",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "global_volume_accumulator"
              },
              {
                kind: "account",
                path: "token_program"
              },
              {
                kind: "account",
                path: "mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "associated_token_program",
          address: "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "token_program"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: [
        {
          name: "start_time",
          type: "i64"
        },
        {
          name: "end_time",
          type: "i64"
        },
        {
          name: "seconds_in_a_day",
          type: "i64"
        },
        {
          name: "day_number",
          type: "u64"
        },
        {
          name: "token_supply_per_day",
          type: "u64"
        }
      ]
    },
    {
      name: "boost_buy_and_burn",
      discriminator: [
        105,
        68,
        6,
        175,
        0,
        7,
        35,
        162
      ],
      accounts: [
        {
          name: "pool"
        },
        {
          name: "authority",
          writable: true,
          signer: true
        },
        {
          name: "global_config",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  103,
                  108,
                  111,
                  98,
                  97,
                  108,
                  95,
                  99,
                  111,
                  110,
                  102,
                  105,
                  103
                ]
              }
            ]
          }
        },
        {
          name: "base_mint",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "quote_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "pool_base_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "pool_quote_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "boost_vault_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  98,
                  111,
                  111,
                  115,
                  116,
                  95,
                  118,
                  97,
                  117,
                  108,
                  116
                ]
              },
              {
                kind: "account",
                path: "pool"
              }
            ]
          }
        },
        {
          name: "boost_vault",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "boost_vault_authority"
              },
              {
                kind: "account",
                path: "quote_token_program"
              },
              {
                kind: "account",
                path: "quote_mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "base_token_program"
        },
        {
          name: "quote_token_program"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: [
        {
          name: "quote_amount_in",
          type: "u64"
        },
        {
          name: "min_base_amount_burned",
          type: "u64"
        }
      ]
    },
    {
      name: "buy",
      docs: [
        "For cashback coins, optionally pass user_volume_accumulator_wsol_ata as remaining_accounts[0].",
        "If provided and valid, the ATA will be initialized if needed."
      ],
      discriminator: [
        102,
        6,
        61,
        18,
        1,
        218,
        235,
        234
      ],
      accounts: [
        {
          name: "pool",
          writable: true
        },
        {
          name: "user",
          writable: true,
          signer: true
        },
        {
          name: "global_config"
        },
        {
          name: "base_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "quote_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "user_base_token_account",
          writable: true
        },
        {
          name: "user_quote_token_account",
          writable: true
        },
        {
          name: "pool_base_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "pool_quote_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "protocol_fee_recipient"
        },
        {
          name: "protocol_fee_recipient_token_account",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "protocol_fee_recipient"
              },
              {
                kind: "account",
                path: "quote_token_program"
              },
              {
                kind: "account",
                path: "quote_mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "base_token_program"
        },
        {
          name: "quote_token_program"
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "associated_token_program",
          address: "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program",
          address: "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
        },
        {
          name: "coin_creator_vault_ata",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "coin_creator_vault_authority"
              },
              {
                kind: "account",
                path: "quote_token_program"
              },
              {
                kind: "account",
                path: "quote_mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "coin_creator_vault_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  99,
                  114,
                  101,
                  97,
                  116,
                  111,
                  114,
                  95,
                  118,
                  97,
                  117,
                  108,
                  116
                ]
              },
              {
                kind: "account",
                path: "pool.coin_creator",
                account: "Pool"
              }
            ]
          }
        },
        {
          name: "global_volume_accumulator",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  103,
                  108,
                  111,
                  98,
                  97,
                  108,
                  95,
                  118,
                  111,
                  108,
                  117,
                  109,
                  101,
                  95,
                  97,
                  99,
                  99,
                  117,
                  109,
                  117,
                  108,
                  97,
                  116,
                  111,
                  114
                ]
              }
            ]
          }
        },
        {
          name: "user_volume_accumulator",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  117,
                  115,
                  101,
                  114,
                  95,
                  118,
                  111,
                  108,
                  117,
                  109,
                  101,
                  95,
                  97,
                  99,
                  99,
                  117,
                  109,
                  117,
                  108,
                  97,
                  116,
                  111,
                  114
                ]
              },
              {
                kind: "account",
                path: "user"
              }
            ]
          }
        },
        {
          name: "fee_config",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  102,
                  101,
                  101,
                  95,
                  99,
                  111,
                  110,
                  102,
                  105,
                  103
                ]
              },
              {
                kind: "const",
                value: [
                  12,
                  20,
                  222,
                  252,
                  130,
                  94,
                  198,
                  118,
                  148,
                  37,
                  8,
                  24,
                  187,
                  101,
                  64,
                  101,
                  244,
                  41,
                  141,
                  49,
                  86,
                  213,
                  113,
                  180,
                  212,
                  248,
                  9,
                  12,
                  24,
                  233,
                  168,
                  99
                ]
              }
            ],
            program: {
              kind: "account",
              path: "fee_program"
            }
          }
        },
        {
          name: "fee_program",
          address: "pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ"
        }
      ],
      args: [
        {
          name: "base_amount_out",
          type: "u64"
        },
        {
          name: "max_quote_amount_in",
          type: "u64"
        },
        {
          name: "track_volume",
          type: {
            defined: {
              name: "OptionBool"
            }
          }
        }
      ]
    },
    {
      name: "buy_exact_quote_in",
      docs: [
        "Given a budget of spendable_quote_in, buy at least min_base_amount_out",
        "Fees will be deducted from spendable_quote_in",
        "",
        "f(quote) = tokens, where tokens >= min_base_amount_out",
        "",
        "Make sure the payer has enough SOL to cover creation of the following accounts (unless already created):",
        "- protocol_fee_recipient_token_account: rent.minimum_balance(TokenAccount::LEN)",
        "- coin_creator_vault_ata: rent.minimum_balance(TokenAccount::LEN)",
        "- user_volume_accumulator: rent.minimum_balance(UserVolumeAccumulator::LEN)",
        "",
        "For cashback coins, optionally pass user_volume_accumulator_wsol_ata as remaining_accounts[0].",
        "If provided and valid, the ATA will be initialized if needed."
      ],
      discriminator: [
        198,
        46,
        21,
        82,
        180,
        217,
        232,
        112
      ],
      accounts: [
        {
          name: "pool",
          writable: true
        },
        {
          name: "user",
          writable: true,
          signer: true
        },
        {
          name: "global_config"
        },
        {
          name: "base_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "quote_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "user_base_token_account",
          writable: true
        },
        {
          name: "user_quote_token_account",
          writable: true
        },
        {
          name: "pool_base_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "pool_quote_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "protocol_fee_recipient"
        },
        {
          name: "protocol_fee_recipient_token_account",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "protocol_fee_recipient"
              },
              {
                kind: "account",
                path: "quote_token_program"
              },
              {
                kind: "account",
                path: "quote_mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "base_token_program"
        },
        {
          name: "quote_token_program"
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "associated_token_program",
          address: "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program",
          address: "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
        },
        {
          name: "coin_creator_vault_ata",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "coin_creator_vault_authority"
              },
              {
                kind: "account",
                path: "quote_token_program"
              },
              {
                kind: "account",
                path: "quote_mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "coin_creator_vault_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  99,
                  114,
                  101,
                  97,
                  116,
                  111,
                  114,
                  95,
                  118,
                  97,
                  117,
                  108,
                  116
                ]
              },
              {
                kind: "account",
                path: "pool.coin_creator",
                account: "Pool"
              }
            ]
          }
        },
        {
          name: "global_volume_accumulator",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  103,
                  108,
                  111,
                  98,
                  97,
                  108,
                  95,
                  118,
                  111,
                  108,
                  117,
                  109,
                  101,
                  95,
                  97,
                  99,
                  99,
                  117,
                  109,
                  117,
                  108,
                  97,
                  116,
                  111,
                  114
                ]
              }
            ]
          }
        },
        {
          name: "user_volume_accumulator",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  117,
                  115,
                  101,
                  114,
                  95,
                  118,
                  111,
                  108,
                  117,
                  109,
                  101,
                  95,
                  97,
                  99,
                  99,
                  117,
                  109,
                  117,
                  108,
                  97,
                  116,
                  111,
                  114
                ]
              },
              {
                kind: "account",
                path: "user"
              }
            ]
          }
        },
        {
          name: "fee_config",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  102,
                  101,
                  101,
                  95,
                  99,
                  111,
                  110,
                  102,
                  105,
                  103
                ]
              },
              {
                kind: "const",
                value: [
                  12,
                  20,
                  222,
                  252,
                  130,
                  94,
                  198,
                  118,
                  148,
                  37,
                  8,
                  24,
                  187,
                  101,
                  64,
                  101,
                  244,
                  41,
                  141,
                  49,
                  86,
                  213,
                  113,
                  180,
                  212,
                  248,
                  9,
                  12,
                  24,
                  233,
                  168,
                  99
                ]
              }
            ],
            program: {
              kind: "account",
              path: "fee_program"
            }
          }
        },
        {
          name: "fee_program",
          address: "pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ"
        }
      ],
      args: [
        {
          name: "spendable_quote_in",
          type: "u64"
        },
        {
          name: "min_base_amount_out",
          type: "u64"
        },
        {
          name: "track_volume",
          type: {
            defined: {
              name: "OptionBool"
            }
          }
        }
      ]
    },
    {
      name: "buy_exact_quote_in_v2",
      discriminator: [
        194,
        171,
        28,
        70,
        104,
        77,
        91,
        47
      ],
      accounts: [
        {
          name: "pool",
          writable: true
        },
        {
          name: "user",
          writable: true,
          signer: true
        },
        {
          name: "global_config"
        },
        {
          name: "base_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "quote_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "user_base_token_account",
          writable: true
        },
        {
          name: "user_quote_token_account",
          writable: true
        },
        {
          name: "pool_base_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "pool_quote_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "base_token_program"
        },
        {
          name: "quote_token_program"
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "user_volume_accumulator",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  117,
                  115,
                  101,
                  114,
                  95,
                  118,
                  111,
                  108,
                  117,
                  109,
                  101,
                  95,
                  97,
                  99,
                  99,
                  117,
                  109,
                  117,
                  108,
                  97,
                  116,
                  111,
                  114
                ]
              },
              {
                kind: "account",
                path: "user"
              }
            ]
          }
        },
        {
          name: "fee_config",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  102,
                  101,
                  101,
                  95,
                  99,
                  111,
                  110,
                  102,
                  105,
                  103
                ]
              },
              {
                kind: "const",
                value: [
                  12,
                  20,
                  222,
                  252,
                  130,
                  94,
                  198,
                  118,
                  148,
                  37,
                  8,
                  24,
                  187,
                  101,
                  64,
                  101,
                  244,
                  41,
                  141,
                  49,
                  86,
                  213,
                  113,
                  180,
                  212,
                  248,
                  9,
                  12,
                  24,
                  233,
                  168,
                  99
                ]
              }
            ],
            program: {
              kind: "const",
              value: [
                12,
                53,
                255,
                169,
                5,
                90,
                142,
                86,
                141,
                168,
                247,
                188,
                7,
                86,
                21,
                39,
                76,
                241,
                201,
                44,
                164,
                31,
                64,
                0,
                156,
                81,
                106,
                164,
                20,
                194,
                124,
                112
              ]
            }
          }
        },
        {
          name: "buyback_fee_recipient",
          writable: true
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program",
          address: "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
        }
      ],
      args: [
        {
          name: "spendable_quote_in",
          type: "u64"
        },
        {
          name: "min_base_amount_out",
          type: "u64"
        }
      ]
    },
    {
      name: "buy_v2",
      discriminator: [
        184,
        23,
        238,
        97,
        103,
        197,
        211,
        61
      ],
      accounts: [
        {
          name: "pool",
          writable: true
        },
        {
          name: "user",
          writable: true,
          signer: true
        },
        {
          name: "global_config"
        },
        {
          name: "base_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "quote_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "user_base_token_account",
          writable: true
        },
        {
          name: "user_quote_token_account",
          writable: true
        },
        {
          name: "pool_base_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "pool_quote_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "base_token_program"
        },
        {
          name: "quote_token_program"
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "user_volume_accumulator",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  117,
                  115,
                  101,
                  114,
                  95,
                  118,
                  111,
                  108,
                  117,
                  109,
                  101,
                  95,
                  97,
                  99,
                  99,
                  117,
                  109,
                  117,
                  108,
                  97,
                  116,
                  111,
                  114
                ]
              },
              {
                kind: "account",
                path: "user"
              }
            ]
          }
        },
        {
          name: "fee_config",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  102,
                  101,
                  101,
                  95,
                  99,
                  111,
                  110,
                  102,
                  105,
                  103
                ]
              },
              {
                kind: "const",
                value: [
                  12,
                  20,
                  222,
                  252,
                  130,
                  94,
                  198,
                  118,
                  148,
                  37,
                  8,
                  24,
                  187,
                  101,
                  64,
                  101,
                  244,
                  41,
                  141,
                  49,
                  86,
                  213,
                  113,
                  180,
                  212,
                  248,
                  9,
                  12,
                  24,
                  233,
                  168,
                  99
                ]
              }
            ],
            program: {
              kind: "const",
              value: [
                12,
                53,
                255,
                169,
                5,
                90,
                142,
                86,
                141,
                168,
                247,
                188,
                7,
                86,
                21,
                39,
                76,
                241,
                201,
                44,
                164,
                31,
                64,
                0,
                156,
                81,
                106,
                164,
                20,
                194,
                124,
                112
              ]
            }
          }
        },
        {
          name: "buyback_fee_recipient",
          writable: true
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program",
          address: "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
        }
      ],
      args: [
        {
          name: "base_amount_out",
          type: "u64"
        },
        {
          name: "max_quote_amount_in",
          type: "u64"
        }
      ]
    },
    {
      name: "claim_cashback",
      docs: [
        "Pays out the user's accrued cashback. `user_wsol_token_account` may be any token account",
        "of `quote_mint` owned by `user`, not only the associated one."
      ],
      discriminator: [
        37,
        58,
        35,
        126,
        190,
        53,
        228,
        197
      ],
      accounts: [
        {
          name: "user",
          writable: true
        },
        {
          name: "user_volume_accumulator",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  117,
                  115,
                  101,
                  114,
                  95,
                  118,
                  111,
                  108,
                  117,
                  109,
                  101,
                  95,
                  97,
                  99,
                  99,
                  117,
                  109,
                  117,
                  108,
                  97,
                  116,
                  111,
                  114
                ]
              },
              {
                kind: "account",
                path: "user"
              }
            ]
          }
        },
        {
          name: "quote_mint"
        },
        {
          name: "quote_token_program"
        },
        {
          name: "user_volume_accumulator_wsol_token_account",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "user_volume_accumulator"
              },
              {
                kind: "account",
                path: "quote_token_program"
              },
              {
                kind: "account",
                path: "quote_mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "user_wsol_token_account",
          writable: true
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program",
          address: "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
        }
      ],
      args: []
    },
    {
      name: "claim_token_incentives",
      discriminator: [
        16,
        4,
        71,
        28,
        204,
        1,
        40,
        27
      ],
      accounts: [
        {
          name: "user"
        },
        {
          name: "user_ata",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "user"
              },
              {
                kind: "account",
                path: "token_program"
              },
              {
                kind: "account",
                path: "mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "global_volume_accumulator",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  103,
                  108,
                  111,
                  98,
                  97,
                  108,
                  95,
                  118,
                  111,
                  108,
                  117,
                  109,
                  101,
                  95,
                  97,
                  99,
                  99,
                  117,
                  109,
                  117,
                  108,
                  97,
                  116,
                  111,
                  114
                ]
              }
            ]
          }
        },
        {
          name: "global_incentive_token_account",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "global_volume_accumulator"
              },
              {
                kind: "account",
                path: "token_program"
              },
              {
                kind: "account",
                path: "mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "user_volume_accumulator",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  117,
                  115,
                  101,
                  114,
                  95,
                  118,
                  111,
                  108,
                  117,
                  109,
                  101,
                  95,
                  97,
                  99,
                  99,
                  117,
                  109,
                  117,
                  108,
                  97,
                  116,
                  111,
                  114
                ]
              },
              {
                kind: "account",
                path: "user"
              }
            ]
          }
        },
        {
          name: "mint",
          relations: [
            "global_volume_accumulator"
          ]
        },
        {
          name: "token_program"
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "associated_token_program",
          address: "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program",
          address: "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
        },
        {
          name: "payer",
          writable: true,
          signer: true
        }
      ],
      args: []
    },
    {
      name: "close_user_volume_accumulator",
      discriminator: [
        249,
        69,
        164,
        218,
        150,
        103,
        84,
        138
      ],
      accounts: [
        {
          name: "user",
          writable: true,
          signer: true
        },
        {
          name: "user_volume_accumulator",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  117,
                  115,
                  101,
                  114,
                  95,
                  118,
                  111,
                  108,
                  117,
                  109,
                  101,
                  95,
                  97,
                  99,
                  99,
                  117,
                  109,
                  117,
                  108,
                  97,
                  116,
                  111,
                  114
                ]
              },
              {
                kind: "account",
                path: "user"
              }
            ]
          }
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: []
    },
    {
      name: "collect_coin_creator_fee",
      discriminator: [
        160,
        57,
        89,
        42,
        181,
        139,
        43,
        66
      ],
      accounts: [
        {
          name: "quote_mint"
        },
        {
          name: "quote_token_program"
        },
        {
          name: "coin_creator"
        },
        {
          name: "coin_creator_vault_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  99,
                  114,
                  101,
                  97,
                  116,
                  111,
                  114,
                  95,
                  118,
                  97,
                  117,
                  108,
                  116
                ]
              },
              {
                kind: "account",
                path: "coin_creator"
              }
            ]
          }
        },
        {
          name: "coin_creator_vault_ata",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "coin_creator_vault_authority"
              },
              {
                kind: "account",
                path: "quote_token_program"
              },
              {
                kind: "account",
                path: "quote_mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "coin_creator_token_account",
          writable: true
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: []
    },
    {
      name: "create_config",
      discriminator: [
        201,
        207,
        243,
        114,
        75,
        111,
        47,
        189
      ],
      accounts: [
        {
          name: "admin",
          writable: true,
          signer: true,
          address: "8LWu7QM2dGR1G8nKDHthckea57bkCzXyBTAKPJUBDHo8"
        },
        {
          name: "global_config",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  103,
                  108,
                  111,
                  98,
                  97,
                  108,
                  95,
                  99,
                  111,
                  110,
                  102,
                  105,
                  103
                ]
              }
            ]
          }
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: [
        {
          name: "lp_fee_basis_points",
          type: "u64"
        },
        {
          name: "protocol_fee_basis_points",
          type: "u64"
        },
        {
          name: "protocol_fee_recipients",
          type: {
            array: [
              "pubkey",
              8
            ]
          }
        },
        {
          name: "coin_creator_fee_basis_points",
          type: "u64"
        },
        {
          name: "admin_set_coin_creator_authority",
          type: "pubkey"
        }
      ]
    },
    {
      name: "create_pool",
      discriminator: [
        233,
        146,
        209,
        142,
        207,
        104,
        64,
        188
      ],
      accounts: [
        {
          name: "pool",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  112,
                  111,
                  111,
                  108
                ]
              },
              {
                kind: "arg",
                path: "index"
              },
              {
                kind: "account",
                path: "creator"
              },
              {
                kind: "account",
                path: "base_mint"
              },
              {
                kind: "account",
                path: "quote_mint"
              }
            ]
          }
        },
        {
          name: "global_config"
        },
        {
          name: "creator",
          writable: true,
          signer: true
        },
        {
          name: "base_mint"
        },
        {
          name: "quote_mint"
        },
        {
          name: "lp_mint",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  112,
                  111,
                  111,
                  108,
                  95,
                  108,
                  112,
                  95,
                  109,
                  105,
                  110,
                  116
                ]
              },
              {
                kind: "account",
                path: "pool"
              }
            ]
          }
        },
        {
          name: "user_base_token_account",
          writable: true
        },
        {
          name: "user_quote_token_account",
          writable: true
        },
        {
          name: "user_pool_token_account",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "creator"
              },
              {
                kind: "account",
                path: "token_2022_program"
              },
              {
                kind: "account",
                path: "lp_mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "pool_base_token_account",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "pool"
              },
              {
                kind: "account",
                path: "base_token_program"
              },
              {
                kind: "account",
                path: "base_mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "pool_quote_token_account",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "pool"
              },
              {
                kind: "account",
                path: "quote_token_program"
              },
              {
                kind: "account",
                path: "quote_mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "token_2022_program",
          address: "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
        },
        {
          name: "base_token_program"
        },
        {
          name: "quote_token_program"
        },
        {
          name: "associated_token_program",
          address: "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: [
        {
          name: "index",
          type: "u16"
        },
        {
          name: "base_amount_in",
          type: "u64"
        },
        {
          name: "quote_amount_in",
          type: "u64"
        },
        {
          name: "coin_creator",
          type: "pubkey"
        },
        {
          name: "is_mayhem_mode",
          type: "bool"
        },
        {
          name: "is_cashback_coin",
          type: {
            defined: {
              name: "OptionBool"
            }
          }
        },
        {
          name: "creator_fee_bps",
          type: {
            defined: {
              name: "OptionU64"
            }
          }
        },
        {
          name: "can_edit_creator_fee",
          type: {
            defined: {
              name: "OptionBool"
            }
          }
        },
        {
          name: "is_holder_reward",
          type: {
            defined: {
              name: "OptionBool"
            }
          }
        }
      ]
    },
    {
      name: "deposit",
      discriminator: [
        242,
        35,
        198,
        137,
        82,
        225,
        242,
        182
      ],
      accounts: [
        {
          name: "pool",
          writable: true
        },
        {
          name: "global_config"
        },
        {
          name: "user",
          signer: true
        },
        {
          name: "base_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "quote_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "lp_mint",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "user_base_token_account",
          writable: true
        },
        {
          name: "user_quote_token_account",
          writable: true
        },
        {
          name: "user_pool_token_account",
          writable: true
        },
        {
          name: "pool_base_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "pool_quote_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "token_program",
          address: "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
        },
        {
          name: "token_2022_program",
          address: "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: [
        {
          name: "lp_token_amount_out",
          type: "u64"
        },
        {
          name: "max_base_amount_in",
          type: "u64"
        },
        {
          name: "max_quote_amount_in",
          type: "u64"
        }
      ]
    },
    {
      name: "disable",
      discriminator: [
        185,
        173,
        187,
        90,
        216,
        15,
        238,
        233
      ],
      accounts: [
        {
          name: "admin",
          signer: true,
          relations: [
            "global_config"
          ]
        },
        {
          name: "global_config",
          writable: true
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: [
        {
          name: "disable_create_pool",
          type: "bool"
        },
        {
          name: "disable_deposit",
          type: "bool"
        },
        {
          name: "disable_withdraw",
          type: "bool"
        },
        {
          name: "disable_buy",
          type: "bool"
        },
        {
          name: "disable_sell",
          type: "bool"
        }
      ]
    },
    {
      name: "extend_account",
      discriminator: [
        234,
        102,
        194,
        203,
        150,
        72,
        62,
        229
      ],
      accounts: [
        {
          name: "account",
          writable: true
        },
        {
          name: "user",
          writable: true,
          signer: true
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: []
    },
    {
      name: "init_boost",
      discriminator: [
        140,
        233,
        33,
        94,
        132,
        90,
        194,
        143
      ],
      accounts: [
        {
          name: "pool",
          writable: true
        },
        {
          name: "global_config",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  103,
                  108,
                  111,
                  98,
                  97,
                  108,
                  95,
                  99,
                  111,
                  110,
                  102,
                  105,
                  103
                ]
              }
            ]
          }
        },
        {
          name: "creator",
          writable: true,
          signer: true
        },
        {
          name: "base_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "quote_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "pool_base_token_account",
          relations: [
            "pool"
          ]
        },
        {
          name: "pool_quote_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "boost_vault_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  98,
                  111,
                  111,
                  115,
                  116,
                  95,
                  118,
                  97,
                  117,
                  108,
                  116
                ]
              },
              {
                kind: "account",
                path: "pool"
              }
            ]
          }
        },
        {
          name: "boost_vault",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "boost_vault_authority"
              },
              {
                kind: "account",
                path: "quote_token_program"
              },
              {
                kind: "account",
                path: "quote_mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "quote_token_program"
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "associated_token_program",
          address: "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: []
    },
    {
      name: "init_user_volume_accumulator",
      discriminator: [
        94,
        6,
        202,
        115,
        255,
        96,
        232,
        183
      ],
      accounts: [
        {
          name: "payer",
          writable: true,
          signer: true
        },
        {
          name: "user"
        },
        {
          name: "user_volume_accumulator",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  117,
                  115,
                  101,
                  114,
                  95,
                  118,
                  111,
                  108,
                  117,
                  109,
                  101,
                  95,
                  97,
                  99,
                  99,
                  117,
                  109,
                  117,
                  108,
                  97,
                  116,
                  111,
                  114
                ]
              },
              {
                kind: "account",
                path: "user"
              }
            ]
          }
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: []
    },
    {
      name: "migrate_pool_coin_creator",
      docs: [
        "Migrate Pool Coin Creator to Sharing Config"
      ],
      discriminator: [
        208,
        8,
        159,
        4,
        74,
        175,
        16,
        58
      ],
      accounts: [
        {
          name: "pool",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  112,
                  111,
                  111,
                  108
                ]
              },
              {
                kind: "account",
                path: "pool.index",
                account: "Pool"
              },
              {
                kind: "account",
                path: "pool.creator",
                account: "Pool"
              },
              {
                kind: "account",
                path: "pool.base_mint",
                account: "Pool"
              },
              {
                kind: "account",
                path: "pool.quote_mint",
                account: "Pool"
              }
            ]
          }
        },
        {
          name: "sharing_config",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  115,
                  104,
                  97,
                  114,
                  105,
                  110,
                  103,
                  45,
                  99,
                  111,
                  110,
                  102,
                  105,
                  103
                ]
              },
              {
                kind: "account",
                path: "pool.base_mint",
                account: "Pool"
              }
            ],
            program: {
              kind: "const",
              value: [
                12,
                53,
                255,
                169,
                5,
                90,
                142,
                86,
                141,
                168,
                247,
                188,
                7,
                86,
                21,
                39,
                76,
                241,
                201,
                44,
                164,
                31,
                64,
                0,
                156,
                81,
                106,
                164,
                20,
                194,
                124,
                112
              ]
            }
          }
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: []
    },
    {
      name: "multi_hop_swap",
      discriminator: [
        43,
        100,
        73,
        19,
        233,
        246,
        111,
        148
      ],
      accounts: [
        {
          name: "user",
          writable: true,
          signer: true
        },
        {
          name: "user_in_token_account",
          writable: true
        },
        {
          name: "user_out_token_account",
          writable: true
        },
        {
          name: "global_config",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  103,
                  108,
                  111,
                  98,
                  97,
                  108,
                  95,
                  99,
                  111,
                  110,
                  102,
                  105,
                  103
                ]
              }
            ]
          }
        },
        {
          name: "fee_config",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  102,
                  101,
                  101,
                  95,
                  99,
                  111,
                  110,
                  102,
                  105,
                  103
                ]
              },
              {
                kind: "const",
                value: [
                  12,
                  20,
                  222,
                  252,
                  130,
                  94,
                  198,
                  118,
                  148,
                  37,
                  8,
                  24,
                  187,
                  101,
                  64,
                  101,
                  244,
                  41,
                  141,
                  49,
                  86,
                  213,
                  113,
                  180,
                  212,
                  248,
                  9,
                  12,
                  24,
                  233,
                  168,
                  99
                ]
              }
            ],
            program: {
              kind: "const",
              value: [
                12,
                53,
                255,
                169,
                5,
                90,
                142,
                86,
                141,
                168,
                247,
                188,
                7,
                86,
                21,
                39,
                76,
                241,
                201,
                44,
                164,
                31,
                64,
                0,
                156,
                81,
                106,
                164,
                20,
                194,
                124,
                112
              ]
            }
          }
        },
        {
          name: "user_volume_accumulator",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  117,
                  115,
                  101,
                  114,
                  95,
                  118,
                  111,
                  108,
                  117,
                  109,
                  101,
                  95,
                  97,
                  99,
                  99,
                  117,
                  109,
                  117,
                  108,
                  97,
                  116,
                  111,
                  114
                ]
              },
              {
                kind: "account",
                path: "user"
              }
            ]
          }
        },
        {
          name: "buyback_fee_recipient",
          writable: true
        },
        {
          name: "token_program",
          address: "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
        },
        {
          name: "token_2022_program",
          address: "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program",
          address: "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
        },
        {
          name: "pump_program",
          address: "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
        },
        {
          name: "pump_global"
        },
        {
          name: "pump_fee_config"
        },
        {
          name: "pump_event_authority"
        }
      ],
      args: [
        {
          name: "amount_in",
          type: "u64"
        },
        {
          name: "min_amount_out",
          type: "u64"
        }
      ]
    },
    {
      name: "sell",
      discriminator: [
        51,
        230,
        133,
        164,
        1,
        127,
        131,
        173
      ],
      accounts: [
        {
          name: "pool",
          writable: true
        },
        {
          name: "user",
          writable: true,
          signer: true
        },
        {
          name: "global_config"
        },
        {
          name: "base_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "quote_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "user_base_token_account",
          writable: true
        },
        {
          name: "user_quote_token_account",
          writable: true
        },
        {
          name: "pool_base_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "pool_quote_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "protocol_fee_recipient"
        },
        {
          name: "protocol_fee_recipient_token_account",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "protocol_fee_recipient"
              },
              {
                kind: "account",
                path: "quote_token_program"
              },
              {
                kind: "account",
                path: "quote_mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "base_token_program"
        },
        {
          name: "quote_token_program"
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "associated_token_program",
          address: "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program",
          address: "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
        },
        {
          name: "coin_creator_vault_ata",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "coin_creator_vault_authority"
              },
              {
                kind: "account",
                path: "quote_token_program"
              },
              {
                kind: "account",
                path: "quote_mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "coin_creator_vault_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  99,
                  114,
                  101,
                  97,
                  116,
                  111,
                  114,
                  95,
                  118,
                  97,
                  117,
                  108,
                  116
                ]
              },
              {
                kind: "account",
                path: "pool.coin_creator",
                account: "Pool"
              }
            ]
          }
        },
        {
          name: "fee_config",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  102,
                  101,
                  101,
                  95,
                  99,
                  111,
                  110,
                  102,
                  105,
                  103
                ]
              },
              {
                kind: "const",
                value: [
                  12,
                  20,
                  222,
                  252,
                  130,
                  94,
                  198,
                  118,
                  148,
                  37,
                  8,
                  24,
                  187,
                  101,
                  64,
                  101,
                  244,
                  41,
                  141,
                  49,
                  86,
                  213,
                  113,
                  180,
                  212,
                  248,
                  9,
                  12,
                  24,
                  233,
                  168,
                  99
                ]
              }
            ],
            program: {
              kind: "account",
              path: "fee_program"
            }
          }
        },
        {
          name: "fee_program",
          address: "pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ"
        }
      ],
      args: [
        {
          name: "base_amount_in",
          type: "u64"
        },
        {
          name: "min_quote_amount_out",
          type: "u64"
        }
      ]
    },
    {
      name: "sell_v2",
      discriminator: [
        93,
        246,
        130,
        60,
        231,
        233,
        64,
        178
      ],
      accounts: [
        {
          name: "pool",
          writable: true
        },
        {
          name: "user",
          writable: true,
          signer: true
        },
        {
          name: "global_config"
        },
        {
          name: "base_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "quote_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "user_base_token_account",
          writable: true
        },
        {
          name: "user_quote_token_account",
          writable: true
        },
        {
          name: "pool_base_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "pool_quote_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "base_token_program"
        },
        {
          name: "quote_token_program"
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "user_volume_accumulator",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  117,
                  115,
                  101,
                  114,
                  95,
                  118,
                  111,
                  108,
                  117,
                  109,
                  101,
                  95,
                  97,
                  99,
                  99,
                  117,
                  109,
                  117,
                  108,
                  97,
                  116,
                  111,
                  114
                ]
              },
              {
                kind: "account",
                path: "user"
              }
            ]
          }
        },
        {
          name: "fee_config",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  102,
                  101,
                  101,
                  95,
                  99,
                  111,
                  110,
                  102,
                  105,
                  103
                ]
              },
              {
                kind: "const",
                value: [
                  12,
                  20,
                  222,
                  252,
                  130,
                  94,
                  198,
                  118,
                  148,
                  37,
                  8,
                  24,
                  187,
                  101,
                  64,
                  101,
                  244,
                  41,
                  141,
                  49,
                  86,
                  213,
                  113,
                  180,
                  212,
                  248,
                  9,
                  12,
                  24,
                  233,
                  168,
                  99
                ]
              }
            ],
            program: {
              kind: "const",
              value: [
                12,
                53,
                255,
                169,
                5,
                90,
                142,
                86,
                141,
                168,
                247,
                188,
                7,
                86,
                21,
                39,
                76,
                241,
                201,
                44,
                164,
                31,
                64,
                0,
                156,
                81,
                106,
                164,
                20,
                194,
                124,
                112
              ]
            }
          }
        },
        {
          name: "buyback_fee_recipient",
          writable: true
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program",
          address: "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
        }
      ],
      args: [
        {
          name: "base_amount_in",
          type: "u64"
        },
        {
          name: "min_quote_amount_out",
          type: "u64"
        }
      ]
    },
    {
      name: "set_boost_authority",
      discriminator: [
        227,
        149,
        76,
        42,
        130,
        39,
        234,
        205
      ],
      accounts: [
        {
          name: "admin",
          signer: true,
          relations: [
            "global_config"
          ]
        },
        {
          name: "global_config",
          writable: true
        },
        {
          name: "boost_authority"
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: []
    },
    {
      name: "set_coin_creator",
      docs: [
        "Sets Pool::coin_creator from Metaplex metadata creator or BondingCurve::creator"
      ],
      discriminator: [
        210,
        149,
        128,
        45,
        188,
        58,
        78,
        175
      ],
      accounts: [
        {
          name: "pool",
          writable: true
        },
        {
          name: "metadata",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  109,
                  101,
                  116,
                  97,
                  100,
                  97,
                  116,
                  97
                ]
              },
              {
                kind: "const",
                value: [
                  11,
                  112,
                  101,
                  177,
                  227,
                  209,
                  124,
                  69,
                  56,
                  157,
                  82,
                  127,
                  107,
                  4,
                  195,
                  205,
                  88,
                  184,
                  108,
                  115,
                  26,
                  160,
                  253,
                  181,
                  73,
                  182,
                  209,
                  188,
                  3,
                  248,
                  41,
                  70
                ]
              },
              {
                kind: "account",
                path: "pool.base_mint",
                account: "Pool"
              }
            ],
            program: {
              kind: "const",
              value: [
                11,
                112,
                101,
                177,
                227,
                209,
                124,
                69,
                56,
                157,
                82,
                127,
                107,
                4,
                195,
                205,
                88,
                184,
                108,
                115,
                26,
                160,
                253,
                181,
                73,
                182,
                209,
                188,
                3,
                248,
                41,
                70
              ]
            }
          }
        },
        {
          name: "bonding_curve",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  98,
                  111,
                  110,
                  100,
                  105,
                  110,
                  103,
                  45,
                  99,
                  117,
                  114,
                  118,
                  101
                ]
              },
              {
                kind: "account",
                path: "pool.base_mint",
                account: "Pool"
              }
            ],
            program: {
              kind: "const",
              value: [
                1,
                86,
                224,
                246,
                147,
                102,
                90,
                207,
                68,
                219,
                21,
                104,
                191,
                23,
                91,
                170,
                81,
                137,
                203,
                151,
                245,
                210,
                255,
                59,
                101,
                93,
                43,
                182,
                253,
                109,
                24,
                176
              ]
            }
          }
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: []
    },
    {
      name: "set_reserved_fee_recipients",
      discriminator: [
        111,
        172,
        162,
        232,
        114,
        89,
        213,
        142
      ],
      accounts: [
        {
          name: "global_config",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  103,
                  108,
                  111,
                  98,
                  97,
                  108,
                  95,
                  99,
                  111,
                  110,
                  102,
                  105,
                  103
                ]
              }
            ]
          }
        },
        {
          name: "admin",
          signer: true,
          relations: [
            "global_config"
          ]
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: [
        {
          name: "whitelist_pda",
          type: "pubkey"
        }
      ]
    },
    {
      name: "sweep_creator_fee",
      discriminator: [
        32,
        246,
        191,
        52,
        8,
        201,
        73,
        186
      ],
      accounts: [
        {
          name: "payer",
          writable: true,
          signer: true
        },
        {
          name: "global_config"
        },
        {
          name: "pool",
          writable: true
        },
        {
          name: "quote_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "quote_token_program"
        },
        {
          name: "pool_quote_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "recipient",
          docs: [
            "protocol fee recipient (`check_protocol_fee_recipient`) or the coin-creator vault",
            "authority PDA of `pool.coin_creator`."
          ]
        },
        {
          name: "recipient_token_account",
          docs: [
            "idempotently when missing (the payer pays)."
          ],
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "recipient"
              },
              {
                kind: "account",
                path: "quote_token_program"
              },
              {
                kind: "account",
                path: "quote_mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "associated_token_program",
          address: "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: []
    },
    {
      name: "sweep_protocol_fee",
      discriminator: [
        8,
        48,
        190,
        7,
        182,
        68,
        183,
        229
      ],
      accounts: [
        {
          name: "payer",
          writable: true,
          signer: true
        },
        {
          name: "global_config"
        },
        {
          name: "pool",
          writable: true
        },
        {
          name: "quote_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "quote_token_program"
        },
        {
          name: "pool_quote_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "recipient",
          docs: [
            "protocol fee recipient (`check_protocol_fee_recipient`) or the coin-creator vault",
            "authority PDA of `pool.coin_creator`."
          ]
        },
        {
          name: "recipient_token_account",
          docs: [
            "idempotently when missing (the payer pays)."
          ],
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "recipient"
              },
              {
                kind: "account",
                path: "quote_token_program"
              },
              {
                kind: "account",
                path: "quote_mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "associated_token_program",
          address: "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: []
    },
    {
      name: "sync_user_volume_accumulator",
      discriminator: [
        86,
        31,
        192,
        87,
        163,
        87,
        79,
        238
      ],
      accounts: [
        {
          name: "user"
        },
        {
          name: "global_volume_accumulator",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  103,
                  108,
                  111,
                  98,
                  97,
                  108,
                  95,
                  118,
                  111,
                  108,
                  117,
                  109,
                  101,
                  95,
                  97,
                  99,
                  99,
                  117,
                  109,
                  117,
                  108,
                  97,
                  116,
                  111,
                  114
                ]
              }
            ]
          }
        },
        {
          name: "user_volume_accumulator",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  117,
                  115,
                  101,
                  114,
                  95,
                  118,
                  111,
                  108,
                  117,
                  109,
                  101,
                  95,
                  97,
                  99,
                  99,
                  117,
                  109,
                  117,
                  108,
                  97,
                  116,
                  111,
                  114
                ]
              },
              {
                kind: "account",
                path: "user"
              }
            ]
          }
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: []
    },
    {
      name: "toggle_boost",
      discriminator: [
        117,
        161,
        160,
        74,
        223,
        137,
        118,
        99
      ],
      accounts: [
        {
          name: "admin",
          signer: true,
          relations: [
            "global_config"
          ]
        },
        {
          name: "global_config",
          writable: true
        }
      ],
      args: [
        {
          name: "enabled",
          type: "bool"
        }
      ]
    },
    {
      name: "toggle_cashback_enabled",
      discriminator: [
        115,
        103,
        224,
        255,
        189,
        89,
        86,
        195
      ],
      accounts: [
        {
          name: "admin",
          signer: true,
          relations: [
            "global_config"
          ]
        },
        {
          name: "global_config",
          writable: true
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: [
        {
          name: "enabled",
          type: "bool"
        }
      ]
    },
    {
      name: "toggle_mayhem_mode",
      discriminator: [
        1,
        9,
        111,
        208,
        100,
        31,
        255,
        163
      ],
      accounts: [
        {
          name: "admin",
          signer: true,
          relations: [
            "global_config"
          ]
        },
        {
          name: "global_config",
          writable: true
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: [
        {
          name: "enabled",
          type: "bool"
        }
      ]
    },
    {
      name: "transfer_creator_fees_to_pump",
      docs: [
        "Transfer creator fees to pump creator vault",
        "If coin creator fees are currently below rent.minimum_balance(TokenAccount::LEN)",
        "The transfer will be skipped"
      ],
      discriminator: [
        139,
        52,
        134,
        85,
        228,
        229,
        108,
        241
      ],
      accounts: [
        {
          name: "wsol_mint",
          docs: [
            "Pump Canonical Pool are quoted in wSOL"
          ]
        },
        {
          name: "token_program"
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "associated_token_program",
          address: "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
        },
        {
          name: "coin_creator"
        },
        {
          name: "coin_creator_vault_authority",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  99,
                  114,
                  101,
                  97,
                  116,
                  111,
                  114,
                  95,
                  118,
                  97,
                  117,
                  108,
                  116
                ]
              },
              {
                kind: "account",
                path: "coin_creator"
              }
            ]
          }
        },
        {
          name: "coin_creator_vault_ata",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "coin_creator_vault_authority"
              },
              {
                kind: "account",
                path: "token_program"
              },
              {
                kind: "account",
                path: "wsol_mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "pump_creator_vault",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  99,
                  114,
                  101,
                  97,
                  116,
                  111,
                  114,
                  45,
                  118,
                  97,
                  117,
                  108,
                  116
                ]
              },
              {
                kind: "account",
                path: "coin_creator"
              }
            ],
            program: {
              kind: "const",
              value: [
                1,
                86,
                224,
                246,
                147,
                102,
                90,
                207,
                68,
                219,
                21,
                104,
                191,
                23,
                91,
                170,
                81,
                137,
                203,
                151,
                245,
                210,
                255,
                59,
                101,
                93,
                43,
                182,
                253,
                109,
                24,
                176
              ]
            }
          }
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: []
    },
    {
      name: "transfer_creator_fees_to_pump_v2",
      discriminator: [
        1,
        33,
        78,
        185,
        33,
        67,
        44,
        92
      ],
      accounts: [
        {
          name: "payer",
          writable: true,
          signer: true
        },
        {
          name: "quote_mint"
        },
        {
          name: "token_program"
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "associated_token_program",
          address: "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
        },
        {
          name: "coin_creator"
        },
        {
          name: "coin_creator_vault_authority",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  99,
                  114,
                  101,
                  97,
                  116,
                  111,
                  114,
                  95,
                  118,
                  97,
                  117,
                  108,
                  116
                ]
              },
              {
                kind: "account",
                path: "coin_creator"
              }
            ]
          }
        },
        {
          name: "coin_creator_vault_ata",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "coin_creator_vault_authority"
              },
              {
                kind: "account",
                path: "token_program"
              },
              {
                kind: "account",
                path: "quote_mint"
              }
            ],
            program: {
              kind: "const",
              value: [
                140,
                151,
                37,
                143,
                78,
                36,
                137,
                241,
                187,
                61,
                16,
                41,
                20,
                142,
                13,
                131,
                11,
                90,
                19,
                153,
                218,
                255,
                16,
                132,
                4,
                142,
                123,
                216,
                219,
                233,
                248,
                89
              ]
            }
          }
        },
        {
          name: "pump_creator_vault",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  99,
                  114,
                  101,
                  97,
                  116,
                  111,
                  114,
                  45,
                  118,
                  97,
                  117,
                  108,
                  116
                ]
              },
              {
                kind: "account",
                path: "coin_creator"
              }
            ],
            program: {
              kind: "const",
              value: [
                1,
                86,
                224,
                246,
                147,
                102,
                90,
                207,
                68,
                219,
                21,
                104,
                191,
                23,
                91,
                170,
                81,
                137,
                203,
                151,
                245,
                210,
                255,
                59,
                101,
                93,
                43,
                182,
                253,
                109,
                24,
                176
              ]
            }
          }
        },
        {
          name: "pump_creator_vault_ata",
          writable: true,
          pda: {
            seeds: [
              {
                kind: "account",
                path: "pump_creator_vault"
              },
              {
                kind: "account",
                path: "token_program"
              },
              {
                kind: "account",
                path: "quote_mint"
              }
            ],
            program: {
              kind: "account",
              path: "associated_token_program"
            }
          }
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: []
    },
    {
      name: "update_admin",
      discriminator: [
        161,
        176,
        40,
        213,
        60,
        184,
        179,
        228
      ],
      accounts: [
        {
          name: "admin",
          signer: true,
          relations: [
            "global_config"
          ]
        },
        {
          name: "global_config",
          writable: true
        },
        {
          name: "new_admin"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: []
    },
    {
      name: "update_buyback_config",
      discriminator: [
        251,
        224,
        171,
        146,
        160,
        26,
        113,
        233
      ],
      accounts: [
        {
          name: "admin",
          signer: true,
          relations: [
            "global_config"
          ]
        },
        {
          name: "global_config",
          writable: true
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: [
        {
          name: "buyback_basis_points",
          type: {
            option: "u64"
          }
        }
      ]
    },
    {
      name: "update_creator_fee_config",
      discriminator: [
        61,
        175,
        160,
        249,
        66,
        66,
        136,
        175
      ],
      accounts: [
        {
          name: "admin",
          writable: true,
          signer: true,
          relations: [
            "global_config"
          ]
        },
        {
          name: "global_config",
          writable: true
        },
        {
          name: "system_program",
          address: "11111111111111111111111111111111"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: [
        {
          name: "creator_fee_configurable",
          type: "bool"
        },
        {
          name: "max_configurable_creator_fee_bps",
          type: "u64"
        }
      ]
    },
    {
      name: "update_fee_config",
      discriminator: [
        104,
        184,
        103,
        242,
        88,
        151,
        107,
        20
      ],
      accounts: [
        {
          name: "admin",
          signer: true,
          relations: [
            "global_config"
          ]
        },
        {
          name: "global_config",
          writable: true
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: [
        {
          name: "lp_fee_basis_points",
          type: "u64"
        },
        {
          name: "protocol_fee_basis_points",
          type: "u64"
        },
        {
          name: "protocol_fee_recipients",
          type: {
            array: [
              "pubkey",
              8
            ]
          }
        },
        {
          name: "coin_creator_fee_basis_points",
          type: "u64"
        },
        {
          name: "admin_set_coin_creator_authority",
          type: "pubkey"
        }
      ]
    },
    {
      name: "withdraw",
      discriminator: [
        183,
        18,
        70,
        156,
        148,
        109,
        161,
        34
      ],
      accounts: [
        {
          name: "pool",
          writable: true
        },
        {
          name: "global_config"
        },
        {
          name: "user",
          signer: true
        },
        {
          name: "base_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "quote_mint",
          relations: [
            "pool"
          ]
        },
        {
          name: "lp_mint",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "user_base_token_account",
          writable: true
        },
        {
          name: "user_quote_token_account",
          writable: true
        },
        {
          name: "user_pool_token_account",
          writable: true
        },
        {
          name: "pool_base_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "pool_quote_token_account",
          writable: true,
          relations: [
            "pool"
          ]
        },
        {
          name: "token_program",
          address: "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
        },
        {
          name: "token_2022_program",
          address: "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
        },
        {
          name: "event_authority",
          pda: {
            seeds: [
              {
                kind: "const",
                value: [
                  95,
                  95,
                  101,
                  118,
                  101,
                  110,
                  116,
                  95,
                  97,
                  117,
                  116,
                  104,
                  111,
                  114,
                  105,
                  116,
                  121
                ]
              }
            ]
          }
        },
        {
          name: "program"
        }
      ],
      args: [
        {
          name: "lp_token_amount_in",
          type: "u64"
        },
        {
          name: "min_base_amount_out",
          type: "u64"
        },
        {
          name: "min_quote_amount_out",
          type: "u64"
        }
      ]
    }
  ],
  accounts: [
    {
      name: "BondingCurve",
      discriminator: [
        23,
        183,
        248,
        55,
        96,
        216,
        172,
        96
      ]
    },
    {
      name: "FeeConfig",
      discriminator: [
        143,
        52,
        146,
        187,
        219,
        123,
        76,
        155
      ]
    },
    {
      name: "GlobalConfig",
      discriminator: [
        149,
        8,
        156,
        202,
        160,
        252,
        176,
        217
      ]
    },
    {
      name: "GlobalVolumeAccumulator",
      discriminator: [
        202,
        42,
        246,
        43,
        142,
        190,
        30,
        255
      ]
    },
    {
      name: "Pool",
      discriminator: [
        241,
        154,
        109,
        4,
        17,
        177,
        109,
        188
      ]
    },
    {
      name: "SharingConfig",
      discriminator: [
        216,
        74,
        9,
        0,
        56,
        140,
        93,
        75
      ]
    },
    {
      name: "UserVolumeAccumulator",
      discriminator: [
        86,
        255,
        112,
        14,
        102,
        53,
        154,
        250
      ]
    }
  ],
  events: [
    {
      name: "AdminCtoPoolEvent",
      discriminator: [
        47,
        35,
        163,
        249,
        150,
        157,
        147,
        122
      ]
    },
    {
      name: "AdminUpdateTokenIncentivesEvent",
      discriminator: [
        147,
        250,
        108,
        120,
        247,
        29,
        67,
        222
      ]
    },
    {
      name: "BoostBuyAndBurnEvent",
      discriminator: [
        63,
        69,
        28,
        22,
        48,
        92,
        194,
        185
      ]
    },
    {
      name: "BuyEvent",
      discriminator: [
        103,
        244,
        82,
        31,
        44,
        245,
        119,
        119
      ]
    },
    {
      name: "ClaimCashbackEvent",
      discriminator: [
        226,
        214,
        246,
        33,
        7,
        242,
        147,
        229
      ]
    },
    {
      name: "ClaimTokenIncentivesEvent",
      discriminator: [
        79,
        172,
        246,
        49,
        205,
        91,
        206,
        232
      ]
    },
    {
      name: "CloseUserVolumeAccumulatorEvent",
      discriminator: [
        146,
        159,
        189,
        172,
        146,
        88,
        56,
        244
      ]
    },
    {
      name: "CollectCoinCreatorFeeEvent",
      discriminator: [
        232,
        245,
        194,
        238,
        234,
        218,
        58,
        89
      ]
    },
    {
      name: "CreateConfigEvent",
      discriminator: [
        107,
        52,
        89,
        129,
        55,
        226,
        81,
        22
      ]
    },
    {
      name: "CreatePoolEvent",
      discriminator: [
        177,
        49,
        12,
        210,
        160,
        118,
        167,
        116
      ]
    },
    {
      name: "DepositEvent",
      discriminator: [
        120,
        248,
        61,
        83,
        31,
        142,
        107,
        144
      ]
    },
    {
      name: "DisableEvent",
      discriminator: [
        107,
        253,
        193,
        76,
        228,
        202,
        27,
        104
      ]
    },
    {
      name: "ExtendAccountEvent",
      discriminator: [
        97,
        97,
        215,
        144,
        93,
        146,
        22,
        124
      ]
    },
    {
      name: "InitBoostEvent",
      discriminator: [
        174,
        124,
        74,
        249,
        4,
        81,
        246,
        17
      ]
    },
    {
      name: "InitUserVolumeAccumulatorEvent",
      discriminator: [
        134,
        36,
        13,
        72,
        232,
        101,
        130,
        216
      ]
    },
    {
      name: "MigratePoolCoinCreatorEvent",
      discriminator: [
        170,
        221,
        82,
        199,
        147,
        165,
        247,
        46
      ]
    },
    {
      name: "ReservedFeeRecipientsEvent",
      discriminator: [
        43,
        188,
        250,
        18,
        221,
        75,
        187,
        95
      ]
    },
    {
      name: "SellEvent",
      discriminator: [
        62,
        47,
        55,
        10,
        165,
        3,
        220,
        42
      ]
    },
    {
      name: "SetBondingCurveCoinCreatorEvent",
      discriminator: [
        242,
        231,
        235,
        102,
        65,
        99,
        189,
        211
      ]
    },
    {
      name: "SetBoostAuthorityEvent",
      discriminator: [
        89,
        128,
        240,
        141,
        91,
        202,
        71,
        105
      ]
    },
    {
      name: "SetMetaplexCoinCreatorEvent",
      discriminator: [
        150,
        107,
        199,
        123,
        124,
        207,
        102,
        228
      ]
    },
    {
      name: "SweepPoolFeeEvent",
      discriminator: [
        130,
        164,
        36,
        97,
        228,
        130,
        135,
        165
      ]
    },
    {
      name: "SyncUserVolumeAccumulatorEvent",
      discriminator: [
        197,
        122,
        167,
        124,
        116,
        81,
        91,
        255
      ]
    },
    {
      name: "UpdateAdminEvent",
      discriminator: [
        225,
        152,
        171,
        87,
        246,
        63,
        66,
        234
      ]
    },
    {
      name: "UpdateCreatorFeeConfigEvent",
      discriminator: [
        152,
        198,
        124,
        124,
        106,
        246,
        127,
        191
      ]
    },
    {
      name: "UpdateFeeConfigEvent",
      discriminator: [
        90,
        23,
        65,
        35,
        62,
        244,
        188,
        208
      ]
    },
    {
      name: "WithdrawEvent",
      discriminator: [
        22,
        9,
        133,
        26,
        160,
        44,
        71,
        192
      ]
    }
  ],
  errors: [
    {
      code: 6e3,
      name: "FeeBasisPointsExceedsMaximum"
    },
    {
      code: 6001,
      name: "ZeroBaseAmount"
    },
    {
      code: 6002,
      name: "ZeroQuoteAmount"
    },
    {
      code: 6003,
      name: "TooLittlePoolTokenLiquidity"
    },
    {
      code: 6004,
      name: "ExceededSlippage"
    },
    {
      code: 6005,
      name: "InvalidAdmin"
    },
    {
      code: 6006,
      name: "UnsupportedBaseMint"
    },
    {
      code: 6007,
      name: "UnsupportedQuoteMint"
    },
    {
      code: 6008,
      name: "InvalidBaseMint"
    },
    {
      code: 6009,
      name: "InvalidQuoteMint"
    },
    {
      code: 6010,
      name: "InvalidLpMint"
    },
    {
      code: 6011,
      name: "AllProtocolFeeRecipientsShouldBeNonZero"
    },
    {
      code: 6012,
      name: "UnsortedNotUniqueProtocolFeeRecipients"
    },
    {
      code: 6013,
      name: "InvalidProtocolFeeRecipient"
    },
    {
      code: 6014,
      name: "InvalidPoolBaseTokenAccount"
    },
    {
      code: 6015,
      name: "InvalidPoolQuoteTokenAccount"
    },
    {
      code: 6016,
      name: "BuyMoreBaseAmountThanPoolReserves"
    },
    {
      code: 6017,
      name: "DisabledCreatePool"
    },
    {
      code: 6018,
      name: "DisabledDeposit"
    },
    {
      code: 6019,
      name: "DisabledWithdraw"
    },
    {
      code: 6020,
      name: "DisabledBuy"
    },
    {
      code: 6021,
      name: "DisabledSell"
    },
    {
      code: 6022,
      name: "SameMint"
    },
    {
      code: 6023,
      name: "Overflow"
    },
    {
      code: 6024,
      name: "Truncation"
    },
    {
      code: 6025,
      name: "DivisionByZero"
    },
    {
      code: 6026,
      name: "NewSizeLessThanCurrentSize"
    },
    {
      code: 6027,
      name: "AccountTypeNotSupported"
    },
    {
      code: 6028,
      name: "OnlyCanonicalPumpPoolsCanHaveCoinCreator"
    },
    {
      code: 6029,
      name: "InvalidAdminSetCoinCreatorAuthority"
    },
    {
      code: 6030,
      name: "StartTimeInThePast"
    },
    {
      code: 6031,
      name: "EndTimeInThePast"
    },
    {
      code: 6032,
      name: "EndTimeBeforeStartTime"
    },
    {
      code: 6033,
      name: "TimeRangeTooLarge"
    },
    {
      code: 6034,
      name: "EndTimeBeforeCurrentDay"
    },
    {
      code: 6035,
      name: "SupplyUpdateForFinishedRange"
    },
    {
      code: 6036,
      name: "DayIndexAfterEndIndex"
    },
    {
      code: 6037,
      name: "DayInActiveRange"
    },
    {
      code: 6038,
      name: "InvalidIncentiveMint"
    },
    {
      code: 6039,
      name: "BuyNotEnoughQuoteTokensToCoverFees",
      msg: "buy: Not enough quote tokens to cover for fees."
    },
    {
      code: 6040,
      name: "BuySlippageBelowMinBaseAmountOut",
      msg: "buy: slippage - would buy less tokens than expected min_base_amount_out"
    },
    {
      code: 6041,
      name: "MayhemModeDisabled"
    },
    {
      code: 6042,
      name: "OnlyPumpPoolsMayhemMode"
    },
    {
      code: 6043,
      name: "MayhemModeInDesiredState"
    },
    {
      code: 6044,
      name: "NotEnoughRemainingAccounts"
    },
    {
      code: 6045,
      name: "InvalidSharingConfigBaseMint"
    },
    {
      code: 6046,
      name: "InvalidSharingConfigCoinCreator"
    },
    {
      code: 6047,
      name: "CoinCreatorMigratedToSharingConfig",
      msg: "coin creator has been migrated to sharing config"
    },
    {
      code: 6048,
      name: "CreatorVaultMigratedToSharingConfig",
      msg: "creator_vault has been migrated to sharing config, use pump:distribute_creator_fees instead"
    },
    {
      code: 6049,
      name: "CashbackNotEnabled",
      msg: "Cashback is disabled"
    },
    {
      code: 6050,
      name: "OnlyPumpPoolsCashback"
    },
    {
      code: 6051,
      name: "CashbackNotInDesiredState"
    },
    {
      code: 6052,
      name: "TokensInVaultLessThanCashbackEarned"
    },
    {
      code: 6053,
      name: "BuybackFeeRecipientNotAuthorized",
      msg: "Buyback fee recipient not authorized"
    },
    {
      code: 6054,
      name: "AllBuybackFeeRecipientsShouldBeNonZero"
    },
    {
      code: 6055,
      name: "NotUniqueBuybackFeeRecipients"
    },
    {
      code: 6056,
      name: "BuybackBasisPointsOutOfRange",
      msg: "buyback_basis_points must be <= 10_000"
    },
    {
      code: 6057,
      name: "WrongBuybackFeeRecipientsCount",
      msg: "buyback fee recipients require exactly 8 remaining accounts (or none)"
    },
    {
      code: 6058,
      name: "BuybackFeeRecipientMissing"
    },
    {
      code: 6059,
      name: "MissingCashbackAccounts",
      msg: "Cashback trade is missing the required remaining accounts"
    },
    {
      code: 6060,
      name: "InvalidCashbackAccumulator",
      msg: "Cashback user_volume_accumulator account is invalid"
    },
    {
      code: 6061,
      name: "InvalidCashbackAccumulatorAta",
      msg: "Cashback user_volume_accumulator ATA is missing or invalid"
    },
    {
      code: 6062,
      name: "InvalidPoolV2",
      msg: "pool_v2 remaining account is missing or invalid"
    },
    {
      code: 6063,
      name: "InsufficientRealQuoteReserves",
      msg: "BOOST: sell output exceeds the real quote vault. effective = real + virtual is pricing-only; payout is capped at real_vault, so quote min(out, real_vault)"
    },
    {
      code: 6064,
      name: "BoostPoolLiquidityUnsupported",
      msg: "BOOST: deposit/withdraw don't apply to boost pools"
    },
    {
      code: 6065,
      name: "PoolCannotBoost",
      msg: "BOOST: pool cannot be boosted (no virtual reserves)"
    },
    {
      code: 6066,
      name: "BoostDisabled",
      msg: "BOOST: boost is disabled"
    },
    {
      code: 6067,
      name: "SeedLockViolation",
      msg: "BOOST: lp_supply must never drop below the circulating LP mint supply"
    },
    {
      code: 6068,
      name: "CreatorFeeNotConfigurable",
      msg: "Configurable creator fee is disabled"
    },
    {
      code: 6069,
      name: "CreatorFeeBpsOutOfRange",
      msg: "Creator fee basis points must be between 1 and the configured maximum"
    },
    {
      code: 6070,
      name: "CreatorFeeNotEditable",
      msg: "Creator fee is not editable for this pool"
    },
    {
      code: 6071,
      name: "CreatorFeeNotAllowedForCashbackCoin",
      msg: "Cashback coins cannot have a creator fee"
    },
    {
      code: 6072,
      name: "SharingConfigNotActive",
      msg: "Sharing config is not active"
    },
    {
      code: 6073,
      name: "NotAuthorized",
      msg: "Not authorized"
    },
    {
      code: 6074,
      name: "HolderRewardCreatorImmutable",
      msg: "The coin creator of a holder-reward pool cannot be changed"
    },
    {
      code: 6075,
      name: "CtoNotAllowedForMayhemPool",
      msg: "CTO is not allowed on a mayhem-mode pool"
    },
    {
      code: 6076,
      name: "InvalidHolderRewardCoinCreator",
      msg: "A holder-reward pool's coin creator must be the holder-rewards PDA"
    },
    {
      code: 6077,
      name: "CreatorFeeNotConfigurableForQuote",
      msg: "Creator fee is not configurable on a SOL or USDC quote; the fee schedule applies"
    },
    {
      code: 6078,
      name: "OnlyPumpPools",
      msg: "Only canonical pump pools are supported by this instruction"
    },
    {
      code: 6079,
      name: "CashbackCoinNotSupported",
      msg: "v2 trades do not support cashback coins; use the v1 instructions"
    },
    {
      code: 6080,
      name: "MayhemPoolNotSupported",
      msg: "v2 trades do not support mayhem-mode pools; use the v1 instructions"
    },
    {
      code: 6081,
      name: "CreatorFeesNotSwept",
      msg: "creator_fees must be swept before the coin creator changes"
    },
    {
      code: 6082,
      name: "FeeTiersEmpty",
      msg: "The fee config tier table is empty"
    },
    {
      code: 6083,
      name: "FeeConfigTooShort",
      msg: "The fee config account is shorter than its initialize size"
    },
    {
      code: 6084,
      name: "MultiHopDiscontinuousPath",
      msg: "multi-hop: a hop's input mint is neither side of its pool or curve, or the route does not end in user_out_token_account's mint"
    },
    {
      code: 6085,
      name: "MultiHopCurveRunMismatch",
      msg: "multi-hop: the balances around the bonding-curve hops do not match the amounts pump reported"
    },
    {
      code: 6086,
      name: "MultiHopMixedDirection",
      msg: "multi-hop: every hop must trade in the same direction, all buys or all sells"
    },
    {
      code: 6087,
      name: "SelfTransferNotAllowed",
      msg: "A transfer's source is its destination and the signer does not own it"
    },
    {
      code: 6088,
      name: "QuoteMintNotWritable",
      msg: "quote_mint must be writable for a quote with a Token-2022 transfer fee: its withheld fees are harvested to the mint"
    }
  ],
  types: [
    {
      name: "AdminCtoPoolEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "base_mint",
            type: "pubkey"
          },
          {
            name: "pool",
            type: "pubkey"
          },
          {
            name: "old_coin_creator",
            type: "pubkey"
          },
          {
            name: "new_coin_creator",
            type: "pubkey"
          },
          {
            name: "is_holder_reward",
            type: "bool"
          },
          {
            name: "is_cashback_coin",
            type: "bool"
          },
          {
            name: "old_creator_fee_bps",
            type: "u64"
          },
          {
            name: "new_creator_fee_bps",
            type: "u64"
          }
        ]
      }
    },
    {
      name: "AdminUpdateTokenIncentivesEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "start_time",
            type: "i64"
          },
          {
            name: "end_time",
            type: "i64"
          },
          {
            name: "day_number",
            type: "u64"
          },
          {
            name: "token_supply_per_day",
            type: "u64"
          },
          {
            name: "mint",
            type: "pubkey"
          },
          {
            name: "seconds_in_a_day",
            type: "i64"
          },
          {
            name: "timestamp",
            type: "i64"
          }
        ]
      }
    },
    {
      name: "BondingCurve",
      type: {
        kind: "struct",
        fields: [
          {
            name: "virtual_token_reserves",
            type: "u64"
          },
          {
            name: "virtual_sol_reserves",
            type: "u64"
          },
          {
            name: "real_token_reserves",
            type: "u64"
          },
          {
            name: "real_sol_reserves",
            type: "u64"
          },
          {
            name: "token_total_supply",
            type: "u64"
          },
          {
            name: "complete",
            type: "bool"
          },
          {
            name: "creator",
            type: "pubkey"
          },
          {
            name: "is_mayhem_mode",
            type: "bool"
          },
          {
            name: "is_cashback_coin",
            type: "bool"
          }
        ]
      }
    },
    {
      name: "BoostBuyAndBurnEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "mint",
            type: "pubkey"
          },
          {
            name: "bonding_curve",
            type: "pubkey"
          },
          {
            name: "pool",
            type: "pubkey"
          },
          {
            name: "authority",
            type: "pubkey"
          },
          {
            name: "quote_amount_in_requested",
            type: "u64"
          },
          {
            name: "quote_amount_in_used",
            type: "u64"
          },
          {
            name: "base_amount_burned",
            type: "u64"
          },
          {
            name: "virtual_quote_reserves",
            type: "i128"
          },
          {
            name: "real_quote_reserves_after",
            type: "u64"
          },
          {
            name: "base_reserves_after",
            type: "u64"
          },
          {
            name: "boost_vault_remaining",
            type: "u64"
          }
        ]
      }
    },
    {
      name: "BuyEvent",
      docs: [
        'ix_name: "buy" | "buy_exact_quote_in"'
      ],
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "base_amount_out",
            type: "u64"
          },
          {
            name: "max_quote_amount_in",
            type: "u64"
          },
          {
            name: "user_base_token_reserves",
            type: "u64"
          },
          {
            name: "user_quote_token_reserves",
            type: "u64"
          },
          {
            name: "pool_base_token_reserves",
            type: "u64"
          },
          {
            name: "pool_quote_token_reserves",
            type: "u64"
          },
          {
            name: "quote_amount_in",
            type: "u64"
          },
          {
            name: "lp_fee_basis_points",
            type: "u64"
          },
          {
            name: "lp_fee",
            type: "u64"
          },
          {
            name: "protocol_fee_basis_points",
            type: "u64"
          },
          {
            name: "protocol_fee",
            type: "u64"
          },
          {
            name: "quote_amount_in_with_lp_fee",
            type: "u64"
          },
          {
            name: "user_quote_amount_in",
            type: "u64"
          },
          {
            name: "pool",
            type: "pubkey"
          },
          {
            name: "user",
            type: "pubkey"
          },
          {
            name: "user_base_token_account",
            type: "pubkey"
          },
          {
            name: "user_quote_token_account",
            type: "pubkey"
          },
          {
            name: "protocol_fee_recipient",
            type: "pubkey"
          },
          {
            name: "protocol_fee_recipient_token_account",
            type: "pubkey"
          },
          {
            name: "coin_creator",
            type: "pubkey"
          },
          {
            name: "coin_creator_fee_basis_points",
            type: "u64"
          },
          {
            name: "coin_creator_fee",
            type: "u64"
          },
          {
            name: "track_volume",
            type: "bool"
          },
          {
            name: "total_unclaimed_tokens",
            type: "u64"
          },
          {
            name: "total_claimed_tokens",
            type: "u64"
          },
          {
            name: "current_sol_volume",
            type: "u64"
          },
          {
            name: "last_update_timestamp",
            type: "i64"
          },
          {
            name: "min_base_amount_out",
            type: "u64"
          },
          {
            name: "ix_name",
            type: "string"
          },
          {
            name: "cashback_fee_basis_points",
            type: "u64"
          },
          {
            name: "cashback",
            type: "u64"
          },
          {
            name: "buyback_fee_basis_points",
            type: "u64"
          },
          {
            name: "buyback_fee",
            type: "u64"
          },
          {
            name: "virtual_quote_reserves",
            type: "i128"
          },
          {
            name: "can_boost",
            type: "bool"
          },
          {
            name: "base_supply",
            type: "u64"
          },
          {
            name: "holder_rewards_bps",
            type: "u64"
          },
          {
            name: "holder_rewards",
            type: "u64"
          },
          {
            name: "creator_fee_unclaimed",
            type: "u64"
          },
          {
            name: "quote_transfer_fee",
            type: "u64"
          }
        ]
      }
    },
    {
      name: "ClaimCashbackEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "user",
            type: "pubkey"
          },
          {
            name: "amount",
            type: "u64"
          },
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "total_claimed",
            type: "u64"
          },
          {
            name: "total_cashback_earned",
            type: "u64"
          }
        ]
      }
    },
    {
      name: "ClaimTokenIncentivesEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "user",
            type: "pubkey"
          },
          {
            name: "mint",
            type: "pubkey"
          },
          {
            name: "amount",
            type: "u64"
          },
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "total_claimed_tokens",
            type: "u64"
          },
          {
            name: "current_sol_volume",
            type: "u64"
          }
        ]
      }
    },
    {
      name: "CloseUserVolumeAccumulatorEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "user",
            type: "pubkey"
          },
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "total_unclaimed_tokens",
            type: "u64"
          },
          {
            name: "total_claimed_tokens",
            type: "u64"
          },
          {
            name: "current_sol_volume",
            type: "u64"
          },
          {
            name: "last_update_timestamp",
            type: "i64"
          }
        ]
      }
    },
    {
      name: "CollectCoinCreatorFeeEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "coin_creator",
            type: "pubkey"
          },
          {
            name: "coin_creator_fee",
            type: "u64"
          },
          {
            name: "coin_creator_vault_ata",
            type: "pubkey"
          },
          {
            name: "coin_creator_token_account",
            type: "pubkey"
          }
        ]
      }
    },
    {
      name: "ConfigStatus",
      type: {
        kind: "enum",
        variants: [
          {
            name: "Paused"
          },
          {
            name: "Active"
          }
        ]
      }
    },
    {
      name: "CreateConfigEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "admin",
            type: "pubkey"
          },
          {
            name: "lp_fee_basis_points",
            type: "u64"
          },
          {
            name: "protocol_fee_basis_points",
            type: "u64"
          },
          {
            name: "protocol_fee_recipients",
            type: {
              array: [
                "pubkey",
                8
              ]
            }
          },
          {
            name: "coin_creator_fee_basis_points",
            type: "u64"
          },
          {
            name: "admin_set_coin_creator_authority",
            type: "pubkey"
          }
        ]
      }
    },
    {
      name: "CreatePoolEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "index",
            type: "u16"
          },
          {
            name: "creator",
            type: "pubkey"
          },
          {
            name: "base_mint",
            type: "pubkey"
          },
          {
            name: "quote_mint",
            type: "pubkey"
          },
          {
            name: "base_mint_decimals",
            type: "u8"
          },
          {
            name: "quote_mint_decimals",
            type: "u8"
          },
          {
            name: "base_amount_in",
            type: "u64"
          },
          {
            name: "quote_amount_in",
            type: "u64"
          },
          {
            name: "pool_base_amount",
            type: "u64"
          },
          {
            name: "pool_quote_amount",
            type: "u64"
          },
          {
            name: "minimum_liquidity",
            type: "u64"
          },
          {
            name: "initial_liquidity",
            type: "u64"
          },
          {
            name: "lp_token_amount_out",
            type: "u64"
          },
          {
            name: "pool_bump",
            type: "u8"
          },
          {
            name: "pool",
            type: "pubkey"
          },
          {
            name: "lp_mint",
            type: "pubkey"
          },
          {
            name: "user_base_token_account",
            type: "pubkey"
          },
          {
            name: "user_quote_token_account",
            type: "pubkey"
          },
          {
            name: "coin_creator",
            type: "pubkey"
          },
          {
            name: "is_mayhem_mode",
            type: "bool"
          },
          {
            name: "creator_fee_bps",
            type: "u64"
          },
          {
            name: "can_edit_creator_fee",
            type: "bool"
          },
          {
            name: "is_holder_reward",
            type: "bool"
          }
        ]
      }
    },
    {
      name: "DepositEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "lp_token_amount_out",
            type: "u64"
          },
          {
            name: "max_base_amount_in",
            type: "u64"
          },
          {
            name: "max_quote_amount_in",
            type: "u64"
          },
          {
            name: "user_base_token_reserves",
            type: "u64"
          },
          {
            name: "user_quote_token_reserves",
            type: "u64"
          },
          {
            name: "pool_base_token_reserves",
            type: "u64"
          },
          {
            name: "pool_quote_token_reserves",
            type: "u64"
          },
          {
            name: "base_amount_in",
            type: "u64"
          },
          {
            name: "quote_amount_in",
            type: "u64"
          },
          {
            name: "lp_mint_supply",
            type: "u64"
          },
          {
            name: "pool",
            type: "pubkey"
          },
          {
            name: "user",
            type: "pubkey"
          },
          {
            name: "user_base_token_account",
            type: "pubkey"
          },
          {
            name: "user_quote_token_account",
            type: "pubkey"
          },
          {
            name: "user_pool_token_account",
            type: "pubkey"
          },
          {
            name: "quote_transfer_fee",
            type: "u64"
          }
        ]
      }
    },
    {
      name: "DisableEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "admin",
            type: "pubkey"
          },
          {
            name: "disable_create_pool",
            type: "bool"
          },
          {
            name: "disable_deposit",
            type: "bool"
          },
          {
            name: "disable_withdraw",
            type: "bool"
          },
          {
            name: "disable_buy",
            type: "bool"
          },
          {
            name: "disable_sell",
            type: "bool"
          }
        ]
      }
    },
    {
      name: "ExtendAccountEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "account",
            type: "pubkey"
          },
          {
            name: "user",
            type: "pubkey"
          },
          {
            name: "current_size",
            type: "u64"
          },
          {
            name: "new_size",
            type: "u64"
          }
        ]
      }
    },
    {
      name: "FeeConfig",
      type: {
        kind: "struct",
        fields: [
          {
            name: "bump",
            type: "u8"
          },
          {
            name: "admin",
            type: "pubkey"
          },
          {
            name: "flat_fees",
            type: {
              defined: {
                name: "Fees"
              }
            }
          },
          {
            name: "fee_tiers",
            type: {
              vec: {
                defined: {
                  name: "FeeTier"
                }
              }
            }
          },
          {
            name: "stable_fee_tiers",
            type: {
              vec: {
                defined: {
                  name: "FeeTier"
                }
              }
            }
          },
          {
            name: "exotic_flat_fees",
            type: {
              defined: {
                name: "Fees"
              }
            }
          }
        ]
      }
    },
    {
      name: "FeeTier",
      type: {
        kind: "struct",
        fields: [
          {
            name: "market_cap_lamports_threshold",
            type: "u128"
          },
          {
            name: "fees",
            type: {
              defined: {
                name: "Fees"
              }
            }
          }
        ]
      }
    },
    {
      name: "Fees",
      type: {
        kind: "struct",
        fields: [
          {
            name: "lp_fee_bps",
            type: "u64"
          },
          {
            name: "protocol_fee_bps",
            type: "u64"
          },
          {
            name: "creator_fee_bps",
            type: "u64"
          }
        ]
      }
    },
    {
      name: "GlobalConfig",
      type: {
        kind: "struct",
        fields: [
          {
            name: "admin",
            docs: [
              "The admin pubkey"
            ],
            type: "pubkey"
          },
          {
            name: "lp_fee_basis_points",
            type: "u64"
          },
          {
            name: "protocol_fee_basis_points",
            type: "u64"
          },
          {
            name: "disable_flags",
            docs: [
              "Flags to disable certain functionality",
              "bit 0 - Disable create pool",
              "bit 1 - Disable deposit",
              "bit 2 - Disable withdraw",
              "bit 3 - Disable buy",
              "bit 4 - Disable sell"
            ],
            type: "u8"
          },
          {
            name: "protocol_fee_recipients",
            docs: [
              "Addresses of the protocol fee recipients"
            ],
            type: {
              array: [
                "pubkey",
                8
              ]
            }
          },
          {
            name: "coin_creator_fee_basis_points",
            type: "u64"
          },
          {
            name: "admin_set_coin_creator_authority",
            docs: [
              "The admin authority for setting coin creators"
            ],
            type: "pubkey"
          },
          {
            name: "whitelist_pda",
            type: "pubkey"
          },
          {
            name: "reserved_fee_recipient",
            type: "pubkey"
          },
          {
            name: "mayhem_mode_enabled",
            type: "bool"
          },
          {
            name: "reserved_fee_recipients",
            type: {
              array: [
                "pubkey",
                7
              ]
            }
          },
          {
            name: "is_cashback_enabled",
            type: "bool"
          },
          {
            name: "buyback_fee_recipients",
            type: {
              array: [
                "pubkey",
                8
              ]
            }
          },
          {
            name: "buyback_basis_points",
            type: "u64"
          },
          {
            name: "boost_authority",
            type: "pubkey"
          },
          {
            name: "boost_enabled",
            type: "bool"
          },
          {
            name: "creator_fee_configurable",
            type: "bool"
          },
          {
            name: "max_configurable_creator_fee_bps",
            type: "u64"
          }
        ]
      }
    },
    {
      name: "GlobalVolumeAccumulator",
      type: {
        kind: "struct",
        fields: [
          {
            name: "start_time",
            type: "i64"
          },
          {
            name: "end_time",
            type: "i64"
          },
          {
            name: "seconds_in_a_day",
            type: "i64"
          },
          {
            name: "mint",
            type: "pubkey"
          },
          {
            name: "total_token_supply",
            type: {
              array: [
                "u64",
                30
              ]
            }
          },
          {
            name: "sol_volumes",
            type: {
              array: [
                "u64",
                30
              ]
            }
          }
        ]
      }
    },
    {
      name: "InitBoostEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "mint",
            type: "pubkey"
          },
          {
            name: "bonding_curve",
            type: "pubkey"
          },
          {
            name: "pool",
            type: "pubkey"
          },
          {
            name: "virtual_quote_reserves",
            type: "i128"
          },
          {
            name: "real_quote_reserves_after",
            type: "u64"
          }
        ]
      }
    },
    {
      name: "InitUserVolumeAccumulatorEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "payer",
            type: "pubkey"
          },
          {
            name: "user",
            type: "pubkey"
          },
          {
            name: "timestamp",
            type: "i64"
          }
        ]
      }
    },
    {
      name: "MigratePoolCoinCreatorEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "base_mint",
            type: "pubkey"
          },
          {
            name: "pool",
            type: "pubkey"
          },
          {
            name: "sharing_config",
            type: "pubkey"
          },
          {
            name: "old_coin_creator",
            type: "pubkey"
          },
          {
            name: "new_coin_creator",
            type: "pubkey"
          }
        ]
      }
    },
    {
      name: "OptionBool",
      type: {
        kind: "struct",
        fields: [
          "bool"
        ]
      }
    },
    {
      name: "OptionU64",
      type: {
        kind: "struct",
        fields: [
          "u64"
        ]
      }
    },
    {
      name: "Pool",
      type: {
        kind: "struct",
        fields: [
          {
            name: "pool_bump",
            type: "u8"
          },
          {
            name: "index",
            type: "u16"
          },
          {
            name: "creator",
            type: "pubkey"
          },
          {
            name: "base_mint",
            type: "pubkey"
          },
          {
            name: "quote_mint",
            type: "pubkey"
          },
          {
            name: "lp_mint",
            type: "pubkey"
          },
          {
            name: "pool_base_token_account",
            type: "pubkey"
          },
          {
            name: "pool_quote_token_account",
            type: "pubkey"
          },
          {
            name: "lp_supply",
            docs: [
              "True circulating supply without burns and lock-ups"
            ],
            type: "u64"
          },
          {
            name: "coin_creator",
            type: "pubkey"
          },
          {
            name: "is_mayhem_mode",
            type: "bool"
          },
          {
            name: "is_cashback_coin",
            type: "bool"
          },
          {
            name: "virtual_quote_reserves",
            docs: [
              "For non-boost pools, value is 0, so the behavior is identical to legacy pools."
            ],
            type: "i128"
          },
          {
            name: "creator_fee_bps",
            type: "u64"
          },
          {
            name: "can_edit_creator_fee",
            type: "bool"
          },
          {
            name: "is_holder_reward",
            type: "bool"
          },
          {
            name: "protocol_fees",
            type: "u64"
          },
          {
            name: "creator_fees",
            type: "u64"
          }
        ]
      }
    },
    {
      name: "ReservedFeeRecipientsEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "reserved_fee_recipient",
            type: "pubkey"
          },
          {
            name: "reserved_fee_recipients",
            type: {
              array: [
                "pubkey",
                7
              ]
            }
          }
        ]
      }
    },
    {
      name: "SellEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "base_amount_in",
            type: "u64"
          },
          {
            name: "min_quote_amount_out",
            type: "u64"
          },
          {
            name: "user_base_token_reserves",
            type: "u64"
          },
          {
            name: "user_quote_token_reserves",
            type: "u64"
          },
          {
            name: "pool_base_token_reserves",
            type: "u64"
          },
          {
            name: "pool_quote_token_reserves",
            type: "u64"
          },
          {
            name: "quote_amount_out",
            type: "u64"
          },
          {
            name: "lp_fee_basis_points",
            type: "u64"
          },
          {
            name: "lp_fee",
            type: "u64"
          },
          {
            name: "protocol_fee_basis_points",
            type: "u64"
          },
          {
            name: "protocol_fee",
            type: "u64"
          },
          {
            name: "quote_amount_out_without_lp_fee",
            type: "u64"
          },
          {
            name: "user_quote_amount_out",
            type: "u64"
          },
          {
            name: "pool",
            type: "pubkey"
          },
          {
            name: "user",
            type: "pubkey"
          },
          {
            name: "user_base_token_account",
            type: "pubkey"
          },
          {
            name: "user_quote_token_account",
            type: "pubkey"
          },
          {
            name: "protocol_fee_recipient",
            type: "pubkey"
          },
          {
            name: "protocol_fee_recipient_token_account",
            type: "pubkey"
          },
          {
            name: "coin_creator",
            type: "pubkey"
          },
          {
            name: "coin_creator_fee_basis_points",
            type: "u64"
          },
          {
            name: "coin_creator_fee",
            type: "u64"
          },
          {
            name: "cashback_fee_basis_points",
            type: "u64"
          },
          {
            name: "cashback",
            type: "u64"
          },
          {
            name: "buyback_fee_basis_points",
            type: "u64"
          },
          {
            name: "buyback_fee",
            type: "u64"
          },
          {
            name: "virtual_quote_reserves",
            type: "i128"
          },
          {
            name: "can_boost",
            type: "bool"
          },
          {
            name: "base_supply",
            type: "u64"
          },
          {
            name: "holder_rewards_bps",
            type: "u64"
          },
          {
            name: "holder_rewards",
            type: "u64"
          },
          {
            name: "creator_fee_unclaimed",
            type: "u64"
          },
          {
            name: "quote_transfer_fee",
            type: "u64"
          }
        ]
      }
    },
    {
      name: "SetBondingCurveCoinCreatorEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "base_mint",
            type: "pubkey"
          },
          {
            name: "pool",
            type: "pubkey"
          },
          {
            name: "bonding_curve",
            type: "pubkey"
          },
          {
            name: "coin_creator",
            type: "pubkey"
          }
        ]
      }
    },
    {
      name: "SetBoostAuthorityEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "admin",
            type: "pubkey"
          },
          {
            name: "old_boost_authority",
            type: "pubkey"
          },
          {
            name: "new_boost_authority",
            type: "pubkey"
          }
        ]
      }
    },
    {
      name: "SetMetaplexCoinCreatorEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "base_mint",
            type: "pubkey"
          },
          {
            name: "pool",
            type: "pubkey"
          },
          {
            name: "metadata",
            type: "pubkey"
          },
          {
            name: "coin_creator",
            type: "pubkey"
          }
        ]
      }
    },
    {
      name: "Shareholder",
      type: {
        kind: "struct",
        fields: [
          {
            name: "address",
            type: "pubkey"
          },
          {
            name: "share_bps",
            type: "u16"
          }
        ]
      }
    },
    {
      name: "SharingConfig",
      type: {
        kind: "struct",
        fields: [
          {
            name: "bump",
            type: "u8"
          },
          {
            name: "version",
            type: "u8"
          },
          {
            name: "status",
            type: {
              defined: {
                name: "ConfigStatus"
              }
            }
          },
          {
            name: "mint",
            type: "pubkey"
          },
          {
            name: "admin",
            type: "pubkey"
          },
          {
            name: "admin_revoked",
            type: "bool"
          },
          {
            name: "shareholders",
            type: {
              vec: {
                defined: {
                  name: "Shareholder"
                }
              }
            }
          }
        ]
      }
    },
    {
      name: "SweepPoolFeeEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "pool",
            type: "pubkey"
          },
          {
            name: "base_mint",
            type: "pubkey"
          },
          {
            name: "quote_mint",
            type: "pubkey"
          },
          {
            name: "recipient",
            type: "pubkey"
          },
          {
            name: "payer",
            type: "pubkey"
          },
          {
            name: "amount",
            type: "u64"
          },
          {
            name: "bucket",
            type: "u8"
          }
        ]
      }
    },
    {
      name: "SyncUserVolumeAccumulatorEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "user",
            type: "pubkey"
          },
          {
            name: "total_claimed_tokens_before",
            type: "u64"
          },
          {
            name: "total_claimed_tokens_after",
            type: "u64"
          },
          {
            name: "timestamp",
            type: "i64"
          }
        ]
      }
    },
    {
      name: "UpdateAdminEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "admin",
            type: "pubkey"
          },
          {
            name: "new_admin",
            type: "pubkey"
          }
        ]
      }
    },
    {
      name: "UpdateCreatorFeeConfigEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "admin",
            type: "pubkey"
          },
          {
            name: "creator_fee_configurable",
            type: "bool"
          },
          {
            name: "max_configurable_creator_fee_bps",
            type: "u64"
          }
        ]
      }
    },
    {
      name: "UpdateFeeConfigEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "admin",
            type: "pubkey"
          },
          {
            name: "lp_fee_basis_points",
            type: "u64"
          },
          {
            name: "protocol_fee_basis_points",
            type: "u64"
          },
          {
            name: "protocol_fee_recipients",
            type: {
              array: [
                "pubkey",
                8
              ]
            }
          },
          {
            name: "coin_creator_fee_basis_points",
            type: "u64"
          },
          {
            name: "admin_set_coin_creator_authority",
            type: "pubkey"
          }
        ]
      }
    },
    {
      name: "UserVolumeAccumulator",
      type: {
        kind: "struct",
        fields: [
          {
            name: "user",
            type: "pubkey"
          },
          {
            name: "needs_claim",
            type: "bool"
          },
          {
            name: "total_unclaimed_tokens",
            type: "u64"
          },
          {
            name: "total_claimed_tokens",
            type: "u64"
          },
          {
            name: "current_sol_volume",
            type: "u64"
          },
          {
            name: "last_update_timestamp",
            type: "i64"
          },
          {
            name: "has_total_claimed_tokens",
            type: "bool"
          },
          {
            name: "cashback_earned",
            type: "u64"
          },
          {
            name: "total_cashback_claimed",
            type: "u64"
          }
        ]
      }
    },
    {
      name: "WithdrawEvent",
      type: {
        kind: "struct",
        fields: [
          {
            name: "timestamp",
            type: "i64"
          },
          {
            name: "lp_token_amount_in",
            type: "u64"
          },
          {
            name: "min_base_amount_out",
            type: "u64"
          },
          {
            name: "min_quote_amount_out",
            type: "u64"
          },
          {
            name: "user_base_token_reserves",
            type: "u64"
          },
          {
            name: "user_quote_token_reserves",
            type: "u64"
          },
          {
            name: "pool_base_token_reserves",
            type: "u64"
          },
          {
            name: "pool_quote_token_reserves",
            type: "u64"
          },
          {
            name: "base_amount_out",
            type: "u64"
          },
          {
            name: "quote_amount_out",
            type: "u64"
          },
          {
            name: "lp_mint_supply",
            type: "u64"
          },
          {
            name: "pool",
            type: "pubkey"
          },
          {
            name: "user",
            type: "pubkey"
          },
          {
            name: "user_base_token_account",
            type: "pubkey"
          },
          {
            name: "user_quote_token_account",
            type: "pubkey"
          },
          {
            name: "user_pool_token_account",
            type: "pubkey"
          },
          {
            name: "quote_transfer_fee",
            type: "u64"
          }
        ]
      }
    }
  ]
};

// src/swap/util.ts
function ceilDiv(a, b) {
  if (b.isZero()) {
    throw new Error("Cannot divide by zero.");
  }
  return a.add(b).subn(1).div(b);
}
function fee(amount, basisPoints) {
  return ceilDiv(amount.mul(basisPoints), new import_bn2.default(1e4));
}
function getPumpAmmProgram(connection) {
  return new import_anchor.Program(
    pump_amm_default,
    new import_anchor.AnchorProvider(connection, null, {})
  );
}
function isPumpPool(baseMint, poolCreator) {
  return pumpPoolAuthorityPda(baseMint).equals(poolCreator);
}
function supportsTradeV2(pool) {
  return !pool.isCashbackCoin;
}
var PUMP_AMM_TOTAL_TOKEN_SUPPLY = new import_bn2.default("1000000000000000");
function poolMarketCap({
  baseMintSupply,
  baseReserve,
  quoteReserve,
  isMayhemMode = false
}) {
  if (baseReserve.isZero()) {
    throw new Error(
      "Division by zero: pool base token reserves cannot be zero"
    );
  }
  const circulatingSupply = isMayhemMode ? PUMP_AMM_TOTAL_TOKEN_SUPPLY : baseMintSupply;
  return quoteReserve.mul(circulatingSupply).div(baseReserve);
}

// src/swap/fees.ts
var USDC_MINT = new import_web32.PublicKey(
  "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
);
var STABLE_QUOTE_MINTS = Object.freeze([
  USDC_MINT
]);
var SOL_LIKE_QUOTE_MINTS = Object.freeze([
  import_web32.PublicKey.default,
  import_spl_token2.NATIVE_MINT,
  import_spl_token2.NATIVE_MINT_2022
]);
function isSolLikeQuoteMint(quoteMint) {
  return SOL_LIKE_QUOTE_MINTS.some((mint) => mint.equals(quoteMint));
}
function isStableQuoteMint(quoteMint) {
  return STABLE_QUOTE_MINTS.some((mint) => mint.equals(quoteMint));
}
function isZeroFees(fees) {
  return fees.lpFeeBps.isZero() && fees.protocolFeeBps.isZero() && fees.creatorFeeBps.isZero();
}
function computeFeesBps({
  globalConfig,
  feeConfig,
  creator,
  baseMintSupply,
  baseMint,
  baseReserve,
  quoteReserve,
  quoteMint = import_spl_token2.NATIVE_MINT,
  isMayhemMode = false,
  creatorFeeBps
}) {
  if (feeConfig != null) {
    const marketCap = poolMarketCap({
      baseMintSupply,
      baseReserve,
      quoteReserve,
      isMayhemMode
    });
    const fees = feesForQuoteMint({
      feeConfig,
      isPumpPool: isPumpPool(baseMint, creator),
      marketCap,
      quoteMint
    });
    return globalConfig.creatorFeeConfigurable && creatorFeeBps?.gtn(0) ? { ...fees, creatorFeeBps } : fees;
  }
  return {
    lpFeeBps: globalConfig.lpFeeBasisPoints,
    protocolFeeBps: globalConfig.protocolFeeBasisPoints,
    creatorFeeBps: globalConfig.coinCreatorFeeBasisPoints
  };
}
function feesForQuoteMint({
  feeConfig,
  isPumpPool: isPumpPool2,
  marketCap,
  quoteMint
}) {
  if (!isPumpPool2) {
    return feeConfig.flatFees;
  }
  if (isSolLikeQuoteMint(quoteMint)) {
    return calculateFeeTier({ feeTiers: feeConfig.feeTiers, marketCap });
  }
  if (isStableQuoteMint(quoteMint)) {
    return calculateFeeTier({
      feeTiers: feeConfig.stableFeeTiers.length > 0 ? feeConfig.stableFeeTiers : feeConfig.feeTiers,
      marketCap
    });
  }
  return isZeroFees(feeConfig.exoticFlatFees) ? feeConfig.flatFees : feeConfig.exoticFlatFees;
}
function calculateFeeTier({
  feeTiers,
  marketCap
}) {
  if (feeTiers.length === 0) {
    throw new Error("Fee tiers cannot be empty.");
  }
  const firstTier = feeTiers[0];
  if (marketCap.lt(firstTier.marketCapLamportsThreshold)) {
    return firstTier.fees;
  }
  for (const tier of feeTiers.slice().reverse()) {
    if (marketCap.gte(tier.marketCapLamportsThreshold)) {
      return tier.fees;
    }
  }
  return firstTier.fees;
}
function getFeeRecipient(globalConfig, isMayhemMode) {
  if (isMayhemMode) {
    const feeRecipients = [
      globalConfig.reservedFeeRecipient,
      ...globalConfig.reservedFeeRecipients
    ];
    return feeRecipients[Math.floor(Math.random() * feeRecipients.length)];
  }
  return globalConfig.protocolFeeRecipients[Math.floor(Math.random() * globalConfig.protocolFeeRecipients.length)];
}
function getBuybackFeeRecipient(globalConfig) {
  return globalConfig.buybackFeeRecipients[Math.floor(Math.random() * globalConfig.buybackFeeRecipients.length)];
}

// src/swap/transferFee.ts
var import_spl_token3 = require("@solana/spl-token");
var import_bn3 = __toESM(require("bn.js"));
var ONE_IN_BASIS_POINTS = new import_bn3.default(1e4);
function parseTransferFeeConfig(quoteMint, quoteMintAccountInfo) {
  if (!quoteMintAccountInfo.owner.equals(import_spl_token3.TOKEN_2022_PROGRAM_ID)) {
    return null;
  }
  return (0, import_spl_token3.getTransferFeeConfig)(
    (0, import_spl_token3.unpackMint)(quoteMint, quoteMintAccountInfo, import_spl_token3.TOKEN_2022_PROGRAM_ID)
  );
}
function transferFeeAt(config, epoch) {
  const fee2 = (0, import_spl_token3.getEpochFee)(config, BigInt(epoch));
  return {
    basisPoints: fee2.transferFeeBasisPoints,
    maximumFee: new import_bn3.default(fee2.maximumFee.toString())
  };
}
function transferFeeOn(fee2, amount) {
  if (!fee2 || fee2.basisPoints === 0 || amount.isZero()) {
    return new import_bn3.default(0);
  }
  return import_bn3.default.min(
    ceilDiv(amount.muln(fee2.basisPoints), ONE_IN_BASIS_POINTS),
    fee2.maximumFee
  );
}
function netOfTransferFee(fee2, amount) {
  return amount.sub(transferFeeOn(fee2, amount));
}
function grossForTransferFee(fee2, net) {
  if (!fee2 || fee2.basisPoints === 0 || net.isZero()) {
    return net;
  }
  if (fee2.basisPoints === 1e4) {
    return net.add(fee2.maximumFee);
  }
  const raw = ceilDiv(
    net.mul(ONE_IN_BASIS_POINTS),
    ONE_IN_BASIS_POINTS.subn(fee2.basisPoints)
  );
  return raw.sub(net).gte(fee2.maximumFee) ? net.add(fee2.maximumFee) : raw;
}

// src/swap/buy.ts
function buyDebit({
  quoteAmountIn,
  lpFee,
  protocolFee,
  coinCreatorFee,
  quoteTransferFee,
  tradeV2 = false,
  globalConfig,
  isMayhemMode = false
}) {
  const booked = quoteAmountIn.add(lpFee).add(protocolFee).add(coinCreatorFee);
  const buybackFee = tradeV2 && !isMayhemMode ? protocolFee.mul(globalConfig.buybackBasisPoints).divn(1e4) : new import_bn4.default(0);
  const vault = tradeV2 ? booked.sub(buybackFee) : quoteAmountIn.add(lpFee);
  return booked.add(grossForTransferFee(quoteTransferFee, vault).sub(vault));
}
function exactQuoteInFees(spendableQuoteIn, {
  lpFeeBps,
  protocolFeeBps,
  creatorFeeBps
}) {
  const totalFeeBps = lpFeeBps.add(protocolFeeBps).add(creatorFeeBps);
  let netQuoteForSwap = spendableQuoteIn.muln(1e4).div(totalFeeBps.addn(1e4));
  if (netQuoteForSwap.lten(0)) {
    throw new Error("The quote budget does not cover the fees.");
  }
  const lpFee = fee(netQuoteForSwap, lpFeeBps);
  const protocolFee = fee(netQuoteForSwap, protocolFeeBps);
  const coinCreatorFee = fee(netQuoteForSwap, creatorFeeBps);
  const excess = netQuoteForSwap.add(lpFee).add(protocolFee).add(coinCreatorFee).sub(spendableQuoteIn);
  if (excess.gtn(0)) {
    netQuoteForSwap = netQuoteForSwap.sub(excess);
    if (netQuoteForSwap.lten(0)) {
      throw new Error("The quote budget does not cover the fees.");
    }
  }
  return { netQuoteForSwap, lpFee, protocolFee, coinCreatorFee };
}
function buyBaseInput({
  base,
  slippage,
  baseReserve,
  quoteReserve,
  virtualQuoteReserves = new import_bn4.default(0),
  globalConfig,
  baseMintAccount,
  baseMint,
  coinCreator,
  creator,
  feeConfig,
  quoteMint,
  isMayhemMode,
  creatorFeeBps,
  quoteTransferFee,
  tradeV2
}) {
  if (baseReserve.isZero() || quoteReserve.isZero()) {
    throw new Error(
      "Invalid input: 'baseReserve' or 'quoteReserve' cannot be zero."
    );
  }
  if (base.gt(baseReserve)) {
    throw new Error("Cannot buy more base tokens than the pool reserves.");
  }
  const effectiveQuoteReserve = quoteReserve.add(virtualQuoteReserves);
  const numerator = effectiveQuoteReserve.mul(base);
  const denominator = baseReserve.sub(base);
  if (denominator.isZero()) {
    throw new Error("Pool would be depleted; denominator is zero.");
  }
  const quoteAmountIn = ceilDiv(numerator, denominator);
  const {
    lpFeeBps,
    protocolFeeBps,
    creatorFeeBps: coinCreatorFeeBps
  } = computeFeesBps({
    globalConfig,
    feeConfig,
    creator,
    baseMintSupply: new import_bn4.default(baseMintAccount.supply.toString()),
    baseMint,
    baseReserve,
    quoteReserve: effectiveQuoteReserve,
    quoteMint,
    isMayhemMode,
    creatorFeeBps
  });
  const lpFee = fee(quoteAmountIn, lpFeeBps);
  const protocolFee = fee(quoteAmountIn, protocolFeeBps);
  const coinCreatorFee = import_web33.PublicKey.default.equals(coinCreator) ? new import_bn4.default(0) : fee(quoteAmountIn, coinCreatorFeeBps);
  const totalQuote = buyDebit({
    quoteAmountIn,
    lpFee,
    protocolFee,
    coinCreatorFee,
    quoteTransferFee,
    tradeV2,
    globalConfig,
    isMayhemMode
  });
  const precision = new import_bn4.default(1e9);
  const slippageFactorFloat = (1 + slippage / 100) * 1e9;
  const slippageFactor = new import_bn4.default(Math.floor(slippageFactorFloat));
  const maxQuote = totalQuote.mul(slippageFactor).div(precision);
  return {
    internalQuoteAmount: quoteAmountIn,
    uiQuote: totalQuote,
    // Final total quote after fees
    maxQuote
  };
}
function buyQuoteInput({
  quote,
  slippage,
  baseReserve,
  quoteReserve,
  virtualQuoteReserves = new import_bn4.default(0),
  globalConfig,
  baseMintAccount,
  baseMint,
  coinCreator,
  creator,
  feeConfig,
  quoteMint,
  isMayhemMode,
  creatorFeeBps,
  quoteTransferFee,
  tradeV2
}) {
  if (baseReserve.isZero() || quoteReserve.isZero()) {
    throw new Error(
      "Invalid input: 'baseReserve' or 'quoteReserve' cannot be zero."
    );
  }
  const effectiveQuoteReserve = quoteReserve.add(virtualQuoteReserves);
  const {
    lpFeeBps,
    protocolFeeBps,
    creatorFeeBps: coinCreatorFeeBps
  } = computeFeesBps({
    globalConfig,
    feeConfig,
    creator,
    baseMintSupply: new import_bn4.default(baseMintAccount.supply.toString()),
    baseMint,
    baseReserve,
    quoteReserve: effectiveQuoteReserve,
    quoteMint,
    isMayhemMode,
    creatorFeeBps
  });
  const totalFeeBps = lpFeeBps.add(protocolFeeBps).add(import_web33.PublicKey.default.equals(coinCreator) ? new import_bn4.default(0) : coinCreatorFeeBps);
  const denominator = new import_bn4.default(1e4).add(totalFeeBps);
  const spendable = netOfTransferFee(quoteTransferFee, quote);
  if (spendable.lten(0)) {
    throw new Error("The quote budget does not cover the transfer fee.");
  }
  let effectiveQuote = spendable.mul(new import_bn4.default(1e4)).div(denominator);
  const lpFee = fee(effectiveQuote, lpFeeBps);
  const protocolFee = fee(effectiveQuote, protocolFeeBps);
  const coinCreatorFee = import_web33.PublicKey.default.equals(coinCreator) ? new import_bn4.default(0) : fee(effectiveQuote, coinCreatorFeeBps);
  const totalWithFees = effectiveQuote.add(lpFee).add(protocolFee).add(coinCreatorFee);
  if (totalWithFees.gt(spendable)) {
    effectiveQuote = effectiveQuote.sub(totalWithFees.sub(spendable));
  }
  const debit = buyDebit({
    quoteAmountIn: effectiveQuote,
    lpFee,
    protocolFee,
    coinCreatorFee,
    quoteTransferFee,
    tradeV2,
    globalConfig,
    isMayhemMode
  });
  if (debit.gt(quote)) {
    effectiveQuote = effectiveQuote.sub(debit.sub(quote));
  }
  if (effectiveQuote.lten(0)) {
    throw new Error("The quote budget does not cover the fees.");
  }
  const inputAmount = effectiveQuote.subn(1);
  const numerator = baseReserve.mul(inputAmount);
  const denominatorEffective = effectiveQuoteReserve.add(inputAmount);
  if (denominatorEffective.isZero()) {
    throw new Error("Pool would be depleted; denominator is zero.");
  }
  const baseAmountOut = numerator.div(denominatorEffective);
  const precision = new import_bn4.default(1e9);
  const slippageFactorFloat = (1 + slippage / 100) * 1e9;
  const slippageFactor = new import_bn4.default(Math.floor(slippageFactorFloat));
  const maxQuote = quote.mul(slippageFactor).div(precision);
  return {
    base: baseAmountOut,
    // Base tokens received after fees
    internalQuoteWithoutFees: effectiveQuote,
    maxQuote
    // Maximum quote tokens to pay (with slippage)
  };
}

// src/swap/deposit.ts
var import_bn5 = __toESM(require("bn.js"));
function depositToken0(token0, slippage, token0Reserve, token1Reserve, totalLpTokens) {
  if (slippage < 0 || slippage > 100) {
    throw new Error("Slippage must be between 0 and 100 (0% to 100%)");
  }
  const token1 = token0.mul(token1Reserve).div(token0Reserve);
  const slippageFactor = new import_bn5.default((1 + slippage / 100) * 1e9);
  const maxToken0 = token0.mul(slippageFactor).div(new import_bn5.default(1e9));
  const maxToken1 = token1.mul(slippageFactor).div(new import_bn5.default(1e9));
  const lpToken = token0.mul(totalLpTokens).div(token0Reserve);
  return {
    token1,
    lpToken,
    maxToken0,
    maxToken1
  };
}
function ceilDiv2(numerator, denominator) {
  return numerator.add(denominator).sub(new import_bn5.default(1)).div(denominator);
}
function depositLpToken(lpToken, slippage, baseReserve, quoteReserve, totalLpTokens, quoteTransferFee) {
  if (totalLpTokens.isZero()) {
    throw new Error("Division by zero: totalLpTokens cannot be zero");
  }
  const baseAmountIn = ceilDiv2(baseReserve.mul(lpToken), totalLpTokens);
  const quoteAmountIn = grossForTransferFee(
    quoteTransferFee,
    ceilDiv2(quoteReserve.mul(lpToken), totalLpTokens)
  );
  const slippageFactor = new import_bn5.default((1 + slippage / 100) * 1e9);
  const slippageDenominator = new import_bn5.default(1e9);
  const maxBase = baseAmountIn.mul(slippageFactor).div(slippageDenominator);
  const maxQuote = quoteAmountIn.mul(slippageFactor).div(slippageDenominator);
  return {
    maxBase,
    maxQuote
  };
}

// src/swap/multiHop.ts
var import_spl_token4 = require("@solana/spl-token");
var import_web35 = require("@solana/web3.js");
var import_bn7 = __toESM(require("bn.js"));

// src/swap/sell.ts
var import_web34 = require("@solana/web3.js");
var import_bn6 = __toESM(require("bn.js"));
function sellBaseInput({
  base,
  slippage,
  baseReserve,
  quoteReserve,
  virtualQuoteReserves = new import_bn6.default(0),
  feeBucketsTotal = new import_bn6.default(0),
  globalConfig,
  baseMintAccount,
  baseMint,
  coinCreator,
  creator,
  feeConfig,
  quoteMint,
  isMayhemMode,
  creatorFeeBps,
  quoteTransferFee
}) {
  if (baseReserve.isZero() || quoteReserve.isZero()) {
    throw new Error(
      "Invalid input: 'baseReserve' or 'quoteReserve' cannot be zero."
    );
  }
  const effectiveQuoteReserve = quoteReserve.add(virtualQuoteReserves);
  const quoteAmountOut = effectiveQuoteReserve.mul(base).div(baseReserve.add(base));
  const {
    lpFeeBps,
    protocolFeeBps,
    creatorFeeBps: coinCreatorFeeBps
  } = computeFeesBps({
    globalConfig,
    feeConfig,
    creator,
    baseMintSupply: new import_bn6.default(baseMintAccount.supply.toString()),
    baseMint,
    baseReserve,
    quoteReserve: effectiveQuoteReserve,
    quoteMint,
    isMayhemMode,
    creatorFeeBps
  });
  const lpFee = fee(quoteAmountOut, lpFeeBps);
  const protocolFee = fee(quoteAmountOut, protocolFeeBps);
  const coinCreatorFee = import_web34.PublicKey.default.equals(coinCreator) ? new import_bn6.default(0) : fee(quoteAmountOut, coinCreatorFeeBps);
  const { userQuoteAmountOut } = sellAmounts(
    quoteAmountOut,
    { lpFee, protocolFee, coinCreatorFee },
    quoteReserve.sub(feeBucketsTotal)
  );
  const finalQuote = netOfTransferFee(quoteTransferFee, userQuoteAmountOut);
  if (finalQuote.isNeg()) {
    throw new Error("Fees exceed total output; final quote is negative.");
  }
  const precision = new import_bn6.default(1e9);
  const slippageFactorFloat = (1 - slippage / 100) * 1e9;
  const slippageFactor = new import_bn6.default(Math.floor(slippageFactorFloat));
  const minQuote = finalQuote.mul(slippageFactor).div(precision);
  return {
    uiQuote: finalQuote,
    // actual tokens user receives after fees
    minQuote,
    // minimum acceptable tokens after applying slippage
    internalQuoteAmountOut: quoteAmountOut
  };
}
function sellAmounts(quoteAmountOut, fees, realQuoteReserves) {
  const quoteAmountOutWithoutLpFee = quoteAmountOut.sub(fees.lpFee);
  if (realQuoteReserves.lt(quoteAmountOutWithoutLpFee)) {
    throw new Error(
      "Insufficient real quote reserves to cover the sell output."
    );
  }
  return {
    quoteAmountOutWithoutLpFee,
    userQuoteAmountOut: quoteAmountOutWithoutLpFee.sub(fees.coinCreatorFee).sub(fees.protocolFee)
  };
}
var MAX_FEE_BASIS_POINTS = new import_bn6.default(1e4);
function calculateQuoteAmountOut(userQuoteAmountOut, lpFeeBasisPoints, protocolFeeBasisPoints, coinCreatorFeeBasisPoints) {
  const totalFeeBasisPoints = lpFeeBasisPoints.add(protocolFeeBasisPoints).add(coinCreatorFeeBasisPoints);
  const denominator = MAX_FEE_BASIS_POINTS.sub(totalFeeBasisPoints);
  return ceilDiv(userQuoteAmountOut.mul(MAX_FEE_BASIS_POINTS), denominator);
}
function sellQuoteInput({
  quote,
  slippage,
  baseReserve,
  quoteReserve,
  virtualQuoteReserves = new import_bn6.default(0),
  feeBucketsTotal = new import_bn6.default(0),
  globalConfig,
  baseMintAccount,
  baseMint,
  coinCreator,
  creator,
  feeConfig,
  quoteMint,
  isMayhemMode,
  creatorFeeBps,
  quoteTransferFee
}) {
  if (baseReserve.isZero() || quoteReserve.isZero()) {
    throw new Error(
      "Invalid input: 'baseReserve' or 'quoteReserve' cannot be zero."
    );
  }
  const effectiveQuoteReserve = quoteReserve.add(virtualQuoteReserves);
  const {
    lpFeeBps,
    protocolFeeBps,
    creatorFeeBps: coinCreatorFeeBps
  } = computeFeesBps({
    globalConfig,
    feeConfig,
    creator,
    baseMintSupply: new import_bn6.default(baseMintAccount.supply.toString()),
    baseMint,
    baseReserve,
    quoteReserve: effectiveQuoteReserve,
    quoteMint,
    isMayhemMode,
    creatorFeeBps
  });
  const rawQuote = calculateQuoteAmountOut(
    grossForTransferFee(quoteTransferFee, quote),
    lpFeeBps,
    protocolFeeBps,
    import_web34.PublicKey.default.equals(coinCreator) ? new import_bn6.default(0) : coinCreatorFeeBps
  );
  if (rawQuote.gte(effectiveQuoteReserve)) {
    throw new Error(
      "Invalid input: Desired quote amount exceeds available reserve."
    );
  }
  const baseAmountIn = ceilDiv(
    baseReserve.mul(rawQuote),
    effectiveQuoteReserve.sub(rawQuote)
  );
  const quoteAmountOut = effectiveQuoteReserve.mul(baseAmountIn).div(baseReserve.add(baseAmountIn));
  if (quoteReserve.sub(feeBucketsTotal).lt(quoteAmountOut.sub(fee(quoteAmountOut, lpFeeBps)))) {
    throw new Error(
      "Insufficient real quote reserves to cover the sell output."
    );
  }
  const precision = new import_bn6.default(1e9);
  const slippageFactorFloat = (1 - slippage / 100) * 1e9;
  const slippageFactor = new import_bn6.default(Math.floor(slippageFactorFloat));
  const minQuote = quote.mul(slippageFactor).div(precision);
  return {
    internalRawQuote: rawQuote,
    base: baseAmountIn,
    // amount of base tokens required to get the desired quote
    minQuote
    // minimum acceptable tokens after applying slippage
  };
}

// src/swap/multiHop.ts
var MULTI_HOP_MAX_HOPS = 6;
var MULTI_HOP_MAX_POOLS_AT_MAX_HOPS = 3;
function isSolCurve(venue) {
  return venue.kind === "curve" && canonicalPoolQuoteMint(venue.quoteMint).equals(import_spl_token4.NATIVE_MINT);
}
function venueMints(venue) {
  if (venue.kind === "pool") {
    return venue.pool;
  }
  return {
    baseMint: venue.baseMint,
    quoteMint: canonicalPoolQuoteMint(venue.quoteMint)
  };
}
function venueQuoteTokenProgram(venue) {
  return isSolCurve(venue) ? import_spl_token4.TOKEN_PROGRAM_ID : venue.quoteTokenProgram;
}
function multiHopLegFees(isBuy, index, hops, isPool = true) {
  const first = index === 0;
  const last = index + 1 === hops;
  const [protocol, target] = isBuy ? [first, last] : [last, first];
  return { protocol, creator: target, lp: target && isPool };
}
function resolveMultiHopRoute(inMint, venues) {
  const hops = venues.length;
  if (hops === 0) {
    throw new Error("A multi-hop route needs at least one hop.");
  }
  const pools = venues.filter((venue) => venue.kind === "pool").length;
  if (hops > MULTI_HOP_MAX_HOPS || hops === MULTI_HOP_MAX_HOPS && pools > MULTI_HOP_MAX_POOLS_AT_MAX_HOPS) {
    throw new Error(
      `A ${hops}-hop route with ${pools} pool hops exceeds the programs' heap (at most ${MULTI_HOP_MAX_HOPS} hops, ${MULTI_HOP_MAX_POOLS_AT_MAX_HOPS} of them pools at that length).`
    );
  }
  inMint = canonicalPoolQuoteMint(inMint);
  const { quoteMint: firstQuote } = venueMints(venues[0]);
  const isBuy = inMint.equals(firstQuote);
  const mints = [inMint];
  const legs = venues.map((venue, i) => {
    const { baseMint, quoteMint } = venueMints(venue);
    const running = mints[i];
    const hopIsBuy = running.equals(quoteMint);
    if (!hopIsBuy && !running.equals(baseMint)) {
      throw new Error(
        `Hop ${i} trades ${baseMint.toBase58()}/${quoteMint.toBase58()}, not the running mint ${running.toBase58()}.`
      );
    }
    if (hopIsBuy !== isBuy) {
      throw new Error(
        "Every hop of a multi-hop route must trade in the same direction."
      );
    }
    mints.push(hopIsBuy ? baseMint : quoteMint);
    const hopLegs = multiHopLegFees(isBuy, i, hops, venue.kind === "pool");
    if (venue.kind === "curve") {
      return hopLegs;
    }
    const { pool, poolKey } = venue;
    if (!isPumpPool(pool.baseMint, pool.creator)) {
      throw new Error(
        `Hop ${i}: pool ${poolKey.toBase58()} is not a canonical pump pool.`
      );
    }
    if (pool.isMayhemMode) {
      throw new Error(`Hop ${i}: pool ${poolKey.toBase58()} is a mayhem pool.`);
    }
    if (pool.isCashbackCoin && hopLegs.creator) {
      throw new Error(
        `Hop ${i}: cashback pool ${poolKey.toBase58()} cannot charge the creator fee.`
      );
    }
    return hopLegs;
  });
  return { isBuy, mints, legs };
}
function multiHopSwapQuote({
  inMint,
  hops,
  amountIn,
  slippage,
  globalConfig,
  feeConfig
}) {
  if (amountIn.lten(0)) {
    throw new Error("amountIn must be positive.");
  }
  const { isBuy, legs } = resolveMultiHopRoute(inMint, hops);
  const hopAmountsOut = [];
  let amount = amountIn;
  hops.forEach((hop, i) => {
    amount = hop.kind === "pool" ? poolHopAmountOut(hop, isBuy, amount, legs[i], globalConfig, feeConfig) : hop.quote(amount, { isBuy, legs: legs[i] });
    hopAmountsOut.push(amount);
  });
  const slippageFactor = new import_bn7.default(Math.floor((1 - slippage / 100) * 1e9));
  const minAmountOut = amount.mul(slippageFactor).div(new import_bn7.default(1e9));
  return {
    amountOut: amount,
    minAmountOut: import_bn7.default.max(minAmountOut, new import_bn7.default(1)),
    hopAmountsOut
  };
}
function poolHopAmountOut(hop, isBuy, amountIn, legs, globalConfig, feeConfig) {
  const { pool, poolBaseAmount: baseReserve, poolQuoteAmount } = hop;
  const quoteReserve = poolQuoteAmount.add(pool.virtualQuoteReserves);
  const rates = computeFeesBps({
    globalConfig,
    feeConfig,
    creator: pool.creator,
    baseMintSupply: hop.baseMintSupply,
    baseMint: pool.baseMint,
    baseReserve,
    quoteReserve,
    quoteMint: pool.quoteMint,
    isMayhemMode: pool.isMayhemMode,
    creatorFeeBps: pool.creatorFeeBps
  });
  const zero = new import_bn7.default(0);
  const masked = {
    lpFeeBps: legs.lp ? rates.lpFeeBps : zero,
    protocolFeeBps: legs.protocol ? rates.protocolFeeBps : zero,
    creatorFeeBps: legs.creator && !pool.coinCreator.equals(import_web35.PublicKey.default) ? rates.creatorFeeBps : zero
  };
  if (isBuy) {
    const received = netOfTransferFee(hop.quoteTransferFee, amountIn);
    const { lpFee, protocolFee, coinCreatorFee } = exactQuoteInFees(
      received,
      masked
    );
    const input = received.sub(lpFee).sub(protocolFee).sub(coinCreatorFee);
    const baseOut = baseReserve.mul(input.subn(1)).div(quoteReserve.add(input.subn(1)));
    if (baseOut.lten(0) || baseOut.gt(baseReserve)) {
      throw new Error("The hop buys no base tokens.");
    }
    return baseOut;
  }
  const quoteOut = quoteReserve.mul(amountIn).div(baseReserve.add(amountIn));
  const { userQuoteAmountOut } = sellAmounts(
    quoteOut,
    {
      lpFee: fee(quoteOut, masked.lpFeeBps),
      protocolFee: fee(quoteOut, masked.protocolFeeBps),
      coinCreatorFee: fee(quoteOut, masked.creatorFeeBps)
    },
    poolQuoteAmount.sub(pool.protocolFees).sub(pool.creatorFees)
  );
  if (userQuoteAmountOut.lten(0)) {
    throw new Error("The hop sells for no quote tokens.");
  }
  return netOfTransferFee(hop.quoteTransferFee, userQuoteAmountOut);
}

// src/swap/withdraw.ts
var import_bn8 = __toESM(require("bn.js"));
function withdraw(lpAmount, slippage, baseReserve, quoteReserve, totalLpTokens, quoteTransferFee) {
  if (lpAmount.isZero() || totalLpTokens.isZero()) {
    throw new Error("LP amount or total LP tokens cannot be zero.");
  }
  const base = baseReserve.mul(lpAmount).div(totalLpTokens);
  const quote = netOfTransferFee(
    quoteTransferFee,
    quoteReserve.mul(lpAmount).div(totalLpTokens)
  );
  const scaleFactor = new import_bn8.default(1e9);
  const slippageFactor = new import_bn8.default((1 - slippage / 100) * 1e9);
  const minBase = base.mul(slippageFactor).div(scaleFactor);
  const minQuote = quote.mul(slippageFactor).div(scaleFactor);
  return {
    base,
    quote,
    minBase,
    minQuote
  };
}

// src/swap/offlinePumpAmm.ts
var POOL_ACCOUNT_NEW_SIZE = 300;
var POOL_SIZE = 287;
var GLOBAL_CONFIG_SIZE = 949;
var FEE_CONFIG_SIZE_PRE_STABLE = 2512;
var FEE_CONFIG_SIZE_POST_STABLE = 4073;
var FEE_CONFIG_SIZE_POST_EXOTIC = 4097;
var FEE_CONFIG_FEE_TIERS_OFFSET = 8 + 1 + 32 + 24;
var FEES_SIZE = 24;
var FEE_TIER_SIZE = 16 + FEES_SIZE;
function padTrailing(data, size) {
  return data.length >= size ? data : Buffer.concat([data, Buffer.alloc(size - data.length)]);
}
function feeTierVecEnd(data, offset) {
  if (offset + 4 > data.length) {
    throw new Error(
      `FeeConfig fee tier vector length at offset ${offset} runs past the account data (${data.length} bytes)`
    );
  }
  const end = offset + 4 + data.readUInt32LE(offset) * FEE_TIER_SIZE;
  if (end > data.length) {
    throw new Error(
      `FeeConfig fee tier vector at offset ${offset} runs past the account data (${data.length} bytes)`
    );
  }
  return end;
}
function versionedFeeConfigData(data) {
  if (data.length < FEE_CONFIG_SIZE_PRE_STABLE) {
    throw new Error(
      `FeeConfig account is ${data.length} bytes; expected at least ${FEE_CONFIG_SIZE_PRE_STABLE}`
    );
  }
  let end = feeTierVecEnd(data, FEE_CONFIG_FEE_TIERS_OFFSET);
  if (data.length >= FEE_CONFIG_SIZE_POST_STABLE) {
    end = feeTierVecEnd(data, end);
  }
  if (data.length >= FEE_CONFIG_SIZE_POST_EXOTIC) {
    end += FEES_SIZE;
    if (end > data.length) {
      throw new Error(
        `FeeConfig exotic flat fees run past the account data (${data.length} bytes)`
      );
    }
  }
  return padTrailing(data.subarray(0, end), FEE_CONFIG_SIZE_POST_EXOTIC);
}
var OFFLINE_PUMP_AMM_PROGRAM = getPumpAmmProgram(
  null
);
var PumpAmmSdk = class {
  constructor() {
    this.offlineProgram = OFFLINE_PUMP_AMM_PROGRAM;
  }
  decodeGlobalConfig(globalConfigAccountInfo) {
    return this.offlineProgram.coder.accounts.decode(
      "globalConfig",
      padTrailing(
        globalConfigAccountInfo.data,
        this.offlineProgram.account.globalConfig.size
      )
    );
  }
  decodeFeeConfig(feeConfigAccountInfo) {
    return this.offlineProgram.coder.accounts.decode(
      "feeConfig",
      versionedFeeConfigData(feeConfigAccountInfo.data)
    );
  }
  decodePool(poolAccountInfo) {
    return this.offlineProgram.coder.accounts.decode(
      "pool",
      padTrailing(poolAccountInfo.data, this.offlineProgram.account.pool.size)
    );
  }
  decodePoolNullable(poolAccountInfo) {
    try {
      return this.decodePool(poolAccountInfo);
    } catch (error) {
      console.warn("Failed to decode pool account", error);
      return null;
    }
  }
  decodeGlobalVolumeAccumulator(globalVolumeAccumulatorAccountInfo) {
    return this.offlineProgram.coder.accounts.decode(
      "globalVolumeAccumulator",
      globalVolumeAccumulatorAccountInfo.data
    );
  }
  decodeUserVolumeAccumulator(userVolumeAccumulatorAccountInfo) {
    return this.offlineProgram.coder.accounts.decode(
      "userVolumeAccumulator",
      userVolumeAccumulatorAccountInfo.data
    );
  }
  decodeUserVolumeAccumulatorNullable(userVolumeAccumulatorAccountInfo) {
    try {
      return this.decodeUserVolumeAccumulator(userVolumeAccumulatorAccountInfo);
    } catch (error) {
      console.warn("Failed to decode user volume accumulator", error);
      return null;
    }
  }
  /**
   * Builds `create_pool` (plus the pool ATA creates and wSOL wrapping it needs) for a
   * permissionless pool: `coin_creator` is the default key and `creator` is a wallet signer (a
   * canonical pump pool's creator is pump's pool-authority PDA, which signs only through pump's
   * `migrate` / `migrate_v2` CPI). `creatorFeeBps`, `canEditCreatorFee` and `isHolderReward` are
   * the instruction's three trailing arguments, always encoded (0 / false when unset), so
   * `create_pool` data is 10 bytes longer than before they existed; the program ignores trailing
   * bytes it does not read. The program stores the values for canonical pools only: a nonzero /
   * true `creatorFeeBps` / `canEditCreatorFee` on a permissionless pool fails with
   * `OnlyCanonicalPumpPoolsCanHaveCoinCreator`, and `isHolderReward` is stored as false on one.
   * The options exist to keep the encoding aligned with the IDL; canonical pools receive the
   * bonding curve's values from `migrate` / `migrate_v2`.
   */
  async createPoolInstructions(createPoolSolanaState, baseIn, quoteIn, {
    creatorFeeBps = new import_bn9.default(0),
    canEditCreatorFee = false,
    isHolderReward = false
  } = {}) {
    const {
      index,
      creator,
      baseMint,
      quoteMint,
      poolKey,
      baseTokenProgram,
      quoteTokenProgram,
      userBaseTokenAccount,
      userQuoteTokenAccount,
      poolBaseTokenAccount,
      poolQuoteTokenAccount,
      userBaseAccountInfo,
      userQuoteAccountInfo,
      poolBaseAccountInfo,
      poolQuoteAccountInfo
    } = createPoolSolanaState;
    return await this.withWsolAccounts(
      creator,
      baseMint,
      userBaseTokenAccount,
      this.accountExists(userBaseAccountInfo, baseTokenProgram),
      baseIn,
      quoteMint,
      userQuoteTokenAccount,
      this.accountExists(userQuoteAccountInfo, quoteTokenProgram),
      quoteIn,
      async () => {
        const instructions = [];
        if (!this.accountExists(poolBaseAccountInfo, baseTokenProgram)) {
          instructions.push(
            (0, import_spl_token5.createAssociatedTokenAccountIdempotentInstruction)(
              creator,
              poolBaseTokenAccount,
              poolKey,
              baseMint,
              baseTokenProgram
            )
          );
        }
        if (!this.accountExists(poolQuoteAccountInfo, quoteTokenProgram)) {
          instructions.push(
            (0, import_spl_token5.createAssociatedTokenAccountIdempotentInstruction)(
              creator,
              poolQuoteTokenAccount,
              poolKey,
              quoteMint,
              quoteTokenProgram
            )
          );
        }
        instructions.push(
          await this.offlineProgram.methods.createPool(
            index,
            baseIn,
            quoteIn,
            import_web36.SystemProgram.programId,
            false,
            { 0: false },
            { 0: creatorFeeBps },
            { 0: canEditCreatorFee },
            { 0: isHolderReward }
          ).accountsPartial({
            globalConfig: GLOBAL_CONFIG_PDA,
            baseMint,
            quoteMint,
            creator,
            userBaseTokenAccount,
            userQuoteTokenAccount,
            baseTokenProgram,
            quoteTokenProgram
          }).instruction()
        );
        return instructions;
      }
    );
  }
  async depositInstructionsInternal(liquiditySolanaState, lpToken, maxBase, maxQuote) {
    const {
      pool,
      user,
      userPoolAccountInfo,
      userBaseTokenAccount,
      userQuoteTokenAccount,
      userPoolTokenAccount,
      userBaseAccountInfo,
      userQuoteAccountInfo,
      baseTokenProgram,
      quoteTokenProgram
    } = liquiditySolanaState;
    const { baseMint, quoteMint, lpMint } = pool;
    const liquidityAccounts = this.liquidityAccounts(liquiditySolanaState);
    return await this.withFixPoolInstructions(
      liquiditySolanaState,
      async () => {
        return await this.withWsolAccounts(
          user,
          baseMint,
          userBaseTokenAccount,
          this.accountExists(userBaseAccountInfo, baseTokenProgram),
          maxBase,
          quoteMint,
          userQuoteTokenAccount,
          this.accountExists(userQuoteAccountInfo, quoteTokenProgram),
          maxQuote,
          async () => {
            const instructions = [];
            if (!this.accountExists(userPoolAccountInfo, import_spl_token5.TOKEN_2022_PROGRAM_ID)) {
              instructions.push(
                (0, import_spl_token5.createAssociatedTokenAccountIdempotentInstruction)(
                  user,
                  userPoolTokenAccount,
                  user,
                  lpMint,
                  import_spl_token5.TOKEN_2022_PROGRAM_ID
                )
              );
            }
            instructions.push(
              await this.offlineProgram.methods.deposit(lpToken, maxBase, maxQuote).accounts(liquidityAccounts).instruction()
            );
            return instructions;
          }
        );
      }
    );
  }
  async withWsolAccounts(user, baseMint, userBaseAta, userBaseAtaExists, baseAmount, quoteMint, userQuoteAta, userQuoteAtaExists, quoteAmount, block) {
    return await this.withWsolAccount(
      user,
      user,
      baseMint,
      userBaseAta,
      userBaseAtaExists,
      baseAmount,
      async () => this.withWsolAccount(
        user,
        user,
        quoteMint,
        userQuoteAta,
        userQuoteAtaExists,
        quoteAmount,
        block
      )
    );
  }
  /**
   * Creates `ata` (the associated token account of `owner` for `mint` under `tokenProgram`) when
   * it does not exist yet; any mint and either token program.
   */
  ensureAtaInstructions(payer, owner, mint, ata, ataExists, tokenProgram) {
    return ataExists ? [] : [
      (0, import_spl_token5.createAssociatedTokenAccountIdempotentInstruction)(
        payer,
        ata,
        owner,
        mint,
        tokenProgram
      )
    ];
  }
  /**
   * Runs `block` with the wSOL handling a legacy-WSOL leg needs: the user's wSOL ATA is created
   * when missing, funded with `amount` lamports and closed again afterwards to unwrap. For any
   * other mint `block` runs alone; that ATA holds the user's own tokens and is left as is.
   */
  async withWsolAccount(payer, user, mint, ata, ataExists, amount, block) {
    const instructions = [];
    if (mint.equals(import_spl_token5.NATIVE_MINT)) {
      instructions.push(
        ...this.ensureAtaInstructions(
          payer,
          user,
          import_spl_token5.NATIVE_MINT,
          ata,
          ataExists,
          import_spl_token5.TOKEN_PROGRAM_ID
        )
      );
      if (amount.gtn(0)) {
        instructions.push(
          import_web36.SystemProgram.transfer({
            fromPubkey: user,
            toPubkey: ata,
            lamports: BigInt(amount.toString())
          }),
          (0, import_spl_token5.createSyncNativeInstruction)(ata)
        );
      }
    }
    const blockInstructions = await block();
    instructions.push(...blockInstructions);
    if (mint.equals(import_spl_token5.NATIVE_MINT)) {
      instructions.push(
        (0, import_spl_token5.createCloseAccountInstruction)(
          ata,
          user,
          user,
          void 0,
          import_spl_token5.TOKEN_PROGRAM_ID
        )
      );
    }
    return instructions;
  }
  accountExists(accountInfo, owner) {
    return accountInfo !== null && accountInfo.owner.equals(owner);
  }
  depositBaseInput(liquiditySolanaState, base, slippage) {
    const { pool, poolBaseTokenAccount, quoteTransferFee } = liquiditySolanaState;
    const { token1, lpToken, maxToken0, maxToken1 } = depositToken0(
      base,
      slippage,
      new import_bn9.default(poolBaseTokenAccount.amount.toString()),
      this.realQuoteReserves(liquiditySolanaState),
      pool.lpSupply
    );
    return {
      quote: grossForTransferFee(quoteTransferFee, token1),
      lpToken,
      maxBase: maxToken0,
      maxQuote: grossForTransferFee(quoteTransferFee, maxToken1)
    };
  }
  depositQuoteInput(liquiditySolanaState, quote, slippage) {
    const { pool, poolBaseTokenAccount, quoteTransferFee } = liquiditySolanaState;
    const { token1, lpToken, maxToken0, maxToken1 } = depositToken0(
      netOfTransferFee(quoteTransferFee, quote),
      slippage,
      this.realQuoteReserves(liquiditySolanaState),
      new import_bn9.default(poolBaseTokenAccount.amount.toString()),
      pool.lpSupply
    );
    return {
      base: token1,
      lpToken,
      maxBase: maxToken1,
      maxQuote: grossForTransferFee(quoteTransferFee, maxToken0)
    };
  }
  async withdrawInstructionsInternal(liquiditySolanaState, lpTokenAmountIn, minBaseAmountOut, minQuoteAmountOut) {
    const {
      pool,
      baseTokenProgram,
      quoteTokenProgram,
      user,
      userBaseAccountInfo,
      userQuoteAccountInfo,
      userBaseTokenAccount,
      userQuoteTokenAccount
    } = liquiditySolanaState;
    const { baseMint, quoteMint } = pool;
    const liquidityAccounts = this.liquidityAccounts(liquiditySolanaState);
    return await this.withFixPoolInstructions(
      liquiditySolanaState,
      async () => {
        const instructions = [];
        let baseWsolAtaCreated = false;
        if (!this.accountExists(userBaseAccountInfo, baseTokenProgram)) {
          instructions.push(
            (0, import_spl_token5.createAssociatedTokenAccountIdempotentInstruction)(
              user,
              userBaseTokenAccount,
              user,
              baseMint,
              baseTokenProgram
            )
          );
          if (baseMint.equals(import_spl_token5.NATIVE_MINT)) {
            baseWsolAtaCreated = true;
          }
        }
        let quoteWsolAtaCreated = false;
        if (!this.accountExists(userQuoteAccountInfo, quoteTokenProgram)) {
          instructions.push(
            (0, import_spl_token5.createAssociatedTokenAccountIdempotentInstruction)(
              user,
              userQuoteTokenAccount,
              user,
              quoteMint,
              quoteTokenProgram
            )
          );
          if (quoteMint.equals(import_spl_token5.NATIVE_MINT)) {
            quoteWsolAtaCreated = true;
          }
        }
        instructions.push(
          await this.offlineProgram.methods.withdraw(lpTokenAmountIn, minBaseAmountOut, minQuoteAmountOut).accounts(liquidityAccounts).instruction()
        );
        if (baseWsolAtaCreated) {
          instructions.push(
            (0, import_spl_token5.createCloseAccountInstruction)(
              userBaseTokenAccount,
              user,
              user,
              void 0,
              import_spl_token5.TOKEN_PROGRAM_ID
            )
          );
        }
        if (quoteWsolAtaCreated) {
          instructions.push(
            (0, import_spl_token5.createCloseAccountInstruction)(
              userQuoteTokenAccount,
              user,
              user,
              void 0,
              import_spl_token5.TOKEN_PROGRAM_ID
            )
          );
        }
        return instructions;
      }
    );
  }
  withdrawInputs(liquiditySolanaState, lpAmount, slippage) {
    const { pool, poolBaseTokenAccount, quoteTransferFee } = liquiditySolanaState;
    return withdraw(
      lpAmount,
      slippage,
      new import_bn9.default(poolBaseTokenAccount.amount.toString()),
      this.realQuoteReserves(liquiditySolanaState),
      pool.lpSupply,
      quoteTransferFee
    );
  }
  /**
   * The pool's quote liquidity: the vault balance less the fee buckets v2 trades left in it,
   * which deposits and withdrawals never touch (pump-amm `real_quote_reserves`).
   */
  realQuoteReserves({
    pool,
    poolQuoteTokenAccount
  }) {
    return new import_bn9.default(poolQuoteTokenAccount.amount.toString()).sub(pool.protocolFees).sub(pool.creatorFees);
  }
  liquidityAccounts(liquiditySolanaState) {
    const {
      poolKey,
      pool,
      user,
      userBaseTokenAccount,
      userQuoteTokenAccount,
      userPoolTokenAccount
    } = liquiditySolanaState;
    const {
      baseMint,
      quoteMint,
      lpMint,
      poolBaseTokenAccount,
      poolQuoteTokenAccount
    } = pool;
    return {
      pool: poolKey,
      globalConfig: GLOBAL_CONFIG_PDA,
      user,
      baseMint,
      quoteMint,
      lpMint,
      userBaseTokenAccount,
      userQuoteTokenAccount,
      userPoolTokenAccount,
      poolBaseTokenAccount,
      poolQuoteTokenAccount,
      tokenProgram: import_spl_token5.TOKEN_PROGRAM_ID,
      token2022Program: import_spl_token5.TOKEN_2022_PROGRAM_ID,
      eventAuthority: PUMP_AMM_EVENT_AUTHORITY_PDA,
      program: PUMP_AMM_PROGRAM_ID
    };
  }
  async buyInstructions(swapSolanaState, baseOut, maxQuoteIn) {
    return await this.withFixPoolInstructions(swapSolanaState, async () => {
      return await this.buyInstructionsNoPool(
        swapSolanaState,
        baseOut,
        maxQuoteIn
      );
    });
  }
  async buyInstructionsNoPool(swapSolanaState, baseOut, maxQuoteIn) {
    const { pool } = swapSolanaState;
    const swapAccounts = this.swapAccounts(swapSolanaState);
    const {
      user,
      quoteMint,
      quoteTokenProgram,
      buybackFeeRecipient,
      buybackFeeRecipientTokenAccount
    } = swapAccounts;
    const poolV2PdaKey = poolV2Pda(pool.baseMint);
    const remainingAccounts = [];
    if (pool.isCashbackCoin) {
      remainingAccounts.push({
        pubkey: (0, import_spl_token5.getAssociatedTokenAddressSync)(
          quoteMint,
          userVolumeAccumulatorPda(user),
          true,
          quoteTokenProgram
        ),
        isWritable: true,
        isSigner: false
      });
    }
    if (!pool.coinCreator.equals(import_web36.PublicKey.default)) {
      remainingAccounts.push({
        pubkey: poolV2PdaKey,
        isWritable: false,
        isSigner: false
      });
    }
    remainingAccounts.push(
      {
        pubkey: buybackFeeRecipient,
        isWritable: false,
        isSigner: false
      },
      {
        pubkey: buybackFeeRecipientTokenAccount,
        isWritable: true,
        isSigner: false
      }
    );
    const instruction = await this.offlineProgram.methods.buy(baseOut, maxQuoteIn, { 0: true }).accounts(swapAccounts).remainingAccounts([...remainingAccounts]).instruction();
    return this.withBuyAccounts(swapSolanaState, maxQuoteIn, instruction);
  }
  /** The buy instruction `swap` with its user-side setup: quote in, base out. */
  withBuyAccounts(swapSolanaState, quoteIn, swap) {
    const { user, pool } = swapSolanaState;
    return this.withSwapUserAccounts(
      user,
      {
        mint: pool.quoteMint,
        account: swapSolanaState.userQuoteTokenAccount,
        tokenProgram: swapSolanaState.quoteTokenProgram,
        accountInfo: swapSolanaState.userQuoteAccountInfo,
        amount: quoteIn
      },
      {
        mint: pool.baseMint,
        account: swapSolanaState.userBaseTokenAccount,
        tokenProgram: swapSolanaState.baseTokenProgram,
        accountInfo: swapSolanaState.userBaseAccountInfo
      },
      swap
    );
  }
  /**
   * The user-side setup around a swap instruction: a legacy-WSOL input is wrapped (`input.amount`
   * lamports; the account is closed again afterwards), the output account is created when it is
   * the user's ATA and `accountInfo` does not show it, and a legacy-WSOL output is closed to
   * unwrap. A custom (non-ATA) account is never created: it must already exist.
   */
  async withSwapUserAccounts(user, input, output, swap) {
    const exists = ({
      mint,
      account,
      tokenProgram,
      accountInfo
    }) => !account.equals(
      (0, import_spl_token5.getAssociatedTokenAddressSync)(mint, user, true, tokenProgram)
    ) || this.accountExists(accountInfo, tokenProgram);
    return this.withWsolAccount(
      user,
      user,
      input.mint,
      input.account,
      exists(input),
      input.amount,
      async () => [
        ...this.ensureAtaInstructions(
          user,
          user,
          output.mint,
          output.account,
          exists(output),
          output.tokenProgram
        ),
        swap,
        ...output.mint.equals(import_spl_token5.NATIVE_MINT) ? [
          (0, import_spl_token5.createCloseAccountInstruction)(
            output.account,
            user,
            user,
            void 0,
            import_spl_token5.TOKEN_PROGRAM_ID
          )
        ] : []
      ]
    );
  }
  async buyBaseInput(swapSolanaState, base, slippage, options = {}) {
    const {
      baseMint,
      baseMintAccount,
      feeConfig,
      globalConfig,
      pool,
      poolBaseAmount,
      poolQuoteAmount
    } = swapSolanaState;
    const { coinCreator, creator } = pool;
    const { maxQuote } = buyBaseInput({
      base,
      slippage,
      quoteTransferFee: swapSolanaState.quoteTransferFee,
      tradeV2: Boolean(options.v2) && supportsTradeV2(pool),
      baseReserve: poolBaseAmount,
      quoteReserve: poolQuoteAmount,
      virtualQuoteReserves: pool.virtualQuoteReserves,
      baseMintAccount,
      baseMint,
      coinCreator,
      creator,
      feeConfig,
      globalConfig,
      quoteMint: pool.quoteMint,
      isMayhemMode: pool.isMayhemMode,
      creatorFeeBps: pool.creatorFeeBps
    });
    return this.routedBuyInstructions(swapSolanaState, base, maxQuote, options);
  }
  async buyQuoteInput(swapSolanaState, quote, slippage, options = {}) {
    const {
      baseMint,
      baseMintAccount,
      feeConfig,
      globalConfig,
      pool,
      poolBaseAmount,
      poolQuoteAmount
    } = swapSolanaState;
    const { coinCreator, creator } = pool;
    const { base, maxQuote } = buyQuoteInput({
      quote,
      slippage,
      quoteTransferFee: swapSolanaState.quoteTransferFee,
      tradeV2: Boolean(options.v2) && supportsTradeV2(pool),
      baseReserve: poolBaseAmount,
      quoteReserve: poolQuoteAmount,
      virtualQuoteReserves: pool.virtualQuoteReserves,
      baseMintAccount,
      baseMint,
      coinCreator,
      creator,
      feeConfig,
      globalConfig,
      quoteMint: pool.quoteMint,
      isMayhemMode: pool.isMayhemMode,
      creatorFeeBps: pool.creatorFeeBps
    });
    return this.routedBuyInstructions(swapSolanaState, base, maxQuote, options);
  }
  async sellInstructions(swapSolanaState, baseAmountIn, minQuoteAmountOut) {
    return await this.withFixPoolInstructions(swapSolanaState, async () => {
      return await this.sellInstructionsNoPool(
        swapSolanaState,
        baseAmountIn,
        minQuoteAmountOut
      );
    });
  }
  async withFixPoolInstructions(commonSolanaState, block) {
    const { poolAccountInfo, poolKey, user } = commonSolanaState;
    const instructions = [];
    if (poolAccountInfo === null || poolAccountInfo.data.length < POOL_ACCOUNT_NEW_SIZE) {
      instructions.push(
        await this.offlineProgram.methods.extendAccount().accountsPartial({
          account: poolKey,
          user
        }).instruction()
      );
    }
    return [...instructions, ...await block()];
  }
  async sellInstructionsNoPool(swapSolanaState, baseAmountIn, minQuoteAmountOut) {
    const { pool } = swapSolanaState;
    const swapAccounts = this.swapAccounts(swapSolanaState);
    const poolV2PdaKey = poolV2Pda(pool.baseMint);
    const {
      user,
      quoteMint,
      quoteTokenProgram,
      buybackFeeRecipient,
      buybackFeeRecipientTokenAccount
    } = swapAccounts;
    const remainingAccounts = [];
    if (pool.isCashbackCoin) {
      remainingAccounts.push(
        {
          pubkey: (0, import_spl_token5.getAssociatedTokenAddressSync)(
            quoteMint,
            userVolumeAccumulatorPda(user),
            true,
            quoteTokenProgram
          ),
          isWritable: true,
          isSigner: false
        },
        {
          pubkey: userVolumeAccumulatorPda(user),
          isWritable: true,
          isSigner: false
        }
      );
    }
    if (!pool.coinCreator.equals(import_web36.PublicKey.default)) {
      remainingAccounts.push({
        pubkey: poolV2PdaKey,
        isWritable: false,
        isSigner: false
      });
    }
    remainingAccounts.push(
      {
        pubkey: buybackFeeRecipient,
        isWritable: false,
        isSigner: false
      },
      {
        pubkey: buybackFeeRecipientTokenAccount,
        isWritable: true,
        isSigner: false
      }
    );
    const instruction = await this.offlineProgram.methods.sell(baseAmountIn, minQuoteAmountOut).accounts(swapAccounts).remainingAccounts([...remainingAccounts]).instruction();
    return this.withSellAccounts(swapSolanaState, baseAmountIn, instruction);
  }
  /** The sell instruction `swap` with its user-side setup: base in, quote out. */
  withSellAccounts(swapSolanaState, baseIn, swap) {
    const { user, pool } = swapSolanaState;
    return this.withSwapUserAccounts(
      user,
      {
        mint: pool.baseMint,
        account: swapSolanaState.userBaseTokenAccount,
        tokenProgram: swapSolanaState.baseTokenProgram,
        accountInfo: swapSolanaState.userBaseAccountInfo,
        amount: baseIn
      },
      {
        mint: pool.quoteMint,
        account: swapSolanaState.userQuoteTokenAccount,
        tokenProgram: swapSolanaState.quoteTokenProgram,
        accountInfo: swapSolanaState.userQuoteAccountInfo
      },
      swap
    );
  }
  async sellBaseInput(swapSolanaState, base, slippage, options = {}) {
    const {
      baseMint,
      baseMintAccount,
      feeConfig,
      globalConfig,
      pool,
      poolBaseAmount,
      poolQuoteAmount
    } = swapSolanaState;
    const { coinCreator, creator } = pool;
    const { minQuote } = sellBaseInput({
      base,
      slippage,
      quoteTransferFee: swapSolanaState.quoteTransferFee,
      baseReserve: poolBaseAmount,
      quoteReserve: poolQuoteAmount,
      virtualQuoteReserves: pool.virtualQuoteReserves,
      feeBucketsTotal: pool.protocolFees.add(pool.creatorFees),
      baseMintAccount,
      baseMint,
      coinCreator,
      creator,
      feeConfig,
      globalConfig,
      quoteMint: pool.quoteMint,
      isMayhemMode: pool.isMayhemMode,
      creatorFeeBps: pool.creatorFeeBps
    });
    return this.routedSellInstructions(
      swapSolanaState,
      base,
      minQuote,
      options
    );
  }
  async sellQuoteInput(swapSolanaState, quote, slippage, options = {}) {
    const {
      baseMint,
      baseMintAccount,
      feeConfig,
      globalConfig,
      pool,
      poolBaseAmount,
      poolQuoteAmount
    } = swapSolanaState;
    const { coinCreator, creator } = pool;
    const { base, minQuote } = sellQuoteInput({
      quote,
      slippage,
      quoteTransferFee: swapSolanaState.quoteTransferFee,
      baseReserve: poolBaseAmount,
      quoteReserve: poolQuoteAmount,
      virtualQuoteReserves: pool.virtualQuoteReserves,
      feeBucketsTotal: pool.protocolFees.add(pool.creatorFees),
      baseMintAccount,
      baseMint,
      coinCreator,
      creator,
      feeConfig,
      globalConfig,
      quoteMint: pool.quoteMint,
      isMayhemMode: pool.isMayhemMode,
      creatorFeeBps: pool.creatorFeeBps
    });
    return this.routedSellInstructions(
      swapSolanaState,
      base,
      minQuote,
      options
    );
  }
  routedBuyInstructions(swapSolanaState, baseOut, maxQuoteIn, { v2 = false }) {
    return v2 && supportsTradeV2(swapSolanaState.pool) ? this.buyV2Instructions(swapSolanaState, baseOut, maxQuoteIn) : this.buyInstructions(swapSolanaState, baseOut, maxQuoteIn);
  }
  routedSellInstructions(swapSolanaState, baseIn, minQuoteOut, { v2 = false }) {
    return v2 && supportsTradeV2(swapSolanaState.pool) ? this.sellV2Instructions(swapSolanaState, baseIn, minQuoteOut) : this.sellInstructions(swapSolanaState, baseIn, minQuoteOut);
  }
  async extendAccount(account, user) {
    return this.offlineProgram.methods.extendAccount().accountsPartial({
      account,
      user
    }).instruction();
  }
  async boostBuyAndBurnInstruction(poolKey, pool, authority, quoteAmountIn, minBaseAmountBurned, baseTokenProgram, quoteTokenProgram) {
    const boostVaultAuthority = boostVaultAuthorityPda(poolKey);
    const instruction = await this.offlineProgram.methods.boostBuyAndBurn(quoteAmountIn, minBaseAmountBurned).accountsPartial({
      pool: poolKey,
      authority,
      globalConfig: GLOBAL_CONFIG_PDA,
      baseMint: pool.baseMint,
      quoteMint: pool.quoteMint,
      poolBaseTokenAccount: pool.poolBaseTokenAccount,
      poolQuoteTokenAccount: pool.poolQuoteTokenAccount,
      boostVaultAuthority,
      boostVault: boostVaultAta(
        boostVaultAuthority,
        pool.quoteMint,
        quoteTokenProgram
      ),
      baseTokenProgram,
      quoteTokenProgram
    }).instruction();
    for (const key of instruction.keys) {
      if (key.pubkey.equals(pool.quoteMint)) {
        key.isWritable = true;
      }
    }
    return instruction;
  }
  /**
   * Moves the creator's accumulated AMM fees, quoted in the state's `quoteMint`, from the creator
   * vault ATA to `coinCreatorTokenAccount`. The program transfers between two existing token
   * accounts and creates neither, so the vault ATA and, when it is the destination, the creator's
   * ATA are created here (rent paid by `payer`) when missing, under the quote mint's token
   * program. The program accepts any token account the creator owns as the destination, but
   * only an ATA can be created idempotently, so a custom `coinCreatorTokenAccount` must already
   * exist (an error is thrown otherwise). A wSOL payout is unwrapped by closing the creator's
   * ATA, but only when the creator pays for the transaction themselves.
   */
  async collectCoinCreatorFee(collectCoinCreatorFeeSolanaState, payer = void 0) {
    const {
      coinCreator,
      quoteMint,
      quoteTokenProgram,
      coinCreatorVaultAuthority,
      coinCreatorVaultAta,
      coinCreatorTokenAccount,
      coinCreatorVaultAtaAccountInfo,
      coinCreatorTokenAccountInfo
    } = collectCoinCreatorFeeSolanaState;
    const actualPayer = payer ?? coinCreator;
    const shouldCloseCoinCreatorATA = quoteMint.equals(import_spl_token5.NATIVE_MINT) && coinCreator.equals(actualPayer);
    const coinCreatorTokenAccountExists = this.accountExists(
      coinCreatorTokenAccountInfo,
      quoteTokenProgram
    );
    const coinCreatorTokenAccountIsAta = coinCreatorTokenAccount.equals(
      (0, import_spl_token5.getAssociatedTokenAddressSync)(
        quoteMint,
        coinCreator,
        true,
        quoteTokenProgram
      )
    );
    if (!coinCreatorTokenAccountExists && !coinCreatorTokenAccountIsAta) {
      throw new Error(
        `coinCreatorTokenAccount=${coinCreatorTokenAccount.toString()} does not exist; only the creator's ATA is created automatically`
      );
    }
    const instructions = [
      ...this.ensureAtaInstructions(
        actualPayer,
        coinCreatorVaultAuthority,
        quoteMint,
        coinCreatorVaultAta,
        this.accountExists(coinCreatorVaultAtaAccountInfo, quoteTokenProgram),
        quoteTokenProgram
      ),
      ...this.ensureAtaInstructions(
        actualPayer,
        coinCreator,
        quoteMint,
        coinCreatorTokenAccount,
        coinCreatorTokenAccountExists,
        quoteTokenProgram
      ),
      await this.offlineProgram.methods.collectCoinCreatorFee().accountsPartial({
        coinCreator,
        coinCreatorTokenAccount,
        quoteMint,
        quoteTokenProgram
      }).instruction()
    ];
    if (shouldCloseCoinCreatorATA) {
      instructions.push(
        (0, import_spl_token5.createCloseAccountInstruction)(
          coinCreatorTokenAccount,
          coinCreator,
          coinCreator,
          void 0,
          import_spl_token5.TOKEN_PROGRAM_ID
        )
      );
    }
    return instructions;
  }
  /**
   * Moves a coin creator's accumulated AMM fees, quoted in `quoteMint`, into their pump creator
   * vault (the `creator-vault` PDA of the pump program), for coins whose creator fees are paid
   * out through that vault. The program unwraps a wSOL vault into the PDA itself and moves any
   * other quote into the PDA's quote ATA, which it creates (rent paid by `payer`) when missing;
   * `pump_creator_vault_ata` is part of the account list even for wSOL. `quoteTokenProgram`
   * must be the quote mint's owner program, SPL Token or Token-2022; every quote-side ATA is
   * derived under it.
   */
  async transferCreatorFeesToPumpV2Instruction({
    payer,
    coinCreator,
    quoteMint,
    quoteTokenProgram
  }) {
    return this.offlineProgram.methods.transferCreatorFeesToPumpV2().accountsPartial({
      payer,
      quoteMint,
      tokenProgram: quoteTokenProgram,
      coinCreator
    }).instruction();
  }
  /**
   * Builds `set_coin_creator`, the permissionless instruction that fills in a canonical pool's
   * coin creator from the base mint's Metaplex metadata (its first creator) or, when the metadata
   * lists none, from the bonding curve's creator; a no-op once the pool has one. With `baseMint`
   * the `metadata` and `bonding_curve` accounts are derived here (`metadataPda`,
   * `bondingCurvePda`). Without it they are left to Anchor's account resolver, which reads the
   * pool through the provider's connection (the offline program has none) and, with this IDL,
   * cannot decode a pre-upgrade 261-byte pool, so pass `baseMint` or use
   * `OnlinePumpAmmSdk.setCoinCreatorInstructions`. The program writes the whole `Pool` back, so a
   * pre-upgrade pool must be grown by `extend_account` first.
   */
  async setCoinCreator(pool, baseMint) {
    return this.offlineProgram.methods.setCoinCreator().accountsPartial(
      baseMint === void 0 ? { pool } : {
        pool,
        metadata: metadataPda(baseMint),
        bondingCurve: bondingCurvePda(baseMint)
      }
    ).instruction();
  }
  /**
   * `buy_v2`: buys exactly `baseOut` for at most `maxQuoteIn` (fees included) on a pool
   * `supportsTradeV2` accepts, with the same user-side accounts as `buyInstructions`. The protocol
   * and coin-creator fees stay in the pool's quote vault (`Pool.protocolFees` /
   * `Pool.creatorFees`, paid out by the sweeps); only the buyback slice of the protocol fee is paid
   * in the trade (none on a mayhem pool), to a listed buyback fee recipient's quote ATA, which
   * must already exist (v2 never creates it, and checks it even when the slice is 0). No
   * `extend_account` is prepended: the program grows a pre-upgrade pool itself.
   */
  async buyV2Instructions(swapSolanaState, baseOut, maxQuoteIn) {
    return this.withBuyAccounts(
      swapSolanaState,
      maxQuoteIn,
      await this.offlineProgram.methods.buyV2(baseOut, maxQuoteIn).accountsStrict(this.tradeV2Accounts(swapSolanaState)).instruction()
    );
  }
  /**
   * `buy_exact_quote_in_v2`: spends at most `spendableQuoteIn` (fees included) for at least
   * `minBaseOut`, which must be nonzero. Accounts and fee handling as `buyV2Instructions`.
   */
  async buyExactQuoteInV2Instructions(swapSolanaState, spendableQuoteIn, minBaseOut) {
    return this.withBuyAccounts(
      swapSolanaState,
      spendableQuoteIn,
      await this.offlineProgram.methods.buyExactQuoteInV2(spendableQuoteIn, minBaseOut).accountsStrict(this.tradeV2Accounts(swapSolanaState)).instruction()
    );
  }
  /**
   * `sell_v2`: sells exactly `baseIn` for at least `minQuoteOut` (fees deducted), with the same
   * user-side accounts as `sellInstructions`. Fee handling as `buyV2Instructions`; the buyback
   * slice leaves the pool vault.
   */
  async sellV2Instructions(swapSolanaState, baseIn, minQuoteOut) {
    return this.withSellAccounts(
      swapSolanaState,
      baseIn,
      await this.offlineProgram.methods.sellV2(baseIn, minQuoteOut).accountsStrict(this.tradeV2Accounts(swapSolanaState)).instruction()
    );
  }
  /**
   * `multi_hop_swap`: spends exactly `amountIn` of `inMint` along `venues` (canonical, non-mayhem
   * pump pools and pump bonding curves, every hop buying or every hop selling) and pays at
   * least `minAmountOut` of the final mint into the user's account (`multiHopSwapQuote` prices
   * it). The route is checked as the program checks it before anything is built
   * (`resolveMultiHopRoute`).
   *
   * `buybackFeeRecipient` is the buyback recipient *wallet* the route's protocol leg (first hop of
   * a buy route, last of a sell route) pays the buyback slice to, through its ATA for that hop's
   * quote mint, which must exist. It must be listed by the venue holding the leg: a pool leg
   * defaults to a `globalConfig.buybackFeeRecipients` entry (picked at random, as the v1 and v2
   * trades do, so every listed recipient needs that ATA); a curve leg checks pump's
   * `Global.buybackFeeRecipients`, which this SDK does not read, so it must be passed.
   *
   * The user's token accounts default to their ATAs; a custom account must exist. A legacy-WSOL
   * input is wrapped (and the account closed afterwards), except on a buy starting on a SOL
   * bonding curve: pump takes `amountIn` from the wallet as lamports, so the user's WSOL ATA is
   * only created when missing (it must exist) and the wallet needs `amountIn` plus rent in SOL.
   * A sell ending on a SOL curve pays into the user's WSOL ATA, which is likewise created and then
   * closed to unwrap. On a SOL protocol leg the buyback slice goes to the recipient's WSOL ATA. the output ATA is created when
   * `userOutAccountInfo` does not show it, and a legacy-WSOL output is closed to unwrap. No
   * compute-budget instruction is added: set a limit of about 50k CU per hop (the 200k default
   * does not cover four hops).
   */
  async multiHopSwapInstructions({
    user,
    inMint,
    venues,
    amountIn,
    minAmountOut,
    globalConfig,
    buybackFeeRecipient,
    userInTokenAccount,
    userOutTokenAccount,
    userInAccountInfo = null,
    userOutAccountInfo = null
  }) {
    if (amountIn.lten(0) || minAmountOut.lten(0)) {
      throw new Error("amountIn and minAmountOut must be positive.");
    }
    const { isBuy, mints } = resolveMultiHopRoute(inMint, venues);
    inMint = mints[0];
    const outMint = mints[mints.length - 1];
    const first = venues[0];
    const last = venues[venues.length - 1];
    const inTokenProgram = isBuy ? venueQuoteTokenProgram(first) : first.baseTokenProgram;
    const outTokenProgram = isBuy ? last.baseTokenProgram : venueQuoteTokenProgram(last);
    const protocolLeg = isBuy ? first : last;
    if (buybackFeeRecipient === void 0) {
      if (protocolLeg.kind === "curve") {
        throw new Error(
          "The route's protocol leg is a bonding curve: pass buybackFeeRecipient (a wallet listed in pump's Global.buybackFeeRecipients)."
        );
      }
      buybackFeeRecipient = getBuybackFeeRecipient(globalConfig);
    }
    const hopAccounts = venues.flatMap((venue) => {
      const { baseMint, quoteMint } = venueMints(venue);
      const venueKey = venue.kind === "pool" ? venue.poolKey : bondingCurvePda(baseMint);
      const [baseVault, quoteVault] = venue.kind === "pool" ? [venue.pool.poolBaseTokenAccount, venue.pool.poolQuoteTokenAccount] : [
        (0, import_spl_token5.getAssociatedTokenAddressSync)(
          baseMint,
          venueKey,
          true,
          venue.baseTokenProgram
        ),
        (0, import_spl_token5.getAssociatedTokenAddressSync)(
          quoteMint,
          venueKey,
          true,
          venueQuoteTokenProgram(venue)
        )
      ];
      return [
        { pubkey: baseMint, isSigner: false, isWritable: false },
        { pubkey: quoteMint, isSigner: false, isWritable: false },
        { pubkey: venueKey, isSigner: false, isWritable: true },
        { pubkey: baseVault, isSigner: false, isWritable: true },
        { pubkey: quoteVault, isSigner: false, isWritable: true }
      ];
    });
    const userIn = userInTokenAccount ?? (0, import_spl_token5.getAssociatedTokenAddressSync)(inMint, user, true, inTokenProgram);
    const userOut = userOutTokenAccount ?? (0, import_spl_token5.getAssociatedTokenAddressSync)(outMint, user, true, outTokenProgram);
    const swap = await this.offlineProgram.methods.multiHopSwap(amountIn, minAmountOut).accountsStrict({
      user,
      userInTokenAccount: userIn,
      userOutTokenAccount: userOut,
      globalConfig: GLOBAL_CONFIG_PDA,
      feeConfig: PUMP_AMM_FEE_CONFIG_PDA,
      userVolumeAccumulator: userVolumeAccumulatorPda(user),
      buybackFeeRecipient: (0, import_spl_token5.getAssociatedTokenAddressSync)(
        venueMints(protocolLeg).quoteMint,
        buybackFeeRecipient,
        true,
        venueQuoteTokenProgram(protocolLeg)
      ),
      tokenProgram: import_spl_token5.TOKEN_PROGRAM_ID,
      token2022Program: import_spl_token5.TOKEN_2022_PROGRAM_ID,
      systemProgram: import_web36.SystemProgram.programId,
      eventAuthority: PUMP_AMM_EVENT_AUTHORITY_PDA,
      program: PUMP_AMM_PROGRAM_ID,
      pumpProgram: PUMP_PROGRAM_ID,
      pumpGlobal: PUMP_GLOBAL_PDA,
      pumpFeeConfig: PUMP_FEE_CONFIG_PDA,
      pumpEventAuthority: PUMP_EVENT_AUTHORITY_PDA
    }).remainingAccounts(hopAccounts).instruction();
    return this.withSwapUserAccounts(
      user,
      {
        mint: inMint,
        account: userIn,
        tokenProgram: inTokenProgram,
        accountInfo: userInAccountInfo,
        // A buy starting on a SOL curve pays from the wallet's lamports: the user's WSOL account
        // only has to exist, so it is created when missing but never funded.
        amount: isBuy && isSolCurve(first) ? new import_bn9.default(0) : amountIn
      },
      {
        mint: outMint,
        account: userOut,
        tokenProgram: outTokenProgram,
        accountInfo: userOutAccountInfo
      },
      swap
    );
  }
  /**
   * `sweep_protocol_fee`: pays a pool's `protocolFees` out of its quote vault to a protocol fee
   * recipient's quote ATA (a reserved one on a mayhem pool; created when missing).
   * Permissionless: `payer` signs and pays that ATA's rent and a pre-upgrade pool's realloc. A
   * no-op when the bucket is empty. `quoteTokenProgram` is the owner of `pool.quoteMint`.
   */
  async sweepProtocolFeeInstruction({
    payer,
    poolKey,
    pool,
    quoteTokenProgram,
    globalConfig
  }) {
    return this.offlineProgram.methods.sweepProtocolFee().accountsStrict(
      this.sweepFeeAccounts(
        payer,
        poolKey,
        pool,
        quoteTokenProgram,
        getFeeRecipient(globalConfig, pool.isMayhemMode)
      )
    ).instruction();
  }
  /**
   * `sweep_creator_fee`: pays a pool's `creatorFees` into the coin-creator vault of
   * `pool.coinCreator` (the vault `collectCoinCreatorFee` pays out from), otherwise as
   * `sweepProtocolFeeInstruction`. The programs refuse to change a coin creator or its fee shares
   * while the bucket is nonzero (pump-amm `CreatorFeesNotSwept`, pump-fees
   * `PoolCreatorFeesNotSwept`), so a CTO, a fee-sharing config creation or an `update_fee_shares`
   * on a coin with v2 volume must carry this instruction before it, in the same transaction.
   */
  async sweepCreatorFeeInstruction({
    payer,
    poolKey,
    pool,
    quoteTokenProgram
  }) {
    return this.offlineProgram.methods.sweepCreatorFee().accountsStrict(
      this.sweepFeeAccounts(
        payer,
        poolKey,
        pool,
        quoteTokenProgram,
        coinCreatorVaultAuthorityPda(pool.coinCreator)
      )
    ).instruction();
  }
  sweepFeeAccounts(payer, poolKey, pool, quoteTokenProgram, recipient) {
    return {
      payer,
      globalConfig: GLOBAL_CONFIG_PDA,
      pool: poolKey,
      quoteMint: pool.quoteMint,
      quoteTokenProgram,
      poolQuoteTokenAccount: pool.poolQuoteTokenAccount,
      recipient,
      recipientTokenAccount: (0, import_spl_token5.getAssociatedTokenAddressSync)(
        pool.quoteMint,
        recipient,
        true,
        quoteTokenProgram
      ),
      systemProgram: import_web36.SystemProgram.programId,
      associatedTokenProgram: import_spl_token5.ASSOCIATED_TOKEN_PROGRAM_ID,
      eventAuthority: PUMP_AMM_EVENT_AUTHORITY_PDA,
      program: PUMP_AMM_PROGRAM_ID
    };
  }
  /** The 17 accounts of `buy_v2` / `buy_exact_quote_in_v2` / `sell_v2`, in IDL order. */
  tradeV2Accounts({
    globalConfig,
    poolKey,
    pool,
    baseTokenProgram,
    quoteTokenProgram,
    user,
    userBaseTokenAccount,
    userQuoteTokenAccount
  }) {
    return {
      pool: poolKey,
      user,
      globalConfig: GLOBAL_CONFIG_PDA,
      baseMint: pool.baseMint,
      quoteMint: pool.quoteMint,
      userBaseTokenAccount,
      userQuoteTokenAccount,
      poolBaseTokenAccount: pool.poolBaseTokenAccount,
      poolQuoteTokenAccount: pool.poolQuoteTokenAccount,
      baseTokenProgram,
      quoteTokenProgram,
      systemProgram: import_web36.SystemProgram.programId,
      userVolumeAccumulator: userVolumeAccumulatorPda(user),
      feeConfig: PUMP_AMM_FEE_CONFIG_PDA,
      // Only the ATA: the program checks it is a listed recipient's canonical quote ATA.
      buybackFeeRecipient: (0, import_spl_token5.getAssociatedTokenAddressSync)(
        pool.quoteMint,
        getBuybackFeeRecipient(globalConfig),
        true,
        quoteTokenProgram
      ),
      eventAuthority: PUMP_AMM_EVENT_AUTHORITY_PDA,
      program: PUMP_AMM_PROGRAM_ID
    };
  }
  swapAccounts(swapSolanaState) {
    const {
      globalConfig,
      poolKey,
      pool,
      baseTokenProgram,
      quoteTokenProgram,
      user,
      userBaseTokenAccount,
      userQuoteTokenAccount
    } = swapSolanaState;
    const protocolFeeRecipient = getFeeRecipient(
      globalConfig,
      pool.isMayhemMode
    );
    const buybackFeeRecipient = getBuybackFeeRecipient(globalConfig);
    const {
      baseMint,
      quoteMint,
      poolBaseTokenAccount,
      poolQuoteTokenAccount,
      coinCreator
    } = pool;
    const coinCreatorVaultAuthority = coinCreatorVaultAuthorityPda(coinCreator);
    return {
      pool: poolKey,
      globalConfig: GLOBAL_CONFIG_PDA,
      user,
      baseMint,
      quoteMint,
      userBaseTokenAccount,
      userQuoteTokenAccount,
      poolBaseTokenAccount,
      poolQuoteTokenAccount,
      protocolFeeRecipient,
      protocolFeeRecipientTokenAccount: (0, import_spl_token5.getAssociatedTokenAddressSync)(
        quoteMint,
        protocolFeeRecipient,
        true,
        quoteTokenProgram
      ),
      buybackFeeRecipient,
      buybackFeeRecipientTokenAccount: (0, import_spl_token5.getAssociatedTokenAddressSync)(
        quoteMint,
        buybackFeeRecipient,
        true,
        quoteTokenProgram
      ),
      baseTokenProgram,
      quoteTokenProgram,
      systemProgram: import_web36.SystemProgram.programId,
      associatedTokenProgram: import_spl_token5.ASSOCIATED_TOKEN_PROGRAM_ID,
      eventAuthority: PUMP_AMM_EVENT_AUTHORITY_PDA,
      program: PUMP_AMM_PROGRAM_ID,
      coinCreatorVaultAta: coinCreatorVaultAtaPda(
        coinCreatorVaultAuthority,
        quoteMint,
        quoteTokenProgram
      ),
      coinCreatorVaultAuthority
    };
  }
  async syncUserVolumeAccumulator(user) {
    return await this.offlineProgram.methods.syncUserVolumeAccumulator().accountsPartial({ user }).instruction();
  }
  async initUserVolumeAccumulator({
    payer,
    user
  }) {
    return await this.offlineProgram.methods.initUserVolumeAccumulator().accountsPartial({ payer, user }).instruction();
  }
  async closeUserVolumeAccumulator(user) {
    return await this.offlineProgram.methods.closeUserVolumeAccumulator().accountsPartial({ user }).instruction();
  }
  // from pumpAmm
  async createAutocompleteInitialPoolPrice(initialBase, initialQuote) {
    return initialQuote.div(initialBase);
  }
  async depositInstructions(liquiditySolanaState, lpToken, slippage) {
    const { pool, poolBaseTokenAccount, quoteTransferFee } = liquiditySolanaState;
    const { maxBase, maxQuote } = depositLpToken(
      lpToken,
      slippage,
      new import_bn9.default(poolBaseTokenAccount.amount.toString()),
      this.realQuoteReserves(liquiditySolanaState),
      pool.lpSupply,
      quoteTransferFee
    );
    return this.depositInstructionsInternal(
      liquiditySolanaState,
      lpToken,
      maxBase,
      maxQuote
    );
  }
  depositAutocompleteQuoteAndLpTokenFromBase(liquiditySolanaState, base, slippage) {
    const { quote, lpToken } = this.depositBaseInput(
      liquiditySolanaState,
      base,
      slippage
    );
    return {
      quote,
      lpToken
    };
  }
  depositAutocompleteBaseAndLpTokenFromQuote(liquiditySolanaState, quote, slippage) {
    const { base, lpToken } = this.depositQuoteInput(
      liquiditySolanaState,
      quote,
      slippage
    );
    return {
      base,
      lpToken
    };
  }
  async withdrawInstructions(liquiditySolanaState, lpToken, slippage) {
    const { minBase, minQuote } = this.withdrawInputs(
      liquiditySolanaState,
      lpToken,
      slippage
    );
    return this.withdrawInstructionsInternal(
      liquiditySolanaState,
      lpToken,
      minBase,
      minQuote
    );
  }
  withdrawAutoCompleteBaseAndQuoteFromLpToken(liquiditySolanaState, lpAmount, slippage) {
    const { base, quote } = this.withdrawInputs(
      liquiditySolanaState,
      lpAmount,
      slippage
    );
    return {
      base,
      quote
    };
  }
};
var PUMP_AMM_SDK = new PumpAmmSdk();

// src/swap/pumpAmmAdmin.ts
var PumpAmmAdminSdk = class {
  constructor(connection) {
    this.connection = connection;
    this.program = getPumpAmmProgram(connection);
  }
  /**
   * Decoded through `PumpAmmSdk.decodeGlobalConfig`, which zero-pads shorter (pre-upgrade)
   * accounts: Anchor's own `fetch` throws on the live 940-byte account once the IDL carries the
   * creator-fee fields.
   */
  async fetchGlobalConfigAccount() {
    const accountInfo = await this.connection.getAccountInfo(GLOBAL_CONFIG_PDA);
    if (accountInfo === null) {
      throw new Error("Global config account not found");
    }
    return PUMP_AMM_SDK.decodeGlobalConfig(accountInfo);
  }
  createConfig(lpFeeBasisPoints, protocolFeeBasisPoints, protocolFeeRecipients, coinCreatorFeeBasisPoints, admin, adminSetCoinCreatorAuthority) {
    return this.program.methods.createConfig(
      lpFeeBasisPoints,
      protocolFeeBasisPoints,
      protocolFeeRecipients,
      coinCreatorFeeBasisPoints,
      adminSetCoinCreatorAuthority
    ).accountsPartial({
      admin
    }).instruction();
  }
  disable(disableCreatePool, disableDeposit, disableWithdraw, disableBuy, disableSell, admin) {
    return this.program.methods.disable(
      disableCreatePool,
      disableDeposit,
      disableWithdraw,
      disableBuy,
      disableSell
    ).accountsPartial({
      admin,
      globalConfig: GLOBAL_CONFIG_PDA
    }).instruction();
  }
  updateAdmin(admin, newAdmin) {
    return this.program.methods.updateAdmin().accountsPartial({
      admin,
      newAdmin,
      globalConfig: GLOBAL_CONFIG_PDA
    }).instruction();
  }
  updateFeeConfig(lpFeeBasisPoints, protocolFeeBasisPoints, protocolFeeRecipients, coinCreatorFeeBasisPoints, admin, adminSetCoinCreatorAuthority) {
    return this.program.methods.updateFeeConfig(
      lpFeeBasisPoints,
      protocolFeeBasisPoints,
      protocolFeeRecipients,
      coinCreatorFeeBasisPoints,
      adminSetCoinCreatorAuthority
    ).accountsPartial({
      admin,
      globalConfig: GLOBAL_CONFIG_PDA
    }).instruction();
  }
  /**
   * Turns per-pool creator fees on or off and sets the ceiling a CTO (pump `admin_cto`, which
   * drives `admin_cto_pool`) accepts. Signed by `GlobalConfig.admin` (read from the account), who also pays the rent that
   * grows a pre-upgrade 940-byte GlobalConfig to `GLOBAL_CONFIG_SIZE` bytes, so it is the first
   * instruction to run after the program upgrade. While the gate is off, stored per-pool rates are
   * neither accepted by a CTO nor read by trades. The coin creator of a canonical pool changes only
   * through pump's `admin_cto`: pump-amm's `admin_cto_pool` accepts pump's pool-authority PDA as
   * its only caller, so this SDK has no builder for it.
   */
  async updateCreatorFeeConfig(creatorFeeConfigurable, maxConfigurableCreatorFeeBps) {
    const { admin } = await this.fetchGlobalConfigAccount();
    return this.program.methods.updateCreatorFeeConfig(
      creatorFeeConfigurable,
      maxConfigurableCreatorFeeBps
    ).accountsPartial({
      admin,
      globalConfig: GLOBAL_CONFIG_PDA
    }).instruction();
  }
  async adminUpdateTokenIncentives(startTime, endTime, dayNumber, tokenSupplyPerDay, secondsInADay = new import_bn10.default(86400), mint = PUMP_MINT, tokenProgram = import_spl_token6.TOKEN_2022_PROGRAM_ID) {
    const { admin } = await this.fetchGlobalConfigAccount();
    return this.program.methods.adminUpdateTokenIncentives(
      startTime,
      endTime,
      secondsInADay,
      dayNumber,
      tokenSupplyPerDay
    ).accountsPartial({
      admin,
      mint,
      tokenProgram
    }).instruction();
  }
};

// src/swap/onlinePumpAmm.ts
var import_spl_token7 = require("@solana/spl-token");
var import_web37 = require("@solana/web3.js");
var import_bn12 = __toESM(require("bn.js"));

// src/swap/tokenIncentives.ts
var import_bn11 = __toESM(require("bn.js"));
function totalUnclaimedTokens(globalVolumeAccumulator, userVolumeAccumulator, currentTimestamp = Date.now() / 1e3) {
  const { startTime, endTime, secondsInADay, totalTokenSupply, solVolumes } = globalVolumeAccumulator;
  const { totalUnclaimedTokens: totalUnclaimedTokens2, currentSolVolume, lastUpdateTimestamp } = userVolumeAccumulator;
  const result = totalUnclaimedTokens2;
  if (startTime.eqn(0) || endTime.eqn(0) || secondsInADay.eqn(0)) {
    return result;
  }
  const currentTimestampBn = new import_bn11.default(currentTimestamp);
  if (currentTimestampBn.lt(startTime)) {
    return result;
  }
  const currentDayIndex = currentTimestampBn.sub(startTime).div(secondsInADay).toNumber();
  if (lastUpdateTimestamp.lt(startTime)) {
    return result;
  }
  const lastUpdatedIndex = lastUpdateTimestamp.sub(startTime).div(secondsInADay).toNumber();
  if (endTime.lt(startTime)) {
    return result;
  }
  const endDayIndex = endTime.sub(startTime).div(secondsInADay).toNumber();
  if (currentDayIndex > lastUpdatedIndex && lastUpdatedIndex <= endDayIndex) {
    const lastUpdatedDayTokenSupply = totalTokenSupply[lastUpdatedIndex];
    const lastUpdatedDaySolVolume = solVolumes[lastUpdatedIndex];
    if (lastUpdatedDaySolVolume.eqn(0)) {
      return result;
    }
    return result.add(
      currentSolVolume.mul(lastUpdatedDayTokenSupply).div(lastUpdatedDaySolVolume)
    );
  }
  return result;
}
function currentDayTokens(globalVolumeAccumulator, userVolumeAccumulator, currentTimestamp = Date.now() / 1e3) {
  const { startTime, endTime, secondsInADay, totalTokenSupply, solVolumes } = globalVolumeAccumulator;
  const { currentSolVolume, lastUpdateTimestamp } = userVolumeAccumulator;
  if (startTime.eqn(0) || endTime.eqn(0) || secondsInADay.eqn(0)) {
    return new import_bn11.default(0);
  }
  const currentTimestampBn = new import_bn11.default(currentTimestamp);
  if (currentTimestampBn.lt(startTime) || currentTimestampBn.gt(endTime)) {
    return new import_bn11.default(0);
  }
  const currentDayIndex = currentTimestampBn.sub(startTime).div(secondsInADay).toNumber();
  if (lastUpdateTimestamp.lt(startTime)) {
    return new import_bn11.default(0);
  }
  const lastUpdatedIndex = lastUpdateTimestamp.sub(startTime).div(secondsInADay).toNumber();
  if (endTime.lt(startTime)) {
    return new import_bn11.default(0);
  }
  if (currentDayIndex !== lastUpdatedIndex) {
    return new import_bn11.default(0);
  }
  const currentDayTokenSupply = totalTokenSupply[currentDayIndex];
  const currentDaySolVolume = solVolumes[currentDayIndex];
  if (currentDaySolVolume.eqn(0)) {
    return new import_bn11.default(0);
  }
  return currentSolVolume.mul(currentDayTokenSupply).div(currentDaySolVolume);
}

// src/swap/onlinePumpAmm.ts
var OnlinePumpAmmSdk = class {
  constructor(connection) {
    this.connection = connection;
    this.program = getPumpAmmProgram(connection);
  }
  async fetchGlobalConfigAccount() {
    const accountInfo = await this.connection.getAccountInfo(GLOBAL_CONFIG_PDA);
    if (accountInfo === null) {
      throw new Error("Global config account not found");
    }
    return PUMP_AMM_SDK.decodeGlobalConfig(accountInfo);
  }
  async fetchFeeConfigAccount() {
    const accountInfo = await this.connection.getAccountInfo(
      PUMP_AMM_FEE_CONFIG_PDA
    );
    if (accountInfo === null) {
      throw new Error("Fee config account not found");
    }
    return PUMP_AMM_SDK.decodeFeeConfig(accountInfo);
  }
  async fetchPool(pool) {
    const accountInfo = await this.connection.getAccountInfo(pool);
    if (accountInfo === null) {
      throw new Error("Pool account not found");
    }
    return PUMP_AMM_SDK.decodePool(accountInfo);
  }
  fetchGlobalVolumeAccumulator() {
    return this.program.account.globalVolumeAccumulator.fetch(
      GLOBAL_VOLUME_ACCUMULATOR_PDA
    );
  }
  fetchUserVolumeAccumulator(user) {
    return this.program.account.userVolumeAccumulator.fetchNullable(
      userVolumeAccumulatorPda(user)
    );
  }
  async createPoolSolanaState(index, creator, baseMint, quoteMint, userBaseTokenAccount = void 0, userQuoteTokenAccount = void 0) {
    const [globalConfigAccountInfo, baseMintAccountInfo, quoteMintAccountInfo] = await this.connection.getMultipleAccountsInfo([
      GLOBAL_CONFIG_PDA,
      baseMint,
      quoteMint
    ]);
    if (globalConfigAccountInfo === null) {
      throw new Error("Global config account not found");
    }
    if (baseMintAccountInfo === null) {
      throw new Error(`baseMint=${baseMint.toString()} not found`);
    }
    if (quoteMintAccountInfo === null) {
      throw new Error(`quoteMint=${quoteMint.toString()} not found`);
    }
    const globalConfig = PUMP_AMM_SDK.decodeGlobalConfig(
      globalConfigAccountInfo
    );
    const [baseTokenProgram, quoteTokenProgram] = [
      baseMintAccountInfo.owner,
      quoteMintAccountInfo.owner
    ];
    const poolKey = poolPda(index, creator, baseMint, quoteMint);
    const poolBaseTokenAccount = (0, import_spl_token7.getAssociatedTokenAddressSync)(
      baseMint,
      poolKey,
      true,
      baseTokenProgram
    );
    const poolQuoteTokenAccount = (0, import_spl_token7.getAssociatedTokenAddressSync)(
      quoteMint,
      poolKey,
      true,
      quoteTokenProgram
    );
    const [poolBaseAccountInfo, poolQuoteAccountInfo] = await this.connection.getMultipleAccountsInfo([
      poolBaseTokenAccount,
      poolQuoteTokenAccount
    ]);
    userBaseTokenAccount ??= (0, import_spl_token7.getAssociatedTokenAddressSync)(
      baseMint,
      creator,
      true,
      baseTokenProgram
    );
    userQuoteTokenAccount ??= (0, import_spl_token7.getAssociatedTokenAddressSync)(
      quoteMint,
      creator,
      true,
      quoteTokenProgram
    );
    const [userBaseAccountInfo, userQuoteAccountInfo] = await this.connection.getMultipleAccountsInfo([
      userBaseTokenAccount,
      userQuoteTokenAccount
    ]);
    return {
      index,
      creator,
      baseMint,
      quoteMint,
      globalConfig,
      poolKey,
      poolBaseTokenAccount,
      poolQuoteTokenAccount,
      baseTokenProgram,
      quoteTokenProgram,
      userBaseTokenAccount,
      userQuoteTokenAccount,
      userBaseAccountInfo,
      userQuoteAccountInfo,
      poolBaseAccountInfo,
      poolQuoteAccountInfo
    };
  }
  async swapSolanaState(poolKey, user, userBaseTokenAccount = void 0, userQuoteTokenAccount = void 0) {
    const [globalConfigAccountInfo, feeConfigAccountInfo, poolAccountInfo] = await this.connection.getMultipleAccountsInfo([
      GLOBAL_CONFIG_PDA,
      PUMP_AMM_FEE_CONFIG_PDA,
      poolKey
    ]);
    if (globalConfigAccountInfo === null) {
      throw new Error("Global config account not found");
    }
    if (poolAccountInfo === null) {
      throw new Error("Pool account not found");
    }
    const globalConfig = PUMP_AMM_SDK.decodeGlobalConfig(
      globalConfigAccountInfo
    );
    const feeConfig = feeConfigAccountInfo ? PUMP_AMM_SDK.decodeFeeConfig(feeConfigAccountInfo) : null;
    const pool = PUMP_AMM_SDK.decodePool(poolAccountInfo);
    const { baseMint, quoteMint, poolBaseTokenAccount, poolQuoteTokenAccount } = pool;
    const [
      baseMintAccountInfo,
      quoteMintAccountInfo,
      poolBaseAccountInfo,
      poolQuoteAccountInfo
    ] = await this.connection.getMultipleAccountsInfo([
      baseMint,
      quoteMint,
      poolBaseTokenAccount,
      poolQuoteTokenAccount
    ]);
    if (baseMintAccountInfo === null) {
      throw new Error(`baseMint=${baseMint.toString()} not found`);
    }
    const decodedBaseMintAccount = import_spl_token7.MintLayout.decode(baseMintAccountInfo.data);
    if (quoteMintAccountInfo === null) {
      throw new Error(`quoteMint=${quoteMint.toString()} not found`);
    }
    if (poolBaseAccountInfo === null) {
      throw new Error(
        `Pool base token account ${poolBaseTokenAccount.toString()} not found`
      );
    }
    if (poolQuoteAccountInfo === null) {
      throw new Error(
        `Pool quote token account ${poolQuoteTokenAccount.toString()} not found`
      );
    }
    const [baseTokenProgram, quoteTokenProgram] = [
      baseMintAccountInfo.owner,
      quoteMintAccountInfo.owner
    ];
    const decodedPoolBaseTokenAccount = import_spl_token7.AccountLayout.decode(
      poolBaseAccountInfo.data
    );
    const decodedPoolQuoteTokenAccount = import_spl_token7.AccountLayout.decode(
      poolQuoteAccountInfo.data
    );
    userBaseTokenAccount ??= (0, import_spl_token7.getAssociatedTokenAddressSync)(
      baseMint,
      user,
      true,
      baseTokenProgram
    );
    userQuoteTokenAccount ??= (0, import_spl_token7.getAssociatedTokenAddressSync)(
      quoteMint,
      user,
      true,
      quoteTokenProgram
    );
    const [userBaseAccountInfo, userQuoteAccountInfo] = await this.connection.getMultipleAccountsInfo([
      userBaseTokenAccount,
      userQuoteTokenAccount
    ]);
    return {
      globalConfig,
      feeConfig,
      poolKey,
      poolAccountInfo,
      pool,
      poolBaseAmount: new import_bn12.default(decodedPoolBaseTokenAccount.amount.toString()),
      poolQuoteAmount: new import_bn12.default(decodedPoolQuoteTokenAccount.amount.toString()),
      baseTokenProgram,
      quoteTokenProgram,
      baseMint,
      baseMintAccount: decodedBaseMintAccount,
      user,
      userBaseTokenAccount,
      userQuoteTokenAccount,
      userBaseAccountInfo,
      userQuoteAccountInfo,
      quoteTransferFee: await this.quoteTransferFee(
        quoteMint,
        quoteMintAccountInfo
      )
    };
  }
  async swapSolanaStateNoPool(poolKey, user, userBaseTokenAccount = void 0, userQuoteTokenAccount = void 0) {
    const [globalConfigAccountInfo, feeConfigAccountInfo, poolAccountInfo] = await this.connection.getMultipleAccountsInfo([
      GLOBAL_CONFIG_PDA,
      PUMP_AMM_FEE_CONFIG_PDA,
      poolKey
    ]);
    if (globalConfigAccountInfo === null) {
      throw new Error("Global config account not found");
    }
    if (poolAccountInfo === null) {
      throw new Error("Pool account not found");
    }
    const globalConfig = PUMP_AMM_SDK.decodeGlobalConfig(
      globalConfigAccountInfo
    );
    const feeConfig = feeConfigAccountInfo ? PUMP_AMM_SDK.decodeFeeConfig(feeConfigAccountInfo) : null;
    const pool = PUMP_AMM_SDK.decodePool(poolAccountInfo);
    const { baseMint, quoteMint, poolBaseTokenAccount, poolQuoteTokenAccount } = pool;
    const [
      baseMintAccountInfo,
      quoteMintAccountInfo,
      poolBaseAccountInfo,
      poolQuoteAccountInfo
    ] = await this.connection.getMultipleAccountsInfo([
      baseMint,
      quoteMint,
      poolBaseTokenAccount,
      poolQuoteTokenAccount
    ]);
    if (baseMintAccountInfo === null) {
      throw new Error(`baseMint=${baseMint.toString()} not found`);
    }
    const decodedBaseMintAccount = import_spl_token7.MintLayout.decode(baseMintAccountInfo.data);
    if (quoteMintAccountInfo === null) {
      throw new Error(`quoteMint=${quoteMint.toString()} not found`);
    }
    if (poolBaseAccountInfo === null) {
      throw new Error(
        `Pool base token account ${poolBaseTokenAccount.toString()} not found`
      );
    }
    if (poolQuoteAccountInfo === null) {
      throw new Error(
        `Pool quote token account ${poolQuoteTokenAccount.toString()} not found`
      );
    }
    const [baseTokenProgram, quoteTokenProgram] = [
      baseMintAccountInfo.owner,
      quoteMintAccountInfo.owner
    ];
    const decodedPoolBaseTokenAccount = import_spl_token7.AccountLayout.decode(
      poolBaseAccountInfo.data
    );
    const decodedPoolQuoteTokenAccount = import_spl_token7.AccountLayout.decode(
      poolQuoteAccountInfo.data
    );
    userBaseTokenAccount ??= (0, import_spl_token7.getAssociatedTokenAddressSync)(
      baseMint,
      user,
      true,
      baseTokenProgram
    );
    userQuoteTokenAccount ??= (0, import_spl_token7.getAssociatedTokenAddressSync)(
      quoteMint,
      user,
      true,
      quoteTokenProgram
    );
    const [userBaseAccountInfo, userQuoteAccountInfo] = await this.connection.getMultipleAccountsInfo([
      userBaseTokenAccount,
      userQuoteTokenAccount
    ]);
    return {
      globalConfig,
      feeConfig,
      poolKey,
      poolAccountInfo,
      pool,
      poolBaseAmount: new import_bn12.default(decodedPoolBaseTokenAccount.amount.toString()),
      poolQuoteAmount: new import_bn12.default(decodedPoolQuoteTokenAccount.amount.toString()),
      baseTokenProgram,
      quoteTokenProgram,
      baseMint,
      baseMintAccount: decodedBaseMintAccount,
      user,
      userBaseTokenAccount,
      userQuoteTokenAccount,
      userBaseAccountInfo,
      userQuoteAccountInfo,
      quoteTransferFee: await this.quoteTransferFee(
        quoteMint,
        quoteMintAccountInfo
      )
    };
  }
  async liquiditySolanaState(poolKey, user, userBaseTokenAccount = void 0, userQuoteTokenAccount = void 0, userPoolTokenAccount = void 0) {
    const [globalConfigAccountInfo, poolAccountInfo] = await this.connection.getMultipleAccountsInfo([
      GLOBAL_CONFIG_PDA,
      poolKey
    ]);
    if (globalConfigAccountInfo === null) {
      throw new Error("Global config account not found");
    }
    if (poolAccountInfo === null) {
      throw new Error("Pool account not found");
    }
    const globalConfig = PUMP_AMM_SDK.decodeGlobalConfig(
      globalConfigAccountInfo
    );
    const pool = PUMP_AMM_SDK.decodePool(poolAccountInfo);
    const {
      baseMint,
      quoteMint,
      lpMint,
      poolBaseTokenAccount,
      poolQuoteTokenAccount
    } = pool;
    const [
      baseMintAccountInfo,
      quoteMintAccountInfo,
      poolBaseAccountInfo,
      poolQuoteAccountInfo
    ] = await this.connection.getMultipleAccountsInfo([
      baseMint,
      quoteMint,
      poolBaseTokenAccount,
      poolQuoteTokenAccount
    ]);
    if (baseMintAccountInfo === null) {
      throw new Error(`baseMint=${baseMint.toString()} not found`);
    }
    if (quoteMintAccountInfo === null) {
      throw new Error(`quoteMint=${quoteMint.toString()} not found`);
    }
    if (poolBaseAccountInfo === null) {
      throw new Error(
        `Pool base token account ${poolBaseTokenAccount.toString()} not found`
      );
    }
    if (poolQuoteAccountInfo === null) {
      throw new Error(
        `Pool quote token account ${poolQuoteTokenAccount.toString()} not found`
      );
    }
    const [baseTokenProgram, quoteTokenProgram] = [
      baseMintAccountInfo.owner,
      quoteMintAccountInfo.owner
    ];
    const decodedPoolBaseTokenAccount = import_spl_token7.AccountLayout.decode(
      poolBaseAccountInfo.data
    );
    const decodedPoolQuoteTokenAccount = import_spl_token7.AccountLayout.decode(
      poolQuoteAccountInfo.data
    );
    userBaseTokenAccount ??= (0, import_spl_token7.getAssociatedTokenAddressSync)(
      baseMint,
      user,
      true,
      baseTokenProgram
    );
    userQuoteTokenAccount ??= (0, import_spl_token7.getAssociatedTokenAddressSync)(
      quoteMint,
      user,
      true,
      quoteTokenProgram
    );
    userPoolTokenAccount ??= (0, import_spl_token7.getAssociatedTokenAddressSync)(
      lpMint,
      user,
      true,
      import_spl_token7.TOKEN_2022_PROGRAM_ID
    );
    const [userBaseAccountInfo, userQuoteAccountInfo, userPoolAccountInfo] = await this.connection.getMultipleAccountsInfo([
      userBaseTokenAccount,
      userQuoteTokenAccount,
      userPoolTokenAccount
    ]);
    return {
      globalConfig,
      poolKey,
      poolAccountInfo,
      pool,
      poolBaseTokenAccount: decodedPoolBaseTokenAccount,
      poolQuoteTokenAccount: decodedPoolQuoteTokenAccount,
      baseTokenProgram,
      quoteTokenProgram,
      user,
      userBaseTokenAccount,
      userQuoteTokenAccount,
      userPoolTokenAccount,
      userBaseAccountInfo,
      userQuoteAccountInfo,
      userPoolAccountInfo,
      quoteTransferFee: await this.quoteTransferFee(
        quoteMint,
        quoteMintAccountInfo
      )
    };
  }
  /**
   * The Token-2022 transfer fee `quoteMint` charges this epoch, or `null` (no RPC call unless
   * the mint carries `TransferFeeConfig`).
   */
  async quoteTransferFee(quoteMint, quoteMintAccountInfo) {
    const config = parseTransferFeeConfig(quoteMint, quoteMintAccountInfo);
    if (config === null) {
      return null;
    }
    return transferFeeAt(config, (await this.connection.getEpochInfo()).epoch);
  }
  /**
   * The quote mint a creator vault is keyed by and the token program owning it. A bonding
   * curve's zero key (a SOL coin's `quote_mint`) is normalized to legacy WSOL, as
   * `canonicalPumpPoolPda` does. The program is `quoteTokenProgram` when given, SPL Token for
   * WSOL (no fetch), otherwise the mint account's owner, which must be SPL Token or Token-2022
   * (what the on-chain `quote_token_program` interface accepts), so an existing non-mint account
   * such as a wallet or the System Program can never be mistaken for a token program.
   */
  async resolveQuote(quoteMint, quoteTokenProgram) {
    quoteMint = canonicalPoolQuoteMint(quoteMint);
    if (quoteTokenProgram !== void 0) {
      return { quoteMint, quoteTokenProgram };
    }
    if (quoteMint.equals(import_spl_token7.NATIVE_MINT)) {
      return { quoteMint, quoteTokenProgram: import_spl_token7.TOKEN_PROGRAM_ID };
    }
    const quoteMintAccountInfo = await this.connection.getAccountInfo(quoteMint);
    if (quoteMintAccountInfo === null) {
      throw new Error(`quoteMint=${quoteMint.toString()} not found`);
    }
    const owner = quoteMintAccountInfo.owner;
    if (!owner.equals(import_spl_token7.TOKEN_PROGRAM_ID) && !owner.equals(import_spl_token7.TOKEN_2022_PROGRAM_ID)) {
      throw new Error(
        `quoteMint=${quoteMint.toString()} is not an SPL Token or Token-2022 mint (owner ${owner.toString()})`
      );
    }
    return { quoteMint, quoteTokenProgram: owner };
  }
  /**
   * Everything `PumpAmmSdk.collectCoinCreatorFee` needs to pay out the creator's AMM fees quoted
   * in `quoteMint` (WSOL by default; a bonding curve's zero key is accepted for SOL coins).
   * `quoteTokenProgram` is resolved from the mint when omitted. `coinCreatorTokenAccount`
   * defaults to the creator's ATA for the quote, the only destination the builder creates when
   * it is missing; any other destination must already exist.
   */
  async collectCoinCreatorFeeSolanaState(coinCreator, coinCreatorTokenAccount = void 0, quoteMint = import_spl_token7.NATIVE_MINT, quoteTokenProgram = void 0) {
    ({ quoteMint, quoteTokenProgram } = await this.resolveQuote(
      quoteMint,
      quoteTokenProgram
    ));
    const coinCreatorVaultAuthority = coinCreatorVaultAuthorityPda(coinCreator);
    const coinCreatorVaultAta = coinCreatorVaultAtaPda(
      coinCreatorVaultAuthority,
      quoteMint,
      quoteTokenProgram
    );
    coinCreatorTokenAccount ??= (0, import_spl_token7.getAssociatedTokenAddressSync)(
      quoteMint,
      coinCreator,
      true,
      quoteTokenProgram
    );
    const [coinCreatorVaultAtaAccountInfo, coinCreatorTokenAccountInfo] = await this.connection.getMultipleAccountsInfo([
      coinCreatorVaultAta,
      coinCreatorTokenAccount
    ]);
    return {
      coinCreator,
      quoteMint,
      quoteTokenProgram,
      coinCreatorVaultAuthority,
      coinCreatorVaultAta,
      coinCreatorTokenAccount,
      coinCreatorVaultAtaAccountInfo,
      coinCreatorTokenAccountInfo
    };
  }
  /**
   * The creator's uncollected AMM fees quoted in `quoteMint` (WSOL by default; a bonding curve's
   * zero key is accepted for SOL coins): the balance of the creator vault ATA, or zero when it
   * does not exist. `quoteTokenProgram` is resolved from the mint when omitted.
   */
  async getCoinCreatorVaultBalance(coinCreator, quoteMint = import_spl_token7.NATIVE_MINT, quoteTokenProgram = void 0) {
    ({ quoteMint, quoteTokenProgram } = await this.resolveQuote(
      quoteMint,
      quoteTokenProgram
    ));
    const coinCreatorVaultAta = coinCreatorVaultAtaPda(
      coinCreatorVaultAuthorityPda(coinCreator),
      quoteMint,
      quoteTokenProgram
    );
    return this.vaultAtaBalance(
      coinCreatorVaultAta,
      await this.connection.getAccountInfo(coinCreatorVaultAta),
      quoteTokenProgram
    );
  }
  /**
   * The creator's uncollected AMM fees for every quote in `quotes`, keyed by the quote mint
   * (base58), in one account fetch per 100 quotes. Callers enumerating every quote mint a vault
   * may hold (the Global whitelist plus the QuoteControl list, plus WSOL) pass each mint with its
   * owner token program; a missing vault ATA reads as zero. Mints are used as given (no zero-key
   * normalization), so every entry lands under its own key.
   */
  async getCoinCreatorVaultBalances(coinCreator, quotes) {
    const coinCreatorVaultAuthority = coinCreatorVaultAuthorityPda(coinCreator);
    const coinCreatorVaultAtas = quotes.map(
      ({ mint, tokenProgram }) => coinCreatorVaultAtaPda(coinCreatorVaultAuthority, mint, tokenProgram)
    );
    const accountInfos = [];
    for (let i = 0; i < coinCreatorVaultAtas.length; i += 100) {
      accountInfos.push(
        ...await this.connection.getMultipleAccountsInfo(
          coinCreatorVaultAtas.slice(i, i + 100)
        )
      );
    }
    return new Map(
      quotes.map(({ mint, tokenProgram }, i) => [
        mint.toBase58(),
        this.vaultAtaBalance(
          coinCreatorVaultAtas[i],
          accountInfos[i],
          tokenProgram
        )
      ])
    );
  }
  /**
   * Token balance of a fetched vault ATA; zero when the account does not exist. `unpackAccount`
   * accepts the extension-bearing (170-182 byte) accounts Token-2022 quotes produce.
   */
  vaultAtaBalance(vaultAta, accountInfo, tokenProgram) {
    if (accountInfo === null) {
      return new import_bn12.default(0);
    }
    try {
      return new import_bn12.default(
        (0, import_spl_token7.unpackAccount)(vaultAta, accountInfo, tokenProgram).amount.toString()
      );
    } catch (error) {
      console.warn(`Error decoding token account ${vaultAta}:`, error);
      return new import_bn12.default(0);
    }
  }
  /**
   * `PumpAmmSdk.transferCreatorFeesToPumpV2Instruction` with the quote token program resolved
   * from the mint account's owner; a bonding curve's zero key is accepted for SOL coins.
   */
  async transferCreatorFeesToPumpV2Instruction(payer, coinCreator, quoteMint) {
    const quote = await this.resolveQuote(quoteMint, void 0);
    return PUMP_AMM_SDK.transferCreatorFeesToPumpV2Instruction({
      payer,
      coinCreator,
      quoteMint: quote.quoteMint,
      quoteTokenProgram: quote.quoteTokenProgram
    });
  }
  /**
   * `PumpAmmSdk.setCoinCreator` for `poolKey`, with `metadata` and `bonding_curve` derived from
   * the pool's base mint (read with `decodePool`, so a pre-upgrade 261-byte pool works) and
   * preceded by `extend_account` (rent paid by `payer`) when the pool is shorter than
   * `POOL_ACCOUNT_NEW_SIZE`: the program writes the whole `Pool` back, which fails on an
   * un-grown account.
   */
  async setCoinCreatorInstructions(poolKey, payer) {
    const poolAccountInfo = await this.connection.getAccountInfo(poolKey);
    if (poolAccountInfo === null) {
      throw new Error("Pool account not found");
    }
    const pool = PUMP_AMM_SDK.decodePool(poolAccountInfo);
    const instructions = [];
    if (poolAccountInfo.data.length < POOL_ACCOUNT_NEW_SIZE) {
      instructions.push(await PUMP_AMM_SDK.extendAccount(poolKey, payer));
    }
    instructions.push(
      await PUMP_AMM_SDK.setCoinCreator(poolKey, pool.baseMint)
    );
    return instructions;
  }
  /**
   * `PumpAmmSdk.sweepCreatorFeeInstruction` for `poolKey`, with the pool and its quote token
   * program read from chain: what a CTO, a fee-sharing config creation or an `update_fee_shares`
   * for the pool's coin must carry before it, in the same transaction.
   */
  async sweepCreatorFeeInstruction(poolKey, payer) {
    const pool = await this.fetchPool(poolKey);
    const { quoteTokenProgram } = await this.resolveQuote(
      pool.quoteMint,
      void 0
    );
    return PUMP_AMM_SDK.sweepCreatorFeeInstruction({
      payer,
      poolKey,
      pool,
      quoteTokenProgram
    });
  }
  /**
   * Canonical pools as `multi_hop_swap` hops, in `poolKeys` order, with the state
   * `multiHopSwapQuote` prices them from (the pool, its mints' token programs, its vault balances,
   * the base mint supply) and the GlobalConfig / FeeConfig it needs. Two RPC round trips for any
   * route length; each hop is usable as a `PumpAmmSdk.multiHopSwapInstructions` venue as is.
   */
  async multiHopPoolHops(poolKeys) {
    const [globalConfigInfo, feeConfigInfo, ...poolInfos] = await this.connection.getMultipleAccountsInfo([
      GLOBAL_CONFIG_PDA,
      PUMP_AMM_FEE_CONFIG_PDA,
      ...poolKeys
    ]);
    if (globalConfigInfo === null) {
      throw new Error("Global config account not found");
    }
    const pools = poolInfos.map((info2, i) => {
      if (info2 === null) {
        throw new Error(`pool=${poolKeys[i].toString()} not found`);
      }
      return PUMP_AMM_SDK.decodePool(info2);
    });
    const keys = [
      ...new Map(
        pools.flatMap((pool) => [
          pool.baseMint,
          pool.quoteMint,
          pool.poolBaseTokenAccount,
          pool.poolQuoteTokenAccount
        ]).map((key) => [key.toBase58(), key])
      ).values()
    ];
    const infos = new Map(
      (await this.connection.getMultipleAccountsInfo(keys)).map((info2, i) => {
        if (info2 === null) {
          throw new Error(`account=${keys[i].toString()} not found`);
        }
        return [keys[i].toBase58(), info2];
      })
    );
    const info = (key) => infos.get(key.toBase58());
    const amount = (key) => new import_bn12.default((0, import_spl_token7.unpackAccount)(key, info(key), info(key).owner).amount.toString());
    const quoteTransferFees = await Promise.all(
      pools.map(
        (pool) => this.quoteTransferFee(pool.quoteMint, info(pool.quoteMint))
      )
    );
    return {
      globalConfig: PUMP_AMM_SDK.decodeGlobalConfig(globalConfigInfo),
      feeConfig: feeConfigInfo ? PUMP_AMM_SDK.decodeFeeConfig(feeConfigInfo) : null,
      hops: pools.map((pool, i) => ({
        kind: "pool",
        poolKey: poolKeys[i],
        pool,
        baseTokenProgram: info(pool.baseMint).owner,
        quoteTokenProgram: info(pool.quoteMint).owner,
        poolBaseAmount: amount(pool.poolBaseTokenAccount),
        poolQuoteAmount: amount(pool.poolQuoteTokenAccount),
        baseMintSupply: new import_bn12.default(
          (0, import_spl_token7.unpackMint)(
            pool.baseMint,
            info(pool.baseMint),
            info(pool.baseMint).owner
          ).supply.toString()
        ),
        quoteTransferFee: quoteTransferFees[i]
      }))
    };
  }
  async boostBuyAndBurnInstruction(poolKey, authority, quoteAmountIn, minBaseAmountBurned) {
    const poolAccountInfo = await this.connection.getAccountInfo(poolKey);
    if (poolAccountInfo === null) {
      throw new Error("Pool account not found");
    }
    const pool = PUMP_AMM_SDK.decodePool(poolAccountInfo);
    const [baseMintAccountInfo, quoteMintAccountInfo] = await this.connection.getMultipleAccountsInfo([
      pool.baseMint,
      pool.quoteMint
    ]);
    if (baseMintAccountInfo === null) {
      throw new Error(`baseMint=${pool.baseMint.toString()} not found`);
    }
    if (quoteMintAccountInfo === null) {
      throw new Error(`quoteMint=${pool.quoteMint.toString()} not found`);
    }
    return PUMP_AMM_SDK.boostBuyAndBurnInstruction(
      poolKey,
      pool,
      authority,
      quoteAmountIn,
      minBaseAmountBurned,
      baseMintAccountInfo.owner,
      quoteMintAccountInfo.owner
    );
  }
  async claimTokenIncentives(user, payer) {
    const { mint } = await this.fetchGlobalVolumeAccumulator();
    if (mint.equals(import_web37.PublicKey.default)) {
      return [];
    }
    const [mintAccountInfo, userAccumulatorAccountInfo] = await this.connection.getMultipleAccountsInfo([
      mint,
      userVolumeAccumulatorPda(user)
    ]);
    if (!mintAccountInfo) {
      return [];
    }
    if (!userAccumulatorAccountInfo) {
      return [];
    }
    return [
      await OFFLINE_PUMP_AMM_PROGRAM.methods.claimTokenIncentives().accountsPartial({
        user,
        payer,
        mint,
        tokenProgram: mintAccountInfo.owner
      }).instruction()
    ];
  }
  async getTotalUnclaimedTokens(user) {
    const [
      globalVolumeAccumulatorAccountInfo,
      userVolumeAccumulatorAccountInfo
    ] = await this.connection.getMultipleAccountsInfo([
      GLOBAL_VOLUME_ACCUMULATOR_PDA,
      userVolumeAccumulatorPda(user)
    ]);
    if (!globalVolumeAccumulatorAccountInfo || !userVolumeAccumulatorAccountInfo) {
      return new import_bn12.default(0);
    }
    const globalVolumeAccumulator = PUMP_AMM_SDK.decodeGlobalVolumeAccumulator(
      globalVolumeAccumulatorAccountInfo
    );
    const userVolumeAccumulator = PUMP_AMM_SDK.decodeUserVolumeAccumulator(
      userVolumeAccumulatorAccountInfo
    );
    return totalUnclaimedTokens(globalVolumeAccumulator, userVolumeAccumulator);
  }
  async getCurrentDayTokens(user) {
    const [
      globalVolumeAccumulatorAccountInfo,
      userVolumeAccumulatorAccountInfo
    ] = await this.connection.getMultipleAccountsInfo([
      GLOBAL_VOLUME_ACCUMULATOR_PDA,
      userVolumeAccumulatorPda(user)
    ]);
    if (!globalVolumeAccumulatorAccountInfo || !userVolumeAccumulatorAccountInfo) {
      return new import_bn12.default(0);
    }
    const globalVolumeAccumulator = PUMP_AMM_SDK.decodeGlobalVolumeAccumulator(
      globalVolumeAccumulatorAccountInfo
    );
    const userVolumeAccumulator = PUMP_AMM_SDK.decodeUserVolumeAccumulator(
      userVolumeAccumulatorAccountInfo
    );
    return currentDayTokens(globalVolumeAccumulator, userVolumeAccumulator);
  }
};

# Independent review: nine SDK source mappings

PASS source-only scope; no blocking defect found. Exact packet manifest
4bcd0ca9d8cb69a219d48d4098cab37556c7899c5ce447df8e55312db019de9e.
No publication, source activation, original read/decoder, SDK JavaScript,
network/provider/transaction/signing/native/VM execution occurred.

Reviewed the complete REPORT/verifier and critical retained TypeScript source.
Pure packet verification returned0, checking archive SHA256/SHA1/SHA512,
regular tar members, exact21 source/IDL member copies, control manifest,
line witnesses and IDL mappings. Independent passive source-object parsing
checked all9 objects/132 supplied fields, raw method argument order and all
IDL account order/signature/write/PDA/relation records. Six AMM helpers have
17 strict fields; three Pump helpers supply10/17 and omit the same7 declared
accounts. Pump local quote/bondingCurve aliases expand as recorded; its
buyback branch is deliberately symbolic rather than a fabricated account.
Two initial review-parser comparisons needed adjustment for helper declaration
selection and symbolic aliases; final checks pass. Neither was a packet defect.

AMM raw builders forward amounts directly and share tradeV2Accounts. Static
GLOBAL_CONFIG_PDA differs from the globalConfig input state used for recipient
selection. Math.random selects an entry; ATA derivation uses actual pool quote
mint and quote program with off-curve owners allowed. Empty/malformed state and
membership remain unresolved. High-level routing requires both options.v2 and
!isCashbackCoin; direct V2 methods bypass that routing test. Setup source wraps
native input, checks canonical output ATA and closes native output; custom
account existence is not established by an object field.

Pump raw methods preserve exact defaults and partialFill argument shape, with
three omitted-account lists bound to IDL recipes but no resolver invocation.
Absent/zero/native quote normalization, curve/base/quote ATA expressions and
legacy random-wallet versus token default-first-wallet ATA are correctly
separated. High-level buy/exact-buy base ATA setup precedes buyback ATA setup
and raw; token-quote sell adds user quote ATA then buyback ATA. The cashback
precheck is high-level only, not proof of target behavior.

Reviewed numeric text against executable definitions, not SDK comments:
AMM booked/net/LP/protocol/creator buyDebit, nonmayhem V2 floor buyback slice,
vault transfer-fee gross-up, exact-budget floor division and net-only shave
match the report. Sell uses virtual quote pricing, real reserves less fee
buckets, post-fee transfer net and floor-scaled slippage. Pump wrapper slippage
uses floor(slippage*10)/1000 with1/0 minimum floors for exact-buy/sell;
this is no domain/finite-input validation. Pump quote source ceilFee,
creator-zero handling, mayhem buyback0, two-leg debit gross-up and exact-budget
shave map as reported. No new numerical evaluation or target quote acceptance
is inferred. Quote helpers and raw instruction builders remain separate calls.

The nine mappings complete only the old25-site symbolic inventory, disjoint
from the previous16 observations. Account flags/coverage do not prove state
versions, epoch transfer fees, valid mint/token-program association, recipients,
ownership/extensions, Anchor compatibility, setup ordering after resolution,
ABI/effects or historical source/binary identity. No stopped V3 crossing,
partial-fill, multi-hop, extension or original-body lane is resumed. Whole
identity remains0/4. This review is suitable for the packet's existing
source-only wording and does not approve a native/runtime follow-on.

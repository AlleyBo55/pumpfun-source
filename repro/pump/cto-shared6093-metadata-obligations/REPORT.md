# Retained metadata correction and remaining obligations

PASS for the metadata facts below. This packet reads saved JSON metadata and four already admitted text files only. It preserves the exact compressed metadata bytes; it does not read an original ELF, decode instructions, acquire a new body or callee, run a VM, compile, or contact the network. Recorded absolute source locations in input-bindings.json are provenance labels. The portable verifier opens bundled files only.

| Original inferred window | Bytes | Normalized relations | Call-consistent relations | Current fdf candidate |
| --- | ---: | ---: | ---: | --- |
| 1108280–1112888 | 4608 | 0 | 0 | Unresolved |
| 1565736–1566664 | 928 | 2 | 1 | 1292560, named associated_token::create_idempotent |
| 604312–606400 | 2088 | 0 | 0 | Unresolved |
| 169240–169712 | 472 | 0 | 0 | Shared frozen helper is 96 bytes; no pattern relation |
| 169712–170160 | 448 | 0 | 0 | Shared raw helper is 440 bytes; no pattern relation |
| 1715000–1715104 | 104 | 1 | 1 | 1387344, named AccountInfo::data_is_empty |

The relation counts above hold in retained71ec, d75, 6e, and current fdf metadata. Candidate addresses change across builds. Window1715000 has zero raw-equal candidate relations in every retained build. The original window hashes, starts, ends and sizes are unchanged across all four inventories. All inventories retain 1,035 original windows.

The phrase “native157128 unknown callee/header” in prior derived review limits is misleading. Address157128 is not a separate entry among the 1,035 original windows. It is an existing branch inside admitted parent141840–169240. The retained metadata records branch150200→157128, and the already admitted text has both the branch instruction and target instruction. Native control correspondence remains open, but missing-callee terminology must not describe this branch. Earlier sealed reports remain unchanged historical evidence.

Window1565736 must also not be described as having no normalized correspondence. It has two normalized candidates, with one surviving call-fixed-point pruning. The surviving current candidate is the928-byte associated-token create_idempotent wrapper. This is stronger correspondence evidence than an unnamed unknown callee, while still leaving caller ABI, argument identity, account roles, privileges, PDA seeds and complete CPI effects unresolved. Calling all three targets1108280/1565736/604312 equally unmapped loses this distinction.

The exact inferred boundaries are entry-to-next-entry metadata, not proof of historical function boundaries. Normalization removes selected address-bearing fields; call-fixed-point pruning checks relations among saved call targets. Neither proves equal pointed-to data, arbitrary inputs, semantic identity or a complete transitive closure. A relation is not a new acquisition authorization.

## Remaining obligations

1. Establish caller argument layout and ownership correspondence at retained parent calls157056→1108280 and166600→604312. Their windows have no normalized candidate relation. Saved call sites identify the remaining questions; they do not prove ABI, argument/account identities, program IDs, signer/writable domains, seeds, return/error ownership, or CPI effects.
2. For create_idempotent, use the existing928-byte normalized and call-consistent relation as an anchor, then establish how caller sites165944 and166408 supply account roles, payer/rent funding, authority, seeds and return ownership. Callee correspondence alone does not close those caller obligations.
3. Establish native branch157128 correspondence within the admitted parent control flow: quote selection, rent/lamport arithmetic, zero/positive routing, payouts, overflow and error propagation. Address order alone is not execution order; this packet does not infer control semantics from sorted call sites.
4. Retain the distinction between original472/448-byte helpers and current96/440-byte shared helpers. Existing empty-return text and finite signed observations support the chosen empty/frozen/amount routes. They do not prove equality for malformed/short data, borrow failures, aliases, header representation, token extensions or every deserialization error. The104-byte data_is_empty relation is syntactic evidence with no raw equality; it does not independently establish the full account-header or borrow ABI.
5. Preserve the actual ordering obligations: shared A has two separate caller empty checks with frozen then conditional amount handling; shared B reads amount then frozen; positive frozen routes own6093 errors; zero routes skip the observed extra AMM/ATA/payout effects. The finite ordinary363 and six-case saved acceptance closes those observations only. Cross-account aliases, CPI/sysvar/drop/OOM behavior, transitive dependencies and all other inputs remain open.
6. Natural source origins differ, compiler/toolchain historical identity is unproved, and whole original byte identity remains false. No field-layout universality, default candidate selection or deployment conclusion follows.

No stopped research probe was resumed. Preparation made one syntax-error metadata query and one oververbose metadata query; neither changed source inputs or decoded anything. The final derive_metadata.py and verify.py perform bounded metadata checks and retain derived records under a separate seal.

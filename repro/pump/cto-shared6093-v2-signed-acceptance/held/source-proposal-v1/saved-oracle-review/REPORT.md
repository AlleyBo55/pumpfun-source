# Saved shared6093 six-case oracle review

**PASS for integrity and cryptography of the saved finite oracle, not a preservation pass or universal field mapping.** One root run completed12 original/candidate sides. This review replayed saved transaction decoding/signature/PDA checks only; it performed no VM, compiler, helper import, original decoder, new callee/body acquisition or network action. Source15/37, candidate6e, captured-original7a, exact plan113b, claim/controller/driver/launch and all raw side/output hashes bind. Raw output and plan stayed unchanged.

All12 saved transactions verify every actual required signature derived from their message headers,24 signature fields total. The fee payer matches the copied seed215 control; the independently derived actual pool-authority PDA is absent from required signers. No signer was injected. The two baseline before-states also exactly equal both sides of their prior363-case receipt, an additional saved check beyond the plan's baseline requirement. Original/candidate before-states match, and variants differ only in their chosen165-byte token account's state108 and amount64:72.

| Family/case | Original result | Existing6e result | Compared-effect differences |
| --- | --- | --- | --- |
|A baseline | success | success | none |
|A coin_creator_vault_ata frozen-positive |6093, original admin_cto.rs660 | success | error,after,events,inner |
|A frozen-zero | success/no6093 | success | inner |
|B baseline | success | success | none |
|B creator_vault_quote_token_account frozen-positive |6093, original admin_cto.rs719 | success | error,after,events,inner |
|B frozen-zero | success/no6093 | success | after,inner |

Every side's raw logs are retained; logs differ between original and candidate in **all six cases**, including the two otherwise matching baselines. The diagnostic's success status means its explicit finite hypotheses were observed; it does not mean candidate preservation or shared behavior completion.

`saved-inner-instructions.json` resolves only saved transaction account indices and inner instruction byte payloads. The nested Solders JSON shortvec prefix is independently decoded and required to equal the remaining item count before interpretation. No program or instruction body is decoded. In familyA frozen-zero the candidate adds one first AMM CPI, data `01214eb921432c5c`, absent from the original. Remaining saved inner calls agree in this fixture; final snapshots agree. In familyB frozen-zero the candidate adds the idempotent ATA instruction and nested token/System CPI sequence before the common later calls. The candidate also changes admin_set_creator_authority and holder_creator_vault_quote_token_account; the original does not. Guards alone would leave these zero-route errors intact.

The admitted c812 text control separately establishes S136's two distinct empty reads, frozen-before-conditional-raw guard660 and conditional addressed call1108280 before the S72 raw-before-frozen guard719 and positive continuation calls1565736/604312. The oracle supplies finite named-account causality consistent with A↔S136 and B↔S72. It does not recover the historical aggregate field layout, generic ABI, call effects, alias domain or all route behavior. The new partial source proposal may apply these local guard/skip obligations while explicitly retaining those gaps. It must not assert complete correspondence of the current CPI and payout wrappers to the unresolved addressed original calls.

Full signatures, required signer keys, complete raw logs, every effect-field difference and all account-name after differences are retained in derived JSON. Frozen-positive mismatches, frozen-zero mismatches and unclosed boundaries remain authoritative. No source, selected candidate, status or default was modified by this review.

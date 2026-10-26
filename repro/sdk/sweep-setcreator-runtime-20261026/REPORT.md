# Saved audit of actual public compiled SDK wrappers

PASS for the bounded offline observation under plan `4ef3bda5…`, root review `d194bebe…` and consumed admission `744669e4…`. Root's actual controller and Node child both exited zero in session 7332. There was one attempt, no observation timeout, no process termination and no retry. The root terminal record is explicitly a tool observation rather than a fabricated separately captured controller stream.

## Actual results

| Public compiled wrapper calls | Constructed and fully compared | Actual errors |
| --- | ---: | ---: |
| AMM protocol/creator sweeps in both SDK copies | 4 | 0 |
| Pump curve protocol/creator sweeps | 2 | 0 |
| Creator update with supplied baseMint, both copies | 2 | 0 |
| Creator update with omitted baseMint, both copies | 0 | 2 |

All eight constructed instruction objects match their independently prepared program ID, discriminator, account keys, order and signer/writable flags: 84 account metas in total. The IDL names attached to output are annotations by index, not properties emitted by TransactionInstruction. Both omitted-baseMint calls genuinely throw `Reached maximum depth for account resolution. Unresolved accounts: metadata, bondingCurve`, with the exact punctuation, names and stacks retained. Those errors are not relabeled as successful account resolution or target-program rejections.

The recorded function text for every one of the ten calls occurs uniquely in the correct authenticated public compiled bundle and matches its recorded function hash. The public package exports route to Pump main, Pump's public `/swap` entry and Swap main. No copied account builder was substituted. Actual arguments match the fixed synthetic keys and minimal Pool-shaped client input. Each protocol recipient array has one member, without a Math.random override. Pump curve calls truly omit quoteTokenProgram and supply the zero quote mint; their observed instructions use the expected token-program default and normalized native quote addresses. The creator negative cases truly omit the second argument.

The current SDK graph uses real public singletons and genuine module exports under declared integrity observation and deny-only transport/signing guards. The loaded function and module evidence is distinct from the earlier TypeScript source interpretations. Successful construction with a supplied base mint observes the two formerly implicit creator accounts resolving to the expected values in these cases; it does not prove arbitrary state or resolver compatibility.

## Numeric and provenance checks

Root independently used existing Solders 0.27.1 Pubkey utilities on saved input data. Its retained record reports sixteen PDA derivation records, thirteen unique addresses and all eight instruction objects/84 metas matching. This audit binds that record, checks every seed/program/bump digest and compressed-point constraint with standard-library arithmetic, and compares each output against the saved instructions. Root's separate native crypto utility import is honestly recorded; this child did not import Solders, Node or SDK modules.

All 316 loaded module paths/hashes are members of the authenticated 4,747-file graph. The two root graph files are separately bound, so all 4,749 before/after graph files agree exactly. A separate live file-hash audit also found the current graph unchanged; default portable replay uses bundled saved data only. Node and Python binary pins, root review/admission, exact launch arguments, raw stdout/stderr, child status, controller status and all source/fixture/oracle bindings agree. Reading compiled bundle bytes as data does not import or execute them.

There are 1,203 recorded module load attempts, which are not 1,203 unique modules. One genuine native addon invocation is recorded LOADED: bufferutil darwin-arm64, SHA256 `688f957f…`; the same file appears in the loaded module inventory. There are no recorded native dlopen errors. Thirteen missing bigint-buffer native resolution candidates produced MODULE_NOT_FOUND before dlopen, and one optional encoding resolution also failed. The exact 77-byte stderr warning reports the genuine BigInt pure-JavaScript fallback. Missing module resolution is not mislabeled as thirteen native loading attempts or a forced loader substitution.

No blocked API events were recorded. This means no calls reached the declared denial hooks; it is not a universal operating-system network or signing audit. In particular, the omitted-account resolver errors do not prove that no internal resolution/fetch path was considered. No provider, fetched account response, signature, SDK helper or package export was mocked. Root's guards and genuine forwarding observer are bound to the actual executed source.

## Scope and preserved preparation history

This is synthetic client instruction construction, not a signed transaction, valid pool/mint/token/metadata state, RPC service acceptance, Metaplex program execution, target VM execution, compiler attribution, historical deployed dependency identity, unrestricted SDK compatibility or whole-contract byte identity. Online fetching, actual extension/rent/ATA execution, arbitrary remaining accounts, other state branches and the nine still-unexpanded original dynamic object sites remain open. Original selected program source/artifacts/status and the Node graph are not changed by this audit.

The first metadata lookup in this audit assumed the root review was a manifest package; it is a directly hashed review.json. That FileNotFoundError is retained as an explicitly labeled tool-observation preparation failure. It changed no inputs and caused no SDK/native rerun. The corrected lookup binds the actual `d194bebe…` review file.

Run `python -B verify.py --expected-seal <trusted review SHA256>` for a portable saved-only replay. It verifies strict membership/hashes and runs only the reviewed standard-library Python audit. It does not follow source_label provenance paths, run the Node script, reload SDKs, import Solders or contact a service. Raw copied SDK JavaScript is an inert witness, not an execution entry point.

# Fees: attribute duplicate bodies through encoded local calls

The stable-sort research candidate has 340 unique normalized body pairs, but another 147 original windows belong to 44 duplicate-body groups. A masked body alone cannot select a counterpart within those groups. This packet uses actual local-CALL targets at corresponding instruction offsets in previously paired callers to attribute **53 additional pairs**: 43 in the first round and 10 in the second. The result contains **393 attributed pairs**, with **2,208 aligned local calls to attributed targets and no conflicts**. Another 26 aligned calls reach different-body frontiers; they are retained as diagnostics and do not create pairs.

The candidate binary is unchanged. This is an attribution improvement, not new instruction coverage or a new build. The underlying counts remain **340 unique body pairs, 147 duplicate-body original windows, and 98 unmatched original windows**. Of the duplicate-body windows, **94 remain unattributed in 31 groups**. The original has 585 inferred windows and the candidate 579; all candidate boundaries/extents exactly reproduce its function symbol table. Core whole-file identity remains **0/4**.

## Verification

```sh
python3 research/fees-call-target-attribution/verify.py
python3 -I research/fees-call-target-attribution/verify.py
python3 -I research/fees-call-target-attribution/test_attribute.py
```

The checker re-derives every boundary, body signature, local-call edge, discovery round and witness from the pinned ELF bytes. Eight adversarial tests cover multi-round propagation, conflicting forward/reverse proposals, inconsistent known targets, conflicts exposed after a promotion, different-body frontiers, shifted call positions, and independence from names, address order and input order. An unreached duplicate stays unresolved even if another member of its body group has been attributed. Function names annotate candidate output only; they never select matches.

Each promotion needs an incoming call from a caller paired in an earlier round, an identical full normalized callee-body signature, and mutually unambiguous proposals from all currently paired callers. A conflict with an existing pair aborts refinement. External relocations are excluded from local-call arithmetic. CALL targets are decoded from the encoded signed immediate, not inferred from disassembly labels. The retained report records all final witnesses and the 26 different-body frontier edges.

Examples include account-parser adapters, allocation/deallocation helpers, arithmetic builtins, and panic wrappers. Such roles remain candidate-derived attributions, conditional on the starting structural correspondences. Equal normalized bodies and aligned calls do not establish equality of opaque pointed-to data, dynamic calls, error payloads or behavior. CALL immediates and actual relocated LDDW addresses are still masked for body signatures; all other encoded bytes and external import identities are retained. Ambiguity is preserved where the evidence does not resolve it.

## Candidate provenance

The unchanged candidate is from [PR #91](https://github.com/lalalune/pumpfun-source/pull/91), pinned at fork commit [`85611ee`](https://github.com/shawkkkkk/pumpfun-source/commit/85611eeadb4432e463832285e4af248ec83aaebe). Its stripped SHA-256 is `f6d23ea00a81b97b6f75d036287a326936cd76534cf6b68a40540e338851ae66`. Both stripped and unstripped outputs are retained here. The checker binds all 26 source inputs, the five complete source overrides, the prior successful build result, and 187 unchanged harness files. The source recipe is official platform-tools v1.44 with the canonical `sbpf-solana-solana` target and `RUSTFLAGS=-Zremap-cwd-prefix=`, stripped with the pinned v1.52 tool. No new build is claimed by this packet.

The same candidate previously passed all 17,331 cases across 18 local original/candidate suites in PR #91; those full execution receipts and rebuild commands remain at the pinned source commit. This analysis does not rerun them or broaden their behavioral scope. Selected sources/candidates, checkpoint ledgers, pinned scripts and workflows remain unchanged.

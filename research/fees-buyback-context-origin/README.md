# Buyback context source-origin recovery

Moving the unchanged `InitializeBuyback` declaration to its observed source
location recovers the **complete 6,256-byte original closure at 358,312**.
There are no lost normalized or raw matches. Fees now has **380 unique
structural pairs and 58 unmatched windows**.

The prior closure differed at two unmasked instruction constants: the source
line (22 instead of 12) and source-path length (33 instead of 50). Its error
origin also pointed to the old path. The declaration now starts at line 12 of
`programs/pump-fees/src/instructions/buyback/mod.rs`, matching the original path,
line and error code 4101. The context fields and attributes are unchanged.
The initializer function remains on its already-recovered line 94.

The old module re-exports the moved declaration and Anchor-generated client
account module through an ordinary glob re-export. This preserves the public
program's imports without hand-writing generated framework code or patching ELF.
Only the two Rust source files involved in the move change; both retain their
line counts and all other 34 source inputs remain unchanged.

## What is now closed locally

| Original address | Bytes | Component | Matching direct callee bodies |
| --- | ---: | --- | ---: |
| 351,128 | 7,184 | Account parser | 58/58 |
| 358,312 | 6,256 | First initialization closure | 17/17 |
| 364,568 | 5,512 | Second initialization closure | 22/22 |
| 370,080 | 560 | Account exit | 7/7 |

The three other bodies were already recovered in the parent. This change adds
one body and closes the parser's remaining direct-call mismatch, for **104/104**
matching direct callee bodies in this four-component set. It does not prove all
referenced data, indirect calls, exhaustive initializer behavior, or full ELF
identity. The previous tier-copy and common-helper panic locations remain equal.

## Reproduction and validation

Parent: `research/fees-buyback-context-ownership`, with its artifact explicitly
reused as the control. A fresh pinned Linux v1.44 root build and its exact
36-file input map are retained. Candidate: 861,000 bytes, SHA-256
`fe11df62162e27700890e5dcd07d5760a66f5528fd89de4b523975dbfc38f112`.

Fresh regression passes 17,331 cases across 18 suites; 1,542 exact
outcome/log/compute comparisons; and the 24 growth, 32 optional-account,
20 user-ID, 8 extension-log and 30 crank-mint cases. Comparison limitations
remain those of each harness. No selected checkpoint is changed.

The full partition is **118 raw-local / 409 normalized-only / 58 unmatched**.
Call refinement gains one additional duplicate correspondence at original
15,440, totaling 442 pairs (380 unique + 62 additionally attributed); 85
duplicate windows remain unattributed. Unmatched original windows span
298,504 / 799,648 text bytes (37.3%). Whole-file equality remains false.

Run `python3 -B research/fees-buyback-context-origin/verify.py` to recheck the
source move, build and artifact hashes, complete bodies, error origin, direct
callees and retained replay. This does not compile or run target programs.

The `test_scope.py` mutation test changes a pathname byte outside `.text` and
confirms that the separate origin check rejects it despite equal instructions.

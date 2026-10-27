# Fees: reproduce the complete authority-update body

A real Rust source file at `programs/pump-fees/src/instructions/admin/update_fee_program_global.rs`, with the guard on line **47**, recovers the complete **3,320-byte original window at 103408**. A Rust `include!` expression keeps its tokens inside the existing public function. This is a compiler reproduction technique, not evidence that the historical source used `include!` or this organization.

The checker proves every body token is preserved, all other public source is unchanged, every subsequent `lib.rs` line position is preserved, and the new file is the only added build input. It reads both actual binary path pointers, all **70 path bytes**, and their line/length stores. The program declaration, namespace and public signature remain unchanged. No executable bytes are patched.

A separately built negative control omits the blank-line preservation. It recovers the same authority window but loses the later windows at 659640 and 660160, falling to 352 unique pairs and 86 unmatched windows. Its complete sources, build and artifacts are retained as static evidence; it is excluded from the proposed source and has no claimed runtime-suite validation.

Unique structural pairs increase from **353 to 354**, with none lost; **84 original windows remain unmatched**. Both candidates have 580 inferred windows, independently equal to all function-symbol extents including aliases. There are 57 unique raw-equal local pairs. Whole-capture and ELF-extent comparisons remain false; core whole-file identity remains **0/4**.

## Verify and rebuild

```sh
python3 research/fees-authority-body-origin/verify.py
python3 -I research/fees-authority-body-origin/verify.py
```

The control and proposal each retain passing **17,331-case** differential suites across 18 local suites, plus **1,542** exact outcome/log/compute comparisons each. The proposal was executed afresh; identical control receipts are explicitly reused from PR #123. The focused matrix covers every optional byte plus absence, both pool flags and three caps in one fixed valid configuration. These finite results do not establish exhaustive program semantics.

The packet retains complete overlays, all **33/34 input hashes**, 187 unchanged harness hashes, stripped/unstripped artifacts, build logs and fresh strip replays. Rebuild from the bound source revision and overlays with official Linux platform-tools v1.44, canonical `sbpf-solana-solana` and `RUSTFLAGS=-Zremap-cwd-prefix=`, following `builds/*-launch.json`. Strip with the pinned v1.52 tool. Logs/hashes document the retained execution; they are not authenticated process traces or proof of historical authenticity.

Packet-local whitespace attributes preserve the exact compiled `lib.rs` captures, including their one trailing space. Root attributes are unchanged.

Structural signatures mask local CALL immediates and actual relocated LDDW addresses while preserving scalar/register/stack/branch bytes and import identities. The exact source-origin checks do not prove all other opaque data or transitive/indirect callees equal. Existing unchecked-input compatibility limits remain. Selected programs, pinned scripts, workflows and checkpoint ledgers are unchanged.

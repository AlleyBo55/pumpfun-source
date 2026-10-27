#!/bin/sh
set -eu
/sdk/rust/bin/rustc -vV > /out/rustc-version.txt
for target in sbf-solana-solana sbpf-solana-solana; do
 /sdk/rust/bin/rustc --crate-name relay_typeid_probe --crate-type lib --edition 2021 -C opt-level=3 -C panic=abort -C overflow-checks=on -Zremap-cwd-prefix= --target "$target" --emit asm /out/probe.rs -o /out/linux-v149-$target.s > /out/linux-v149-$target.log 2>&1
done

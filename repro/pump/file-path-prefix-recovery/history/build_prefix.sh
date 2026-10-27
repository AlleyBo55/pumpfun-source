#!/usr/bin/env bash
# Reproduce the Pump build with workspace-root-relative file!() paths
# ("programs/pump/src/...") instead of the standalone crate's bare "src/...".
#
# The standalone programs/pump/Cargo.toml declares its own [workspace], so cargo
# roots the crate at itself and file!() emits "src/lib.rs" (10 chars). The
# original pump.fun program was built as a monorepo member, so its Anchor error
# macros captured "programs/pump/src/lib.rs" (24 chars). This script builds pump
# as a member of a parent workspace, preserving pump's own Cargo.lock, so the
# emitted paths (and the &str lengths baked into every error site) match.
#
# Usage: build_prefix.sh <repo-root> <out-dir>
set -euo pipefail
REPO="${1:?repo root}"; OUT="${2:?out dir}"
: "${RUSTUP_TOOLCHAIN:=1.87-x86_64-unknown-linux-gnu}"; export RUSTUP_TOOLCHAIN
WS="$(mktemp -d)"; mkdir -p "$WS/programs"
cp -r "$REPO/programs/pump" "$WS/programs/pump"
# strip the standalone [workspace] table (normalize CRLF first)
sed -i 's/\r$//' "$WS/programs/pump/Cargo.toml"
sed -i '/^\[workspace\]$/d' "$WS/programs/pump/Cargo.toml"
cat > "$WS/Cargo.toml" <<EOF
[workspace]
members = ["programs/pump"]
resolver = "2"
[profile.release]
panic = "abort"
overflow-checks = true
lto = false
codegen-units = 1
EOF
cp "$REPO/programs/pump/Cargo.lock" "$WS/Cargo.lock"   # pump's own locked deps
mkdir -p "$OUT/artifacts"
( cd "$WS" && cargo-build-sbf \
    --manifest-path "$WS/programs/pump/Cargo.toml" \
    --tools-version v1.44 \
    --sbf-out-dir "$OUT/artifacts" -- --locked )
echo "stripped: $(sha256sum "$OUT/artifacts/pump_recovered.so")"

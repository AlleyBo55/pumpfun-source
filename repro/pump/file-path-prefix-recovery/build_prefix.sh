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
REPO="${1:?repo root}"; OUT="${2:?fresh out dir}"
REPO="$(cd "$REPO" && pwd -P)"
# Anchor OUT before entering the throwaway workspace; never overwrite evidence.
OUT_PARENT="$(dirname -- "$OUT")"; OUT_NAME="$(basename -- "$OUT")"
OUT_PARENT="$(cd "$OUT_PARENT" && pwd -P)"
OUT="$OUT_PARENT/$OUT_NAME"
if [[ -e "$OUT" || -L "$OUT" ]]; then
    echo "Output already exists; preserve it and choose a fresh path: $OUT" >&2
    exit 2
fi
# Resolve an explicit target relative to the caller, before changing workspace.
# Both output and target must be fresh; no prior build cache is adopted.
if [[ -n "${CARGO_TARGET_DIR:-}" ]]; then
    TARGET_PARENT="$(dirname -- "$CARGO_TARGET_DIR")"
    TARGET_NAME="$(basename -- "$CARGO_TARGET_DIR")"
    TARGET_PARENT="$(cd "$TARGET_PARENT" && pwd -P)"
    CARGO_TARGET_DIR="$TARGET_PARENT/$TARGET_NAME"
    if [[ -e "$CARGO_TARGET_DIR" || -L "$CARGO_TARGET_DIR" ]]; then
        echo "Target already exists; preserve it and choose a fresh path: $CARGO_TARGET_DIR" >&2
        exit 2
    fi
    if [[ "$CARGO_TARGET_DIR" == "$OUT" ]]; then
        echo "Target must be distinct from the fresh output: $CARGO_TARGET_DIR" >&2
        exit 2
    fi
else
    CARGO_TARGET_DIR="$OUT/target"
fi
export CARGO_TARGET_DIR
mkdir -- "$OUT"
# Exclusive directory creation also rejects a target created after admission.
mkdir -- "$CARGO_TARGET_DIR"
# Keep the unstripped (symbol) build under this fresh target directory;
# the throwaway workspace is removed on exit.
: "${RUSTUP_TOOLCHAIN:=1.87-x86_64-unknown-linux-gnu}"; export RUSTUP_TOOLCHAIN
WS="$(mktemp -d)"; trap 'rm -rf "$WS"' EXIT; mkdir -p "$WS/programs"
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
mkdir "$OUT/artifacts"
( cd "$WS" && cargo-build-sbf \
    --manifest-path "$WS/programs/pump/Cargo.toml" \
    --tools-version v1.44 \
    --sbf-out-dir "$OUT/artifacts" -- --locked )
echo "stripped:   $(sha256sum "$OUT/artifacts/pump_recovered.so")"
echo "unstripped: $(sha256sum "$CARGO_TARGET_DIR/sbf-solana-solana/release/pump_recovered.so")"

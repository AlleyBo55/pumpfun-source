#!/usr/bin/env bash
# Read local binary inputs and write regenerated reports to a separate directory.
set -euo pipefail
cd "$(dirname "$0")"
OUTPUT_DIR="${1:-$PWD/reproduced}"
# Require an existing parent and atomically reject any existing output directory.
mkdir -- "$OUTPUT_DIR"

echo "== ATA preset-window hash cross-check =="
python3 verify_ata_order.py --output "$OUTPUT_DIR/ata_order_report.json"

echo
echo "== ATA byte-distance (307 residual, re-derived) =="
# Read-only: byte_distance.py asserts the recorded ATA result and writes no file.
# It exits 3 only when the candidate pair is not materialized (for example in a
# sparse checkout); that case is reported and skipped. Any other non-zero exit is
# a measured drift and fails this runner. The runner never changes checkout state.
set +e
python3 byte_distance.py
BYTE_DISTANCE_STATUS=$?
set -e
if [ "$BYTE_DISTANCE_STATUS" -eq 3 ]; then
  echo "(byte_distance skipped: candidate pair not present; in a sparse checkout run"
  echo " 'git sparse-checkout add repro/ata/monomorph-order-proof' and rerun)"
elif [ "$BYTE_DISTANCE_STATUS" -ne 0 ]; then
  exit "$BYTE_DISTANCE_STATUS"
fi

echo
echo "== Local binary inventory (linear/heuristic) =="
python3 inventory.py --output "$OUTPUT_DIR/inventory.json"

cat <<'NOTE'

Optional Ghidra listing export; the historical Ghidra comparison is author-
reported and unreverified here because its raw/version/comparison receipts are
absent. This command is an example, not a retained successful oracle run.
Ghidra/JDK are bring-your-own and are not installed here. Use fresh project and
output paths; Ghidra writes a project and the script writes a listing:

  export JAVA_HOME=/absolute/path/to/jdk-21
  export GHIDRA_HEADLESS_MAXMEM=8G
  export REA_DUMP_OUT=/fresh/output/ghidra_text_dump.tsv
  "$GHIDRA_INSTALL_DIR/support/analyzeHeadless" /fresh/project ata \
    -import /path/to/evidence/dependencies/associated_token/deployed.so \
    -processor "eBPF:LE:64:default" \
    -loader ElfLoader -loader-applyRelocations false \
    -scriptPath "$PWD/ghidra_scripts" -postScript DumpText.java -deleteProject
NOTE

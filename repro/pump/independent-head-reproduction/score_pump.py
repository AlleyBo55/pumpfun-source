#!/usr/bin/env python3
"""Score a Pump build with the repository's own window scorer (catalog.py).

Read-only wrapper: runs repro/function-inventory/2026-10-24-374fcf0/work/
pump-amm-current-body-inventory/catalog.py unmodified, with its pump candidate
pointed at the given build instead of the frozen 374fcf0 candidate. Writes
pump-bodies.json and body-summary.json to <out-dir>; never writes to an ELF.

Usage: score_pump.py <stripped pump_recovered.so> <unstripped pump_recovered.so> <out-dir>
(stripped = the --sbf-out-dir artifact; unstripped = target/sbf-solana-solana/
release/pump_recovered.so from the same build).
"""
import hashlib, json, sys
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
SCORER = ROOT / 'repro/function-inventory/2026-10-24-374fcf0/work/pump-amm-current-body-inventory'
sys.path.insert(0, str(SCORER))
import catalog, elf_reader  # noqa: E402

if len(sys.argv) != 4:
    sys.exit(__doc__)
candidate, symbols, out = (Path(a).resolve() for a in sys.argv[1:])
out.mkdir(parents=True, exist_ok=True)
# Builds usually live outside the repository; report their absolute paths
# instead of failing on the repo-relative identity() path.
_identity = elf_reader.Elf.identity
def identity(self):
    try:
        return _identity(self)
    except ValueError:
        return {'path': self.path.name, 'sha256': hashlib.sha256(self.b).hexdigest(),
                'text_sha256': hashlib.sha256(self.b[self.lo:self.hi]).hexdigest()}
elf_reader.Elf.identity = identity
catalog.ROOT = ROOT  # canonical evidence/original/pump/deployed.so
catalog.HERE = out
settings = {'candidate': str(candidate), 'symbols': str(symbols),
            'candidate_sha256': hashlib.sha256(candidate.read_bytes()).hexdigest()}
report = catalog.catalog('pump', settings)
(out / 'body-summary.json').write_text(json.dumps({'pump': report['summary']}, indent=2) + '\n')
print(json.dumps({'pump': report['summary']}, indent=2))

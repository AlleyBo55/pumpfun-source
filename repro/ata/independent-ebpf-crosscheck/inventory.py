"""Function/instruction inventory for the local Solana binaries.

Uses our own sBPF reader/disassembler (no external engine required) to report,
per binary: ELF machine, section layout, a linear instruction count over .text,
and a heuristic function count from local call targets plus the entrypoint.

Heuristic, by design: without symbols, function starts are approximated by the
set of pc-relative `call` targets that land inside .text, plus the ELF entry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sbpf  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
TARGETS = [
    ("pump", "evidence/original/pump/deployed.so"),
    ("pump_amm", "evidence/original/pump_amm/deployed.so"),
    ("pump_fees", "evidence/original/pump_fees/deployed.so"),
    ("mayhem", "evidence/original/mayhem/deployed.so"),
    ("spl_token", "evidence/dependencies/spl_token/deployed.so"),
    ("spl_token_2022", "evidence/dependencies/spl_token_2022/deployed.so"),
    ("associated_token", "evidence/dependencies/associated_token/deployed.so"),
    ("token_metadata", "evidence/dependencies/token_metadata/deployed.so"),
    ("donation_relay", "evidence/dependencies/donation_relay/deployed.so"),
]


def inventory(path: Path) -> dict:
    data = path.read_bytes()
    elf = sbpf.parse_elf(data)
    text = elf.section(".text")
    tbuf = data[text.offset:text.offset + text.size] if text else b""
    insns = sbpf.decode(tbuf, base_pc=text.addr if text else 0)
    # Heuristic function starts: local call targets inside .text + entry.
    lo = text.addr
    hi = text.addr + text.size
    starts = set()
    if lo <= elf.e_entry < hi:
        starts.add(elf.e_entry)
    calls_local = 0
    calls_syscall = 0
    for x in insns:
        if x.is_call and x.text.startswith("call local"):
            calls_local += 1
            tgt = x.pc + 8 + x.imm * 8
            if lo <= tgt < hi:
                starts.add(tgt)
        elif x.is_call:
            calls_syscall += 1
    return {
        "name": path.parent.name,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "e_machine": elf.e_machine,
        "machine_name": {247: "EM_BPF", 263: "EM_SBF(Solana)"}.get(
            elf.e_machine, str(elf.e_machine)),
        "text_bytes": text.size if text else 0,
        "linear_instructions": len(insns),
        "local_calls": calls_local,
        "syscall_or_extern_calls": calls_syscall,
        "heuristic_functions": len(starts),
        "sections": [{"name": s.name, "size": s.size} for s in elf.sections
                     if s.name],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="Path for the regenerated inventory; saved receipts are not overwritten by the runner")
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error("output already exists or is a symlink; choose a fresh report path")
    if not args.output.parent.is_dir():
        parser.error("output parent must already exist")
    results = []
    print(f"{'binary':18} {'mach':14} {'file':>9} {'.text':>8} "
          f"{'insns':>7} {'fns~':>6} {'loc.calls':>9} {'sys.calls':>9}")
    for name, rel in TARGETS:
        p = REPO / rel
        if not p.exists():
            print(f"{name:18} MISSING {rel}")
            continue
        inv = inventory(p)
        inv["id"] = name
        results.append(inv)
        print(f"{name:18} {inv['machine_name']:14} {inv['bytes']:>9} "
              f"{inv['text_bytes']:>8} {inv['linear_instructions']:>7} "
              f"{inv['heuristic_functions']:>6} {inv['local_calls']:>9} "
              f"{inv['syscall_or_extern_calls']:>9}")
    out = args.output
    with out.open("x") as output_file:
        output_file.write(json.dumps(results, indent=2))
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

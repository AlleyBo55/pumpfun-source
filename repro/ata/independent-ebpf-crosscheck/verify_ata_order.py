"""Independent cross-check of the ATA `reserve_for_push` ordering finding.

Prior repository evidence attributes an ATA residual to two reserve_for_push
windows. This tool checks the two preset witness windows only. It does not
independently compare the closest candidate, establish historical Cargo-unit
metadata causality, or prove byte identity impossible.

This script checks the retained window hashes using:
  - the local deployed binary evidence/dependencies/associated_token/deployed.so
  - our own ELF reader + sBPF disassembler (sbpf.py)
  - the recorded window hashes (vendored below from
    repro/ata/monomorph-order-proof/capture-witnesses.json), used as the
    comparison target, not as trusted decoding.

It does not modify any binary and makes no claim of achieving byte identity.
Exits non-zero if any window hash or the deployed order fails to match.
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
ATA = REPO / "evidence/dependencies/associated_token/deployed.so"

# Ground-truth original windows, vendored verbatim from
# repro/ata/monomorph-order-proof/capture-witnesses.json.
WITNESS = {
    "AccountMeta": {
        "start": 28592, "end": 29032,
        "raw_sha256":
            "8e46c99eac4736d2fcff3fc0f8133cd49a19b8a7d67a36b26e1804f21fcba7c9",
        "mask_sha256":
            "dc100a37f063db208892947d02dbe73fc545b4392ddb6cab44ca59a83ea28f1c",
    },
    "u8": {
        "start": 29032, "end": 29384,
        "raw_sha256":
            "37b37fdcf5a13862220b07be1c9fb9d9c90870cfe198748cc96f2aa1052a0a9b",
        "mask_sha256":
            "170c4b5dbc41e9c54d8f428df708fad66b7eeea30a38b421ea6d3dee415a884f",
    },
}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def analyze_window(text_buf: bytes, text_off: int, start: int,
                   end: int) -> dict:
    body = text_buf[start - text_off:end - text_off]
    insns = sbpf.decode(body, base_pc=start)
    masked = sbpf.mask_call_immediates(body)
    calls = [x for x in insns if x.is_call]
    width_hits: dict[int, int] = {}
    for x in insns:
        mn = x.text.split()[0]
        if mn in ("mul", "mul32", "mov", "mov32", "lddw") \
                and isinstance(x.imm, int):
            width_hits[x.imm] = width_hits.get(x.imm, 0) + 1
    return {
        "file_offset_start": start, "file_offset_end": end,
        "bytes": end - start, "instructions": len(insns), "calls": len(calls),
        "raw_sha256": sha(body), "mask_sha256": sha(masked),
        "small_immediates_in_mul_mov_lddw":
            {k: v for k, v in sorted(width_hits.items()) if 0 < k <= 64},
        "disasm": [f"0x{x.pc:05x}: {x.text}" for x in insns],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="Path for a regenerated report; preserve the saved author receipt")
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error("output already exists or is a symlink; choose a fresh report path")
    if not args.output.parent.is_dir():
        parser.error("output parent must already exist")
    data = ATA.read_bytes()
    elf = sbpf.parse_elf(data)
    assert elf.e_machine in (247, 263), f"unexpected machine {elf.e_machine}"
    text = elf.section(".text")
    tbuf = data[text.offset:text.offset + text.size]
    print(f"ATA deployed.so: {len(data)} bytes, sha256 {sha(data)[:16]}, "
          f"e_machine={elf.e_machine}, .text @ 0x{text.offset:x} "
          f"size 0x{text.size:x}")

    report = {"binary": str(ATA.relative_to(REPO)), "binary_sha256": sha(data),
              "e_machine": elf.e_machine, "windows": {}, "checks": {}}
    all_ok = True
    for name in ("AccountMeta", "u8"):
        w = WITNESS[name]
        res = analyze_window(tbuf, text.offset, w["start"], w["end"])
        raw_ok = res["raw_sha256"] == w["raw_sha256"]
        mask_ok = res["mask_sha256"] == w["mask_sha256"]
        res["raw_sha256_matches_witness"] = raw_ok
        res["mask_sha256_matches_witness"] = mask_ok
        all_ok = all_ok and raw_ok and mask_ok
        report["windows"][name] = res
        print(f"\n[{name}] {w['start']}..{w['end']} ({w['end'] - w['start']} B)"
              f", {res['instructions']} insns, {res['calls']} calls")
        print(f"   raw  sha256 {res['raw_sha256'][:16]} match={raw_ok}")
        print(f"   mask sha256 {res['mask_sha256'][:16]} match={mask_ok}")
        print(f"   small immediates in mul/mov/lddw: "
              f"{res['small_immediates_in_mul_mov_lddw']}")

    am = report["windows"]["AccountMeta"]
    u8 = report["windows"]["u8"]
    order_ok = am["file_offset_start"] < u8["file_offset_start"]
    has34 = 34 in am["small_immediates_in_mul_mov_lddw"]
    no34 = 34 not in u8["small_immediates_in_mul_mov_lddw"]
    report["checks"] = {
        "all_window_hashes_match_witness": all_ok,
        "deployed_order_accountmeta_then_u8": order_ok,
        "accountmeta_body_uses_element_width_34": has34,
        "u8_body_does_not_use_width_34": no34,
    }
    report["conclusion"] = (
        "Preset-window hash cross-check: two retained "
        "reserve_for_push-attributed windows occupy file offsets "
        f"{am['file_offset_start']} (AccountMeta-attributed) and "
        f"{u8['file_offset_start']} (u8-attributed), in that offset order. "
        "Raw/masked hash-match flags are recorded above. These checks do not independently "
        "prove historical -C metadata causality, uniquely identify types, "
        "compare the closest candidate, or establish whole-file identity or "
        "its impossibility."
    )

    out = args.output
    with out.open("x") as output_file:
        output_file.write(json.dumps(report, indent=2))
    passed = all(report["checks"].values())
    print(f"\nchecks: {report['checks']}")
    print(f"PASS={passed}  report -> {out}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

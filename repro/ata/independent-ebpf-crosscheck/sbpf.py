"""Minimal, dependency-free sBPF / eBPF ELF reader and disassembler.

Written from scratch to analyze Solana programs (ELF e_machine 247 EM_BPF and
263 "EM_SBF"), which mainstream RE front-ends on this host refuse to open.

Instruction semantics follow the eBPF instruction set as encoded in Ghidra's
`eBPF.sinc` and the Linux kernel docs; Solana-specific call handling (pc-relative
`call` with src=1, syscall `call` with src=0) is modelled explicitly.

Scope: this is an honest linear-sweep disassembler for evidence and
cross-checking, not a full CFG recovery engine. Every decoded field is derived
directly from the instruction bytes.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field


# --- ELF (little-endian, 64-bit) -------------------------------------------

@dataclass
class Section:
    name: str
    sh_type: int
    addr: int
    offset: int
    size: int
    entsize: int
    link: int


@dataclass
class Elf:
    data: bytes
    e_machine: int
    e_entry: int
    sections: list[Section]

    def section(self, name: str) -> Section | None:
        for s in self.sections:
            if s.name == name:
                return s
        return None

    def section_bytes(self, name: str) -> bytes:
        s = self.section(name)
        if s is None or s.sh_type == 8:  # SHT_NOBITS
            return b""
        return self.data[s.offset:s.offset + s.size]


def parse_elf(data: bytes) -> Elf:
    if data[:4] != b"\x7fELF":
        raise ValueError("not an ELF")
    if data[4] != 2:
        raise ValueError("only ELF64 supported")
    (e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags,
     e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum,
     e_shstrndx) = struct.unpack_from("<HHIQQQIHHHHHH", data, 16)
    raw = []
    for i in range(e_shnum):
        (sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size, sh_link,
         sh_info, sh_addralign, sh_entsize) = struct.unpack_from(
            "<IIQQQQIIQQ", data, e_shoff + i * e_shentsize)
        raw.append((sh_name, sh_type, sh_addr, sh_offset, sh_size, sh_entsize,
                    sh_link))
    stroff = raw[e_shstrndx][3]

    def name_at(off: int) -> str:
        end = data.index(b"\x00", stroff + off)
        return data[stroff + off:end].decode("utf-8", "replace")

    sections = [Section(name_at(r[0]), r[1], r[2], r[3], r[4], r[5], r[6])
                for r in raw]
    return Elf(data, e_machine, e_entry, sections)


# --- sBPF instruction decoding ---------------------------------------------

ALU = {0x0: "add", 0x1: "sub", 0x2: "mul", 0x3: "div", 0x4: "or", 0x5: "and",
       0x6: "lsh", 0x7: "rsh", 0x8: "neg", 0x9: "mod", 0xa: "xor",
       0xb: "mov", 0xc: "arsh", 0xd: "end"}
JMP = {0x0: "ja", 0x1: "jeq", 0x2: "jgt", 0x3: "jge", 0x4: "jset", 0x5: "jne",
       0x6: "jsgt", 0x7: "jsge", 0x8: "call", 0x9: "exit", 0xa: "jlt",
       0xb: "jle", 0xc: "jslt", 0xd: "jsle"}
SIZES = {0x00: "w", 0x08: "h", 0x10: "b", 0x18: "dw"}


@dataclass
class Insn:
    pc: int            # byte offset within the decoded buffer
    size: int          # 8 or 16
    raw: bytes
    opcode: int
    dst: int
    src: int
    off: int           # signed 16
    imm: int           # signed 32 (or 64 for lddw)
    text: str
    is_call: bool = False


def _s16(v: int) -> int:
    return v - 0x10000 if v & 0x8000 else v


def _s32(v: int) -> int:
    return v - 0x100000000 if v & 0x80000000 else v


def decode(buf: bytes, base_pc: int = 0) -> list[Insn]:
    """Linear-sweep decode of a byte buffer into sBPF instructions."""
    out: list[Insn] = []
    i = 0
    n = len(buf)
    while i + 8 <= n:
        op, regs, off_u, imm_u = struct.unpack_from("<BBHI", buf, i)
        dst, src = regs & 0x0f, (regs >> 4) & 0x0f
        off, imm = _s16(off_u), _s32(imm_u)
        cls = op & 0x07
        size = 8
        text = ""
        is_call = False

        if op == 0x18:  # lddw: 64-bit immediate load, 16 bytes
            if i + 16 <= n:
                imm2 = struct.unpack_from("<I", buf, i + 12)[0]
                imm64 = (imm_u | (imm2 << 32))
                size = 16
                text = f"lddw r{dst}, 0x{imm64:x}"
                imm = imm64
            else:
                text = f"(truncated lddw) 0x{op:02x}"
        elif cls in (0x04, 0x07):  # ALU / ALU64
            suffix = "32" if cls == 0x04 else ""
            name = ALU.get(op >> 4, f"alu?{op >> 4:x}")
            use_src = bool(op & 0x08)
            if name == "neg":
                text = f"neg{suffix} r{dst}"
            elif name == "end":
                # byteswap: src bit picks le/be, imm picks width
                order = "be" if use_src else "le"
                text = f"{order}{imm} r{dst}"
            elif use_src:
                text = f"{name}{suffix} r{dst}, r{src}"
            else:
                text = f"{name}{suffix} r{dst}, {imm}"
        elif cls in (0x05, 0x06):  # JMP / JMP32
            suffix = "32" if cls == 0x06 else ""
            name = JMP.get(op >> 4, f"j?{op >> 4:x}")
            use_src = bool(op & 0x08)
            if name == "exit":
                text = "exit"
            elif name == "ja":
                tgt = base_pc + i + 8 + off * 8
                text = f"ja {off:+d}   # -> 0x{tgt:x}"
            elif name == "call":
                is_call = True
                if src == 1:
                    tgt = base_pc + i + 8 + imm * 8  # pc-relative, insn units
                    text = f"call local {imm:+d}   # -> 0x{tgt:x}"
                else:
                    if imm == -1:
                        text = "call <relocated>   # imm=-1"
                    else:
                        text = f"call 0x{imm_u:08x}   # syscall/extern hash"
            else:
                rhs = f"r{src}" if use_src else f"{imm}"
                tgt = base_pc + i + 8 + off * 8
                text = f"{name}{suffix} r{dst}, {rhs}, {off:+d}   # -> 0x{tgt:x}"
        elif cls == 0x01:  # LDX  dst = *(size*)(src+off)
            sz = SIZES.get(op & 0x18, "?")
            text = f"ldx{sz} r{dst}, [r{src}{off:+d}]"
        elif cls == 0x02:  # ST   *(size*)(dst+off) = imm
            sz = SIZES.get(op & 0x18, "?")
            text = f"st{sz} [r{dst}{off:+d}], {imm}"
        elif cls == 0x03:  # STX  *(size*)(dst+off) = src
            sz = SIZES.get(op & 0x18, "?")
            text = f"stx{sz} [r{dst}{off:+d}], r{src}"
        elif cls == 0x00:  # LD (abs/ind/imm) — rare in Solana bodies
            sz = SIZES.get(op & 0x18, "?")
            text = f"ld{sz} (mode 0x{op & 0xe0:02x}) r{dst}, {imm}"
        else:
            text = f"(unknown 0x{op:02x})"

        out.append(Insn(base_pc + i, size, buf[i:i + size], op, dst, src,
                        off, imm, text, is_call))
        i += size
    return out


def mask_call_immediates(buf: bytes) -> bytes:
    """Zero the 4-byte immediate of every 8-byte CALL (opcode 0x85).

    This normalizes away link-time-dependent call targets, matching the
    `call_immediate_mask` the pumpfun-source evidence uses to compare
    function bodies independently of where the linker placed callees.
    """
    b = bytearray(buf)
    i = 0
    n = len(b)
    while i + 8 <= n:
        op = b[i]
        if op == 0x18 and i + 16 <= n:  # lddw occupies 16 bytes; skip both
            i += 16
            continue
        if op == 0x85:  # JMP|CALL|K
            b[i + 4:i + 8] = b"\x00\x00\x00\x00"
        i += 8
    return bytes(b)

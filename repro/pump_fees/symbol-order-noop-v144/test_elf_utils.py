#!/usr/bin/env python3
"""Focused tests for the strict Pump Fees ELF64 header parser."""

from __future__ import annotations

import struct
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from elf_utils import Elf64, GateError


def minimal_elf64(*, section_stride: int = 64) -> bytes:
    """Create a bounded EM_SBF ELF with distinct program/section entry sizes."""
    names = b"\0.shstrtab\0"
    section_offset = 64
    names_offset = section_offset + 2 * 64
    data = bytearray(names_offset + len(names))
    data[:4] = b"\x7fELF"
    data[4:7] = bytes((2, 1, 1))  # ELF64, little endian, current version
    struct.pack_into("<HHI", data, 16, 3, 263, 1)  # ET_DYN, EM_SBF
    struct.pack_into("<Q", data, 40, section_offset)
    # e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx
    struct.pack_into("<HHHHHH", data, 52, 64, 56, 2, section_stride, 2, 1)
    struct.pack_into(
        "<IIQQQQIIQQ",
        data,
        section_offset + 64,
        1,  # name offset
        3,  # SHT_STRTAB
        0,
        0,
        names_offset,
        len(names),
        0,
        0,
        1,
        0,
    )
    data[names_offset:] = names
    return bytes(data)


class ElfHeaderTests(unittest.TestCase):
    def test_reads_section_fields_after_program_header_fields(self) -> None:
        elf = Elf64(minimal_elf64(), "synthetic")
        self.assertEqual(elf.header["machine"], 263)
        self.assertEqual(elf.header["section_count"], 2)
        self.assertEqual(elf.section(".shstrtab")["size"], len(b"\0.shstrtab\0"))

    def test_rejects_non_elf64_section_stride(self) -> None:
        with self.assertRaisesRegex(GateError, "unexpected section entry size"):
            Elf64(minimal_elf64(section_stride=56), "synthetic")


if __name__ == "__main__":
    unittest.main()

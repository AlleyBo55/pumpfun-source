#!/usr/bin/env python3
"""Strict, candidate-only ELF64 helpers for the Pump Fees no-op gate."""

from __future__ import annotations

import hashlib
from pathlib import Path
import struct
from typing import Any, Optional

ELF_MAGIC = b"\x7fELF"
ELFCLASS64 = 2
ELFDATA2LSB = 1
ET_DYN = 3
EM_SBF = 263
SHT_SYMTAB = 2
SHT_STRTAB = 3
SHT_RELA = 4
SHT_NOBITS = 8
SHT_REL = 9
SHT_DYNSYM = 11
SHN_UNDEF = 0
STT_FUNC = 2
SHF_ALLOC = 2


class GateError(ValueError):
    """A fail-closed applicability or evidence error."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise GateError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def regular_file(path: Path, root: Optional[Path] = None) -> Path:
    """Require a non-symlink regular file, optionally below a non-symlink root."""
    path = path.resolve(strict=True)
    require(path.is_file() and not path.is_symlink(), f"Not a regular file: {path}")
    if root is not None:
        root = root.resolve(strict=True)
        require(path == root or root in path.parents, f"File escapes evidence root: {path}")
        current = path.parent
        while current != root:
            require(not current.is_symlink(), f"Symlinked evidence parent: {current}")
            current = current.parent
    return path


class Elf64:
    """Bounds-checked little-endian EM_SBF shared ELF reader."""

    def __init__(self, data: bytes, label: str = "ELF") -> None:
        self.data = data
        self.label = label
        require(len(data) >= 64, f"{label}: truncated ELF header")
        require(data[:4] == ELF_MAGIC, f"{label}: missing ELF magic")
        require(data[4] == ELFCLASS64, f"{label}: expected ELF64")
        require(data[5] == ELFDATA2LSB, f"{label}: expected little-endian ELF")
        require(data[6] == 1, f"{label}: unsupported ELF ident version")

        elf_type, machine, version = struct.unpack_from("<HHI", data, 16)
        require(elf_type == ET_DYN, f"{label}: expected ET_DYN, got {elf_type}")
        require(machine == EM_SBF, f"{label}: expected EM_SBF 263, got {machine}")
        require(version == 1, f"{label}: unsupported ELF version {version}")
        self.entry = struct.unpack_from("<Q", data, 24)[0]
        section_offset = struct.unpack_from("<Q", data, 40)[0]
        flags = struct.unpack_from("<I", data, 48)[0]
        (
            header_size,
            program_stride,
            program_count,
            section_stride,
            section_count,
            names_index,
        ) = struct.unpack_from("<HHHHHH", data, 52)
        require(header_size == 64, f"{label}: unexpected ELF header size")
        require(
            (program_count == 0 and program_stride in (0, 56))
            or (program_count > 0 and program_stride == 56),
            f"{label}: unexpected program header layout",
        )
        require(section_stride == 64, f"{label}: unexpected section entry size")
        require(section_count > 0, f"{label}: extended/empty section tables unsupported")
        require(names_index < section_count, f"{label}: invalid section-name table")
        self._region(section_offset, section_count * section_stride)

        sections: list[dict[str, Any]] = []
        keys = (
            "name_offset",
            "type",
            "flags",
            "address",
            "offset",
            "size",
            "link",
            "info",
            "alignment",
            "entry_size",
        )
        for index in range(section_count):
            values = struct.unpack_from(
                "<IIQQQQIIQQ", data, section_offset + index * section_stride
            )
            row = dict(zip(keys, values))
            row["index"] = index
            if row["type"] != SHT_NOBITS:
                self._region(row["offset"], row["size"])
            sections.append(row)

        names_section = sections[names_index]
        require(
            names_section["type"] == SHT_STRTAB,
            f"{label}: section names do not use a string table",
        )
        names = self._region(names_section["offset"], names_section["size"])
        by_name: dict[str, dict[str, Any]] = {}
        for row in sections:
            row["name"] = self._string(names, row["name_offset"])
            if row["name"]:
                require(
                    row["name"] not in by_name,
                    f"{label}: duplicate section name {row['name']}",
                )
                by_name[row["name"]] = row
        self.sections = sections
        self.by_name = by_name
        self.header = {
            "class": ELFCLASS64,
            "data": ELFDATA2LSB,
            "type": elf_type,
            "machine": machine,
            "version": version,
            "entry": self.entry,
            "flags": flags,
            "section_count": section_count,
        }

    @classmethod
    def from_path(cls, path: Path, label: Optional[str] = None) -> "Elf64":
        return cls(path.read_bytes(), label or str(path))

    def _region(self, offset: int, size: int) -> bytes:
        require(
            0 <= offset <= len(self.data) and 0 <= size <= len(self.data) - offset,
            f"{self.label}: ELF range is outside the file",
        )
        return self.data[offset : offset + size]

    def _string(self, table: bytes, offset: int) -> str:
        require(0 <= offset < len(table), f"{self.label}: invalid string offset")
        end = table.find(b"\0", offset)
        require(end >= 0, f"{self.label}: unterminated ELF string")
        try:
            return table[offset:end].decode("utf-8")
        except UnicodeDecodeError as error:
            raise GateError(f"{self.label}: non-UTF-8 ELF string") from error

    def section(self, name: str) -> dict[str, Any]:
        require(name in self.by_name, f"{self.label}: missing {name} section")
        return self.by_name[name]

    def section_bytes(self, name: str) -> bytes:
        row = self.section(name)
        require(row["type"] != SHT_NOBITS, f"{self.label}: {name} has no file bytes")
        return self._region(row["offset"], row["size"])

    def _symbols(self, symbol_section: dict[str, Any]) -> list[dict[str, Any]]:
        require(
            symbol_section["type"] in (SHT_SYMTAB, SHT_DYNSYM),
            f"{self.label}: invalid symbol table type",
        )
        require(
            symbol_section["entry_size"] == 24
            and symbol_section["size"] % 24 == 0,
            f"{self.label}: invalid symbol table entry size",
        )
        require(
            symbol_section["link"] < len(self.sections),
            f"{self.label}: invalid symbol string-table link",
        )
        strings_section = self.sections[symbol_section["link"]]
        require(
            strings_section["type"] == SHT_STRTAB,
            f"{self.label}: symbols do not link to a string table",
        )
        strings = self._region(strings_section["offset"], strings_section["size"])
        rows: list[dict[str, Any]] = []
        start = symbol_section["offset"]
        for index, at in enumerate(range(start, start + symbol_section["size"], 24)):
            name_offset, info, other, section_index, value, size = struct.unpack_from(
                "<IBBHQQ", self.data, at
            )
            rows.append(
                {
                    "symbol_index": index,
                    "name": self._string(strings, name_offset),
                    "binding": info >> 4,
                    "type": info & 15,
                    "other": other,
                    "section_index": section_index,
                    "address": value,
                    "size": size,
                }
            )
        return rows

    def function_symbol_map(self) -> list[dict[str, Any]]:
        """Return every defined STT_FUNC, requiring an unambiguous .text extent."""
        symbol_section = self.section(".symtab")
        require(
            symbol_section["type"] == SHT_SYMTAB,
            f"{self.label}: .symtab has the wrong type",
        )
        text = self.section(".text")
        functions: list[dict[str, Any]] = []
        for symbol in self._symbols(symbol_section):
            if symbol["type"] != STT_FUNC or symbol["section_index"] == SHN_UNDEF:
                continue
            require(
                symbol["section_index"] == text["index"],
                f"{self.label}: defined function is outside .text: {symbol['name']}",
            )
            name = symbol["name"]
            require(name, f"{self.label}: unnamed function symbol")
            require(
                not any(character.isspace() for character in name),
                f"{self.label}: function name contains whitespace: {name!r}",
            )
            address = symbol["address"]
            size = symbol["size"]
            require(size > 0, f"{self.label}: zero-size function symbol: {name}")
            require(
                text["address"] <= address
                and size <= text["address"] + text["size"] - address,
                f"{self.label}: function extent leaves .text: {name}",
            )
            functions.append(
                {
                    "symbol_index": symbol["symbol_index"],
                    "name": name,
                    "address": address,
                    "size": size,
                    "binding": symbol["binding"],
                    "other": symbol["other"],
                    "section": ".text",
                }
            )
        require(functions, f"{self.label}: no defined .text function symbols")
        require(
            len({row["name"] for row in functions}) == len(functions),
            f"{self.label}: duplicate function names cannot form an order file",
        )
        functions.sort(key=lambda row: (row["address"], row["symbol_index"]))
        previous_end = text["address"]
        previous_name = ""
        for row in functions:
            require(
                row["address"] >= previous_end,
                f"{self.label}: overlapping/aliased functions: {previous_name} and {row['name']}",
            )
            previous_end = row["address"] + row["size"]
            previous_name = row["name"]
        return functions

    def symbol_order_bytes(self) -> bytes:
        functions = self.function_symbol_map()
        return ("".join(row["name"] + "\n" for row in functions)).encode("utf-8")

    def text_record(self) -> dict[str, Any]:
        text = self.section(".text")
        body = self.section_bytes(".text")
        return {
            "address": text["address"],
            "size": text["size"],
            "flags": text["flags"],
            "alignment": text["alignment"],
            "sha256": sha256_bytes(body),
        }

    def relocation_map(self) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for section in self.sections:
            if section["type"] not in (SHT_REL, SHT_RELA):
                continue
            expected_size = 16 if section["type"] == SHT_REL else 24
            require(
                section["entry_size"] == expected_size
                and section["size"] % expected_size == 0,
                f"{self.label}: invalid relocation entry size in {section['name']}",
            )
            require(
                section["link"] < len(self.sections),
                f"{self.label}: invalid relocation symbol-table link",
            )
            symbols_section = self.sections[section["link"]]
            symbols = self._symbols(symbols_section)
            target = ""
            if section["info"]:
                require(
                    section["info"] < len(self.sections),
                    f"{self.label}: invalid relocation target link",
                )
                target = self.sections[section["info"]]["name"]
            entries: list[dict[str, Any]] = []
            start = section["offset"]
            for index, at in enumerate(
                range(start, start + section["size"], expected_size)
            ):
                if section["type"] == SHT_REL:
                    offset, info = struct.unpack_from("<QQ", self.data, at)
                    addend = None
                else:
                    offset, info, addend = struct.unpack_from("<QQq", self.data, at)
                symbol_index = info >> 32
                require(
                    symbol_index < len(symbols),
                    f"{self.label}: relocation symbol index is out of range",
                )
                entries.append(
                    {
                        "index": index,
                        "offset": offset,
                        "info": info,
                        "type": info & 0xFFFFFFFF,
                        "symbol_index": symbol_index,
                        "symbol": symbols[symbol_index]["name"],
                        "addend": addend,
                    }
                )
            raw = self._region(section["offset"], section["size"])
            result.append(
                {
                    "section": section["name"],
                    "target": target,
                    "symbol_table": symbols_section["name"],
                    "address": section["address"],
                    "size": section["size"],
                    "entry_size": section["entry_size"],
                    "sha256": sha256_bytes(raw),
                    "entries": entries,
                }
            )
        require(result, f"{self.label}: no relocation sections")
        return result

    def allocated_sections(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for section in self.sections:
            if not section["name"] or not section["flags"] & SHF_ALLOC:
                continue
            body = None
            if section["type"] != SHT_NOBITS:
                body = self._region(section["offset"], section["size"])
            rows.append(
                {
                    "name": section["name"],
                    "type": section["type"],
                    "flags": section["flags"],
                    "address": section["address"],
                    "size": section["size"],
                    "alignment": section["alignment"],
                    "sha256": None if body is None else sha256_bytes(body),
                }
            )
        require(rows, f"{self.label}: no allocated sections")
        rows.sort(key=lambda row: row["name"])
        return rows

    def evidence(self) -> dict[str, Any]:
        return {
            "header": self.header,
            "function_symbol_map": self.function_symbol_map(),
            "text": self.text_record(),
            "relocations": self.relocation_map(),
            "allocated_sections": self.allocated_sections(),
        }


def artifact_record(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    elf = Elf64(data, str(path))
    return {
        "path": str(path),
        "bytes": len(data),
        "sha256": sha256_bytes(data),
        "header": elf.header,
    }

import struct
from types import SimpleNamespace
import unittest

import cross_program as cross
import verify as v


def instruction(op=0x95, registers=0, immediate=0):
    return struct.pack("<BBhi", op, registers, 0, immediate)


def fixture(code, *, address=0x100000, external_call_at=None):
    """Minimal section model with distinct virtual addresses and file offsets."""
    offset = 64
    data = b"\0" * offset + code
    text = dict(name=".text", type=1, offset=offset, addr=address, size=len(code))
    sections = [text]
    if external_call_at is not None:
        sections.append(dict(type=9, offset=len(data), size=16, entsize=16))
        data += struct.pack("<QQ", address + external_call_at, (7 << 32) | 10)
    return SimpleNamespace(kind=3, machine=263, flags=0, data=data, sections=sections,
                           section_named=lambda name: (0, text))


class CallBoundaryTests(unittest.TestCase):
    def test_relative_call_uses_virtual_addresses(self):
        elf = fixture(instruction(0x85, 0x10, 1) + instruction() * 2)
        entry, = cross.direct_call_entries(elf)[80]
        self.assertEqual(entry["virtual_address"], 0x100000)
        self.assertEqual(entry["target_virtual_address"], 0x100010)
        self.assertEqual(entry["file_offset"], 64)

    def test_negative_displacement(self):
        elf = fixture(instruction() + instruction(0x85, 0x10, -2))
        entry, = cross.direct_call_entries(elf)[64]
        self.assertEqual(entry["signed_displacement"], -2)
        self.assertEqual(entry["file_offset"], 72)

    def test_external_relocation_does_not_invent_self_entry(self):
        elf = fixture(instruction(0x85, 0x10, -1), external_call_at=0)
        self.assertEqual(cross.direct_call_entries(elf), {})
        self.assertEqual(cross.dynamic_relocations(elf),
                         [dict(virtual_address=0x100000, type=10, symbol_index=7)])

    def test_lddw_continuation_not_decoded_as_call(self):
        elf = fixture(instruction(0x18) + instruction(0x85, 0x10, 0) + instruction())
        self.assertEqual(cross.direct_call_entries(elf), {})

    def test_indirect_calls_not_direct_boundaries(self):
        elf = fixture(instruction(0x8d, 0x10, 0) + instruction())
        self.assertEqual(cross.direct_call_entries(elf), {})

    def test_outside_text_target_is_not_boundary(self):
        elf = fixture(instruction(0x85, 0x10, 1))
        self.assertEqual(cross.direct_call_entries(elf), {})

    def test_truncated_lddw_rejected(self):
        with self.assertRaisesRegex(ValueError, "truncated LDDW"):
            cross.direct_call_entries(fixture(instruction(0x18)))

    def test_non_generic_abi_rejected(self):
        elf = fixture(instruction())
        elf.flags = 2
        with self.assertRaisesRegex(ValueError, "generic SBF"):
            cross.direct_call_entries(elf)

    def test_raw_search_is_bounded_to_text(self):
        elf = fixture(b"abcdefgh")
        elf.data += b"needle"
        self.assertEqual(cross.raw_occurrences(elf, b"needle"), [])
        self.assertEqual(cross.raw_occurrences(elf, b"bcde"), [65])


class CrossCaptureTests(unittest.TestCase):
    def test_saved_cross_capture_evidence(self):
        actual = cross.analyze()
        self.assertEqual(actual, v.read_json(v.HERE / "cross-program-analysis.json"))
        for capture in actual["captures"].values():
            results = capture["helper_occurrences"]
            self.assertEqual(results["v1461_fmt_write"], [])
            for name in ("v144_core_fmt_write", "v144_integer_entry"):
                row, = results[name]
                self.assertTrue(row["instruction_aligned"])
                self.assertTrue(row["occupies_complete_direct_call_window"])
                self.assertTrue(row["start_direct_callers"])
                self.assertTrue(row["end_direct_callers"])
                self.assertEqual(row["loader_relocations"], [])
                self.assertEqual(row["end"], row["next_direct_call_target"])


if __name__ == "__main__":
    unittest.main()

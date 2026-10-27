"""In-memory negative controls for the restricted value-flow diagnostic."""

import hashlib
import struct
import unittest
from verify import load


class ValueFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (
            cls.parser,
            cls.model,
            cls.original,
            cls.candidate,
            cls.om,
            cls.cm,
            cls.subjects,
        ) = load()
        cls.row, _ = cls.subjects[94]
        cls.start, cls.size = cls.row["start"], cls.row["bytes"]
        cls.before_hash = hashlib.sha256(cls.original.b).hexdigest()

    def trace(self, elf=None, mode="success"):
        return self.model.trace(
            elf or self.original, self.start, self.size, self.om, mode
        )

    def patch(self, relative, raw):
        section = self.original.by_name[".text"]
        offset = section["offset"] + self.start - section["address"] + relative
        mutated = bytearray(self.original.b)
        mutated[offset : offset + len(raw)] = raw
        result = self.parser.Elf(bytes(mutated))
        self.assertEqual(hashlib.sha256(self.original.b).hexdigest(), self.before_hash)
        return result

    def instructions(self):
        cursor = 0
        while cursor < self.size:
            instruction = struct.unpack(
                "<BBhi", self.original.at(self.start + cursor, 8)
            )
            yield cursor, instruction
            cursor += 16 if instruction[0] == 0x18 else 8

    def test_actual_return_boundaries(self):
        for ordinal, (original, candidate) in self.subjects.items():
            for mode in ("success", "error"):
                left = self.model.trace(
                    self.original, original["start"], original["bytes"], self.om, mode
                )
                right = self.model.trace(
                    self.candidate, candidate["start"], candidate["size"], self.cm, mode
                )
                self.assertEqual(left["boundary"], right["boundary"], (ordinal, mode))
                self.assertEqual(left["output"], right["output"], (ordinal, mode))

    def test_wrong_bump_is_detected_at_argument_boundary(self):
        self.assertEqual(self.original.at(self.start, 2), bytes([0x7B, 0x5A]))
        changed = self.trace(self.patch(1, bytes([0x4A])))
        self.assertNotEqual(
            self.trace()["boundary"]["arguments"], changed["boundary"]["arguments"]
        )

    def test_wrong_event_discriminator_is_detected(self):
        positions = [
            offset
            for offset, (op, _, field, imm) in self.instructions()
            if op == 0x72 and field == 0x98 and imm == 0
        ]
        self.assertEqual(len(positions), 1)
        changed = self.trace(self.patch(positions[0] + 4, struct.pack("<i", 1)))
        self.assertEqual(self.trace()["boundary"], changed["boundary"])
        self.assertNotEqual(self.trace()["output"][152], changed["output"][152])

    def test_shortened_copy_fails_on_unwritten_return_bytes(self):
        positions = [
            offset
            for offset, (op, regs, _, imm) in self.instructions()
            if op == 0xB7 and regs == 3 and imm == 88
        ]
        self.assertEqual(len(positions), 1)
        with self.assertRaisesRegex(AssertionError, "uninitialized memory"):
            self.trace(self.patch(positions[0] + 4, struct.pack("<i", 80)))

    def test_changed_overflow_guard_is_not_silently_assumed(self):
        positions = [
            offset
            for offset, (op, _, _, imm) in self.instructions()
            if op == 0x07 and imm == 1
        ]
        with self.assertRaisesRegex(AssertionError, "unsupported symbolic branch"):
            self.trace(self.patch(positions[0] + 4, struct.pack("<i", 2)))

    def test_unknown_instruction_is_rejected(self):
        with self.assertRaises(AssertionError):
            self.trace(self.patch(0, bytes([0xFF])))

    def test_clobbered_register_reads_are_rejected(self):
        registers = self.model.Registers({1: None})
        with self.assertRaisesRegex(AssertionError, "undefined register"):
            _ = registers[1]

    def test_pointer_offset_cancellation(self):
        value = self.model.pointer("fixture")
        self.assertEqual(value.bs, value.add(24).add(-24).bs)
        self.assertEqual(value.addr(), value.add(24).add(-24).addr())


if __name__ == "__main__":
    unittest.main()

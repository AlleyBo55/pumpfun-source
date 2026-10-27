import hashlib
import struct
import unittest
from verify import load, calls, compare, key


class CallAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser, cls.original, cls.rows, cls.images = load()
        cls.functions = {row["start"]: row for row in cls.rows}
        cls.groups = {}
        for row in cls.rows:
            cls.groups.setdefault(key(row), []).append(row["ordinal"])
        cls.subject = cls.rows[99]
        cls.baseline = calls(cls.original, cls.subject, cls.functions, cls.groups)
        cls.original_hash = hashlib.sha256(cls.original.b).hexdigest()

    def patch(self, relative, data):
        text = self.original.by_name[".text"]
        offset = text["offset"] + self.subject["start"] - text["address"] + relative
        raw = bytearray(self.original.b)
        raw[offset : offset + len(data)] = data
        image = self.parser.Elf(bytes(raw))
        row = image.function(self.subject["start"], self.subject["bytes"], [])
        self.assertEqual(
            hashlib.sha256(self.original.b).hexdigest(), self.original_hash
        )
        return image, row

    def retarget(self, target):
        call = self.subject["direct_calls"][0]
        displacement = (target - call["pc"] - 8) // 8
        return self.patch(call["offset"] + 4, struct.pack("<i", displacement))

    def test_changed_matched_callee_is_detected(self):
        image, row = self.retarget(self.rows[116]["start"])
        changed = calls(image, row, self.functions, self.groups)
        self.assertFalse(compare(self.baseline, changed)["multiset_equal"])

    def test_non_function_target_is_rejected(self):
        image, row = self.retarget(self.rows[116]["start"] + 8)
        with self.assertRaisesRegex(AssertionError, "not a function start"):
            calls(image, row, self.functions, self.groups)

    def test_noncall_change_is_not_proved_by_call_counts(self):
        body = self.original.at(self.subject["start"], self.subject["bytes"])
        offset = next(i for i in range(0, len(body), 8) if body[i] == 0xBF)
        changed_registers = (body[offset + 1] & 15) | 0x30
        self.assertNotEqual(changed_registers, body[offset + 1])
        image, row = self.patch(offset + 1, bytes([changed_registers]))
        changed = calls(image, row, self.functions, self.groups)
        self.assertTrue(compare(self.baseline, changed)["multiset_equal"])
        self.assertNotEqual(row["normalized_sha256"], self.subject["normalized_sha256"])

    def test_reordering_retains_counts_but_not_sequence(self):
        changed = list(self.baseline)
        changed[0], changed[1] = changed[1], changed[0]
        result = compare(self.baseline, changed)
        self.assertTrue(result["multiset_equal"])
        self.assertFalse(result["same_linear_sequence"])

    def test_repeated_call_count_is_significant(self):
        changed = self.baseline + [self.baseline[0]]
        self.assertFalse(compare(self.baseline, changed)["multiset_equal"])


if __name__ == "__main__":
    unittest.main()

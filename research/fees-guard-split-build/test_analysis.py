import importlib.util
from pathlib import Path
import struct
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('analysis', HERE / 'analysis.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class DecoderTests(unittest.TestCase):
    def test_lddw_second_slot_is_data(self):
        raw = bytes.fromhex('18010000030000000000000000000080')
        rows = a.instructions(raw, 1000)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['lddw_bytes'], a.ERROR)
        self.assertNotIn('branch_target', rows[0])

    def test_signed_call_and_branch_edges(self):
        rows = a.instructions(struct.pack('<BBhiBBhi',0x85,0x10,0,-4,0xa5,2,-3,8),1000)
        self.assertEqual(rows[0]['encoded_call_target'],976)
        self.assertEqual(rows[1]['branch_target'],992)

    def test_external_call_is_not_relative(self):
        row, = a.instructions(struct.pack('<BBhi',0x85,0,0,123),1000)
        self.assertNotIn('encoded_call_target',row)
        self.assertNotIn('branch_target',row)

    def test_truncated_lddw_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'Truncated LDDW'):
            a.instructions(bytes.fromhex('1801000003000000'),0)

    def test_unaligned_body_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'complete slots'):
            a.instructions(bytes(9),0)

    def test_padding_remains_a_raw_difference(self):
        self.assertEqual(a.raw_difference(b'ELF',b'ELF\0'), dict(raw_equal=False,common_length=3,
            differing_positions_in_common_prefix=0,unmatched_tail_bytes=1))

    def test_bad_elf_class_rejected(self):
        with self.assertRaisesRegex(ValueError,'little-endian ELF64'):
            a.Elf(b'\x7fELF\x01\x01'+bytes(100))


if __name__ == '__main__':
    unittest.main()

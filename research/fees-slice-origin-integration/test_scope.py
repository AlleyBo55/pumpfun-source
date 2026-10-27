"""Adversarial checks for data and encoded targets hidden by body normalization."""
import gzip
import importlib.util
import json
from pathlib import Path
import struct
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('slice_origin_analysis', HERE / 'analyze.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ContractScope(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        e = json.loads((HERE / 'experiment.json').read_text())
        cls.image = gzip.decompress((HERE / e['variants']['origins']['files']['symbols']['path']).read_bytes())
        original = (m.ROOT / 'evidence/original/pump_fees/deployed.so').read_bytes()
        cls.windows = m.wm.windows(cls.image)
        pairs = m.wm.compare(m.wm.windows(original), cls.windows)['unique_pairs']
        cls.pairs = {r['original']['address']: r['candidate']['address'] for r in pairs}
        cls.details = m.contract(cls.image, cls.windows, cls.pairs)

    def test_source_column_is_not_covered_by_equal_text(self):
        changed = bytearray(self.image)
        address = self.details['locations'][0]['record_address'] + 20
        changed[m.file_offset(changed, address)] -= 1
        self.assertEqual(m.wm.m.section_data(changed, '.text'), m.wm.m.section_data(self.image, '.text'))
        with self.assertRaises(AssertionError):
            m.contract(changed, self.windows, self.pairs)

    def test_message_byte_is_not_covered_by_equal_text(self):
        changed = bytearray(self.image)
        rows = {r['offset']: r for r in m.wm.m.instructions(changed, self.pairs[784168], 200)}
        packed, _ = struct.unpack('<QQ', m.wm.m.at_address(changed, rows[16]['lddw_value'], 16))
        changed[m.file_offset(changed, packed >> 32)] ^= 0x20
        self.assertEqual(m.wm.m.section_data(changed, '.text'), m.wm.m.section_data(self.image, '.text'))
        with self.assertRaises(AssertionError):
            m.contract(changed, self.windows, self.pairs)

    def test_masked_call_target_requires_its_own_binding(self):
        changed = bytearray(self.image)
        helper = self.pairs[784168]
        address = helper + 192
        section = next(s for s in m.wm.m.elf_layout(changed)['sections'] if s['name'] == '.text')
        immediate = (self.details['formatter'] - address - 8) // 8
        struct.pack_into('<i', changed, section['offset'] + address - section['address'] + 4, immediate)
        windows = m.wm.windows(changed)
        before = next(r['signature'] for r in self.windows if r['address'] == helper)
        after = next(r['signature'] for r in windows if r['address'] == helper)
        self.assertEqual(before, after)
        with self.assertRaises(AssertionError):
            m.contract(changed, windows, self.pairs)


if __name__ == '__main__':
    unittest.main()

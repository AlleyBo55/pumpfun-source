"""Ensure body equality cannot conceal the location/message checks."""
from pathlib import Path
import importlib.util
import struct
import unittest
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('probe_analysis',HERE/'analyze.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class ScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=(a.ROOT/'evidence/original/pump_fees/deployed.so').read_bytes()
        cls.windows=a.wm.windows(cls.raw)
        cls.target=next(w for w in cls.windows if w['address']==700568)
    def replace(self,address,raw):
        section=next(s for s in a.wm.m.elf_layout(self.raw)['sections']if s['type']!=8 and s['address']<=address and address+len(raw)<=s['address']+s['size'])
        offset=section['offset']+address-section['address'];image=bytearray(self.raw);image[offset:offset+len(raw)]=raw;return bytes(image)
    def test_threshold_is_not_masked(self):
        image=self.replace(700568+148,struct.pack('<i',10002))
        target=next(w for w in a.wm.windows(image)if w['address']==700568)
        self.assertNotEqual(target['signature'],self.target['signature'])
    def test_location_is_checked_separately(self):
        image=self.replace(822896+16,struct.pack('<I',29))
        target=next(w for w in a.wm.windows(image)if w['address']==700568)
        self.assertEqual(target['signature'],self.target['signature'])
        self.assertEqual(a.predicate_details(image,self.windows,700568)['location']['line'],29)
    def test_pointer_requires_relocation_encoding(self):
        image=self.replace(822896,b'\x01')
        with self.assertRaises(AssertionError):a.relocated_slice(image,822896)
if __name__=='__main__':unittest.main()

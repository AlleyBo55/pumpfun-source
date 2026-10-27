"""Synthetic arithmetic only: never opens/decode an original or candidate ELF."""
import importlib.util
from pathlib import Path
import struct, unittest
spec=importlib.util.spec_from_file_location('boundary_inventory',Path(__file__).with_name('verify.py'))
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class RelativeCallTests(unittest.TestCase):
    def test_forward_instruction_units_and_next_pc(self):
        data=bytes(16)+bytes([0x85,0x10,0,0])+struct.pack('<i',3)
        self.assertEqual(v.resolve_call(data,16),48)
    def test_backward_signed_units(self):
        data=bytes(16)+bytes([0x85,0x10,0,0])+struct.pack('<i',-2)
        self.assertEqual(v.resolve_call(data,16),8)
    def test_external_hash_is_not_local_offset(self):
        with self.assertRaises(ValueError):v.resolve_call(bytes([0x85,0,0,0])+bytes(4),0)
    def test_reject_truncated_or_unaligned(self):
        for data,off in [(bytes(7),0),(bytes(16),1)]:
            with self.assertRaises(ValueError):v.resolve_call(data,off)
if __name__=='__main__':unittest.main()

#!/usr/bin/env python3
"""Mutation checks for metadata evidence boundaries; does not run target code."""
import gzip
import importlib.util
from pathlib import Path
import struct
import unittest

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('security_verify_tests', P / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
parser = v.module('security_test_parser', v.ROOT / v.PARSER)


class MetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = gzip.decompress((P / 'artifacts/candidate.so.gz').read_bytes())
        _, source = v.sources()
        cls.payload = v.semantic_payload(source)
        cls.elf = parser.Elf(cls.raw)
        cls.symbol = next(s for s in v.dynamic_symbols(cls.elf) if s['name'] == 'SECURITY_TXT')
        cls.object = v.security_object(cls.elf, cls.payload)

    def altered(self, offset, replacement):
        raw = bytearray(self.raw)
        raw[offset:offset + len(replacement)] = replacement
        return parser.Elf(bytes(raw))

    def test_exact_payload_and_source(self):
        self.assertEqual(len(self.payload), 510)
        self.assertEqual(self.object['payload_sha256'], 'c99e97216cf9d32f75f63b82caf56af585f95e486ef12e9b85ed122114aec171')

    def test_payload_mutation_rejected(self):
        section = self.elf.by_name['.rodata']
        offset = section['offset'] + self.object['payload_address'] - section['address']
        with self.assertRaises(AssertionError):
            v.security_object(self.altered(offset, b'!'), self.payload)

    def test_object_length_mutation_rejected(self):
        section = self.elf.by_name['.data.rel.ro']
        offset = section['offset'] + self.symbol['address'] - section['address'] + 8
        with self.assertRaises(AssertionError):
            v.security_object(self.altered(offset, struct.pack('<Q', 509)), self.payload)

    def test_nonzero_low_pointer_word_rejected(self):
        section = self.elf.by_name['.data.rel.ro']
        offset = section['offset'] + self.symbol['address'] - section['address']
        with self.assertRaises(AssertionError):
            v.security_object(self.altered(offset, b'\x01'), self.payload)

    def test_missing_relocation_rejected(self):
        elf = parser.Elf(self.raw)
        del elf.relocations[self.symbol['address']]
        with self.assertRaises(AssertionError):
            v.security_object(elf, self.payload)

    def test_wrong_relocation_kind_rejected(self):
        elf = parser.Elf(self.raw)
        elf.relocations[self.symbol['address']]['type'] = 10
        with self.assertRaises(AssertionError):
            v.security_object(elf, self.payload)

    def test_missing_export_rejected(self):
        section = self.elf.by_name['.dynstr']
        offset = self.raw.index(b'SECURITY_TXT\0', section['offset'], section['offset'] + section['size'])
        with self.assertRaises(AssertionError):
            v.security_object(self.altered(offset, b'X'), self.payload)

    def test_baseline_missing_export_rejected(self):
        descriptor = v.read(P / 'metadata.json')['baseline_artifacts']['candidate']
        elf = parser.Elf(gzip.decompress((v.ROOT / descriptor['path']).read_bytes()))
        with self.assertRaises(AssertionError):
            v.security_object(elf, self.payload)

    def test_extent_distinguishes_allocation_padding(self):
        extent = v.elf_extent(parser.Elf(self.raw + bytes(32)))
        self.assertEqual(extent['elf_extent_bytes'], len(self.raw))
        self.assertEqual(extent['trailing_bytes'], 32)
        self.assertTrue(extent['trailing_all_zero'])
        self.assertFalse(v.elf_extent(parser.Elf(self.raw + b'\x01'))['trailing_all_zero'])

    def test_unsafe_materialization_paths_rejected(self):
        for name in ['/tmp/escape', '../escape', 'src/../../escape', '', './src/file']:
            with self.subTest(name=name), self.assertRaises(AssertionError):
                v.safe_source_name(name)
        self.assertEqual(v.safe_source_name('src/embedded_security.rs'), Path('src/embedded_security.rs'))


if __name__ == '__main__':
    unittest.main()

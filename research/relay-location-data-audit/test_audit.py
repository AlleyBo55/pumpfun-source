#!/usr/bin/env python3
"""Static negative controls: no network, compiler, program execution or VM."""
import importlib.util
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('location_audit_tests', P / 'audit.py')
a = importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
p = a.module('location_proposal_tests', P / 'proposals.py')

class Fixture:
    def __init__(self, path=b'path/x.rs', length=None, low=0, line=7, column=1):
        self.record = struct.pack('<IIQII', low, 0x200, len(path) if length is None else length, line, column)
        self.string = path
        self.relocations = {0x100: {'type': 8, 'symbol': '', 'record_offset': 0x300}}
    def containing(self, address):
        return {'name': '.data.rel.ro' if address == 0x100 else '.rodata'}
    def at(self, address, n):
        data = self.record if address == 0x100 else self.string if address == 0x200 else b''
        if len(data) < n:
            raise ValueError('outside exact bound')
        return data[:n]

class Tests(unittest.TestCase):
    def test_full_bounded_location(self):
        value = a.read_location(Fixture(path=b'path/x.rsUNRELATED', length=9), 0x100)
        self.assertEqual(a.key(value), ('path/x.rs', 7, 1))
        self.assertEqual(value['object_bytes'], 24)
        self.assertEqual(value['string_bytes'], 9)

    def test_unrelocated_pointer_rejected(self):
        fixture = Fixture(); fixture.relocations.clear()
        self.assertIsNone(a.read_location(fixture, 0x100))

    def test_wrong_relocation_type_rejected(self):
        fixture = Fixture(); fixture.relocations[0x100]['type'] = 10
        self.assertIsNone(a.read_location(fixture, 0x100))

    def test_short_record_rejected(self):
        fixture = Fixture(); fixture.record = fixture.record[:-1]
        self.assertIsNone(a.read_location(fixture, 0x100))

    def test_zero_column_rejected(self):
        self.assertIsNone(a.read_location(Fixture(column=0), 0x100))

    def test_nonzero_low_word_rejected(self):
        self.assertIsNone(a.read_location(Fixture(low=1), 0x100))

    def test_incomplete_extent_rejected(self):
        self.assertIsNone(a.read_location(Fixture(length=10), 0x100))

    def test_non_source_string_rejected(self):
        self.assertIsNone(a.read_location(Fixture(path=b'something'), 0x100))

    def test_column_mutation_is_not_address_normalized_away(self):
        before = a.read_location(Fixture(column=1), 0x100)
        after = a.read_location(Fixture(column=5), 0x100)
        self.assertNotEqual(a.key(before), a.key(after))
        self.assertEqual(before['string_sha256'], after['string_sha256'])
        self.assertNotEqual(before['object_sha256'], after['object_sha256'])

    def test_real_audit_rederives(self):
        report = a.derive()
        self.assertEqual((report['recognized_location_pairs'], report['equal_location_pairs']), (346, 303))
        self.assertEqual((report['different_location_uses'], len(report['groups'])), (43, 6))
        self.assertFalse(report['compiled'])
        self.assertFalse(report['whole_file_equal'])
        self.assertEqual(report['new_raw_or_normalized_gains_claimed'], 0)

    def test_expanded_proposals_preserve_non_whitespace_source(self):
        before, groups = p.proposals()
        strip = lambda b: b''.join(b.split())
        self.assertEqual(strip(before['src/lib.rs']), strip(groups['program-column']['src/lib.rs']))
        self.assertEqual(strip(before['src/tools/fair_distribution.rs']), strip(groups['remainder-push-location']['src/tools/fair_distribution.rs']))
        events = groups['event-locations']
        expanded = events['src/anchor_donate.rs']
        for name, data in events.items():
            if name != 'src/anchor_donate.rs':
                include = ('include!("' + name.removeprefix('src/') + '");').encode()
                self.assertEqual(expanded.count(include), 1)
                expanded = expanded.replace(include, data)
        self.assertEqual(strip(before['src/anchor_donate.rs']), strip(expanded))
        mint = groups['mint-borrow-location']
        expanded = mint['src/mint_policy.rs'].replace(b'include!("tools/checks.rs");', mint['src/tools/checks.rs'])
        self.assertEqual(strip(before['src/mint_policy.rs']), strip(expanded))

    def test_patches_apply_to_exact_52_input_tree(self):
        source = p.full_sources()
        _, groups = p.proposals()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, data in source.items():
                file = root / name; file.parent.mkdir(parents=True, exist_ok=True); file.write_bytes(data)
            for label, changes in groups.items():
                patch = P / 'patches' / (label + '.patch')
                subprocess.run(['git', 'apply', '--check', str(patch)], cwd=root, check=True, capture_output=True)
                subprocess.run(['git', 'apply', str(patch)], cwd=root, check=True, capture_output=True)
                source.update(changes)
            actual = {str(f.relative_to(root)): f.read_bytes() for f in root.rglob('*') if f.is_file()}
            self.assertEqual(actual, source)

    def test_all_four_patch_proposals_exact(self):
        self.assertEqual(len(p.verify_proposals()), 4)

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""Synthetic unit checks only: no compiler, VM, network, or external process."""
import json
from pathlib import Path
import struct
import unittest
import verify as analysis


def instruction(opcode, registers=0, offset=0, immediate=0):
    return struct.pack('<BBhi', opcode, registers, offset, immediate)


class NarrowNormalizationTests(unittest.TestCase):
    def test_direct_call_masks_only_displacement(self):
        raw = instruction(0x85, 0x10, 0, -7)
        normalized, masks, calls = analysis.normalize(raw, 80, {})
        self.assertEqual(normalized, instruction(0x85, 0x10))
        self.assertEqual(masks, [dict(offset=4, bytes=4, reason='direct-call displacement')])
        self.assertEqual(calls, [dict(offset=0, target=32)])
        self.assertEqual(raw, instruction(0x85, 0x10, 0, -7))

    def test_external_call_immediate_is_not_masked(self):
        raw = instruction(0x85, 0x10, 0, 123)
        self.assertEqual(analysis.normalize(raw, 80, {80:10}), (raw, [], []))
        other = instruction(0x85, 0, 0, 123)
        self.assertEqual(analysis.normalize(other, 80, {}), (other, [], []))

    def test_only_relocated_lddw_words_are_masked(self):
        raw = instruction(0x18, 7, 0, 123) + instruction(0, 0, 0, 456)
        self.assertEqual(analysis.normalize(raw, 80, {})[0], raw)
        normalized, masks, calls = analysis.normalize(raw, 80, {80:1})
        self.assertEqual(normalized, instruction(0x18, 7) + instruction(0))
        self.assertEqual([x['offset'] for x in masks], [4, 12])
        self.assertEqual(calls, [])

    def test_register_branch_and_constant_differences_remain(self):
        samples = [instruction(0x4f, 0x21), instruction(0x4f, 0x12),
                   instruction(0x15, 1, 4, 0), instruction(0x15, 1, 5, 0),
                   instruction(0x57, 1, 0, 65535), instruction(0x57, 1, 0, 65534)]
        normalized = [analysis.normalize(raw, 0, {})[0] for raw in samples]
        self.assertEqual(samples, normalized)
        self.assertEqual(len(set(normalized)), len(samples))

    def test_truncated_instructions_are_rejected(self):
        for raw in (b'\0', instruction(0x18)):
            with self.assertRaises(ValueError):
                analysis.normalize(raw, 0, {})

    def test_invalid_elf_is_rejected(self):
        for data in (b'', b'\0' * 64, b'\x7fELF\x02\x01' + b'\0' * 58):
            with self.assertRaises(ValueError):
                analysis.Elf(data)


class ProposalTests(unittest.TestCase):
    def test_full_evidence_and_patches_rederive(self):
        analysis.verify()

    def test_mint_trial_is_only_operand_order(self):
        evidence = json.loads((analysis.PACKAGE / 'evidence.json').read_text())
        patch = evidence['mint']['proposal']['patch']
        deleted = [line[1:] for line in patch.splitlines() if line.startswith('-') and not line.startswith('---')]
        inserted = [line[1:] for line in patch.splitlines() if line.startswith('+') and not line.startswith('+++')]
        self.assertEqual(len(deleted), 1)
        self.assertEqual(len(inserted), 1)
        self.assertIn('older_transfer_fee', deleted[0].split('|')[0])
        self.assertIn('newer_transfer_fee', inserted[0].split('|')[0])
        # Bounded examples supplement the algebraic a | b == b | a identity;
        # they are not program runtime coverage.
        for a in (0, 1, 255, 256, 10000, 32768, 65535):
            for b in (0, 1, 255, 256, 10000, 32768, 65535):
                self.assertEqual(a | b, b | a)

    def test_compared_values_trial_retains_error_and_coordinates(self):
        patch = (analysis.PACKAGE / 'proposals/shares-compared-values.patch').read_text()
        deleted = [line for line in patch.splitlines() if line.startswith('-') and not line.startswith('---')]
        inserted = [line for line in patch.splitlines() if line.startswith('+') and not line.startswith('+++')]
        self.assertEqual(len(deleted), 1)
        self.assertEqual(len(inserted), 1)
        self.assertEqual(inserted[0][1:].replace('.with_values((sum, 10_000u32))', ''), deleted[0][1:])


if __name__ == '__main__':
    unittest.main()

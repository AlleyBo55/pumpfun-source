#!/usr/bin/env python3
"""Reject incomplete, mutated, or misaddressed SBF disassembly evidence."""
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parents[1] / 'scripts'
sys.path.insert(0, str(HERE))
from verify_disassembly import verify_listing


def elf(text):
    names = b'\0.text\0.shstrtab\0'
    header = b'\x7fELF\x02\x01' + bytes(10)
    header += struct.pack('<HHIQQQIHHHHHH', 3, 263, 1, 288, 0, 64,
                          0, 64, 56, 0, 64, 3, 2)
    sections = bytes(64)
    sections += struct.pack('<IIQQQQIIQQ', 1, 1, 6, 288, 288, len(text), 0, 0, 8, 0)
    sections += struct.pack('<IIQQQQIIQQ', 7, 3, 0, 0, 256, len(names), 0, 0, 1, 0)
    return (header + sections + names).ljust(288, b'\0') + text


EXIT = bytes.fromhex('95 00 00 00 00 00 00 00')
LDDW = bytes.fromhex('18 01 00 00 01 00 00 00 00 00 00 00 02 00 00 00')


def row(slot, code, mnemonic='exit'):
    return f' {slot}:\t{code.hex(" ")}\t{mnemonic}\n'


def listing(rows):
    return 'fixture.so:\tfile format elf64-sbf\n\nDisassembly of section .text:\n\n0000000000000120 <entrypoint>:\n' + rows


class DisassemblyTests(unittest.TestCase):
    def test_complete_listing(self):
        result = verify_listing(elf(EXIT), listing(row(36, EXIT)))
        self.assertTrue(result['complete_executable_byte_coverage'])
        self.assertEqual(result['executable_bytes_verified'], 8)
        self.assertFalse(result['semantic_decode_verified'])
        self.assertFalse(result['function_boundaries_verified'])

    def test_lddw_uses_two_slots_on_one_row(self):
        result = verify_listing(elf(LDDW + EXIT), listing(row(36, LDDW, 'lddw r1, 0x200000001') + row(38, EXIT)))
        self.assertEqual(result['instruction_rows'], 2)
        self.assertEqual(result['instruction_slots'], 3)
        self.assertEqual(result['sections']['.text']['lddw_rows'], 1)

    def test_empty_output(self):
        with self.assertRaisesRegex(ValueError, 'Missing executable'):
            verify_listing(elf(EXIT), '')

    def test_wrong_elf_machine(self):
        binary = bytearray(elf(EXIT))
        struct.pack_into('<H', binary, 18, 62)
        with self.assertRaisesRegex(ValueError, 'ELF machine'):
            verify_listing(bytes(binary), listing(row(36, EXIT)))

    def test_truncated_listing(self):
        with self.assertRaisesRegex(ValueError, 'Missing executable'):
            verify_listing(elf(EXIT * 2), listing(row(36, EXIT)))

    def test_changed_byte(self):
        with self.assertRaisesRegex(ValueError, 'bytes differ'):
            verify_listing(elf(EXIT), listing(row(36, bytes(8))))

    def test_missing_first_instruction(self):
        with self.assertRaisesRegex(ValueError, 'Noncontiguous'):
            verify_listing(elf(EXIT * 2), listing(row(37, EXIT)))

    def test_duplicate_row(self):
        with self.assertRaisesRegex(ValueError, 'Noncontiguous'):
            verify_listing(elf(EXIT * 2), listing(row(36, EXIT) * 2))

    def test_wrong_slot_unit(self):
        with self.assertRaisesRegex(ValueError, 'Noncontiguous'):
            verify_listing(elf(EXIT), listing(row(288, EXIT)))

    def test_missing_lddw_continuation(self):
        with self.assertRaisesRegex(ValueError, 'instruction width'):
            verify_listing(elf(LDDW), listing(row(36, LDDW[:8], 'lddw')))

    def test_non_lddw_cannot_consume_two_slots(self):
        with self.assertRaisesRegex(ValueError, 'instruction width'):
            verify_listing(elf(EXIT * 2), listing(row(36, EXIT * 2)))

    def test_unknown_instruction(self):
        with self.assertRaisesRegex(ValueError, 'Undecoded'):
            verify_listing(elf(EXIT), listing(row(36, EXIT, '<unknown>')))

    def test_data_directive(self):
        with self.assertRaisesRegex(ValueError, 'Undecoded'):
            verify_listing(elf(EXIT), listing(row(36, EXIT, '.byte 0x95')))

    def test_unparsed_executable_line(self):
        with self.assertRaisesRegex(ValueError, 'Unrecognized'):
            verify_listing(elf(EXIT), listing(' ...\n'))

    def test_wrong_section(self):
        with self.assertRaisesRegex(ValueError, 'Unexpected'):
            verify_listing(elf(EXIT), listing(row(36, EXIT)).replace('section .text:', 'section .rodata:'))

    def test_repeated_section(self):
        with self.assertRaisesRegex(ValueError, 'repeated section'):
            verify_listing(elf(EXIT), listing(row(36, EXIT)) + 'Disassembly of section .text:\n')

    def test_instruction_outside_section(self):
        with self.assertRaisesRegex(ValueError, 'outside a section'):
            verify_listing(elf(EXIT), row(36, EXIT))

    def test_instruction_beyond_section(self):
        with self.assertRaisesRegex(ValueError, 'exceeds section'):
            verify_listing(elf(EXIT), listing(row(36, EXIT) + row(37, EXIT)))


class DisassemblyCliTests(unittest.TestCase):
    def capture(self, payload):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        tools = root / 'research/disassembly-coverage'
        tools.mkdir(parents=True)
        (root / 'scripts').mkdir()
        for name in ('disassemble_checked.py', 'verify_disassembly.py'):
            shutil.copyfile(HERE / name, tools / name)
        shutil.copyfile(SCRIPTS / 'analyze.py', root / 'scripts/analyze.py')
        (root / 'repro').mkdir()
        (root / 'repro/programs.json').write_text('{"pump": "fixture"}')
        (root / 'evidence/original/pump').mkdir(parents=True)
        (root / 'evidence/original/pump/deployed.so').write_bytes(elf(EXIT))
        tool = root / 'objdump'
        tool.write_text('#!' + sys.executable + '\nimport sys\n'
                        'print("test objdump" if "--version" in sys.argv else ' + repr(payload) + ')\n')
        tool.chmod(0o755)
        process = subprocess.run(
            [sys.executable, str(tools / 'disassemble_checked.py'), '--objdump',
             str(tool), '--output', str(root / 'output')], capture_output=True, text=True)
        return process, root / 'output/manifest.json'

    def test_successful_empty_objdump_cannot_publish_manifest(self):
        process, manifest = self.capture('')
        self.assertNotEqual(process.returncode, 0)
        self.assertIn('Missing executable bytes', process.stderr)
        self.assertFalse(manifest.exists())

    def test_success_manifest_requires_verified_bytes(self):
        process, manifest = self.capture(listing(row(36, EXIT)))
        self.assertEqual(process.returncode, 0, process.stderr)
        result = json.loads(manifest.read_text())
        self.assertTrue(result['inputs_unchanged'])
        self.assertEqual(result['outputs']['pump']['listing_validation']['executable_bytes_verified'], 8)


if __name__ == '__main__':
    unittest.main()

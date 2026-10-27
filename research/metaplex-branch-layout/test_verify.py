import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import verify as v


class SavedEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.members = v.evidence()

    def mutated(self):
        return copy.deepcopy(self.members)

    def replace_log(self, members, filename, raw):
        members[filename] = raw
        state = json.loads(members['observation.json'])
        for command in state['commands']:
            for stream in ('stdout', 'stderr'):
                record = command[stream]
                if record['file'] == filename:
                    record.update(bytes=len(raw), sha256=v.sha(raw))
        members['observation.json'] = json.dumps(state).encode()

    def test_packet(self):
        self.assertTrue(v.verify()['verified'])

    def test_full_named_cfg_and_observed_branches(self):
        result = v.analyze_members(self.members)
        self.assertTrue(result['same_named_input_blocks'])
        self.assertFalse(result['reproduces_candidate12_extra_jump'])
        self.assertEqual(result['variants']['near-error']['object']['instructions'][2]['raw'], '3d24040000000000')

    def test_input_change_rejected(self):
        members = self.mutated()
        members['near-error.ll'] = members['near-error.ll'].replace(b'icmp ult', b'icmp ugt')
        with self.assertRaisesRegex(ValueError, 'IR input changed'):
            v.analyze_members(members)

    def test_final_selection_predicate_change_rejected(self):
        members = self.mutated()
        name = 'near-error-compile.stderr.log'
        self.replace_log(members, name, members[name].replace(b'icmp ult', b'icmp ugt'))
        with self.assertRaisesRegex(ValueError, 'final selection IR changed'):
            v.analyze_members(members)

    def test_missing_stage_rejected(self):
        members = self.mutated()
        name = 'far-error-compile.stderr.log'
        self.replace_log(members, name, members[name].replace(b'Before Control Flow Optimizer', b'Unidentified Optimizer'))
        with self.assertRaisesRegex(ValueError, 'machine stages'):
            v.analyze_members(members)

    def test_changed_selected_direction_rejected(self):
        members = self.mutated()
        name = 'near-error-compile.stderr.log'
        self.replace_log(members, name, members[name].replace(b'JUGE_rr', b'JUGT_rr', 1))
        with self.assertRaisesRegex(ValueError, 'conditional direction'):
            v.analyze_members(members)

    def test_raw_object_change_rejected(self):
        members = self.mutated()
        raw = bytearray(members['near-error.o'])
        raw[64 + 16] = 0x2d
        members['near-error.o'] = bytes(raw)
        self.replace_log(members, 'near-error-read-object.stdout.log', bytes(raw))
        with self.assertRaisesRegex(ValueError, 'emitted remaining-use branch'):
            v.analyze_members(members)

    def test_network_enabled_compilation_rejected(self):
        members = self.mutated()
        state = json.loads(members['observation.json'])
        command = next(c for c in state['commands'] if c['label'] == 'start')['command']
        command[command.index('--network') + 1] = 'bridge'
        members['observation.json'] = json.dumps(state).encode()
        with self.assertRaisesRegex(ValueError, 'isolation differs'):
            v.analyze_members(members)

    def test_non_diagnostic_flags_change_rejected(self):
        members = self.mutated()
        state = json.loads(members['observation.json'])
        for command in state['commands']:
            if command['label'].endswith('-compile'):
                command['command'][command['command'].index('-O3')] = '-O2'
        members['observation.json'] = json.dumps(state).encode()
        with self.assertRaisesRegex(ValueError, 'compiler arguments differ'):
            v.analyze_members(members)

    def test_relocated_offline_packet(self):
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder) / 'standalone'
            shutil.copytree(v.P, dest, ignore=shutil.ignore_patterns('__pycache__'))
            self.assertTrue(v.verify(dest)['verified'])


if __name__ == '__main__':
    unittest.main()

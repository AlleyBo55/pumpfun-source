import json
import unittest
import verify as v


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.files = v.load_run(v.HERE/'runs/40375285745')
        cls.policy = v.read(v.HERE/'policy.json')

    def changed_json(self, name, change):
        files = dict(self.files); value = json.loads(files[name]); change(value)
        files[name] = json.dumps(value).encode()
        return files

    def test_successful_run_and_four_raw_reference_matches(self):
        v.validate_success(self.files,self.policy)
        self.assertTrue(all(x['raw_equal'] for x in v.validate_references(self.files).values()))

    def test_padded_output_rejected(self):
        files = dict(self.files); files['baseline.stripped.so'] += b'\0'
        with self.assertRaisesRegex(ValueError,'Output digest differs'):
            v.validate_success(files,self.policy)

    def test_extra_source_change_rejected(self):
        files = self.changed_json('split-source-before.json',lambda o:o.update({'Cargo.toml':'0'*64}))
        with self.assertRaisesRegex(ValueError,'Source state differs'):
            v.validate_success(files,self.policy)

    def test_different_actual_compiler_arguments_rejected(self):
        files = self.changed_json('split-rustc-argv.json',lambda o:o.append('-Copt-level=2'))
        with self.assertRaisesRegex(ValueError,'Compiler arguments differ'):
            v.validate_success(files,self.policy)

    def test_online_compiler_receipt_rejected(self):
        def change(rows):
            argv = next(r for r in rows if r['label']=='container-split')['argv']
            argv[argv.index('--network')+1] = 'bridge'
        files = self.changed_json('host-commands.json',change)
        with self.assertRaisesRegex(ValueError,'Compilation network not disabled'):
            v.validate_success(files,self.policy)

    def test_wrong_registry_checksum_rejected(self):
        files = self.changed_json('registry-before.json',lambda o:o[0].update({'sha256':'0'*64}))
        with self.assertRaisesRegex(ValueError,'Recorded registry archives differ'):
            v.validate_success(files,self.policy)

    def test_changed_reference_comparison_rejected(self):
        files = dict(self.files); files['split.stripped.so'] += b'\0'
        with self.assertRaisesRegex(ValueError,'Fresh output differs from PR75 raw bytes'):
            v.validate_references(files)


if __name__ == '__main__':
    unittest.main()

"""Exercise object/path bindings and retained positive/negative observations."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import verify


class ArchivedRevisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = Path(__file__).resolve().parent
        cls.revision = json.loads((cls.package / ('responses/' + verify.REVISION + '.response')).read_bytes())
        cls.directories = {path.stem:json.loads(path.read_bytes()) for path in (cls.package / 'directories').iterdir()}
        cls.members = verify.crate_members((cls.package / 'archives/mpl-token-metadata-1.13.2-beta.1.crate').read_bytes(), '1.13.2-beta.1')
        cls.vcs = json.loads(cls.members['.cargo_vcs_info.json'])

    def test_retained_positive_and_negative_evidence(self):
        result = verify.check()
        self.assertEqual(result['distributed_files_matched'],162)
        self.assertEqual(result['git_trees_verified'],24)
        self.assertEqual([row['archive_status'] for row in result['revision_observations']],[404,404,404,200,404])
        self.assertFalse(result['deployed_source_identified'])

    def test_commit_message_and_parent_are_bound(self):
        for field, value in [('message','changed\n'),('parents',[])]:
            revision = copy.deepcopy(self.revision)
            revision[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError,'Git commit hash'):
                verify.commit_payload(revision)

    def test_timezone_spelling_is_not_silently_normalized(self):
        revision = copy.deepcopy(self.revision)
        revision['date'] = '2023-08-14T10:35:51+00:00'
        with self.assertRaisesRegex(ValueError,'Git commit hash'):
            verify.commit_payload(revision)

    def test_synthetic_revision_cannot_claim_git_association(self):
        revision = copy.deepcopy(self.revision)
        revision['synthetic'] = True
        with self.assertRaisesRegex(ValueError,'synthetic revision'):
            verify.commit_payload(revision)

    def test_tree_entry_order_uses_git_byte_sorting(self):
        root = self.directories[verify.ROOT_TREE]
        self.assertEqual(verify.tree_payload(root,verify.ROOT_TREE),
                         verify.tree_payload(list(reversed(root)),verify.ROOT_TREE))

    def test_tree_mode_or_target_change_is_rejected(self):
        for field,value in [('perms',0o100755),('target','0'*40)]:
            rows = copy.deepcopy(self.directories[verify.ROOT_TREE])
            row = next(item for item in rows if item['name']=='README.md')
            row[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError,'Git tree hash'):
                verify.tree_payload(rows,verify.ROOT_TREE)

    def test_duplicate_tree_name_is_rejected(self):
        rows = copy.deepcopy(self.directories[verify.ROOT_TREE])
        rows.append(rows[0])
        with self.assertRaisesRegex(ValueError,'Duplicate tree name'):
            verify.tree_payload(rows,verify.ROOT_TREE)

    def test_missing_intermediate_tree_breaks_path_proof(self):
        directories = dict(self.directories)
        del directories['288508afe2cb420eb7631f13d3940e846135fc86']
        with self.assertRaisesRegex(ValueError,'Missing tree'):
            verify.compare_crate(self.members,directories,self.vcs)

    def test_wrong_embedded_package_path_is_rejected(self):
        vcs = copy.deepcopy(self.vcs)
        vcs['path_in_vcs'] = 'token-metadata/program'
        with self.assertRaisesRegex(ValueError,'Embedded crate revision/path'):
            verify.compare_crate(self.members,self.directories,vcs)

    def test_changed_distributed_source_is_rejected(self):
        members = dict(self.members)
        name = 'src/processor/uses/utilize.rs'
        members[name] += b'\n'
        with self.assertRaisesRegex(ValueError,'Distributed file differs'):
            verify.compare_crate(members,self.directories,self.vcs)

    def test_license_mapping_requires_actual_declared_path(self):
        members = dict(self.members)
        members['Cargo.toml.orig'] = members['Cargo.toml.orig'].replace(b'../../../LICENSE',b'../../LICENSE')
        with self.assertRaisesRegex(ValueError,'license mapping'):
            verify.compare_crate(members,self.directories,self.vcs)

    def test_changed_directory_metadata_is_rejected(self):
        directories = copy.deepcopy(self.directories)
        entry,_ = verify.locate('LICENSE',directories)
        entry['length'] += 1
        with self.assertRaisesRegex(ValueError,'Archived content metadata'):
            verify.compare_crate(self.members,directories,self.vcs)

    def test_minimal_relocated_replay_and_tampering(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'package'
            shutil.copytree(self.package,root)
            self.assertEqual(verify.check(root)['distributed_files_matched'],162)
            path = root / 'findings.json'
            saved = json.loads(path.read_bytes())
            saved['deployed_source_identified'] = True
            path.write_text(json.dumps(saved),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Saved findings'):
                verify.check(root)

    def test_missing_observation_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'package'
            shutil.copytree(self.package,root)
            path = root / 'revision-receipts.json'
            rows = json.loads(path.read_bytes())
            rows.pop()
            path.write_text(json.dumps(rows),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Changed evidence: revision-receipts'):
                verify.check(root)


if __name__ == '__main__':
    unittest.main()

"""Failure and one-attempt policy tests; compiler/native launcher always mocked."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('controller',Path(__file__).with_name('controller.py'));c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
class Tests(unittest.TestCase):
 def test_existing_claim_stops_before_native(self):
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp)
   with patch.object(c,'CLAIM',p/'claim'),patch.object(c,'EXPERIMENT',p/'experiment'),patch.object(c.subprocess,'run')as runner:
    (p/'claim').write_text('{}')
    with self.assertRaises(AssertionError):c.path_checks()
    runner.assert_not_called()
 def test_ancestor_cargo_config_rejected(self):
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp);(p/'.cargo').mkdir();(p/'.cargo/config.toml').write_text('[build]\nrustflags=["bad"]\n')
   with patch.object(c,'CLAIM',p/'claim'),patch.object(c,'EXPERIMENT',p/'experiment'),patch.object(c.subprocess,'run')as runner:
    with self.assertRaises(AssertionError):c.path_checks()
    runner.assert_not_called()
 def test_symlink_parent_rejected(self):
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp);(p/'real').mkdir();(p/'alias').symlink_to(p/'real',target_is_directory=True)
   with patch.object(c,'CLAIM',p/'alias/claim'),patch.object(c,'EXPERIMENT',p/'alias/experiment'):
    with self.assertRaises(AssertionError):c.path_checks()
if __name__=='__main__':unittest.main()

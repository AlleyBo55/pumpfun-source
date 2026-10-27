"""Regression tests for misleading completion counts and false perfection claims."""
import unittest
from unittest.mock import patch
import audit


def row(start, raw, **kw):
    return dict(start=start, end=start+len(raw), raw_sha256=audit.sha(raw), names=['candidate_helper'], **kw)


class ClassificationTests(unittest.TestCase):
    def run_inventory(self, original, candidate, originals, candidates, matches):
        with patch.object(audit, 'at', side_effect=lambda image, start, size: image[start:start+size]):
            return audit.inventory('test', 'selected', original, candidate, 'fixture', originals, candidates,
                                   lambda r: matches, lambda r: [])

    def test_duplicate_raw_pairs_count_one_original_window(self):
        rows=self.run_inventory(b'abc', b'abcabc', [row(0,b'abc')], [row(0,b'abc'),row(3,b'abc')], [0,3])
        summary=audit.summarize(rows)
        self.assertEqual(summary['raw_body_equal_original_windows'],1)
        self.assertEqual(summary['raw_match_ambiguous_original_windows'],1)
        self.assertEqual(rows[0]['raw_candidate_starts'],[0,3])

    def test_opaque_raw_match_is_not_promoted_to_semantic_proof(self):
        rows=self.run_inventory(b'abc',b'abc',[row(0,b'abc',scope='opaque')],[row(0,b'abc')],[])
        self.assertTrue(rows[0]['opaque_in_source_ledger'])
        self.assertEqual(rows[0]['disposition'],'raw_body_equal')
        self.assertFalse(rows[0]['semantic_perfection_proven'])
        self.assertEqual(audit.summarize(rows)['normalized_match_original_windows'],0)

    def test_normalized_relation_does_not_claim_raw_equality(self):
        rows=self.run_inventory(b'abc',b'abd',[row(0,b'abc')],[row(0,b'abd')],[0])
        self.assertEqual(rows[0]['disposition'],'normalized_body_only')
        self.assertEqual(rows[0]['raw_candidate_starts'],[])
        self.assertFalse(rows[0]['semantic_perfection_proven'])

    def test_hash_mismatch_rejects_stale_candidate_ledger(self):
        with self.assertRaises(AssertionError):
            self.run_inventory(b'abc',b'abd',[row(0,b'abc')],[row(0,b'abc')],[])

    def test_absent_match_does_not_discard_original_window(self):
        rows=self.run_inventory(b'abc',b'def',[row(0,b'abc')],[row(0,b'def')],[])
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['disposition'],'no_complete_body_match')

    def test_exact_names_exclude_normalized_only_alternatives(self):
        a=row(0,b'abc');a['names']=['exact_helper']
        b=row(3,b'abd');b['names']=['normalized_only_helper']
        rows=self.run_inventory(b'abc',b'abcabd',[row(0,b'abc')],[a,b],[0,3])
        self.assertEqual(rows[0]['raw_candidate_names'],['exact_helper'])


if __name__=='__main__':unittest.main()

"""Adversarial tests for call-context attribution, independent of saved counts."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('call_attribute', Path(__file__).with_name('attribute.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def node(address, signature):
    return dict(address=address, signature=signature, name='annotation-' + str(address))


class AttributionTests(unittest.TestCase):
    def chain(self):
        original = [node(10, 'seed'), node(20, 'dup-a'), node(30, 'dup-a'),
                    node(40, 'dup-b'), node(50, 'dup-b')]
        candidate = [node(110, 'seed'), node(120, 'dup-a'), node(130, 'dup-a'),
                     node(140, 'dup-b'), node(150, 'dup-b')]
        a = {10: {8: 20}, 20: {16: 40}, 30: {16: 50}, 40: {}, 50: {}}
        b = {110: {8: 120}, 120: {16: 140}, 130: {16: 150}, 140: {}, 150: {}}
        return original, candidate, a, b

    def test_two_round_chain_keeps_unreached_duplicates_unresolved(self):
        result = module.attribute(*self.chain())
        self.assertEqual(result['known'], {10: 110, 20: 120, 40: 140})
        self.assertEqual([len(row['additions']) for row in result['rounds']], [1, 1])
        self.assertEqual(result['rounds'][1]['additions'][0]['witnesses'][0]['original_caller'], 20)

    def test_conflicting_forward_proposals_do_not_choose_first(self):
        a, b, calls_a, calls_b = self.chain()
        a.append(node(11, 'second-seed'))
        b.append(node(111, 'second-seed'))
        calls_a[11] = {8: 20}
        calls_b[111] = {8: 130}
        result = module.attribute(a, b, calls_a, calls_b)
        self.assertNotIn(20, result['known'])
        self.assertEqual(result['proposals'][20], {120, 130})

    def test_conflicting_reverse_proposals_do_not_assume_a_bijection(self):
        a, b, calls_a, calls_b = self.chain()
        a.append(node(11, 'second-seed'))
        b.append(node(111, 'second-seed'))
        calls_a[11] = {8: 30}
        calls_b[111] = {8: 120}
        result = module.attribute(a, b, calls_a, calls_b)
        self.assertNotIn(20, result['known'])
        self.assertNotIn(30, result['known'])
        self.assertEqual(result['reverse_proposals'][120], {20, 30})

    def test_conflict_with_known_target_rejects_refinement(self):
        a = [node(10, 'caller'), node(20, 'target-a'), node(30, 'target-b')]
        b = [node(110, 'caller'), node(120, 'target-a'), node(130, 'target-b')]
        with self.assertRaisesRegex(AssertionError, 'conflict'):
            module.attribute(a, b, {10: {8: 20}, 20: {}, 30: {}},
                             {110: {8: 130}, 120: {}, 130: {}})

    def test_different_body_target_is_frontier_not_a_promotion(self):
        a = [node(10, 'caller'), node(20, 'left-only'), node(30, 'left-only')]
        b = [node(110, 'caller'), node(120, 'right-only'), node(130, 'right-only')]
        result = module.attribute(a, b, {10: {8: 20}, 20: {}, 30: {}},
                                  {110: {8: 120}, 120: {}, 130: {}})
        self.assertEqual(result['known'], {10: 110})
        self.assertEqual(len(result['frontier']), 1)

    def test_frontier_conflict_after_promotion_rejects_the_result(self):
        a, b, calls_a, calls_b = self.chain()
        a.append(node(11, 'second-seed'))
        b.append(node(111, 'second-seed'))
        calls_a[11] = {8: 20}
        calls_b[111] = {8: 140}
        with self.assertRaisesRegex(AssertionError, 'conflict'):
            module.attribute(a, b, calls_a, calls_b)

    def test_call_position_is_part_of_the_evidence(self):
        a, b, calls_a, calls_b = self.chain()
        calls_b[110] = {16: 120}
        with self.assertRaisesRegex(AssertionError, 'local-call shape'):
            module.attribute(a, b, calls_a, calls_b)

    def test_names_address_order_and_input_order_do_not_select_pairs(self):
        a, b, calls_a, calls_b = copy.deepcopy(self.chain())
        left_map = {10: 700, 20: 900, 30: 100, 40: 200, 50: 500}
        right_map = {110: 80, 120: 60, 130: 40, 140: 20, 150: 100}
        for rows, address_map in [(a, left_map), (b, right_map)]:
            for row in rows:
                row['address'] = address_map[row['address']]
                row['name'] = 'deliberately-incorrect-name'
            rows.reverse()
        remap = lambda calls, table: {table[k]: {o: table[v] for o, v in values.items()}
                                      for k, values in calls.items()}
        result = module.attribute(a, b, remap(calls_a, left_map), remap(calls_b, right_map))
        self.assertEqual(result['known'], {700: 80, 900: 60, 200: 20})


if __name__ == '__main__':
    unittest.main()

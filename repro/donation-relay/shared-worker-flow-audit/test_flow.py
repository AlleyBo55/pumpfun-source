"""Guard against false cleanup postdominance from CFG decoding mistakes."""
import struct
import unittest
from flow import graph, path


def instruction(opcode, offset=0, immediate=0):
    return struct.pack('<BBhi', opcode, 0, offset, immediate)


class FlowTests(unittest.TestCase):
    def test_conditional_bypass_is_not_postdominated(self):
        nodes = graph(instruction(0x15, 1) + instruction(0x85) + instruction(0x95))
        self.assertEqual(path(nodes, 0, [16], [8]), [0, 16])

    def test_unconditional_jump_has_no_fallthrough(self):
        nodes = graph(instruction(0x05, 1) + instruction(0x95) + instruction(0x95))
        self.assertIsNone(path(nodes, 0, [8]))
        self.assertEqual(path(nodes, 0, [16]), [0, 16])

    def test_lddw_continuation_is_not_a_node(self):
        nodes = graph(instruction(0x18) + bytes(8) + instruction(0x95))
        self.assertEqual(list(nodes), [0, 16])
        self.assertEqual(path(nodes, 0, [16]), [0, 16])

    def test_reject_jump_into_lddw_continuation(self):
        with self.assertRaises(AssertionError):
            graph(instruction(0x05, 1) + instruction(0x18) + bytes(8) + instruction(0x95))

    def test_returning_call_does_not_follow_immediate(self):
        nodes = graph(instruction(0x85, immediate=10000) + instruction(0x95))
        self.assertEqual(path(nodes, 0, [8]), [0, 8])

    def test_cycle_terminates_without_inventing_exit(self):
        nodes = graph(instruction(0x05, -1) + instruction(0x95))
        self.assertIsNone(path(nodes, 0, [8]))

    def test_unknown_control_opcode_rejected(self):
        with self.assertRaises(AssertionError):
            graph(instruction(0x06) + instruction(0x95))

    def test_jmp32_has_two_edges(self):
        nodes = graph(instruction(0x16, 1) + instruction(0x95) + instruction(0x95))
        self.assertEqual(nodes[0]['successors'], [8, 16])


if __name__ == '__main__':
    unittest.main()

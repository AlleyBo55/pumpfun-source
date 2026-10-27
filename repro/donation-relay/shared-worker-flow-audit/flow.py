"""Conservative intraprocedural SBF control flow, with returning-call assumption."""
import collections
import struct


def graph(raw):
    assert len(raw) % 8 == 0
    nodes = {}
    cursor = 0
    while cursor < len(raw):
        opcode, registers, offset, immediate = struct.unpack_from('<BBhi', raw, cursor)
        step = 16 if opcode == 0x18 else 8
        assert cursor + step <= len(raw)
        if opcode == 0x95:
            successors = []
        elif opcode == 0x05:
            successors = [cursor + 8 + offset * 8]
        elif opcode & 7 in (5, 6) and opcode not in (0x85, 0x8d):
            assert opcode & 0xf0 in (0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0xa0, 0xb0, 0xc0, 0xd0), 'unsupported control opcode'
            successors = [cursor + 8, cursor + 8 + offset * 8]
        else:
            successors = [cursor + step]
        nodes[cursor] = dict(opcode=opcode, registers=registers, offset=offset,
                             immediate=immediate, successors=successors)
        cursor += step
    assert all(target in nodes for node in nodes.values() for target in node['successors'])
    return nodes


def path(nodes, source, targets, avoid=()):
    queue = collections.deque([source])
    parents = {source: None}
    while queue:
        current = queue.popleft()
        if current in avoid:
            continue
        if current in targets:
            result = []
            while current is not None:
                result.append(current)
                current = parents[current]
            return result[::-1]
        for successor in nodes[current]['successors']:
            if successor not in parents:
                parents[successor] = current
                queue.append(successor)
    return None


def analyze(elf, start, size, target_ordinals):
    nodes = graph(elf.at(start, size))
    calls = [dict(offset=row['offset'], target=row['target'],
                  original_ordinals=target_ordinals.get(row['target'], []))
             for row in elf.function(start, size, [])['direct_calls']]
    drop_calls = [row['offset'] for row in calls if row['original_ordinals'] == [51]]
    transfer_calls = [row['offset'] for row in calls if row['original_ordinals'] == [226]]
    assert len(drop_calls) == len(transfer_calls) == 1
    drop, transfer = drop_calls[0], transfer_calls[0]
    exits = [offset for offset, node in nodes.items() if node['opcode'] == 0x95]
    assert exits
    entry_bypass = path(nodes, 0, exits, [drop])
    transfer_bypass = path(nodes, transfer + 8, exits, [drop])
    transfer_to_drop = path(nodes, transfer + 8, [drop])
    drop_to_exit = path(nodes, drop + 8, exits)
    assert entry_bypass is None and transfer_bypass is None
    assert transfer_to_drop is not None and drop_to_exit is not None
    return dict(start=start, bytes=size, instructions=nodes, direct_calls=calls,
                context_drop_offset=drop, transfer_offset=transfer, exit_offsets=exits,
                entry_to_exit_avoiding_context_drop=entry_bypass,
                transfer_to_exit_avoiding_context_drop=transfer_bypass,
                transfer_to_context_drop=transfer_to_drop, context_drop_to_exit=drop_to_exit)

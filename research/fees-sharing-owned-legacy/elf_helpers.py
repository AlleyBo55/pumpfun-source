"""Small ELF/SBF readers used by the standalone dispatch-order packet."""
import hashlib
import importlib.util
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('pinned_elf_layout', ROOT / 'scripts/analyze.py')
layout_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layout_module)
elf_layout = layout_module.elf_layout


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def section_data(image, name):
    section = next(s for s in elf_layout(image)['sections'] if s['name'] == name)
    return image[section['offset']:section['offset'] + section['size']]


def at_address(image, address, size):
    section = next(s for s in elf_layout(image)['sections']
                   if s['type'] != 8 and s['address'] <= address
                   and address + size <= s['address'] + s['size'])
    offset = section['offset'] + address - section['address']
    return image[offset:offset + size]


def functions(image):
    h = struct.unpack_from('<HHIQQQIHHHHHH', image, 16)
    sections = [struct.unpack_from('<IIQQQQIIQQ', image, h[5] + i * h[10])
                for i in range(h[11])]
    result = []
    for s in sections:
        if s[1] != 2:
            continue
        strings = sections[s[6]]
        names = image[strings[4]:strings[4] + strings[5]]
        for p in range(s[4], s[4] + s[5], s[9]):
            name, info, _, _, address, size = struct.unpack_from('<IBBHQQ', image, p)
            if info & 15 == 2 and size:
                result.append(dict(address=address, bytes=size,
                    name=names[name:].split(b'\0', 1)[0].decode()))
    return result


def instructions(image, address, size):
    raw = at_address(image, address, size)
    result, p = [], 0
    while p < len(raw):
        opcode, registers, displacement, immediate = struct.unpack_from('<BBhi', raw, p)
        width = 16 if opcode == 0x18 else 8
        assert p + width <= len(raw)
        data = raw[p:p + width]
        row = dict(offset=p, opcode=opcode, destination=registers & 15,
                   source=registers >> 4, displacement=displacement,
                   immediate=immediate, raw=data.hex())
        if opcode == 0x85 and row['source'] == 1:
            row['call_target'] = address + p + 8 + immediate * 8
        if opcode == 0x18:
            row['lddw_value'] = int.from_bytes(data[4:8] + data[12:16], 'little')
        result.append(row)
        p += width
    return result


def cfg(rows):
    by_offset = {r['offset']: r for r in rows}
    pending, seen, outside = [0], set(), set()
    while pending:
        offset = pending.pop()
        if offset in seen:
            continue
        if offset not in by_offset:
            outside.add(offset)
            continue
        seen.add(offset)
        row = by_offset[offset]
        opcode = row['opcode']
        next_offset = offset + len(bytes.fromhex(row['raw']))
        if opcode == 0x95:
            continue
        if opcode & 7 in (5, 6) and opcode != 0x85:
            pending.append(offset + 8 + row['displacement'] * 8)
            if opcode == 0x05:
                continue
        pending.append(next_offset)
    return dict(instructions=len(rows), reachable_instructions=len(seen),
                outside_successors=sorted(outside))


def relocations(image):
    result = []
    for section in elf_layout(image)['sections']:
        if section['type'] == 9:
            for offset in range(section['offset'], section['offset'] + section['size'], 16):
                address, info = struct.unpack_from('<QQ', image, offset)
                result.append((address, info))
    return result

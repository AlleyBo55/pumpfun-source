#!/usr/bin/env python3
"""Recompute bounded account-parser differences from retained ELF outputs."""
import difflib
import gzip
import hashlib
import importlib.util
import json
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


def call_masked(row):
    raw = bytearray.fromhex(row['raw'])
    if 'call_target' in row:
        raw[4:8] = bytes(4)
    return bytes(raw)


def compare(original_image, original, candidate_image, candidate):
    a, b = [call_masked(r) for r in original], [call_masked(r) for r in candidate]
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    result = dict(original_instructions=len(a), candidate_instructions=len(b),
        call_masked_sequence_matches=sum(m.size for m in matcher.get_matching_blocks()),
        call_masked_equal=a == b, differences=[])
    # This extra classification requires the same instruction positions and sizes.
    # It records actual changed operands; it is not an equivalence or acceptance rule.
    if [r['offset'] for r in original] != [r['offset'] for r in candidate]:
        return result
    for i, (left, right) in enumerate(zip(original, candidate)):
        if left['raw'] == right['raw']:
            continue
        row = dict(offset=left['offset'], original_raw=left['raw'], candidate_raw=right['raw'])
        x, y = bytes.fromhex(left['raw']), bytes.fromhex(right['raw'])
        if 'call_target' in left and call_masked(left) == call_masked(right):
            row.update(kind='encoded_call_immediate', original_target=left['call_target'],
                       candidate_target=right['call_target'])
        elif left['opcode'] == right['opcode'] == 0x18 and left['offset'] in (32, 96):
            assert x[:4] == y[:4] and x[8:12] == y[8:12]
            # Both constants are passed to memcmp with a 32-byte length.
            original_data = at_address(original_image, left['lddw_value'], 32)
            candidate_data = at_address(candidate_image, right['lddw_value'], 32)
            assert original_data == candidate_data
            row.update(kind='address_of_equal_32_byte_constant', constant=original_data.hex(),
                       original_address=left['lddw_value'], candidate_address=right['lddw_value'])
        elif (x[:2] == y[:2] and x[4:] == y[4:]
              and ((left['opcode'] == 0x79 and left['source'] == 10)
                   or (left['opcode'] == 0x7b and left['destination'] == 10))):
            row.update(kind='stack_displacement', original=left['displacement'],
                       candidate=right['displacement'])
        elif (left['opcode'] == right['opcode'] == 0x07 and x[:4] == y[:4]
              and i and original[i - 1]['raw'] == candidate[i - 1]['raw']
              and original[i - 1]['opcode'] == 0xbf
              and original[i - 1]['source'] == 10
              and original[i - 1]['destination'] == left['destination']):
            row.update(kind='stack_address_addend', original=left['immediate'],
                       candidate=right['immediate'])
        else:
            row['kind'] = 'other'
        result['differences'].append(row)
    result['unclassified_differences'] = sum(r['kind'] == 'other' for r in result['differences'])
    return result


def analyze():
    experiment = json.loads((HERE / 'experiment.json').read_text())
    original_image = (ROOT / 'evidence/original/pump_fees/deployed.so').read_bytes()
    assert digest(original_image) == '4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
    original = instructions(original_image, 36072, 1248)
    decoder_rows = instructions(original_image, 257264, 704)
    result = dict(original_sha256=digest(original_image), original_window=[36072, 37320],
        original_decoder=dict(encoded_target=257264, inspected_prefix_bytes=704,
            length_branches=[r for r in decoder_rows
                             if r['opcode'] == 0xa5 and r['immediate'] in (2504, 4065, 4089)]),
        variants={})
    assert next(r for r in original if r['offset'] == 1080)['call_target'] == 257264
    assert [r['immediate'] for r in result['original_decoder']['length_branches']] == [2504, 4065, 4089]
    discriminator = int.from_bytes(bytes.fromhex('8f3492bbdb7b4c9b'), 'little')
    for label, entry in experiment['variants'].items():
        images = {}
        for kind, f in entry['files'].items():
            images[kind] = gzip.decompress((HERE / f['path']).read_bytes())
            assert len(images[kind]) == f['bytes'] and digest(images[kind]) == f['sha256']
        image = images['symbols']
        assert section_data(image, '.text') == section_data(images['candidate'], '.text')
        matches = []
        symbols = functions(image)
        for symbol in symbols:
            if 'Account$LT$T$GT$8try_from' not in symbol['name']:
                continue
            rows = instructions(image, symbol['address'], symbol['bytes'])
            if any(r.get('lddw_value') == discriminator for r in rows):
                matches.append((symbol, rows))
        assert len(matches) == 1
        symbol, rows = matches[0]
        decoder_calls = []
        for row in rows:
            for callee in symbols:
                if (callee['address'] == row.get('call_target') and 'FeeConfig' in callee['name']
                    and ('try_deserialize_unchecked' in callee['name'] or 'deserialize_body' in callee['name'])):
                    decoder_calls.append(dict(call_offset=row['offset'], symbol=callee,
                        length_branches=[r for r in instructions(image, callee['address'], callee['bytes'])
                                         if r['opcode'] == 0xa5
                                         and r['immediate'] in (2504, 2512, 4065, 4073, 4089, 4097)]))
        assert len(decoder_calls) == 1
        result['variants'][label] = dict(symbol=symbol, decoder=decoder_calls[0],
            discriminator_sites=[r['offset'] for r in rows if r.get('lddw_value') == discriminator],
            invalid_data_entries=[r['offset'] for r in rows
                                  if r.get('lddw_value') == 0x8000000000000003],
            comparison=compare(original_image, original, image, rows))
    return result


if __name__ == '__main__':
    print(json.dumps(analyze(), indent=2))

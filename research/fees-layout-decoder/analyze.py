#!/usr/bin/env python3
"""Recompute bounded Fees decoder and caller evidence from retained ELF outputs."""
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


def cursor_stores_before_first_call(rows):
    """Track copies of the unmodified incoming r2 pointer until the first CALL."""
    aliases, stores = {2}, []
    for row in rows:
        if row['opcode'] == 0x85:
            break
        opcode, destination, source = row['opcode'], row['destination'], row['source']
        if opcode == 0x7b and destination in aliases and row['displacement'] in (0, 8):
            stores.append(row)
        if opcode & 7 in (0, 1, 4, 7):
            if opcode == 0xbf and source in aliases:
                aliases.add(destination)
            else:
                aliases.discard(destination)
    return stores


def sequence_summary(original, candidate):
    a, b = [call_masked(r) for r in original], [call_masked(r) for r in candidate]
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return dict(original_instructions=len(a), candidate_instructions=len(b),
        equal_after_masking_call_immediates=a == b,
        matching_sequence_instructions=sum(m.size for m in matcher.get_matching_blocks()))


def account_comparison_bytes(image, rows):
    output = bytearray()
    for row in rows:
        raw = bytearray(call_masked(row))
        if row['offset'] in (32, 96):
            assert row['opcode'] == 0x18
            expected = bytes(32) if row['offset'] == 32 else bytes.fromhex(
                '0c35ffa9055a8e568da8f7bc075615274cf1c92ca41f40009c516aa414c27c70')
            assert at_address(image, row['lddw_value'], 32) == expected
            raw[4:8] = raw[12:16] = bytes(4)
        output.extend(raw)
    return bytes(output)


def analyze():
    experiment = json.loads((HERE / 'experiment.json').read_text())
    original_image = (ROOT / 'evidence/original/pump_fees/deployed.so').read_bytes()
    assert digest(original_image) == '4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
    original_account = instructions(original_image, 36072, 1248)
    original_decoder = instructions(original_image, 257264, 2648)
    text = next(s for s in elf_layout(original_image)['sections'] if s['name'] == '.text')
    all_rows = instructions(original_image, text['address'], text['size'])
    next_entry = min(r['call_target'] for r in all_rows
                     if r.get('call_target', 0) > 257264)
    assert next_entry == 259912
    result = dict(original_sha256=digest(original_image),
        original_decoder_window=[257264, next_entry], original_decoder_cfg=cfg(original_decoder),
        original_cursor_stores=cursor_stores_before_first_call(original_decoder),
        original_decoder_calls=[r for r in original_decoder if 'call_target' in r],
        variants={})
    assert result['original_decoder_cfg'] == dict(instructions=325, reachable_instructions=325,
                                                outside_successors=[])
    assert [r['displacement'] for r in result['original_cursor_stores']] == [8, 0]
    accounts = {}
    for label, entry in experiment['variants'].items():
        images = {}
        for kind, f in entry['files'].items():
            images[kind] = gzip.decompress((HERE / f['path']).read_bytes())
            assert len(images[kind]) == f['bytes'] and digest(images[kind]) == f['sha256']
        image = images['symbols']
        assert section_data(image, '.text') == section_data(images['candidate'], '.text')
        symbols = functions(image)
        account_matches = []
        for symbol in symbols:
            if 'Account$LT$T$GT$8try_from' in symbol['name']:
                rows = instructions(image, symbol['address'], symbol['bytes'])
                if any(r.get('lddw_value') == 0x9b4c7bdbbb92348f for r in rows):
                    account_matches.append((symbol, rows))
        assert len(account_matches) == 1
        account_symbol, account_rows = account_matches[0]
        decoder_symbols = [s for s in symbols if 'FeeConfig' in s['name']
                           and 'try_deserialize_unchecked' in s['name']]
        assert len(decoder_symbols) == 1
        decoder_symbol = decoder_symbols[0]
        decoder_rows = instructions(image, decoder_symbol['address'], decoder_symbol['bytes'])
        assert any(r.get('call_target') == decoder_symbol['address'] for r in account_rows)
        accounts[label] = account_comparison_bytes(image, account_rows)
        result['variants'][label] = dict(account_symbol=account_symbol,
            account_comparison=compare(original_image, original_account, image, account_rows),
            decoder_symbol=decoder_symbol, decoder_cfg=cfg(decoder_rows),
            decoder_sequence_comparison=sequence_summary(original_decoder, decoder_rows),
            cursor_stores=cursor_stores_before_first_call(decoder_rows),
            decoder_calls=[dict(instruction=r,
                                candidate_target_symbols=[s for s in symbols if s['address'] == r['call_target']])
                           for r in decoder_rows if 'call_target' in r],
            allocation_branches=[r for r in decoder_rows
                if r['opcode'] & 7 in (5, 6) and r['opcode'] not in (0x85, 0x95)
                and r['immediate'] in (2504, 4064, 4065, 4088, 4089)])
    result['v145_account_equals_v144_after_call_and_verified_constant_pointer_masks'] = (
        accounts['control-v144'] == accounts['control-v145'])
    assert result['v145_account_equals_v144_after_call_and_verified_constant_pointer_masks']
    return result



if __name__ == '__main__':
    print(json.dumps(analyze(), indent=2))

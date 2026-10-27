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


def account_pointer_pattern_present(image, rows):
    by_offset = {r['offset']: r for r in rows}
    for offset, expected in [(32, bytes(32)), (96, bytes.fromhex(
            '0c35ffa9055a8e568da8f7bc075615274cf1c92ca41f40009c516aa414c27c70'))]:
        row = by_offset.get(offset)
        if row is None or row['opcode'] != 0x18:
            return False
        if at_address(image, row['lddw_value'], 32) != expected:
            return False
    return True


def analyze():
    experiment = json.loads((HERE / 'experiment.json').read_text())
    original = (ROOT / 'evidence/original/pump_fees/deployed.so').read_bytes()
    assert digest(original) == '4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
    original_layout = elf_layout(original)
    account = instructions(original, 36072, 1248)
    decoder = instructions(original, 257264, 2648)
    original_account_normalized = account_comparison_bytes(original, account)
    original_query = instructions(original, 518976, 1784)
    original_wrapper = instructions(original, 71256, 200)
    assert next(r for r in original_query if 'call_target' in r)['call_target'] == 71256
    assert [r for r in original_wrapper if 'call_target' in r][-1]['call_target'] == 36072
    result = dict(original_sha256=digest(original),
        original_account_window=[36072, 37320], original_account_cfg=cfg(account),
        original_decoder_window=[257264, 259912], original_decoder_cfg=cfg(decoder),
        original_decoder_calls=[r for r in decoder if 'call_target' in r], variants={})
    assert result['original_decoder_cfg'] == dict(instructions=325,
        reachable_instructions=325, outside_successors=[])
    decoder_rows = {}
    for label, entry in experiment['variants'].items():
        images = {}
        for kind, descriptor in entry['files'].items():
            raw = gzip.decompress((HERE / descriptor['path']).read_bytes())
            assert len(raw) == descriptor['bytes'] and digest(raw) == descriptor['sha256']
            images[kind] = raw
        image, candidate = images['symbols'], images['candidate']
        assert section_data(image, '.text') == section_data(candidate, '.text')
        symbols = functions(image)
        matches = []
        for symbol in symbols:
            if 'Account$LT$T$GT$8try_from' in symbol['name']:
                rows = instructions(image, symbol['address'], symbol['bytes'])
                if any(r.get('lddw_value') == 0x9b4c7bdbbb92348f for r in rows):
                    matches.append((symbol, rows))
        assert len(matches) == 1
        account_symbol, account_rows = matches[0]
        decoders = [s for s in symbols if 'FeeConfig' in s['name']
                    and 'try_deserialize_unchecked' in s['name']]
        assert len(decoders) == 1
        decoder_symbol = decoders[0]
        assert any(r.get('call_target') == decoder_symbol['address'] for r in account_rows)
        rows = instructions(image, decoder_symbol['address'], decoder_symbol['bytes'])
        decoder_rows[label] = rows
        wrappers = []
        for symbol in symbols:
            if symbol['bytes'] != 200 or 'try_accounts' not in symbol['name']:
                continue
            wrapper_rows = instructions(image, symbol['address'], symbol['bytes'])
            calls = [r for r in wrapper_rows if 'call_target' in r]
            if calls and calls[-1]['call_target'] == account_symbol['address']:
                wrappers.append(dict(symbol=symbol, encoded_calls=calls,
                    equals_original_after_call_masking=(
                        b''.join(call_masked(r) for r in wrapper_rows) ==
                        b''.join(call_masked(r) for r in original_wrapper))))
        queries = []
        for symbol in symbols:
            if 'GetFeesWithQuoteMint' in symbol['name'] and 'try_accounts' in symbol['name']:
                query_rows = instructions(image, symbol['address'], symbol['bytes'])
                queries.append(dict(symbol=symbol,
                    first_encoded_call=next(r for r in query_rows if 'call_target' in r)))
        if label == 'consuming-checked':
            assert len(wrappers) == len(queries) == 1
            assert wrappers[0]['equals_original_after_call_masking']
            assert queries[0]['first_encoded_call']['call_target'] == wrappers[0]['symbol']['address']
        pointer_pattern = account_pointer_pattern_present(image, account_rows)
        result['variants'][label] = dict(account_symbol=account_symbol,
            incoming_wrappers=wrappers, query_parsers=queries,
            account_comparison=compare(original, account, image, account_rows),
            account_constant_pointer_mask_applicable=pointer_pattern,
            account_equal_after_calls_and_verified_constant_pointers=(
                pointer_pattern and account_comparison_bytes(image, account_rows) == original_account_normalized),
            decoder_symbol=decoder_symbol, decoder_cfg=cfg(rows),
            decoder_sequence_comparison=sequence_summary(decoder, rows),
            cursor_stores_before_first_call=cursor_stores_before_first_call(rows),
            decoder_calls=[dict(instruction=r,
                candidate_target_symbols=[s for s in symbols if s['address'] == r['call_target']])
                for r in rows if 'call_target' in r],
            equals_original_capture=candidate == original,
            equals_original_elf_extent=candidate == original[:original_layout['elf_extent']])
    assert result['variants']['consuming-checked']['account_equal_after_calls_and_verified_constant_pointers']
    differences = result['variants']['consuming-checked']['account_comparison']['differences']
    assert {d['kind'] for d in differences} == {
        'encoded_call_immediate', 'address_of_equal_32_byte_constant'}
    assert sum(d['kind'] == 'encoded_call_immediate' for d in differences) == 12
    assert sum(d['kind'] == 'address_of_equal_32_byte_constant' for d in differences) == 2
    baseline = decoder_rows['anchor-result-v144']
    result['compiler_noncall_decoder_differences'] = {}
    for label, rows in decoder_rows.items():
        if label.startswith('anchor-result-v') and label != 'anchor-result-v144':
            result['compiler_noncall_decoder_differences'][label] = dict(
                comparison=sequence_summary(baseline, rows),
                same_instruction_offsets=[r['offset'] for r in baseline] == [r['offset'] for r in rows],
                differing_rows=[dict(offset=a['offset'], v144_raw=a['raw'], candidate_raw=b['raw'])
                    for a, b in zip(baseline, rows) if call_masked(a) != call_masked(b)])
    return result


if __name__ == '__main__':
    print(json.dumps(analyze(), indent=2))

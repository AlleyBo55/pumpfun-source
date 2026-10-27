#!/usr/bin/env python3
"""Attribute the Fees query's first account parser using encoded calls and data.

No binary, source, selected checkpoint, or historical ledger is modified. Original
windows have inferred extents; encoded edges are not a runtime relocation proof.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from analyze import elf_layout  # noqa: E402

ORIGINAL = 'evidence/original/pump_fees/deployed.so'
CANDIDATE = 'repro/pump_fees/sharing-authorize-main-v144/main/candidate.so'
SYMBOLS = 'repro/pump_fees/sharing-authorize-main-v144/main/symbols.so'
IDL = 'evidence/upstream/pump_fees.json'
TYPES = 'programs/pump-fees/src/types.rs'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def records(image, start, size):
    text = next(s for s in elf_layout(image)['sections'] if s['name'] == '.text')
    assert start >= text['address'] and start + size <= text['address'] + text['size']
    rows, address = [], start
    while address < start + size:
        offset = text['offset'] + address - text['address']
        op, regs, displacement, immediate = struct.unpack_from('<BBhi', image, offset)
        width = 16 if op == 0x18 else 8
        assert address + width <= start + size
        row = dict(address=address, opcode=op, destination=regs & 15,
                   source=regs >> 4, displacement=displacement, immediate=immediate,
                   raw=image[offset:offset + width].hex())
        if op == 0x85 and regs >> 4 == 1:
            row['encoded_call_target'] = address + 8 + immediate * 8
        if op == 0x18:
            row['lddw_bytes'] = (image[offset + 4:offset + 8] +
                                 image[offset + 12:offset + 16]).hex()
        rows.append(row)
        address += width
    return rows


def function_symbols(image):
    header = struct.unpack_from('<HHIQQQIHHHHHH', image, 16)
    sections = [struct.unpack_from('<IIQQQQIIQQ', image, header[5] + n * header[10])
                for n in range(header[11])]
    result = {}
    for section in sections:
        if section[1] != 2:
            continue
        strings = sections[section[6]]
        names = image[strings[4]:strings[4] + strings[5]]
        for offset in range(section[4], section[4] + section[5], section[9]):
            name, info, _, _, address, size = struct.unpack_from('<IBBHQQ', image, offset)
            if info & 15 == 2:
                result.setdefault(address, []).append({
                    'name': names[name:].split(b'\0', 1)[0].decode(), 'size': size})
    return result


def masked_calls(rows):
    output = bytearray()
    for row in rows:
        raw = bytearray.fromhex(row['raw'])
        if 'encoded_call_target' in row:
            raw[4:8] = bytes(4)
        output.extend(raw)
    return bytes(output)


def analyze(root):
    paths = [ORIGINAL, CANDIDATE, SYMBOLS, IDL, TYPES]
    inputs = {p: (root / p).read_bytes() for p in paths}
    original, candidate = inputs[ORIGINAL], inputs[CANDIDATE]
    assert sha(original) == '4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
    assert sha(candidate) == '2387f8139a13918a5c9c523f140ecdd72db7243c8e2ed9cd7e1ff9d42ad6c8af'
    assert sha(inputs[TYPES]) == '8a18c23a6e1d097d40156864fc4b2d2959b3423845ec41bfb470fa340bbbadb8'
    # Bind the symbol-bearing ELF to the stripped artifact's actual .text.
    def text(raw):
        s = next(s for s in elf_layout(raw)['sections'] if s['name'] == '.text')
        return raw[s['offset']:s['offset'] + s['size']]
    assert text(candidate) == text(inputs[SYMBOLS])
    symbols = function_symbols(inputs[SYMBOLS])
    idl = json.loads(inputs[IDL])
    account = next(a for a in idl['accounts'] if a['name'] == 'FeeConfig')
    discriminator = bytes(account['discriminator']).hex()
    assert discriminator == '8f3492bbdb7b4c9b'
    assert discriminator == hashlib.sha256(b'account:FeeConfig').digest()[:8].hex()
    queries = {}
    for label, image, start in [('original', original, 518976),
                                ('candidate', candidate, 127336)]:
        rows = records(image, start, 1784)
        queries[label] = [r for r in rows if 'encoded_call_target' in r]
    assert queries['original'][0]['encoded_call_target'] == 71256
    assert queries['candidate'][0]['encoded_call_target'] == 83552
    original_wrapper = records(original, 71256, 200)
    original_account = records(original, 36072, 1248)
    original_calls = [r for r in original_wrapper if 'encoded_call_target' in r]
    assert original_calls[-1]['encoded_call_target'] == 36072
    alternatives = []
    for wrapper, helper, size in [(83152, 35856, 1024), (83352, 30752, 1024),
                                   (83552, 26680, 1144)]:
        rows = records(candidate, wrapper, 200)
        calls = [r for r in rows if 'encoded_call_target' in r]
        assert calls[-1]['encoded_call_target'] == helper
        assert masked_calls(original_wrapper) == masked_calls(rows)
        assert any(s['size'] == size for s in symbols[helper])
        child = records(candidate, helper, size)
        alternatives.append(dict(wrapper_address=wrapper, helper_address=helper,
            helper_bytes=size, wrapper_symbols=symbols[wrapper],
            helper_symbols=symbols[helper], wrapper_calls=calls,
            wrapper_equal_after_masking_call_immediates=True,
            fee_config_discriminator_sites=[r['address'] for r in child
                                             if r.get('lddw_bytes') == discriminator],
            helper_calls=[dict(address=r['address'], target=r['encoded_call_target'],
                               candidate_target_symbols=symbols.get(r['encoded_call_target'], []))
                          for r in child if 'encoded_call_target' in r]))
    matching = [a for a in alternatives if a['fee_config_discriminator_sites']]
    assert len(matching) == 1 and matching[0]['wrapper_address'] == 83552
    original_sites = [r['address'] for r in original_account
                      if r.get('lddw_bytes') == discriminator]
    assert original_sites == [36696]
    by_address = {r['address']: r for r in original_account}
    current = {r['address']: r for r in records(candidate, 26680, 1144)}
    short_original, short_current = by_address[36672], current[27304]
    assert short_original['opcode'] == short_current['opcode'] == 0xa5
    assert short_original['immediate'] == short_current['immediate'] == 8
    short_target = lambda r: r['address'] + 8 + 8 * r['displacement']
    assert short_target(short_original) == 36936
    assert short_target(short_current) == 27344
    assert by_address[36712]['opcode'] == current[27336]['opcode'] == 0x1d
    assert by_address[36720]['lddw_bytes'] == by_address[36936]['lddw_bytes']
    assert by_address[36720]['lddw_bytes'] == current[27344]['lddw_bytes'] == '0300000000000080'
    for address in (36776, 36992):
        assert by_address[address]['encoded_call_target'] == 709368
    assert current[27400]['encoded_call_target'] == 694392
    return dict(scope='Static source attribution and guard-shape evidence only; no runtime or new source-build acceptance.',
        source_revision='58519a8e601ed17bc6d931483686a08ee656233d',
        input_sha256={p: sha(b) for p, b in inputs.items()},
        idl_account='FeeConfig', discriminator=discriminator,
        query_first_calls={k: v[0] for k, v in queries.items()},
        original_wrapper_calls=original_calls, alternatives=alternatives,
        original_discriminator_sites=original_sites,
        attributed_candidate_wrapper=83552, attributed_candidate_helper=26680,
        guard_shape=dict(original_short_branch=short_original,
            candidate_short_branch=short_current,
            original_error_entries=[36720, 36936], candidate_error_entries=[27344],
            original_conversion_calls=[36776, 36992], candidate_conversion_calls=[27400],
            original_helper_window_bytes=1248, candidate_helper_symbol_bytes=1144),
        limits=['Original names and historical function boundaries remain inferred.',
                'CALL targets are encoded relative targets, not a loader/runtime proof.',
                'Discriminator attribution does not establish full parser or decoder equivalence.',
                'Splitting the source guards is an uncompiled hypothesis, not a byte-identity result.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository-root', type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(analyze(args.repository_root), indent=2) + '\n', end='')


if __name__ == '__main__':
    main()

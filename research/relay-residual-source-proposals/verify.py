#!/usr/bin/env python3
"""Re-derive static source hypotheses; never build or execute a target program."""
from __future__ import annotations
import difflib
import gzip
import hashlib
import json
from pathlib import Path
import struct

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = 'repro/donation-relay/swap-receipt-coordinate-recovery'
LATEST = 'repro/donation-relay/token-extension-version-recovery'
ORIGINAL = 'evidence/dependencies/donation_relay/deployed.so'
SYMBOLS = LATEST + '/builds/anchor-v8/symbols.so.gz'
CANDIDATE = LATEST + '/builds/anchor-v8/candidate.so.gz'
WINDOWS = BASE + '/original-windows.json'
LEDGER = LATEST + '/builds/anchor-v8/match-ledger.json'
MINT_SOURCE = BASE + '/sources/recovered/src/mint_policy.rs'
SHARES_SOURCE = BASE + '/sources/recovered/src/settlement_handlers.rs'
EXPECTED_ORIGINAL = '367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563'
EXPECTED_SYMBOLS = 'f4691718db894fd7de8ae2cb7c58274428773893518527072f7fa61140071a11'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Elf:
    """Small independent ELF64 reader, with only the existing narrow SBF masks."""
    def __init__(self, data: bytes):
        self.data = data
        if len(data) < 64 or data[:6] != b'\x7fELF\x02\x01':
            raise ValueError('expected little-endian ELF64')
        header = struct.unpack_from('<16sHHIQQQIHHHHHH', data)
        section_offset, entry_size, count = header[6], header[11], header[12]
        if entry_size != 64 or section_offset + count * entry_size > len(data):
            raise ValueError('invalid section table')
        self.sections = []
        for index in range(count):
            row = struct.unpack_from('<IIQQQQIIQQ', data, section_offset + index * 64)
            _, kind, flags, address, offset, size, link, _, _, stride = row
            if kind != 8 and offset + size > len(data):
                raise ValueError('section outside file')
            self.sections.append(dict(kind=kind, flags=flags, address=address,
                                      offset=offset, size=size, link=link, stride=stride))
        self.symbols = []
        self.relocations = {}
        for section in self.sections:
            if section['kind'] == 2:
                strings = self.section_data(self.sections[section['link']])
                if section['size'] % 24 or section['stride'] != 24:
                    raise ValueError('invalid symbol table')
                for position in range(section['offset'], section['offset'] + section['size'], 24):
                    name, info, _, _, address, size = struct.unpack_from('<IBBHQQ', data, position)
                    end = strings.find(b'\0', name)
                    if name >= len(strings) or end == -1:
                        raise ValueError('invalid symbol name')
                    if info & 15 == 2 and size:
                        self.symbols.append(dict(name=strings[name:end].decode(), start=address, bytes=size))
            if section['kind'] == 9:
                if section['size'] % 16 or section['stride'] != 16:
                    raise ValueError('invalid relocation table')
                for position in range(section['offset'], section['offset'] + section['size'], 16):
                    address, info = struct.unpack_from('<QQ', data, position)
                    self.relocations[address] = info & 0xffffffff

    def section_data(self, section: dict) -> bytes:
        return self.data[section['offset']:section['offset'] + section['size']]

    def at(self, address: int, size: int) -> bytes:
        if size < 0:
            raise ValueError('negative size')
        for section in self.sections:
            if (section['kind'] != 8 and section['flags'] & 2
                    and section['address'] <= address
                    and address + size <= section['address'] + section['size']):
                offset = section['offset'] + address - section['address']
                return self.data[offset:offset + size]
        raise ValueError('address outside allocated file-backed section')

    def body(self, address: int, size: int) -> dict:
        raw = self.at(address, size)
        normalized, masks, calls = normalize(raw, address, self.relocations)
        return dict(start=address, bytes=size, raw_sha256=digest(raw),
                    raw_hex=raw.hex(), normalized_sha256=digest(normalized),
                    masks=masks, calls=calls)


def normalize(raw: bytes, address: int, relocations: dict[int, int]):
    if len(raw) % 8:
        raise ValueError('partial SBF instruction')
    normalized = bytearray(raw)
    masks, calls = [], []
    offset = 0
    while offset < len(raw):
        opcode, registers, _, immediate = struct.unpack_from('<BBhi', raw, offset)
        pc = address + offset
        if opcode == 0x85 and registers >> 4 == 1 and relocations.get(pc) != 10:
            normalized[offset + 4:offset + 8] = b'\0' * 4
            masks.append(dict(offset=offset + 4, bytes=4, reason='direct-call displacement'))
            calls.append(dict(offset=offset, target=pc + 8 + immediate * 8))
        if opcode == 0x18:
            if offset + 16 > len(raw):
                raise ValueError('partial LDDW instruction')
            if pc in relocations:
                for start in (offset + 4, offset + 12):
                    normalized[start:start + 4] = b'\0' * 4
                    masks.append(dict(offset=start, bytes=4, reason='relocated LDDW word'))
            offset += 16
        else:
            offset += 8
    return bytes(normalized), masks, calls


def normalized_differences(original: dict, candidate: dict) -> list[dict]:
    a, b = bytearray.fromhex(original['raw_hex']), bytearray.fromhex(candidate['raw_hex'])
    if len(a) != len(b):
        raise ValueError('different body lengths')
    for body, report in ((a, original), (b, candidate)):
        for mask in report['masks']:
            body[mask['offset']:mask['offset'] + mask['bytes']] = b'\0' * mask['bytes']
    return [dict(offset=i, original=a[i:i + 8].hex(), candidate=b[i:i + 8].hex())
            for i in range(0, len(a), 8) if a[i:i + 8] != b[i:i + 8]]


def proposal(source_path: str, before: str, after: str) -> dict:
    source = (ROOT / source_path).read_text()
    if source.count(before) != 1:
        raise ValueError('source anchor is not unique')
    proposed = source.replace(before, after)
    filename = source_path.split('/sources/recovered/', 1)[1]
    patch = ''.join(difflib.unified_diff(source.splitlines(True), proposed.splitlines(True),
                                       fromfile='a/' + filename, tofile='b/' + filename, n=0))
    return dict(source_path=source_path, source_sha256=digest(source.encode()),
                proposed_sha256=digest(proposed.encode()), patch=patch)


def derive() -> dict:
    original = Elf((ROOT / ORIGINAL).read_bytes())
    candidate = Elf(gzip.decompress((ROOT / SYMBOLS).read_bytes()))
    assert digest(original.data) == EXPECTED_ORIGINAL
    assert digest(candidate.data) == EXPECTED_SYMBOLS
    stripped = gzip.decompress((ROOT / CANDIDATE).read_bytes())
    assert digest(stripped) == '4256c58be30adeda38bfa1a47102179a6e45666a63876cc568828fdf72daddef'
    assert stripped != original.data
    windows = json.loads((ROOT / WINDOWS).read_text())
    ledger = json.loads((ROOT / LEDGER).read_text())
    symbols = {}
    for symbol in candidate.symbols:
        symbols.setdefault((symbol['start'], symbol['bytes']), []).append(symbol['name'])
    functions = [dict(start=a, bytes=n, names=sorted(names)) for (a, n), names in sorted(symbols.items())]

    def original_body(ordinal):
        window = windows[ordinal]
        assert window['ordinal'] == ordinal
        body = original.body(window['start'], window['bytes'])
        assert body['raw_sha256'] == window['sha256']
        return dict(ordinal=ordinal, **body)

    def candidate_body(index):
        function = functions[index]
        return dict(index=index, names=function['names'], **candidate.body(function['start'], function['bytes']))

    mint_original, mint_candidate = original_body(106), candidate_body(89)
    assert any('mint_policy15typed_mint_safe' in name for name in mint_candidate['names'])
    mint_differences = normalized_differences(mint_original, mint_candidate)
    assert mint_differences == [
        dict(offset=1360, original='4f21000000000000', candidate='4f12000000000000'),
        dict(offset=1368, original='57010000ffff0000', candidate='57020000ffff0000'),
        dict(offset=1376, original='1501040000000000', candidate='1502040000000000'),
    ]
    values_original, values_candidate = original_body(4), candidate_body(3)
    assert any('anchor_lang5error5Error11with_values' in name for name in values_candidate['names'])
    values_differences = normalized_differences(values_original, values_candidate)
    assert len(values_differences) == 8
    callers = []
    for window in windows:
        body = original.body(window['start'], window['bytes'])
        for call in body['calls']:
            if call['target'] == values_original['start']:
                begin = max(0, call['offset'] - 48)
                callers.append(dict(ordinal=window['ordinal'], body_sha256=body['raw_sha256'],
                                    start=window['start'], call_offset=call['offset'],
                                    target=call['target'], context_offset=begin,
                                    context_hex=original.at(window['start'] + begin, call['offset'] - begin + 8).hex()))
    assert [(x['ordinal'], x['call_offset']) for x in callers] == [(97, 2416), (98, 3296), (100, 1344)]
    assert not ledger[4]['normalized_candidate_indices']
    assert not ledger[106]['normalized_candidate_indices']
    assert sum(bool(row['normalized_candidate_indices']) for row in ledger) == 470
    assert sum(bool(row['raw_candidate_indices']) for row in ledger) == 88
    mint_proposal = proposal(MINT_SOURCE,
        'u16::from(fee.older_transfer_fee.transfer_fee_basis_points) | u16::from(fee.newer_transfer_fee.transfer_fee_basis_points)',
        'u16::from(fee.newer_transfer_fee.transfer_fee_basis_points) | u16::from(fee.older_transfer_fee.transfer_fee_basis_points)')
    shares_proposal = proposal(SHARES_SOURCE,
        'BpsSumDoesNotEqualTenThousand,204));',
        'BpsSumDoesNotEqualTenThousand,204).with_values((sum, 10_000u32)));')
    return dict(schema_version=1, status='static source proposals; unbuilt and unexecuted',
                baseline_normalized_windows=470, baseline_unmatched_windows=22,
                whole_binary_identity=False,
                full_file=dict(original_bytes=len(original.data), candidate_bytes=len(stripped),
                               candidate_sha256=digest(stripped), equal=original.data == stripped),
                inputs={name:digest((ROOT / name).read_bytes()) for name in
                        (ORIGINAL, SYMBOLS, CANDIDATE, WINDOWS, LEDGER, MINT_SOURCE, SHARES_SOURCE)},
                mint=dict(original=mint_original, candidate=mint_candidate,
                          normalized_differences=mint_differences, proposal=mint_proposal),
                compared_values=dict(original=values_original, candidate_u64_control=values_candidate,
                                     normalized_differences=values_differences, original_callers=callers,
                                     proposal=shares_proposal))


def verify() -> None:
    evidence = derive()
    assert evidence == json.loads((PACKAGE / 'evidence.json').read_text()), 'static evidence changed'
    for name, key in (('mint-or-order.patch', 'mint'), ('shares-compared-values.patch', 'compared_values')):
        assert (PACKAGE / 'proposals' / name).read_text() == evidence[key]['proposal']['patch']
    print(json.dumps(dict(verified=True, proposals=2, compiled_trials=0,
                          baseline_normalized_windows=470, whole_binary_identity=False)))


if __name__ == '__main__':
    verify()

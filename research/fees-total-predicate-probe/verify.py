"""Verify an isolated compiler probe; no full-candidate match is claimed."""
from pathlib import Path
import hashlib
import importlib.util
import json
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda data: hashlib.sha256(data).hexdigest()

def compare(original, probe):
    assert len(original) == len(probe) == 192
    # Relocated source-location pointer and out-of-object panic target only.
    left, right = bytearray(original), bytearray(probe)
    for start, end in [(172, 176), (180, 184), (188, 192)]:
        left[start:end] = right[start:end] = bytes(end-start)
    return left == right

def object_section(image, name):
    h = struct.unpack_from('<HHIQQQIHHHHHH', image, 16)
    assert h[0] == 1 and h[10] == 64  # ELF relocatable object
    rows = [struct.unpack_from('<IIQQQQIIQQ', image, h[5] + i*64) for i in range(h[11])]
    table = rows[h[12]]
    names = image[table[4]:table[4]+table[5]]
    row = next(r for r in rows if names[r[0]:].split(b'\0',1)[0].decode() == name)
    return image[row[4]:row[4]+row[5]]

def analyze():
    for name, digest in json.loads((HERE/'inputs.json').read_text()).items():
        assert sha((ROOT/name).read_bytes()) == digest, name
    spec = importlib.util.spec_from_file_location('predicate_elf', ROOT / 'research/fees-authority-body-origin/elf_helpers.py')
    elf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(elf)
    original = (ROOT / 'evidence/original/pump_fees/deployed.so').read_bytes()
    assert sha(original) == '4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
    body = elf.at_address(original, 700568, 192)
    obj = (HERE / 'fee_total.o').read_bytes()
    probe = object_section(obj, '.text.fee_total_is_valid')
    assert compare(body, probe)
    # Check that only actual address-bearing operands have been ignored.
    assert dict(elf.relocations(original))[700568 + 168] & 0xffffffff == 8
    rel = object_section(obj, '.rel.text.fee_total_is_valid')
    assert [(offset, info & 0xffffffff) for offset, info in struct.iter_unpack('<QQ', rel)] == [(168, 1), (184, 10)]
    calls = []
    # .text is one executable section; scan encoded local calls without inferring names.
    section = next(s for s in elf.elf_layout(original)['sections'] if s['name'] == '.text')
    for row in elf.instructions(original, section['address'], section['size']):
        if row.get('call_target') == 700568:
            calls.append(section['address'] + row['offset'])
    assert calls == [260600, 261224, 264056, 268216]
    mutations = []
    for offset in [8, 64, 148]:  # field load, overflow branch, threshold
        changed = bytearray(probe)
        changed[offset] ^= 1
        assert not compare(body, changed)
        mutations.append(offset)
    return dict(original_sha256=sha(original), original_start=700568, body_bytes=192,
                object_sha256=sha(obj), source_sha256=sha((HERE/'fee_total.rs').read_bytes()),
                address_operand_normalized_equal=True, raw_equal=body == probe,
                excluded_byte_ranges=[[172,176],[180,184],[188,192]], incoming_call_addresses=calls,
                mutation_tests=mutations, full_candidate_coverage_added=0,
                scope='Isolated Darwin v1.44 compiler object; panic target/data and full Fees integration unverified.')

if __name__ == '__main__':
    manifest = json.loads((HERE/'manifest.json').read_text())
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name != 'manifest.json' and '__pycache__' not in p.parts}
    assert actual == set(manifest)
    for name, digest in manifest.items():
        assert sha((HERE/name).read_bytes()) == digest, name
    assert analyze() == json.loads((HERE/'report.json').read_text())
    print('PASS: isolated 192-byte predicate; four original callers; three negative mutations; zero full-candidate coverage added')

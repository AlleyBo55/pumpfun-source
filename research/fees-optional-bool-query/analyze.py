"""Recompute the optional-boolean wrapper match and error-path bindings."""
import gzip
import importlib.util
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('optional_windows', HERE / 'window_map.py')
wm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wm)


def analyze():
    experiment = json.loads((HERE / 'experiment.json').read_text())
    original = (ROOT / 'evidence/original/pump_fees/deployed.so').read_bytes()
    assert wm.m.digest(original) == '4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
    original_windows = wm.windows(original)
    original_by_address = {row['address']: row for row in original_windows}
    assert original_by_address[636160]['bytes'] == 1560
    result = dict(original_sha256=wm.m.digest(original), original_windows=len(original_windows), variants={})
    retained = {}
    for label, variant in experiment['variants'].items():
        images = {}
        for kind, descriptor in variant['files'].items():
            raw = gzip.decompress((HERE / descriptor['path']).read_bytes())
            assert len(raw) == descriptor['bytes'] and wm.m.digest(raw) == descriptor['sha256']
            images[kind] = raw
        candidate = images['symbols']
        assert wm.m.section_data(candidate, '.text') == wm.m.section_data(images['candidate'], '.text')
        windows = wm.windows(candidate)
        assert {row['address']: row['bytes'] for row in windows} == {
            row['address']: row['bytes'] for row in wm.m.functions(candidate)}
        comparison = wm.compare(original_windows, windows)
        comparison.update(candidate_sha256=wm.m.digest(images['candidate']), candidate_windows=len(windows),
            inferred_boundaries_equal_symbols=True,
            unique_raw_pairs=sum(pair['original']['raw_sha256'] == pair['candidate']['raw_sha256']
                                 for pair in comparison['unique_pairs']),
            equals_original_capture=images['candidate'] == original,
            equals_original_elf_extent=images['candidate'] == original[:wm.m.elf_layout(original)['elf_extent']])
        result['variants'][label] = comparison
        retained[label] = images
    before = {row['original']['address'] for row in result['variants']['control']['unique_pairs']}
    after = {row['original']['address'] for row in result['variants']['optional']['unique_pairs']}
    result['delta'] = dict(added_original_windows=sorted(after - before), lost_original_windows=sorted(before - after))
    assert after - before == {636160} and not before - after
    paired = {row['original']['address']: row['candidate']
              for row in result['variants']['optional']['unique_pairs']}
    candidate = retained['optional']['symbols']
    address = paired[636160]['address']
    a = {row['offset']: row for row in wm.m.instructions(original, 636160, 1560)}
    b = {row['offset']: row for row in wm.m.instructions(candidate, address, 1560)}
    kinds = []
    for offset, value in [(288, 20), (1144, 21)]:
        for rows in (a, b):
            assert rows[offset]['opcode'] == 0xb7 and rows[offset]['destination'] == 1
            assert rows[offset]['immediate'] == value
        kinds.append(dict(offset=offset, encoded_kind=value, original=a[offset], candidate=b[offset]))
    edges = []
    for offset, target in [(504, 518976), (1208, 700760)]:
        assert a[offset]['call_target'] == target
        assert b[offset]['call_target'] == paired[target]['address']
        edges.append(dict(offset=offset, original_target=target, candidate_target=b[offset]['call_target']))
    format_records = []
    for offset in (120, 976):
        strings = []
        for image, start, rows in [(original, 636160, a), (candidate, address, b)]:
            pointer = rows[offset]['lddw_value']
            relocations = dict(wm.m.relocations(image))
            assert relocations[start + offset] & 0xffffffff == 8
            assert relocations[pointer] & 0xffffffff == 8
            raw_pointer, length = struct.unpack('<QQ', wm.m.at_address(image, pointer, 16))
            assert raw_pointer & 0xffffffff == 0 and length == 29
            text = wm.m.at_address(image, raw_pointer >> 32, length)
            assert text == b'Invalid bool representation: '
            strings.append(dict(pieces_pointer=pointer, string_pointer=raw_pointer >> 32,
                                bytes=length, text=text.decode()))
        format_records.append(dict(offset=offset, original=strings[0], candidate=strings[1]))
    callbacks = []
    candidate_by_address = {row['address']: row for row in wm.windows(candidate)}
    for offset in (168, 1024):
        left, right = a[offset]['lddw_value'], b[offset]['lddw_value']
        assert original_by_address[left]['signature'] == candidate_by_address[right]['signature']
        callbacks.append(dict(offset=offset, original=original_by_address[left], candidate=candidate_by_address[right]))
    result.update(optional_wrapper=paired[636160], encoded_error_kinds=kinds,
                  encoded_callee_bindings=edges, format_records=format_records, format_callbacks=callbacks)
    return result


if __name__ == '__main__':
    print(json.dumps(analyze(), indent=2))

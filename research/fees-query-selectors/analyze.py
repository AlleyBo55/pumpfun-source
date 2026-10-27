"""Verify three complete query-window recoveries and their direct data/call bindings."""
import gzip
import importlib.util
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('query_windows', HERE / 'window_map.py')
wm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wm)


def analyze():
    experiment = json.loads((HERE / 'experiment.json').read_text())
    original = (ROOT / 'evidence/original/pump_fees/deployed.so').read_bytes()
    assert wm.m.digest(original) == '4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
    original_windows = wm.windows(original)
    original_by_address = {row['address']: row for row in original_windows}
    targets = {259912: 656, 637720: 1384, 700760: 376}
    for address, size in targets.items():
        assert original_by_address[address]['bytes'] == size
    result = dict(original_sha256=wm.m.digest(original), original_windows=len(original_windows), variants={})
    images_by_label = {}
    for label, variant in experiment['variants'].items():
        images = {}
        for name, descriptor in variant['files'].items():
            image = gzip.decompress((HERE / descriptor['path']).read_bytes())
            assert len(image) == descriptor['bytes'] and wm.m.digest(image) == descriptor['sha256']
            images[name] = image
        candidate = images['symbols']
        assert wm.m.section_data(candidate, '.text') == wm.m.section_data(images['candidate'], '.text')
        windows = wm.windows(candidate)
        assert {row['address']: row['bytes'] for row in windows} == {
            row['address']: row['bytes'] for row in wm.m.functions(candidate)}
        comparison = wm.compare(original_windows, windows)
        comparison.update(candidate_sha256=wm.m.digest(images['candidate']), candidate_windows=len(windows),
            inferred_boundaries_equal_symbols=True,
            unique_raw_pairs=sum(row['original']['raw_sha256'] == row['candidate']['raw_sha256']
                                 for row in comparison['unique_pairs']),
            equals_original_capture=images['candidate'] == original,
            equals_original_elf_extent=images['candidate'] == original[:wm.m.elf_layout(original)['elf_extent']])
        result['variants'][label] = comparison
        images_by_label[label] = images
    before = {row['original']['address'] for row in result['variants']['control']['unique_pairs']}
    after = {row['original']['address'] for row in result['variants']['selectors']['unique_pairs']}
    result['delta'] = dict(added_original_windows=sorted(after - before), lost_original_windows=sorted(before - after))
    assert after - before == set(targets) and not before - after
    paired = {row['original']['address']: row['candidate']
              for row in result['variants']['selectors']['unique_pairs']}
    candidate = images_by_label['selectors']['symbols']
    edges = []
    for caller, size, offset, target in [(637720, 1384, 1048, 259912), (259912, 656, 552, 700760),
                                       *[(259912, 656, offset, 796464) for offset in (176, 240, 304, 368)]]:
        a = next(row for row in wm.m.instructions(original, caller, size) if row['offset'] == offset)
        b = next(row for row in wm.m.instructions(candidate, paired[caller]['address'], size)
                 if row['offset'] == offset)
        assert a['call_target'] == target and b['call_target'] == paired[target]['address']
        edges.append(dict(original_caller=caller, candidate_caller=paired[caller]['address'],
                          original_instruction=a, candidate_instruction=b,
                          original_target=target, candidate_target=paired[target]['address']))
    source = (HERE / experiment['variants']['selectors']['source_overrides']['programs/pump-fees/src/lib.rs']).read_text()
    data_records = []
    original_relocations = dict(wm.m.relocations(original))
    candidate_relocations = dict(wm.m.relocations(candidate))
    for offset, name in [(216, 'WRAPPED_SOL'), (280, 'OTHER_NORMAL_QUOTE'), (336, 'USDC')]:
        constant = bytes(json.loads(re.search(r'pub const ' + name + r':[^=]+=(\s*\[[^\]]+\]);', source)[1]))
        assert len(constant) == 32
        a = next(row for row in wm.m.instructions(original, 259912, 656) if row['offset'] == offset)
        b = next(row for row in wm.m.instructions(candidate, paired[259912]['address'], 656)
                 if row['offset'] == offset)
        assert original_relocations[259912 + offset] & 0xffffffff == 8
        assert candidate_relocations[paired[259912]['address'] + offset] & 0xffffffff == 8
        assert wm.m.at_address(original, a['lddw_value'], 32) == constant
        assert wm.m.at_address(candidate, b['lddw_value'], 32) == constant
        data_records.append(dict(name=name, offset=offset, bytes=32, value_hex=constant.hex(),
                                 original_pointer=a['lddw_value'], candidate_pointer=b['lddw_value']))
    result['encoded_callee_bindings'] = edges
    result['quote_constant_bindings'] = data_records
    return result


if __name__ == '__main__':
    print(json.dumps(analyze(), indent=2))

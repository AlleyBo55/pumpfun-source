"""Bind complete sharing wrapper/drop windows to their exact source changes."""
import gzip
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('sharing_ownership_windows', HERE / 'window_map.py')
wm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wm)


def source(e, label, name):
    override = e['variants'][label]['source_overrides'].get(name)
    return (HERE / override if override else ROOT / name).read_bytes().decode('utf-8')


def analyze():
    e = json.loads((HERE / 'experiment.json').read_text())
    original = (ROOT / 'evidence/original/pump_fees/deployed.so').read_bytes()
    assert wm.m.digest(original) == '4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
    original_windows = wm.windows(original)
    originals = {r['address']: r for r in original_windows}
    result = dict(original_sha256=wm.m.digest(original), variants={})
    retained, candidates = {}, {}
    for label, variant in e['variants'].items():
        images = {}
        for kind, descriptor in variant['files'].items():
            image = gzip.decompress((HERE / descriptor['path']).read_bytes())
            assert len(image) == descriptor['bytes'] and wm.m.digest(image) == descriptor['sha256']
            images[kind] = image
        candidate = images['symbols']
        assert wm.m.section_data(candidate, '.text') == wm.m.section_data(images['candidate'], '.text')
        windows = wm.windows(candidate)
        by_address = {r['address']: r for r in windows}
        symbols = wm.m.functions(candidate)
        assert set(by_address) == {r['address'] for r in symbols}
        assert all(by_address[r['address']]['bytes'] == r['bytes'] for r in symbols)
        comparison = wm.compare(original_windows, windows)
        comparison.update(candidate_windows=len(windows), candidate_sha256=wm.m.digest(images['candidate']),
            unique_raw_pairs=sum(r['original']['raw_sha256'] == r['candidate']['raw_sha256'] for r in comparison['unique_pairs']),
            equals_original_capture=images['candidate'] == original,
            equals_original_elf_extent=images['candidate'] == original[:wm.m.elf_layout(original)['elf_extent']])
        result['variants'][label] = comparison
        retained[label], candidates[label] = images, by_address
    before = {r['original']['address'] for r in result['variants']['control']['unique_pairs']}
    after = {r['original']['address'] for r in result['variants']['origins']['unique_pairs']}
    result['delta'] = dict(added_original_windows=sorted(after - before), lost_original_windows=sorted(before - after))
    assert after - before == {r[0] for r in e['targets']} and not before - after
    name = 'programs/pump-fees/src/sharing_update.rs'
    previous = source(e, 'control', name)
    start = previous.index('pub struct ' + e['handler']['struct'] + "<'info>")
    end = previous.index('\n}', start) + 2
    block = previous[start:end]
    changed = block.replace("UncheckedAccount<'info>", "AccountInfo<'info>")
    if e['kind'] == 'legacy':
        assert block.count('UncheckedAccount') == 6
        changed = changed.replace("Box<Account<'info,pump_global::Global>>", "Account<'info,pump_global::Global>")
    else:
        assert block.count('UncheckedAccount') == 7
        changed = changed.replace("pub event_authority:AccountInfo<'info>", "pub event_authority:UncheckedAccount<'info>")
        changed = changed.replace("pub sharing_config:Account<'info,SharingConfig>", "pub sharing_config:Box<Account<'info,SharingConfig>>")
        changed = changed.replace("pub bonding_curve:Account<'info,BondingCurve>", "pub bonding_curve:Box<Account<'info,BondingCurve>>")
    assert changed.count("AccountInfo<'info>") == 6
    assert source(e, 'origins', name) == previous[:start] + changed + previous[end:]
    assert set(e['variants']['control']['input_sha256']) == set(e['variants']['origins']['input_sha256'])
    for item in e['variants']['control']['input_sha256']:
        if item != name:
            assert source(e, 'control', item) == source(e, 'origins', item)
    pairs = {r['original']['address']: r['candidate'] for r in result['variants']['origins']['unique_pairs']}
    h = e['handler']
    drop = pairs[h['original_drop']]
    assert originals[h['original_drop']]['bytes'] == drop['bytes'] == 776
    assert originals[h['original_drop']]['raw_sha256'] == drop['raw_sha256']
    assert not drop['annotations']
    image = retained['origins']['symbols']
    for raw, address in [(original, h['original_drop']), (image, drop['address'])]:
        rows = {r['offset']: r for r in wm.m.instructions(raw, address, 776)}
        assert not any('call_target' in r for r in rows.values())
        for index in range(6):
            for offset, register, inner in [(0, 2, 16), (8, 3, 8)]:
                r = rows[index * 128 + offset]
                destination = 1 if index == 5 and offset == 8 else register
                assert (r['opcode'], r['destination'], r['source'], r['displacement']) == (0x79, destination, 1, h['first_owned_offset'] + index * 48 + inner)
    symbol = '__global' + str(len(h['method'])) + h['method'] + '17h'
    control = next(r for r in candidates['control'].values() if symbol in (r['name'] or ''))
    original_memcpy = {r['offset']: r for r in wm.m.instructions(original, h['original_global'], h['global_bytes'])}[424]['call_target']
    wrappers = [('original', original, h['original_global'], h['global_bytes'], h['copied_bytes']),
                ('control', retained['control']['symbols'], control['address'], control['bytes'], h['previous_copied_bytes']),
                ('origins', image, pairs[h['original_global']]['address'], h['global_bytes'], h['copied_bytes'])]
    bindings = []
    for label, raw, address, size, count in wrappers:
        rows = {r['offset']: r for r in wm.m.instructions(raw, address, size)}
        assert wm.m.at_address(raw, rows[40]['lddw_value'], len(h['log'])) == h['log'].encode()
        assert (rows[416]['opcode'], rows[416]['destination'], rows[416]['immediate']) == (0xb7, 3, count)
        record = dict(label=label, address=address, copied_bytes=count, log_pointer=rows[40]['lddw_value'])
        if label != 'control':
            target = h['original_drop'] if label == 'original' else drop['address']
            assert all(rows[o]['call_target'] == target for o in h['cleanup_call_offsets'])
            memcpy = rows[424]['call_target']
            window = originals[memcpy] if label == 'original' else candidates['origins'][memcpy]
            assert window['raw_sha256'] == originals[original_memcpy]['raw_sha256']
            record.update(cleanup_target=target, cleanup_call_offsets=h['cleanup_call_offsets'], raw_equal_memcpy_target=memcpy)
        bindings.append(record)
    result['ownership_bindings'] = dict(handler=h['struct'], owned_account_handles=6,
        raw_equal_drop=dict(original=h['original_drop'], candidate=drop['address'], bytes=776), dispatch=bindings,
        only_account_field_types_changed=True, business_code_unchanged=True)
    return result

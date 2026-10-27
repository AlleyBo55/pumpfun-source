#!/usr/bin/env python3
"""Recompute the post-burn-recovery inventory; never changes selected checkpoints."""
import argparse
import collections
import csv
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = {}
REVISION = 'e2d7855848a3411d665deb915077ef20672e7cdd'
FEES = 'research/fees-unchecked-prefix-recovery'
RELAY = 'repro/donation-relay/burn-mint-ownership-recovery'


def read(name):
    raw = (ROOT / name).read_bytes()
    INPUTS[name] = hashlib.sha256(raw).hexdigest()
    return raw


def load(name):
    raw = read(name)
    return json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)


def module(name, path):
    read(path)
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def name(symbol):
    """Display-only decoding, never used to choose a match."""
    s = symbol.removeprefix('_')
    if not s.startswith('ZN'):
        return symbol
    s, parts = s[2:], []
    while s and s[0].isdigit():
        n = 0
        while n < len(s) and s[n].isdigit():
            n += 1
        length, s = int(s[:n]), s[n:]
        parts.append(s[:length])
        s = s[length:]
    if parts and parts[-1].startswith('h') and len(parts[-1]) == 17:
        parts.pop()
    result = '::'.join(parts) or symbol
    for old, new in {'$LT$': '<', '$GT$': '>', '$u20$': ' ', '$RF$': '&', '$C$': ',', '$LP$': '(', '$RP$': ')', '$u27$': "'", '..': '::'}.items():
        result = result.replace(old, new)
    return result


def row(program, original, raw, normalized, source):
    return dict(program=program, variant='research', original_start=original['address'],
                original_end=original['address'] + original['bytes'], bytes=original['bytes'],
                disposition='raw_body_equal' if raw else 'normalized_body_only' if normalized else 'no_complete_body_match',
                candidate_names=sorted({name(c['name']) for c in raw + normalized if c.get('name')}),
                raw_candidate_names=sorted({name(c['name']) for c in raw if c.get('name')}),
                raw_candidate_starts=sorted({c['address'] for c in raw}),
                normalized_candidate_starts=sorted({c['address'] for c in normalized}),
                source_status='unique_structural_pair' if len(normalized) == 1 and original.get('unique') else 'ambiguous_or_unattributed',
                source_ledger=source)


def generate():
    INPUTS.clear()
    read(str(Path(__file__).relative_to(ROOT)))
    read('scripts/analyze.py')
    baseline = load('repro/reconstruction-audit-2026-10-26/audit.json')
    selected = {(r['program'], r['original_start']): r for r in baseline['windows'] if r['variant'] == 'selected'}
    reader = csv.DictReader(io.StringIO(read('repro/reconstruction-audit-2026-10-26/functions.tsv').decode()), delimiter='\t')
    rows = []
    for r in reader:
        if r['variant'] != 'selected':
            continue
        for key in ('original_start', 'original_end', 'bytes'):
            r[key] = int(r[key])
        for key in ('candidate_names', 'raw_candidate_starts', 'normalized_candidate_starts'):
            r[key] = json.loads(r[key])
        r['raw_candidate_names'] = selected[r['program'], r['original_start']]['raw_candidate_names']
        rows.append(r)
    assert len(rows) == 3338

    wm = module('status_fee_windows', FEES + '/window_map.py')
    read(FEES + '/elf_helpers.py')
    original = read('evidence/original/pump_fees/deployed.so')
    symbols = gzip.decompress(read(FEES + '/artifacts/origins-symbols.so.gz'))
    candidate = gzip.decompress(read(FEES + '/artifacts/origins-candidate.so.gz'))
    ow, cw = wm.windows(original), wm.windows(symbols)
    comparison = wm.compare(ow, cw)
    saved = load(FEES + '/analysis.json.gz')['variants']['origins']
    assert all(comparison[k] == saved[k] for k in comparison)
    assert len(comparison['unique_pairs']) == 395 and len(comparison['unmatched_original']) == 43
    raw_index, normalized_index = collections.defaultdict(list), collections.defaultdict(list)
    for c in cw:
        raw_index[c['raw_sha256']].append(c)
        normalized_index[c['signature']].append(c)
    unique = {r['original']['address'] for r in comparison['unique_pairs']}
    for o in ow:
        o['unique'] = o['address'] in unique
        rows.append(row('pump_fees_research', o, raw_index[o['raw_sha256']], normalized_index[o['signature']], FEES + '/analysis.json.gz'))
    fees_meta = dict(candidate_sha256=hashlib.sha256(candidate).hexdigest(), candidate_bytes=len(candidate),
                     whole_capture_equal=candidate == original,
                     raw_file_equals_original_elf_extent=candidate == original[:wm.m.elf_layout(original)['elf_extent']],
                     unique_structural_pairs=395, ambiguous_original_windows=sum(len(g['original']) for g in comparison['ambiguous']),
                     candidate_windows=len(cw))

    attribution_path = 'research/fees-refreshed-call-attribution'
    attribution_module = module('status_fee_attribution', attribution_path + '/attribute.py')
    for filename in ['window_map.py', 'elf_helpers.py', 'input-provenance.json']:
        read(attribution_path + '/' + filename)
    experiment = load(FEES + '/experiment.json')
    provenance = dict(files={key: dict(value, path='../' + FEES.split('/')[-1] + '/' + value['path'])
                            for key, value in experiment['variants']['origins']['files'].items()})
    attribution = attribution_module.analyze(provenance)
    assert attribution['candidate_sha256'] == fees_meta['candidate_sha256']
    attributed = {pair['original']['address']: pair['candidate']['address'] for pair in attribution['newly_attributed_pairs']}
    assert len(attributed) == 65 and attribution['graph_attributed_pairs'] == 460
    for record in rows:
        record['call_attributed_candidate_starts'] = []
        if record['program'] == 'pump_fees_research' and record['original_start'] in attributed:
            address = attributed[record['original_start']]
            assert address in record['normalized_candidate_starts']
            record['call_attributed_candidate_starts'] = [address]
            record['source_status'] = 'call_attributed_duplicate_pair'
    fees_meta.update(additional_call_attributed_pairs=65, total_attributed_pairs=460,
                     remaining_unattributed_duplicate_windows=82)

    parser = module('status_relay_windows', 'repro/donation-relay/swap-receipt-coordinate-recovery/analyze.py')
    relay_artifacts = load(RELAY + '/metadata.json')['variants']['recovered']['artifacts']
    with tempfile.TemporaryDirectory() as temp:
        d = Path(temp)
        for output, path, compressed in [
            ('original.so', 'evidence/dependencies/donation_relay/deployed.so', False),
            ('candidate.so', RELAY + '/' + relay_artifacts['candidate']['path'], True),
            ('unstripped.so', RELAY + '/' + relay_artifacts['symbols']['path'], True),
            ('original-windows.json', 'repro/donation-relay/swap-receipt-coordinate-recovery/original-windows.json', False),
        ]:
            raw = read(path)
            (d / output).write_bytes(gzip.decompress(raw) if compressed else raw)
        analysis = parser.analyze(d)
    assert analysis['comparison-summary.json'] == load(RELAY + '/builds/recovered/comparison-summary.json')
    assert analysis['match-ledger.json'] == load(RELAY + '/builds/recovered/match-ledger.json')
    multiplicity = collections.Counter(o['normalized_sha256'] for o in analysis['original-function-ledger.json'])
    for o, r in zip(analysis['original-function-ledger.json'], analysis['match-ledger.json']):
        c = analysis['candidate-function-ledger.json']
        convert = lambda indices: [dict(address=c[i]['start'], name=n) for i in indices for n in (c[i]['names'] or [''])]
        rows.append(row('donation_relay_research', dict(address=o['start'], bytes=o['bytes'], unique=multiplicity[o['normalized_sha256']] == 1 and len(r['normalized_candidate_indices']) == 1),
                        convert(r['raw_candidate_indices']),
                        convert(r['normalized_candidate_indices']), RELAY + '/builds/recovered/match-ledger.json'))
    for record in rows:
        record.setdefault('call_attributed_candidate_starts', [])
    counts = {}
    for program in dict.fromkeys(r['program'] for r in rows):
        group = [r for r in rows if r['program'] == program]
        counts[program] = dict(windows=len(group), dispositions=dict(collections.Counter(r['disposition'] for r in group)),
                               body_bytes=sum(r['bytes'] for r in group),
                               unmatched_body_bytes=sum(r['bytes'] for r in group if r['disposition'] == 'no_complete_body_match'))
    assert len(rows) == 4415
    report = dict(snapshot=REVISION, selected_snapshot=baseline['audited_revision'], counts=counts,
                  fees=fees_meta, relay=analysis['comparison-summary.json'],
                  selected_handler_dispositions=dict(collections.Counter(r['selected_status'] for r in baseline['handlers'])),
                  input_sha256=dict(sorted(INPUTS.items())),
                  scope='Local body equality and separately scoped normalized windows; no semantic-perfection, transitive identity, selection promotion or effort-percentage claim.')
    fields = list(rows[0])
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fields, delimiter='\t', lineterminator='\n')
    writer.writeheader()
    for r in rows:
        writer.writerow({k: json.dumps(v) if isinstance(v, list) else v for k, v in r.items()})
    generated = {'fees-call-attribution.json': json.dumps(attribution, indent=2, sort_keys=True) + '\n', 'functions.tsv': output.getvalue(), 'status.json': json.dumps(report, indent=2, sort_keys=True) + '\n'}
    overview = ['# Current function-window inventory', '', f'Evidence snapshot: `{REVISION}`. Selected inputs retain their verified `{baseline["audited_revision"]}` checkpoint bindings. Research rows replace the older Fees/Relay research inventory; they do not replace selections.', '',
                '| Program / build | Windows | Exact local bytes | Normalized only | No complete match | Opaque |',
                '| --- | ---: | ---: | ---: | ---: | ---: |']
    for program, c in counts.items():
        d = c['dispositions']
        overview.append(f'| {program} | {c["windows"]} | {d.get("raw_body_equal", 0)} | {d.get("normalized_body_only", 0)} | {d.get("no_complete_body_match", 0)} | {d.get("opaque_unassessed", 0)} |')
    overview += ['', 'Fees has 380 body-unique pairs plus 62 additional call-attributed duplicate pairs (442 correspondences); 85 duplicate windows remain unattributed. These are not 62 additional body matches. Rows count inferred original windows, not unique source functions or effort. Raw matches may be duplicate/ambiguous and do not establish referenced data or transitive callees. The Fees matcher and Relay matcher use separately documented masks; do not add their counts into a source-completion score.', '',
                 '- [Comprehensive review: all handlers, unresolved text size and closure criteria](review.md)',
                 '- [Every window, symbol candidate, match address and evidence path](functions.tsv)',
                 '- [Every exact local body match](raw-body-matches.md)',
                 '- [Every unmatched or opaque window](remaining-windows.md)',
                 '- [All 150 public-handler dispositions](../reconstruction-audit-2026-10-26/handlers.md)',
                 '- [Counts, candidate hashes and input hashes](status.json)', '',
                 'Verify: `python3 -B repro/reconstruction-status-2026-10-26/refresh.py --check`. This re-reads binaries and checks the declared masks; it does not compile or execute target programs. Also run the parent audit and both owning research verifiers to check source bindings, retained runtime receipts and selected artifacts.']
    generated['README.md'] = '\n'.join(overview) + '\n'
    for filename, title, predicate in [
        ('raw-body-matches.md', 'Every exact local body match', lambda r: r['disposition'] == 'raw_body_equal'),
        ('remaining-windows.md', 'Every unmatched or opaque window', lambda r: r['disposition'] in ('no_complete_body_match', 'opaque_unassessed')),
    ]:
        lines = ['# ' + title, '', 'Snapshot and limitations: [inventory](README.md). Addresses are decimal virtual addresses. Candidate names are display labels, not authenticated original symbols. An empty label does not prove the source is absent.', '', '| Program / build | Original start | Bytes | Status | Candidate label(s) |', '| --- | ---: | ---: | --- | --- |']
        for r in rows:
            if predicate(r):
                names = r['raw_candidate_names'] if filename == 'raw-body-matches.md' else r['candidate_names']
                labels = '; '.join(names).replace('|', '\\|').replace('\n', ' ')
                lines.append(f'| {r["program"]} | {r["original_start"]} | {r["bytes"]} | {r["disposition"]} | {labels} |')
        generated[filename] = '\n'.join(lines) + '\n'
    return generated


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    for filename, value in generate().items():
        path = HERE / filename
        if args.check:
            assert path.read_text() == value, filename
        else:
            path.write_text(value)
    print('PASS: 4,415 window rows; 3,338 selected plus 585 Fees and 492 Relay research rows; complete byte-match and remaining-window inventories')


if __name__ == '__main__':
    main()

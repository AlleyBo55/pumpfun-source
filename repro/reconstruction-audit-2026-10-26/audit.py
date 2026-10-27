#!/usr/bin/env python3
"""Read-only audit of selected artifacts and explicitly separate research snapshots.

No compilation, target execution, source promotion, or binary normalization is
performed here. Existing normalized relations are retained as evidence, whereas
raw body equality and whole-file differences are recomputed from actual bytes.
"""
import argparse
import collections
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASELINE = '1463bd22fb7811825c5e7acf1cb963eb39ab68d9'
INPUTS = {}
LAYOUTS = {}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(name):
    data = (ROOT / name).read_bytes()
    INPUTS[name] = sha(data)
    return data


def load(name):
    data = read(name)
    return json.loads(gzip.decompress(data) if name.endswith('.gz') else data)


spec = importlib.util.spec_from_file_location('audit_elf_layout', ROOT / 'scripts/analyze.py')
elf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf)


def at(image, address, size):
    if id(image) not in LAYOUTS:
        LAYOUTS[id(image)] = (image, elf.elf_layout(image))
    for section in LAYOUTS[id(image)][1]['sections']:
        if section['type'] != 8 and section['address'] <= address and address + size <= section['address'] + section['size']:
            offset = section['offset'] + address - section['address']
            return image[offset:offset + size]
    raise ValueError(('window outside file-backed sections', address, size))


def byte_comparison(name, original_path, candidate_path, kind, compressed=False):
    original, candidate = read(original_path), read(candidate_path)
    if compressed:
        candidate = gzip.decompress(candidate)
    ol, cl = elf.elf_layout(original), elf.elf_layout(candidate)
    common = min(len(original), len(candidate))
    different = sum(a != b for a, b in zip(original, candidate))
    return dict(name=name, kind=kind, original_path=original_path,
                candidate_path=candidate_path, original_sha256=sha(original),
                candidate_sha256=sha(candidate), original_bytes=len(original),
                candidate_bytes=len(candidate), original_elf_extent=ol['elf_extent'],
                original_trailing_bytes=ol['trailing_bytes'],
                original_trailing_all_zero=ol['trailing_all_zero'],
                candidate_elf_extent=cl['elf_extent'], whole_capture_equal=original == candidate,
                raw_file_equals_original_elf_extent=candidate == original[:ol['elf_extent']],
                common_extent_bytes=common, common_extent_differing_bytes=different,
                excess_bytes=abs(len(original) - len(candidate)),
                differing_or_missing_positions=different + abs(len(original) - len(candidate)))


def simple_name(name):
    """Display-only legacy Rust symbol decoding; never used to choose matches."""
    s = name.removeprefix('_')
    if not s.startswith('ZN'):
        return name
    s, parts = s[2:], []
    while s and s[0].isdigit():
        n = 0
        while n < len(s) and s[n].isdigit():
            n += 1
        length, s = int(s[:n]), s[n:]
        parts.append(s[:length]); s = s[length:]
    if parts and parts[-1].startswith('h') and len(parts[-1]) == 17:
        parts.pop()
    result = '::'.join(parts) or name
    for old, new in {'$LT$': '<', '$GT$': '>', '$u20$': ' ', '$RF$': '&', '$C$': ',', '$LP$': '(', '$RP$': ')', '$u27$': "'", '..': '::'}.items():
        result = result.replace(old, new)
    return result


def selected_rows(name, record):
    files = record['full_ledger_files']
    for f in files:
        assert sha(read(f['path'])) == f['sha256'], f['path']
    if name == 'pump':
        path = files[0]['path']; d = load(path)['after']
        return path, d['original_windows'], d['candidate_symbol_windows'], lambda r: r['pattern_candidates'], lambda r: r['call_consistent_candidates']
    if name == 'pump_amm':
        path = next(f['path'] for f in files if 'residual-ledger' in f['path']); d = load(path)
        return path, d['original'], d['candidate'], lambda r: [x['start'] for x in r['candidate_matches']], lambda r: [x['start'] for x in r['candidate_matches'] if x.get('recursive_direct_graph_correspondence')]
    if name == 'pump_fees':
        path = files[0]['path']; d = load(path)
        return path, d['original_rows'], d['candidate_rows'], lambda r: [x['candidate_start'] for x in r['candidate_matches']], lambda r: [x['candidate_start'] for x in r['candidate_matches'] if x.get('unique_calls_consistent')]
    if name == 'mayhem':
        path = files[0]['path']; d = load(path); ids = {r['id']: r['start'] for r in d['candidate_rows']}
        return path, d['original_rows'], d['candidate_rows'], lambda r: [ids[x] for x in r['fresh_normalized_matches']], lambda r: []
    path = next(f['path'] for f in files if f['path'].endswith('/match-ledger.json'))
    original = load(next(f['path'] for f in files if f['path'].endswith('/original-function-ledger.json')))
    candidates = load(next(f['path'] for f in files if f['path'].endswith('/candidate-function-ledger.json')))
    matched = load(path)
    rows = [dict(o, **{'match_record': m}) for o, m in zip(original, matched)]
    assert len(rows) == len(original) == len(matched)
    return path, rows, candidates, lambda r: [candidates[i]['start'] for i in r['match_record']['normalized_candidate_indices']], lambda r: []


def inventory(name, variant, original_image, candidate_image, source, originals, candidates, normalized, consistent):
    assert len({r['start'] for r in originals}) == len(originals), 'duplicate original windows'
    by_start, raw_groups = {}, collections.defaultdict(list)
    for r in candidates:
        start, end = r['start'], r['end']
        raw = at(candidate_image, start, end - start)
        assert sha(raw) == r['raw_sha256'], (name, variant, 'candidate hash', start)
        by_start[start] = r
        raw_groups[(len(raw), sha(raw))].append(start)
    result = []
    for r in originals:
        start, end = r['start'], r['end']; raw = at(original_image, start, end - start)
        if 'raw_sha256' in r:
            assert sha(raw) == r['raw_sha256'], (name, variant, 'original hash', start)
        exact = raw_groups[len(raw), sha(raw)]
        assert all(raw == at(candidate_image, x, len(raw)) for x in exact)
        norm = sorted(set(normalized(r))); calls = sorted(set(consistent(r)))
        assert all(x in by_start for x in norm + calls)
        opaque = r.get('scope') == 'opaque'
        disposition = ('raw_body_equal' if exact else 'normalized_body_only' if norm else 'opaque_unassessed' if opaque else 'no_complete_body_match')
        names = sorted({simple_name(n) for x in exact + norm for n in by_start[x].get('names', [])})
        raw_names = sorted({simple_name(n) for x in exact for n in by_start[x].get('names', [])})
        result.append(dict(program=name, variant=variant, original_start=start,
                           original_end=end, bytes=end-start, disposition=disposition,
                           original_raw_sha256=sha(raw), raw_candidate_starts=exact,
                           normalized_candidate_starts=norm, call_supported_candidate_starts=calls,
                           candidate_names=names, raw_candidate_names=raw_names, opaque_in_source_ledger=opaque,
                           source_status=r.get('status', r.get('category', r.get('match_record', {}).get('status'))),
                           source_ledger=source, semantic_perfection_proven=False))
    return result


def summarize(rows):
    return dict(original_windows=len(rows), dispositions=dict(collections.Counter(r['disposition'] for r in rows)),
                raw_body_equal_original_windows=sum(bool(r['raw_candidate_starts']) for r in rows),
                raw_match_ambiguous_original_windows=sum(len(r['raw_candidate_starts']) > 1 for r in rows),
                normalized_match_original_windows=sum(bool(r['normalized_candidate_starts']) for r in rows),
                call_supported_original_windows=sum(bool(r['call_supported_candidate_starts']) for r in rows),
                opaque_in_source_ledger=sum(r['opaque_in_source_ledger'] for r in rows),
                raw_equal_body_bytes=sum(r['bytes'] for r in rows if r['raw_candidate_starts']))


def build():
    INPUTS.clear(); read('scripts/analyze.py')
    index = load('repro/layered-passes/pass-26/current-metadata/current-analysis-index.json')
    completion = load('repro/completion.json'); status = load('repro/status.json')
    bindings=load('repro/layered-passes/pass-27/current-metadata/bindings.json')
    declarations=collections.defaultdict(list)
    for program,record in bindings['compiled'].items():
        for path, expected in record['source'].items():
            raw=read(path)
            assert sha(raw) == expected, ('selected compile input changed', path)
            if path.endswith('.rs'):
                source_text=raw.decode()
                for match in re.finditer(r'\bpub\s+fn\s+(\w+)\b',source_text):
                    declarations[program,match[1]].append(dict(path=path,line=source_text.count('\n',0,match.start())+1))
    windows, counts, comparisons = [], {}, []
    old_bytes = load('repro/layered-passes/pass-26/current-metadata/after-corrections/all-byte-ranges.json.gz')
    for row in old_bytes['programs'] + old_bytes['raw_compiler_supplement']:
        comparisons.append(byte_comparison(row['name'], row['original_path'], row['candidate_path'], row['kind']))
    comparisons.append(byte_comparison('associated_token', 'evidence/dependencies/associated_token/deployed.so', 'repro/ata/reconstructed-order/results/run-40287588927/ordered.so', 'research_exact_linker_order'))
    comparisons.append(byte_comparison('associated_token', 'evidence/dependencies/associated_token/deployed.so', 'repro/ata/synthetic-ordering-exact-build/results/b2/spl_associated_token_account.so', 'research_exact_empty_feature'))
    for name, record in index['programs'].items():
        original, candidate = read(record['original_path']), read(record['candidate_path'])
        assert sha(original) == record['original_sha256'] and sha(candidate) == record['candidate_sha256']
        source, rows, candidates, norm, calls = selected_rows(name, record)
        result = inventory(name, 'selected', original, candidate, source, rows, candidates, norm, calls)
        windows.extend(result); counts[name] = summarize(result)
    # Latest Fees research is kept separate from the selected Fees checkpoint.
    fp = 'research/fees-stable-share-sort/analysis.json.gz'; f = load(fp)
    source = load('research/fees-stable-share-sort/experiment.json')
    descriptor = source['variants']['stable']['files']['candidate']
    fimage = gzip.decompress(read('research/fees-stable-share-sort/' + descriptor['path']))
    assert sha(fimage) == descriptor['sha256']
    v = f['variants']['stable']; pairs = v['unique_pairs']; ambiguous = v['ambiguous']
    oa, ca, matches = {}, {}, collections.defaultdict(list)
    for pair in pairs:
        a,b=pair['original'],pair['candidate'];oa[a['address']]=a;ca[b['address']]=b;matches[a['address']].append(b['address'])
    for group in ambiguous:
        for a in group['original']:oa[a['address']]=a;matches[a['address']].extend(b['address'] for b in group['candidate'])
        for b in group['candidate']:ca[b['address']]=b
    for a in v['unmatched_original']:oa[a['address']]=a
    for b in v['unmatched_candidate']:ca[b['address']]=b
    def adapt(r):return dict(start=r['address'],end=r['address']+r['bytes'],raw_sha256=r['raw_sha256'],names=[r['name']] if r.get('name') else [])
    result=inventory('pump_fees','research_stable_sort',read(index['programs']['pump_fees']['original_path']),fimage,fp,[adapt(r) for r in sorted(oa.values(),key=lambda r:r['address'])],[adapt(r) for r in ca.values()],lambda r:matches[r['start']],lambda r:[])
    windows.extend(result);counts['pump_fees_research']=summarize(result)
    attribution=load('research/fees-call-target-attribution/analysis.json.gz')
    counts['pump_fees_research']['unique_structural_pairs']=attribution['body_unique_pairs']
    counts['pump_fees_research']['call_attributed_pairs']=attribution['graph_attributed_pairs']
    counts['pump_fees_research']['remaining_ambiguous_windows']=sum(len(x['original_unbound']) for x in attribution['remaining_ambiguous'])
    comparisons.append(byte_comparison('pump_fees',index['programs']['pump_fees']['original_path'],'research/fees-stable-share-sort/'+descriptor['path'],'research_stable_sort',compressed=True))
    # Latest Relay research retains an independent full partition.
    rp='repro/donation-relay/distribution-worker-source-recovery/settlement/'
    original,candidate=read(index['programs']['donation_relay']['original_path']),read(rp+'candidate.so')
    originals=load(rp+'original-function-ledger.json.gz');candidates=load(rp+'candidate-function-ledger.json.gz');matched=load(rp+'match-ledger.json.gz')
    assert len(originals) == len(matched) == 492
    rows=[dict(o,match_record=m) for o,m in zip(originals,matched)]
    result=inventory('donation_relay','research_distribution_worker',original,candidate,rp+'match-ledger.json.gz',rows,candidates,lambda r:[candidates[i]['start'] for i in r['match_record']['normalized_candidate_indices']],lambda r:[])
    windows.extend(result);counts['donation_relay_research']=summarize(result)
    comparisons.append(byte_comparison('donation_relay',index['programs']['donation_relay']['original_path'],rp+'candidate.so','research_distribution_worker'))
    read('repro/donation-relay/distribution-worker-source-recovery/remaining-windows.json')
    handlers=[]
    for r in completion['instructions']:
        name,ix=r['program'],r['instruction']; selected=status[name]
        assert (ix in selected['implemented_handlers']) == (r['status']=='bounded_implementation'),(name,ix)
        handlers.append(dict(program=name,instruction=ix,selected_status=r['status'],
                             limitation=r['limitation'],selected_candidate=selected['candidate_artifact'],
                             selected_candidate_sha256=sha(read(selected['candidate_artifact'])),
                             source_declarations=declarations[name,ix],
                             semantic_perfection_proven=False))
    assert len(handlers)==150 and sum(r['variant']=='selected' for r in windows)==3338
    assert len(windows) == 4415
    return dict(schema=1, audited_revision=BASELINE, scope='Static audit of selected checkpoints and separate research snapshots; no new builds or target execution.',
                definitions={'raw_body_equal':'Complete local window bytes equal at some candidate window; calls/data/identity may remain unresolved.',
                             'normalized_body_only':'Retained full-window relation under the owning ledger normalization; not raw byte equality or semantic perfection.',
                             'no_complete_body_match':'No complete normalized relation in this inventory; source may exist with different code generation.',
                             'opaque_unassessed':'Original window not admitted to normalized comparison in the owning ledger.'},
                counts=counts,byte_comparisons=comparisons,handlers=handlers,windows=windows,input_sha256=dict(sorted(INPUTS.items())))


OVERLAY = {
    ('pump','admin_update_token_incentives'): 'Unselected overlay: 299 bounded comparisons; needs a selected build and exhaustive validation.',
    ('pump','claim_token_incentives'): 'Unselected overlay: implemented, but its receipt must be rebound and rerun against the current overlay build.',
    ('pump','set_mayhem_virtual_params'): 'Unselected overlay: 84 signer-stub comparisons; genuine-caller and AccountInfo ownership questions remain.',
    ('pump','create_v2'): 'Unselected overlay extends Mayhem creation; ancestry, account validation and Token-2022 combinations remain incomplete.',
    ('pump','buy_v3'): 'Unselected overlay extends transfer-fee quotes; other routes, account/extension validation and event suffix remain incomplete.',
    ('pump','sell_v3'): 'Unselected overlay extends transfer-fee quotes; other routes, account/extension validation and event suffix remain incomplete.',
    ('pump','buy_exact_quote_in_v3'): 'Unselected overlay extends transfer-fee quotes; nested routes and exhaustive validation remain incomplete.',
    ('pump','multi_hop_curve_swap'): 'Finite one/two/three-hop coverage; arbitrary depth, quote mints, lifecycle and extension/mode combinations remain incomplete.',
    ('pump','sell_v2'): 'KNOWN GAP despite bounded acceptance: quote transfer-fee minimum-output/event mismatch.',
    ('pump_amm','create_config'): 'Static source/normalized bodies exist; no authentic successful fixed-admin initializer replay.',
    ('mayhem','initialize_mayhem_state'): 'Unselected corrected overlay: 53 rejection cases plus real Pump CPI cases; not selected or exhaustively validated.'
}


def cell(value):
    return str(value).replace('|','\\|').replace('\n',' ')


def outputs(data):
    result={'audit.json':json.dumps(data,indent=2,sort_keys=True)+'\n'}
    out=io.StringIO();columns=['program','variant','original_start','original_end','bytes','disposition','candidate_names','raw_candidate_starts','normalized_candidate_starts','source_status','source_ledger']
    writer=csv.DictWriter(out,columns,delimiter='\t',lineterminator='\n');writer.writeheader()
    for row in data['windows']:
        writer.writerow({k:json.dumps(row[k],ensure_ascii=False)if isinstance(row[k],list)else row[k]for k in columns})
    result['functions.tsv']=out.getvalue()
    lines=['# Complete handler disposition ledger', '',
           'Generated from `repro/completion.json`, checked against the current selected handler lists, and rebound to current candidate hashes.', '',
           '**No handler is certified exhaustively perfect.** “Bounded” means retained finite comparison coverage. A missing per-handler note is not evidence that all branches, logs, data or account combinations match.', '',
           '| Program | Instruction | Selected disposition | Public source declarations | Known gap / newer research |',
           '| --- | --- | --- | --- | --- |']
    for r in data['handlers']:
        note=OVERLAY.get((r['program'],r['instruction']),r['limitation'] or 'Bounded finite coverage; whole binary, transitive behavior and security acceptance unresolved.')
        sources='; '.join('['+x['path'].split('/')[-1]+':'+str(x['line'])+'](../../'+x['path']+'#L'+str(x['line'])+')' for x in r['source_declarations']) or 'No public fn declaration in selected compile inputs'
        lines.append('| '+ ' | '.join(cell(x) for x in [r['program'],'`'+r['instruction']+'`',r['selected_status'],sources,note])+' |')
    result['handlers.md']='\n'.join(lines)+'\n'
    lines=['# Exact local body-byte matches', '',
           'Every row below was compared directly against the selected or explicitly named research binary. Names come from candidate symbols; the original function name and semantic identity are not established by a byte match alone.', '',
           'Duplicate candidates remain ambiguous. Equal local CALL bytes at different addresses can reach different functions; relocated data, indirect calls and input behavior require separate proofs. These are **not** a list of completely proven functions.', '',
           '| Program / variant | Original address | Bytes | Candidate addresses | Candidate symbol labels |',
           '| --- | ---: | ---: | --- | --- |']
    for r in data['windows']:
        if r['raw_candidate_starts']:
            lines.append('| '+ ' | '.join(cell(x) for x in [r['program']+' / '+r['variant'],hex(r['original_start']),r['bytes'],', '.join(hex(x) for x in r['raw_candidate_starts']),'; '.join(r['raw_candidate_names'])])+' |')
    result['raw-body-matches.md']='\n'.join(lines)+'\n'
    lines=['# Function-window audit summary', '',
           'Snapshot: `'+data['audited_revision']+'`. Raw bodies were rehashed from actual binary bytes; normalized relations use each pinned source ledger’s own rules. Counts are original windows, never candidate-pair counts.', '',
           '| Program / build | Windows | Exact local bytes | Normalized only | No complete match | Opaque, no byte match |',
           '| --- | ---: | ---: | ---: | ---: | ---: |']
    for name,c in data['counts'].items():
        d=c['dispositions'];lines.append('| '+ ' | '.join(str(x) for x in [name,c['original_windows'],d.get('raw_body_equal',0),d.get('normalized_body_only',0),d.get('no_complete_body_match',0),d.get('opaque_unassessed',0)])+' |')
    lines += ['', 'These columns partition the rows. Mayhem has 257 source-ledger opaque windows; 12 happen to have equal local byte bodies and are counted in the exact-byte column, leaving 245 in the last column. Its 177 admitted normalized matches remain a separate count.', '',
              'The selected Fees ledger also retains two call-conflicting rows. A raw or normalized body match does not erase that conflict. Pump’s 617 historical raw **pairs** represent 98 distinct original windows in this audit, not 617 reconstructed functions.', '',
              '- [All 150 handlers](handlers.md)', '- [Every exact local body match](raw-body-matches.md)', '- [All 4,415 selected/research window rows](functions.tsv)', '- [Machine-readable evidence and input hashes](audit.json)', '',
              'Rebuild these tables with `python3 -B repro/reconstruction-audit-2026-10-26/audit.py`; check them with the same command plus `--check`. No target programs are executed.']
    result['README.md']='\n'.join(lines)+'\n'
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    data=build()
    for name,body in outputs(data).items():
        path=HERE/name
        if a.check:assert path.read_text()==body, name+' is stale'
        else:path.write_text(body)
    print(json.dumps({'selected_original_windows':3338,'handler_dispositions':dict(collections.Counter(r['selected_status']for r in data['handlers'])),'counts':data['counts']},indent=2))


if __name__=='__main__':main()

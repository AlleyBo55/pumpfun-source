#!/usr/bin/env python3
"""Summarize the verified window partition without treating it as semantic proof."""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def generate():
    paths = ['functions.tsv', 'status.json', 'fees-call-attribution.json']
    inputs = {p: (HERE / p).read_bytes() for p in paths}
    audit_path = 'repro/reconstruction-audit-2026-10-26/audit.json'
    inputs[audit_path] = (ROOT / audit_path).read_bytes()
    status = json.loads(inputs['status.json'])
    audit = json.loads(inputs[audit_path])
    calls = json.loads(inputs['fees-call-attribution.json'])
    rows = list(csv.DictReader(inputs['functions.tsv'].decode().splitlines(), delimiter='\t'))
    assert len(rows) == 4415
    summary = {}
    for program, expected in status['counts'].items():
        group = [r for r in rows if r['program'] == program]
        counts = dict(collections.Counter(r['disposition'] for r in group))
        assert counts == expected['dispositions'] and len(group) == expected['windows']
        body_bytes = sum(int(r['bytes']) for r in group)
        assert body_bytes == expected['body_bytes']
        sizes = {k: sum(int(r['bytes']) for r in group if r['disposition'] == k) for k in counts}
        summary[program] = dict(windows=len(group), counts=counts, body_bytes=body_bytes, bytes_by_disposition=sizes)
    handlers = audit['handlers']
    assert len(handlers) == 150 and not any(h['semantic_perfection_proven'] for h in handlers)
    report = dict(reviewed_revision=status['snapshot'], selected_revision=status['selected_snapshot'], programs=summary,
                  handler_dispositions=dict(collections.Counter(h['selected_status'] for h in handlers)),
                  input_sha256={p: hashlib.sha256(v).hexdigest() for p, v in inputs.items()})
    lines = ['# Comprehensive reconstruction review', '', f"Reviewed merged evidence: `{status['snapshot']}`. Selected builds remain bound to `{status['selected_snapshot']}`.", '',
        '**No core program or Relay is whole-file byte-identical. No public handler is proved exhaustively perfect.**', '',
        '## How to read the classifications', '',
        '- **Exact local bytes:** an entire inferred original window has a raw-byte counterpart. Calls, referenced data, placement and duplicate identity still need verification.',
        '- **Normalized only:** complete local body matches under the owning study’s masks. This is reconstructed machine structure, with masked operands and transitive behavior still unresolved.',
        '- **Unmatched:** no complete counterpart under that matcher. This can include extensive existing source; it does not mean every instruction is missing.',
        '- **Opaque:** no admitted normalized comparison and no raw counterpart. Investigate source attribution before claiming recovery.',
        '- **Bounded handler:** source has retained finite execution evidence. It can still have known discrepancies. Public handlers and compiler-generated windows are different inventories.', '',
        '## All programs: remaining machine-code scope', '',
        '| Build | Exact local windows | Normalized only | Unmatched | Opaque | Unmatched + opaque bytes / original text |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    for program, s in summary.items():
        c, b = s['counts'], s['bytes_by_disposition']
        unresolved = b.get('no_complete_body_match', 0) + b.get('opaque_unassessed', 0)
        lines.append(f"| {program} | {c.get('raw_body_equal',0)} | {c.get('normalized_body_only',0)} | {c.get('no_complete_body_match',0)} | {c.get('opaque_unassessed',0)} | {unresolved:,} / {s['body_bytes']:,} ({100*unresolved/s['body_bytes']:.1f}%) |")
    lines += ['', 'These byte totals count entire unresolved original windows, not differing bytes or development effort. Raw and normalized matches can still contain unresolved references. Do not add selected and research rows: they represent alternative builds of the same programs. Mayhem has 257 source-ledger opaque windows; 12 have raw counterparts and therefore appear in the exact column.', '',
        f"Fees research has {calls['body_unique_pairs']} unique structural pairs, {calls['graph_attributed_pairs']-calls['body_unique_pairs']} additional call-attributed pairs and 85 unattributed duplicate windows. Its encoded-call ledger has {calls['local_call_edge_counts']['bound_target']:,} bound-target edges and {calls['local_call_edge_counts']['different_body_frontier']} different-body frontier edges. A bound edge is not a full semantic proof. Selected Fees retains two call-conflicting rows.", '',
        '## Every public handler: source/behavior status', '',
        'All 150 names appear below. The detailed [handler ledger](../reconstruction-audit-2026-10-26/handlers.md) contains source links and per-handler gaps. Unaccepted includes source that exists only in overlays, as well as static-only implementation; it must not be read as universally absent source.', '',
        '| Program | Classification | Count | Handler names |', '| --- | --- | ---: | --- |']
    for program in dict.fromkeys(h['program'] for h in handlers):
        for classification in ('bounded_implementation', 'partial', 'unrecovered'):
            hs = [h for h in handlers if h['program']==program and h['selected_status']==classification]
            if hs:
                label = {'bounded_implementation':'Bounded; perfection unproved','partial':'Partial','unrecovered':'Unaccepted / unrecovered'}[classification]
                lines.append(f"| {program} | {label} | {len(hs)} | " + ', '.join('`'+h['instruction']+'`' for h in hs) + ' |')
    lines += ['', 'Exact local matches are individually listed in [raw-body-matches.md](raw-body-matches.md); every normalized match, original address, candidate name and correspondence is in [functions.tsv](functions.tsv). A stripped original does not supply authoritative source names, so no unverified name is presented as certain.', '', '## Largest unresolved bodies', '', 'The five largest unresolved windows per build focus the next investigation. Empty candidate names are deliberately not replaced with guessed source names. All residuals, including smaller windows, are in [remaining-windows.md](remaining-windows.md).', '', '| Build | Original address | Bytes | Classification |', '| --- | ---: | ---: | --- |']
    for program in summary:
        residual = [r for r in rows if r['program']==program and r['disposition'] in ('no_complete_body_match','opaque_unassessed')]
        for r in sorted(residual, key=lambda r: (-int(r['bytes']),int(r['original_start'])))[:5]:
            lines.append(f"| {program} | {int(r['original_start']):,} | {int(r['bytes']):,} | {r['disposition']} |")
    lines += ['', '## Remaining acceptance gates', '',
        '1. **Behavior:** finish partial/unaccepted public handlers and known discrepancies. Pump `sell_v2` remains a bounded implementation with a known transfer-fee discrepancy. Mayhem field roles, initialization and diagnostic contracts remain unresolved. Existing stopped lanes remain stopped.',
        '2. **Complete bodies:** recover the ten Relay donation/settlement/worker windows and 58 Fees residuals; complete Pump/AMM reconstruction and attribute Mayhem opaque windows. Small helper matches alone do not close callers.',
        '3. **Identity:** establish referenced data, call targets, duplicate attribution, indirect calls, layout, relocations, full ELF equality and allocation-padding accounting for each exact proposed build.',
        '4. **Build provenance:** retain source hashes, dependency/toolchain inputs and reproducible recipes. A synthetic exact recipe does not establish the historical recipe.',
        '5. **Selection:** research candidates require explicit selected-source integration, rebuilt artifacts, bound validation and guard transitions. Current research gains do not update selected checkpoints.', '',
        'The next practical work is targeted Relay value/lifetime recovery and Fees caller/ownership recovery, with regression checks against the retained frontier. Avoid repeating the documented rejected source/compiler variants. Pump/AMM and Mayhem remain substantial independent workstreams. See [the prioritized work list](../../docs/REMAINING-WORK.md). No reliable total effort percentage or ETA follows from these counts.', '',
        '## Evidence and validation', '',
        'This report derives from the full window inventory, current call ledger and immutable selected-handler audit. It does not rerun runtime cases or claim new execution coverage. Current Fees retains 17,331 suite comparisons, 1,542 exact outcome/log/compute comparisons and 24 exotic-growth boundary cases, plus 32 signed optional-account and 20 social-claim user-ID cases, plus 8 extension program-log cases and 30 crank mint cases. Relay retains 536 records / 534 unique fixtures per tested recipe. Their exclusions and observation scopes remain those of their owning packets.', '',
        'Verify inventory/binary bindings with `python3 -B repro/reconstruction-status-2026-10-26/refresh.py --check`, then this report with `python3 -B repro/reconstruction-status-2026-10-26/review.py --check`. The [current analysis](../../docs/RECONSTRUCTION-STATUS.md) links the recovery studies and dependency evidence.', '']
    return {'review.md':'\n'.join(lines), 'review.json':json.dumps(report,indent=2,sort_keys=True)+'\n'}

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    for name, content in generate().items():
        if args.check:
            assert (HERE/name).read_text()==content, name
        else:
            (HERE/name).write_text(content)
    print('PASS: comprehensive review; all 4,415 windows and 150 handler classifications reconciled')

"""Attribute duplicate SBF bodies using calls from previously paired callers.

The result is a correspondence hypothesis supported by encoded call context.
It is neither new machine-code coverage nor proof of data/behavioral identity.
"""
import collections
import gzip
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('attribution_windows', HERE / 'window_map.py')
wm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wm)


def local_calls(image, windows):
    relocations = dict(wm.m.relocations(image))
    result = {}
    for window in windows:
        address = window['address']
        result[address] = {
            row['offset']: row['call_target']
            for row in wm.m.instructions(image, address, window['bytes'])
            if 'call_target' in row
            and relocations.get(address + row['offset'], 0) & 0xffffffff != 10
        }
    return result


def attribute(original, candidate, original_calls, candidate_calls):
    """Propagate only mutually unambiguous, body-compatible call proposals.

    Input names and address order never select a pair. Each promotion must
    have an actual incoming call from an earlier paired caller. A conflicting
    known target aborts the refinement. Unreached duplicates stay unresolved.
    """
    left = {row['address']: row for row in original}
    right = {row['address']: row for row in candidate}
    comparison = wm.compare(original, candidate)
    seeds = {pair['original']['address']: pair['candidate']['address']
             for pair in comparison['unique_pairs']}
    known = dict(seeds)
    round_of = {address: 0 for address in seeds}
    history = []
    for iteration in range(1, len(original) + 1):
        inverse = {target: address for address, target in known.items()}
        assert len(inverse) == len(known), 'non-injective known attribution'
        proposals = collections.defaultdict(set)
        reverse = collections.defaultdict(set)
        witnesses = collections.defaultdict(list)
        frontier, conflicts = [], []
        for caller, counterpart in sorted(known.items()):
            a, b = original_calls[caller], candidate_calls[counterpart]
            assert a.keys() == b.keys(), 'paired body has a different local-call shape'
            for offset, target in sorted(a.items()):
                other = b[offset]
                assert target in left and other in right, 'local target is not a window start'
                witness = dict(original_caller=caller, candidate_caller=counterpart,
                               offset=offset, original_target=target, candidate_target=other)
                if ((target in known and known[target] != other)
                        or (other in inverse and inverse[other] != target)):
                    conflicts.append(witness)
                elif left[target]['signature'] != right[other]['signature']:
                    frontier.append(witness)
                else:
                    proposals[target].add(other)
                    reverse[other].add(target)
                    witnesses[target, other].append(witness)
        assert not conflicts, ('encoded calls conflict with an earlier attribution', conflicts)
        added = []
        for target, options in sorted(proposals.items()):
            if target in known or len(options) != 1:
                continue
            other = next(iter(options))
            if len(reverse[other]) != 1 or other in inverse:
                continue
            added.append(dict(original=target, candidate=other,
                              witnesses=witnesses[target, other]))
        if not added:
            break
        history.append(dict(round=iteration, additions=added))
        for pair in added:
            known[pair['original']] = pair['candidate']
            round_of[pair['original']] = iteration
    else:
        raise AssertionError('attribution did not converge')
    return dict(seeds=seeds, known=known, discovery_round=round_of,
                rounds=history, final_witnesses=witnesses,
                frontier=frontier, conflicts=conflicts,
                proposals=proposals, reverse_proposals=reverse)


def analyze():
    provenance = json.loads((HERE / 'input-provenance.json').read_text())
    original = (ROOT / 'evidence/original/pump_fees/deployed.so').read_bytes()
    assert wm.m.digest(original) == '4f2955d0f6b40cc9ff7daa18ccad7d19119ba1249759f4e7e3bb691beee6b35e'
    images = {}
    for name, descriptor in provenance['files'].items():
        raw = gzip.decompress((HERE / descriptor['path']).read_bytes())
        assert len(raw) == descriptor['bytes'] and wm.m.digest(raw) == descriptor['sha256']
        images[name] = raw
    candidate = images['symbols']
    assert wm.m.section_data(candidate, '.text') == wm.m.section_data(images['candidate'], '.text')
    a, b = wm.windows(original), wm.windows(candidate)
    assert {row['address']: row['bytes'] for row in b} == {
        row['address']: row['bytes'] for row in wm.m.functions(candidate)}
    original_calls, candidate_calls = local_calls(original, a), local_calls(candidate, b)
    result = attribute(a, b, original_calls, candidate_calls)
    comparison = wm.compare(a, b)
    by_a = {row['address']: row for row in a}
    by_b = {row['address']: row for row in b}
    newly_attributed = []
    for address, other in sorted(result['known'].items()):
        if address in result['seeds']:
            continue
        newly_attributed.append(dict(original=by_a[address], candidate=by_b[other],
            round=result['discovery_round'][address],
            final_witnesses=result['final_witnesses'][address, other]))
    remaining = []
    for group in comparison['ambiguous']:
        original_unbound = [row['address'] for row in group['original'] if row['address'] not in result['known']]
        if original_unbound:
            remaining.append(dict(signature=group['original'][0]['signature'],
                original_unbound=original_unbound,
                candidate_bodies=[row['address'] for row in group['candidate']]))
    all_edges = []
    for caller, counterpart in sorted(result['known'].items()):
        for offset, target in sorted(original_calls[caller].items()):
            other = candidate_calls[counterpart][offset]
            kind = ('bound_target' if result['known'].get(target) == other
                    else 'unbound_same_body' if by_a[target]['signature'] == by_b[other]['signature']
                    else 'different_body_frontier')
            all_edges.append(dict(original_caller=caller, candidate_caller=counterpart,
                offset=offset, original_target=target, candidate_target=other, kind=kind))
    edge_counts = collections.Counter(row['kind'] for row in all_edges)
    return dict(original_sha256=wm.m.digest(original),
        candidate_sha256=wm.m.digest(images['candidate']),
        symbols_sha256=wm.m.digest(candidate), original_windows=len(a), candidate_windows=len(b),
        inferred_boundaries_equal_symbols=True,
        body_unique_pairs=len(comparison['unique_pairs']),
        ambiguous_body_groups=len(comparison['ambiguous']),
        ambiguous_original_windows=sum(len(row['original']) for row in comparison['ambiguous']),
        unmatched_original_windows=len(comparison['unmatched_original']),
        unique_body_raw_equal_pairs=sum(row['original']['raw_sha256'] == row['candidate']['raw_sha256']
                                       for row in comparison['unique_pairs']),
        graph_attributed_pairs=len(result['known']), newly_attributed_pairs=newly_attributed,
        rounds=result['rounds'], remaining_ambiguous=remaining,
        local_call_edge_counts=dict(sorted(edge_counts.items())), local_call_edges=all_edges,
        encoded_call_conflicts=result['conflicts'], different_body_frontier=result['frontier'],
        candidate_equals_original_capture=images['candidate'] == original,
        candidate_equals_original_elf_extent=images['candidate'] == original[:wm.m.elf_layout(original)['elf_extent']])


if __name__ == '__main__':
    print(json.dumps(analyze(), indent=2))

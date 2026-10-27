#!/usr/bin/env python3
"""Construct source-only coordinate proposals; no compiler or ELF rewriting."""
import difflib
import hashlib
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
BASE = ROOT / 'repro/donation-relay/swap-receipt-coordinate-recovery/sources/recovered'
LATEST = ROOT / 'repro/donation-relay/mint-fee-pair-recovery'
SOURCE_INPUTS = {
    'src/lib.rs': (BASE / 'src/lib.rs', '358c67f818071be63fb4092c74fa145076e1bddc8f07fb78054cade9dbf5a7b8'),
    'src/anchor_donate.rs': (BASE / 'src/anchor_donate.rs', 'e2e54921b638fad001e3201f2fb31816ef2e4554573016804ff4c191685ee640'),
    'src/tools/fair_distribution.rs': (BASE / 'src/tools/fair_distribution.rs', 'a677b81837488c5c106c2eb4465b87c3ef4d5f1c3de8486be73bd27f07333a9b'),
    'src/mint_policy.rs': (LATEST / 'mint_policy.rs', 'bd8d559d364c5513bb0a1863705288153f784a4d6107d7b713be3782374ec14a'),
}


def H(b):
    return hashlib.sha256(b).hexdigest()


def inputs():
    out = {}
    for name, (path, digest) in SOURCE_INPUTS.items():
        assert not path.is_symlink() and H(path.read_bytes()) == digest, name
        out[name] = path.read_bytes()
    return out


def full_sources():
    """Assemble the exact 52-input recorded candidate tree without compilation."""
    import json
    result = {}
    for file in BASE.rglob("*"):
        if file.is_file():
            assert not file.is_symlink()
            result[str(file.relative_to(BASE))] = file.read_bytes()
    overrides = ROOT / "repro/donation-relay/framework-sysroot-recovery/sources/share-values"
    for name in ["Cargo.toml", "Cargo.lock"]:
        result[name] = (overrides / name).read_bytes()
    result["src/settlement_handlers.rs"] = (overrides / "settlement_handlers.rs").read_bytes()
    result["src/mint_policy.rs"] = (LATEST / "mint_policy.rs").read_bytes()
    launch = (LATEST / "launch.json").read_bytes()
    assert H(launch) == "7d8ac1016fa2ac9787bd5b5cba7f583d6c346165a68c4243a0a541c62fdeaee1"
    assert {name: H(data) for name, data in result.items()} == json.loads(launch)["inputs"]
    assert len(result) == 52
    return result


def column(line, token):
    assert line.count(token) == 1
    return line.index(token) + 1


def proposals():
    before = inputs()
    groups = {}
    old = before['src/lib.rs'].splitlines(True)
    assert old[35] == b'    #[program]\n'
    new = list(old); new[35] = b'#[program]\n'
    groups['program-column'] = {'src/lib.rs': b''.join(new)}

    old = before['src/anchor_donate.rs'].splitlines(True)
    new = list(old); events = {}
    for index, filename in [(30, 'donation_epoch_closed'), (35, 'donation_epoch_just_swapped'),
                            (43, 'donation_epoch_processed')]:
        assert old[index] == b'#[event]\n' and old[index + 1].startswith(b'pub struct ')
        path = 'src/events/v1/' + filename + '.rs'
        events[path] = b'\n' * 4 + old[index] + old[index + 1]
        new[index] = ('include!("events/v1/' + filename + '.rs");\n').encode()
        new[index + 1] = b'\n'
    assert len(new) == len(old)
    events['src/anchor_donate.rs'] = b''.join(new)
    groups['event-locations'] = events

    old = before['src/mint_policy.rs'].splitlines(True)
    assert old[111].startswith(b'pub fn typed_mint_safe(')
    assert column(old[115], b'borrow') == 21
    moved = list(old[111:]); moved[4] = b' ' * 10 + moved[4]
    new_path = 'src/tools/checks.rs'
    new_file = b'\n' * 91 + b''.join(moved)
    assert column(new_file.splitlines()[95], b'borrow') == 31
    groups['mint-borrow-location'] = {
        'src/mint_policy.rs': b''.join(old[:111]) + b'include!("tools/checks.rs");\n',
        new_path: new_file,
    }

    old = before['src/tools/fair_distribution.rs'].splitlines(True)
    assert old[32] == b'  amounts.push(amount);remainders.push((index,remainder));\n'
    assert column(old[32], b'push((index') == 35
    assert all(line == b'\n' for line in old[40:62])
    # Move only whitespace/line breaks. Consume existing blank lines so the
    # following indexed amount update stays on its already recovered line63.
    new = old[:32] + [b'  amounts.push(amount);\n'] + [b'\n'] * 12
    new += [b'        remainders.push((index,remainder));\n'] + old[33:40]
    new += [b'\n'] * (62 - len(new)) + old[62:]
    assert len(new) == len(old) and new[62:] == old[62:]
    assert column(new[45], b'push') == 20
    assert b''.join(b''.join(old).split()) == b''.join(b''.join(new).split())
    groups['remainder-push-location'] = {'src/tools/fair_distribution.rs': b''.join(new)}
    return before, groups


def patch_bytes(before, changes):
    output = []
    for name, data in sorted(changes.items()):
        original = before.get(name, b'')
        output.extend(difflib.unified_diff(original.decode().splitlines(True), data.decode().splitlines(True),
                      fromfile='a/' + name if name in before else '/dev/null', tofile='b/' + name))
    return ''.join(output).encode()


def verify_proposals():
    before, groups = proposals()
    result = []
    for label, changes in groups.items():
        patch = patch_bytes(before, changes)
        assert (P / 'patches' / (label + '.patch')).read_bytes() == patch, label
        result.append({'proposal': label, 'patch_sha256': H(patch),
                       'files': {name: {'before_sha256': H(before[name]) if name in before else None,
                                         'proposed_sha256': H(value)} for name, value in changes.items()},
                       'compiled': False})
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-patches', action='store_true')
    args = parser.parse_args()
    before, groups = proposals()
    if args.write_patches:
        for label, changes in groups.items():
            (P / 'patches' / (label + '.patch')).write_bytes(patch_bytes(before, changes))
    print(verify_proposals())

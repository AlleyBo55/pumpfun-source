#!/usr/bin/env python3
"""Offline verifier for the ATA synthetic-ordering exact build.

Re-derives every claim in REPORT.md from the retained files using only the standard
library. Exits non-zero on any drift. Run from anywhere:

    python3 verify.py          # assert
    python3 verify.py --json   # machine-readable
"""
import hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))

DEPLOYED_SHA = '6804554e69fd3a58caa191dc4a58f4c67223d30ca28ab8987f39fc18d2f7374d'
CANDIDATE2_SHA = 'ba8dd8a42ca7bff4b668c72e1b5614e9363b271924d520253f5724760ba2d65b'
LOCK_SHA = '3c8f402f40488908503e9cc088388c1f95848d79da5141b5cb1a14006d74428b'
FLAG = 'ordering-probe-b2'
PATCHED = {'associated-token-account/program/Cargo.toml', 'token/program/Cargo.toml', 'token/program-2022/Cargo.toml'}
IMAGE = 'solanafoundation/solana-verifiable-build@sha256:ee9ad7809009a99a70f659f7cba959e0c3c124e10f771b524914fd42f2b605a8'
INPUTS = {
    'spl-f5ce86.tar.gz': '1b324f4c0f476f0581556ee6fd1e0fe0b4e74252fd8d5fe690a459611568be5c',
    'solana-bpf-tools-linux.tar.bz2': '8a2d6a7d8b498202d2ae37062dad94be0c33ca37444e35ab7732927d3fe9a8ff',
    'criterion-v2.3.3-linux-x86_64.tar.bz2': 'ee7f92d7268563848aa3ae90bbf5df86604b8d0fb0e4942b0ecfbf6201596550',
}

def sha(b): return hashlib.sha256(b).hexdigest()
def rd(*p): return open(os.path.join(HERE, *p), 'rb').read()
def js(*p): return json.loads(rd(*p))

def main(argv):
    checks = {}
    # 1. The exact build output is byte-identical to the deployed ATA program.
    out = rd('results', 'b2', 'spl_associated_token_account.so')
    checks['output_bytes_105032'] = len(out) == 105032
    checks['output_sha256_equals_deployed'] = sha(out) == DEPLOYED_SHA
    dep_path = os.path.join(ROOT, 'evidence/dependencies/associated_token/deployed.so')
    if os.path.exists(dep_path):
        dep = open(dep_path, 'rb').read()
        checks['output_cmp_equal_to_evidence_deployed_so'] = out == dep
    # 2. The build record agrees, and the build was offline, --locked, lock unchanged.
    b2 = js('results', 'b2', 'result.json')
    checks['b2_record_identical'] = b2['byte_identical_to_deployed'] is True and b2['differing_positions_vs_deployed'] == 0
    checks['b2_record_sha_matches_file'] = b2['output_sha256'] == sha(out)
    checks['b2_flag'] = b2['flag'] == FLAG
    checks['b2_build_rc_0'] = b2['build_returncode'] == 0
    checks['b2_lock_unchanged'] = b2['lock_sha256_before'] == b2['lock_sha256_after'] == LOCK_SHA
    cmd = ' '.join(b2['command'])
    checks['b2_cmd_offline_locked_warnings'] = ('--offline' in cmd and '--locked' in cmd and 'RUSTFLAGS=-D warnings' in cmd
                                                and f'--features {FLAG}' in cmd and 'cargo build-bpf' in cmd)
    checks['b2_edits_only_three_manifests'] = {e['file'] for e in b2['edits']} == PATCHED
    # 3. Determinism: an independent rerun with the same flag reproduced the same bytes.
    b2r = js('results', 'b2r', 'result.json')
    checks['rerun_same_sha'] = b2r['output_sha256'] == b2['output_sha256'] == DEPLOYED_SHA
    checks['rerun_identical'] = b2r['byte_identical_to_deployed'] is True
    # 4. Control reproduces the repository's candidate2 (307 differing positions) under the same rig.
    ctl = js('results', 'control', 'result.json')
    checks['control_equals_candidate2'] = ctl['output_sha256'] == CANDIDATE2_SHA and ctl['equals_candidate2'] is True
    checks['control_307'] = ctl['differing_positions_vs_deployed'] == 307
    checks['control_unperturbed'] = ctl['flag'] is None and ctl['edits'] == []
    # 5. Negative attempts retained: a1 (token-2022-only) and b1 (ATA-only) equal candidate2.
    for a in ('a1', 'b1'):
        r = js('results', a, 'result.json')
        checks[f'{a}_equals_candidate2'] = r['output_sha256'] == CANDIDATE2_SHA and r['differing_positions_vs_deployed'] == 307
    # 6. The patch touches only the three manifests and only adds the no-op feature.
    patch = rd('source.patch').decode()
    files = set(re.findall(r'^--- a/(\S+)', patch, re.M))
    checks['patch_files'] = files == PATCHED
    added = [l[1:] for l in patch.splitlines() if l.startswith('+') and not l.startswith('+++')]
    removed = [l[1:] for l in patch.splitlines() if l.startswith('-') and not l.startswith('---')]
    checks['patch_adds_only_flag_lines'] = len(added) == 5 and all(FLAG in l for l in added)
    checks['patch_removes_only_two_dep_lines'] = (len(removed) == 2 and all(('spl-token' in l and 'features = ["no-entrypoint"]' in l) for l in removed))
    checks['patch_no_code_files'] = not any(f.endswith('.rs') for f in files)
    # 7. Pinned inputs and image.
    inputs = dict(re.findall(r'^([0-9a-f]{64})  (\S+)', rd('inputs.sha256').decode(), re.M))
    inputs = {v: k for k, v in inputs.items()}
    checks['inputs_pinned'] = all(inputs.get(k) == v for k, v in INPUTS.items())
    img = js('image-inspect.json')[0]
    checks['image_digest'] = IMAGE in img['RepoDigests'] and img['Architecture'] == 'amd64'
    vm = js('vendor-manifest.json')
    checks['vendor_632_crates_pinned'] = vm['crates'] == 632 and len(vm['package_sha256']) == 632 and all(vm['package_sha256'].values())

    ok = all(checks.values())
    rep = {'package': 'ata-synthetic-ordering-exact-build',
           'claim': 'f5ce86 source + pinned v1.27 toolchain + one no-op feature flag compiles to the deployed ATA bytes exactly',
           'not_claimed': 'historical build recipe; the flag is a synthetic ordering input',
           'output_sha256': sha(out), 'deployed_sha256': DEPLOYED_SHA, 'checks': checks, 'pass': ok}
    if '--json' in argv:
        print(json.dumps(rep, indent=2))
    else:
        print(f"output   {sha(out)[:16]}  {len(out)} B")
        print(f"deployed {DEPLOYED_SHA[:16]}  byte-identical: {sha(out) == DEPLOYED_SHA}")
        for k, v in checks.items(): print(f"  [{'OK' if v else 'FAIL'}] {k}")
        print(f"PASS={ok}")
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

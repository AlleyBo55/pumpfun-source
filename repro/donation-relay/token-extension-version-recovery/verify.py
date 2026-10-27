#!/usr/bin/env python3
"""Re-derive dependency/source/window/receipt bindings; no build or VM execution."""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile
import tempfile
import tomllib

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
SHA={'direct-v8':'bba550be99bd37ebd70a4d865f28b0fc5cff67a2362c3faaa681322006507fe6',
     'anchor-v8':'4256c58be30adeda38bfa1a47102179a6e45666a63876cc568828fdf72daddef'}

def H(b):return hashlib.sha256(b).hexdigest()
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def mod(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def archive_files(path,prefix):
    with tarfile.open(path)as t:
        return {m.name[len(prefix):]:t.extractfile(m).read() for m in t.getmembers()if m.isfile()and m.name.startswith(prefix)}

def verify(check_registry=False):
    manifest=read(P/'manifest.json')
    actual={str(f.relative_to(P))for f in P.rglob('*')if f.is_file()and f.name!='manifest.json'and '__pycache__'not in f.parts}
    assert actual==set(manifest)
    for n,h in manifest.items():assert (P/n).resolve().is_relative_to(P)and not(P/n).is_symlink()and H((P/n).read_bytes())==h,n
    parent_record=read(P/'parent.json');parent=ROOT/parent_record['path']
    assert H((parent/'manifest.json').read_bytes())==parent_record['manifest_sha256']
    original=(ROOT/'evidence/dependencies/donation_relay/deployed.so').read_bytes()
    analysis=mod('extension_elf',parent/'analyze.py')
    helper=mod('extension_receipts',parent/'verify.py')
    assert H(original)==helper.ORIGINAL
    base={str(f.relative_to(parent/'sources/recovered')):f.read_bytes()for f in (parent/'sources/recovered').rglob('*')if f.is_file()}
    old_lock=tomllib.loads(base['Cargo.lock'].decode())
    pin=next(x['checksum']for x in old_lock['package']if x['name']=='anchor-spl'and x['version']=='0.31.1')
    assert H((P/'upstream/anchor-spl-0.31.1.crate').read_bytes())==pin
    upstream=archive_files(P/'upstream/anchor-spl-0.31.1.crate','anchor-spl-0.31.1/')
    summaries={};ledgers={}
    for label in SHA:
        source=dict(base);overrides=P/'source-overrides'/label
        for name in ['Cargo.toml','Cargo.lock']:source[name]=(overrides/name).read_bytes()
        assert source['Cargo.toml']==base['Cargo.toml'].replace(b'version = "=7.0.0"',b'version = "=8.0.1"').replace(
            b'anchor-spl = { version = "=0.31.1"',b'anchor-spl = { path = "anchor-spl"'if label=='anchor-v8'else b'anchor-spl = { version = "=0.31.1"')
        if label=='anchor-v8':
            source.update({'anchor-spl/'+n:b for n,b in upstream.items()})
            original_manifest=upstream['Cargo.toml'];start=original_manifest.index(b'[dependencies.spl-token-2022]');stop=original_manifest.index(b'\n[',start+1)
            patched=original_manifest[:start]+original_manifest[start:stop].replace(b'version = "6"',b'version = "8.0.1"')+original_manifest[stop:]
            assert (overrides/'anchor-spl/Cargo.toml').read_bytes()==patched
            source['anchor-spl/Cargo.toml']=patched
            for name in ['.cargo-checksum.json','.cargo-ok']:
                if (overrides/'anchor-spl'/name).exists():source['anchor-spl/'+name]=(overrides/'anchor-spl'/name).read_bytes()
        folder=P/'builds'/label;launch=read(folder/'launch.json');result=read(folder/'result.json')
        assert launch['inputs']=={n:H(b)for n,b in source.items()}
        assert launch['target']=='sbpf-solana-solana'and '--offline'in launch['command']and '--locked'in launch['command']
        image=gzip.decompress((folder/'candidate.so.gz').read_bytes());symbols=gzip.decompress((folder/'symbols.so.gz').read_bytes())
        assert H(image)==SHA[label]==result['candidate_sha256']and H(symbols)==result['symbols_sha256']
        assert result['exit_code']==0 and result['source_unchanged']and result['log_sha256']==H((folder/'build.log').read_bytes())
        with tempfile.TemporaryDirectory()as td:
            d=Path(td);(d/'original.so').write_bytes(original);(d/'candidate.so').write_bytes(image);(d/'unstripped.so').write_bytes(symbols);(d/'original-windows.json').write_bytes((parent/'original-windows.json').read_bytes());out=analysis.analyze(d)
        summaries[label]=out['comparison-summary.json'];ledgers[label]=out['match-ledger.json']
        assert summaries[label]==read(folder/'comparison-summary.json')and ledgers[label]==read(folder/'match-ledger.json')
    assert summaries['direct-v8']['original_normalized_match_windows']==466
    assert summaries['anchor-v8']['original_normalized_match_windows']==470
    assert summaries['anchor-v8']['unmatched_original_windows']==22
    old=read(parent/'builds/recovered/match-ledger.json')
    assert [r['ordinal']for a,r in zip(old,ledgers['direct-v8'])if bool(a['normalized_candidate_indices'])!=bool(r['normalized_candidate_indices'])]==[]
    gains=[r['ordinal']for a,r in zip(old,ledgers['anchor-v8'])if not a['normalized_candidate_indices']and r['normalized_candidate_indices']]
    losses=[r['ordinal']for a,r in zip(old,ledgers['anchor-v8'])if a['normalized_candidate_indices']and not r['normalized_candidate_indices']]
    assert gains==[240,242,243,244]and losses==[]
    assert all(not x['whole_file_equal']for x in summaries.values())
    audit=read(P/'registry-audit.json');assert audit['package_count']==len(audit['packages'])==187
    assert audit['file_count']==sum(len(x['files'])for x in audit['packages'])==4135
    lock=tomllib.loads((P/'source-overrides/anchor-v8/Cargo.lock').read_text());checks={(x['name'],x['version']):x['checksum']for x in lock['package']if 'checksum'in x}
    for package in audit['packages']:assert package['archive_sha256']==checks[package['name'],package['version']]
    assert H((P/'upstream/spl-token-2022-8.0.1.crate').read_bytes())==checks['spl-token-2022','8.0.1']
    if check_registry:
        metadata=read(P/'metadata.json');packages={(x['name'],x['version']):x for x in metadata['packages']}
        for record in audit['packages']:
            source=Path(packages[record['name'],record['version']]['manifest_path']).parent
            for name,h in record['files'].items():assert H((source/name).read_bytes())==h,(record['name'],name)
    runtime=read(P/'fresh-runtime.json.gz');frozen={}
    assert runtime['candidate_sha256']==SHA['anchor-v8']and runtime['runner_sha256']==H((P/'replay_saved.py').read_bytes())
    harness_path=ROOT/'repro/donation-relay/local-validation-proposal/harness_proposal.py'
    assert runtime['harness_sha256']==H(harness_path.read_bytes())
    assert runtime['token2022_sha256']==H((ROOT/'evidence/dependencies/spl_token_2022/deployed.so').read_bytes())
    for name,h in runtime['input_reports'].items():
        path=ROOT/name;assert H(path.read_bytes())==h
        for i,row in enumerate(read(path)['cases']):frozen[str(path.relative_to(ROOT/'repro/donation-relay/distribution-worker-source-recovery/settlement'))+':'+str(i)]=row
    # Rebind only the candidate digest in the prior independent checker. No fixture,
    # signature, original-reproduction or effect-comparison rule is changed.
    helper.EXPECTED=dict(helper.EXPECTED,recovered=SHA['anchor-v8'])
    result=helper.check_runtime(runtime,frozen,mod('extension_harness',harness_path))
    print(json.dumps(dict(verified=True,gains=gains,losses=losses,normalized_windows=470,unmatched_windows=22,raw_windows=88,runtime=result,registry_sources_rechecked=check_registry,whole_byte_identity=False)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check-registry',action='store_true');verify(p.parse_args().check_registry)

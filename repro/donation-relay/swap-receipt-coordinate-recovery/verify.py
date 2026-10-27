#!/usr/bin/env python3
"""Recompute retained Relay evidence. Does not compile or execute a target."""
import argparse
import base64
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import tempfile

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
ORIGINAL='367f07a62e3f74d358187d175cf3228848e81a56c781a9a75b9df7fed1268563'
EXPECTED={'legacy':'fb4fcb3a95211ff2b3b4dde34257eb6632876a2d0ad4658fd32d45f159c7d518',
          'canonical':'89d02fbb3d153aed132740cf8e793420c350bfc53b663af2232e65f93e7420cf',
          'recovered':'03b725918aca825b316254311ea6ebe83da708bc3775df72c5d04be3b63fe978'}


def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


def check_runtime(report, frozen, harness):
    from solders.transaction import Transaction
    assert report['original_sha256']==ORIGINAL and report['candidate_sha256']==EXPECTED['recovered']
    assert report['case_count']==len(report['cases'])==536
    assert not report['failures']
    seen=set();stimuli=set()
    for row in report['cases']:
        assert row['id'] not in seen;seen.add(row['id'])
        prior=frozen[row['id']]
        assert row['fixture']==prior['fixture']
        old=prior.get('original',prior.get('results',{}).get('original'))
        left,right=row['original'],row['candidate']
        assert left['transaction_base64']==right['transaction_base64']==old['transaction_base64']
        tx=Transaction.from_bytes(base64.b64decode(left['transaction_base64'],validate=True))
        assert all(tx.verify_with_results()), 'invalid transaction signature'
        x,y=harness.comparable(left),harness.comparable(right)
        assert x==harness.comparable(old), 'original replay differs from saved observation'
        assert row['original_reproduced'] and row['differences']==[] and x==y
        fixture=row['fixture'];stimuli.add(sha(json.dumps({k:fixture[k] for k in ['accounts','instruction_hex','instruction_accounts']},sort_keys=True,separators=(',',':')).encode()))
    assert seen==set(frozen) and len(stimuli)==534
    return dict(records=536,unique_fixtures=534,mismatches=0)


def main():
    manifest=read(P/'manifest.json')
    actual={str(p.relative_to(P)) for p in P.rglob('*') if p.is_file() and p.name!='manifest.json' and '__pycache__' not in p.parts}
    assert actual==set(manifest)
    for name,expected in manifest.items():
        path=P/name;assert path.resolve().is_relative_to(P) and not path.is_symlink()
        assert sha(path.read_bytes())==expected,name
    analysis=module('coordinate_elf_analysis',P/'analyze.py')
    provenance=read(P/'window-provenance.json');window_source=ROOT/provenance['path']
    assert sha(window_source.read_bytes())==provenance['sha256']
    assert read(P/'original-windows.json')==[{k:r[k] for k in provenance['fields']} for r in read(window_source)]
    original=(ROOT/'evidence/dependencies/donation_relay/deployed.so').read_bytes()
    assert sha(original)==ORIGINAL
    sources={}
    for label in ['baseline','recovered']:
        directory=P/'sources'/label
        sources[label]={str(p.relative_to(directory)):p.read_bytes() for p in directory.rglob('*') if p.is_file()}
    name='src/state/v1/swap_receipt.rs'
    expected=dict(sources['baseline'])
    expected[name]=expected[name].replace(b'#[account]',b'\n\n\n#[account]',1)
    assert sources['recovered']==expected
    assert [x for x in sources['baseline'][name].splitlines() if x.strip()]==[x for x in sources['recovered'][name].splitlines() if x.strip()]
    summaries={};ledgers={};images={}
    for label in ['legacy','canonical','recovered']:
        folder=P/'builds'/label;image=gzip.decompress((folder/'candidate.so.gz').read_bytes());symbols=gzip.decompress((folder/'symbols.so.gz').read_bytes());images[label]=image
        assert sha(image)==EXPECTED[label]
        launch=read(folder/'launch.json');result=read(folder/'result.json')
        assert result['exit_code']==0 and result['source_unchanged']
        assert result['candidate_sha256']==sha(image) and result['symbols_sha256']==sha(symbols)
        assert result['log_sha256']==sha((folder/'build.log').read_bytes())
        src=sources['recovered' if label=='recovered' else 'baseline']
        assert launch['inputs']=={n:sha(b) for n,b in src.items()}
        assert launch['target']==('sbf-solana-solana' if label=='legacy' else 'sbpf-solana-solana')
        assert '--offline' in launch['command'] and '--locked' in launch['command']
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp);(d/'original.so').write_bytes(original);(d/'candidate.so').write_bytes(image);(d/'unstripped.so').write_bytes(symbols);shutil.copyfile(P/'original-windows.json',d/'original-windows.json')
            computed=analysis.analyze(d)
        summaries[label]=computed['comparison-summary.json'];ledgers[label]=computed['match-ledger.json']
        if label!='legacy':
            assert summaries[label]==read(folder/'comparison-summary.json')
            assert ledgers[label]==read(folder/'match-ledger.json')
    assert summaries['legacy']['original_normalized_match_windows']==465
    assert summaries['canonical']['original_normalized_match_windows']==465
    assert summaries['recovered']['original_normalized_match_windows']==466
    assert summaries['recovered']['original_raw_match_windows']==88
    assert summaries['recovered']['unmatched_original_windows']==26
    changes=[(i,a,b) for i,(a,b) in enumerate(zip(images['canonical'],images['recovered'])) if a!=b]
    assert changes==[(469212,2,5),(769096,2,5)]
    gains=[b['ordinal'] for a,b in zip(ledgers['canonical'],ledgers['recovered']) if not a['normalized_candidate_indices'] and b['normalized_candidate_indices']]
    losses=[b['ordinal'] for a,b in zip(ledgers['canonical'],ledgers['recovered']) if a['normalized_candidate_indices'] and not b['normalized_candidate_indices']]
    assert gains==[167] and losses==[]
    o=analysis.Elf(original);c=analysis.Elf(images['recovered']);r=ledgers['recovered'][167]
    assert (r['start'],r['bytes'])==(513680,1120)
    original_path=o.at(757785,47);candidate_path=c.at(753825,47)
    assert original_path==candidate_path==b'programs/contracts/src/state/v1/swap_receipt.rs'
    assert struct.unpack('<BBhi',o.at(513680+392,8))==(0x62,0x0a,-256,5)
    assert struct.unpack('<BBhi',c.at(468816+392,8))==(0x62,0x0a,-256,5)
    assert all(not s['whole_file_equal'] for s in summaries.values())
    report=read(P/'fresh-runtime.json.gz');frozen={}
    assert report['runner_sha256']==sha((P/'replay_saved.py').read_bytes())
    harness_path=ROOT/'repro/donation-relay/local-validation-proposal/harness_proposal.py'
    assert report['harness_sha256']==sha(harness_path.read_bytes())
    assert report['token2022_sha256']==sha((ROOT/'evidence/dependencies/spl_token_2022/deployed.so').read_bytes())
    for name,expected in report['input_reports'].items():
        path=ROOT/name;assert sha(path.read_bytes())==expected
        for i,row in enumerate(read(path)['cases']):
            rel=path.relative_to(ROOT/'repro/donation-relay/distribution-worker-source-recovery/settlement')
            frozen[str(rel)+':'+str(i)]=row
    runtime=check_runtime(report,frozen,module('frozen_coordinate_runtime',harness_path))
    print(json.dumps(dict(verified=True,normalized_windows=466,unmatched_windows=26,raw_windows=88,gains=gains,losses=losses,changed_bytes=changes,runtime=runtime,whole_byte_identity=False)))


if __name__=='__main__':main()

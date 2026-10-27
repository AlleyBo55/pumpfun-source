"""Verify retained builds, source changes, windows, data and bounded receipts."""
from pathlib import Path
import gzip
import hashlib
import importlib.util
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sha=lambda raw:hashlib.sha256(raw).hexdigest()
load=lambda path:json.loads(path.read_text())

def main():
    manifest=load(HERE/'manifest.json')
    actual={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()and p.name!='manifest.json'and '__pycache__'not in p.parts}
    assert actual==set(manifest)
    for name,digest in manifest.items():
        path=HERE/name
        assert not path.is_symlink()and path.resolve().is_relative_to(HERE)and sha(path.read_bytes())==digest,name
    for name,digest in load(HERE/'parents.json').items():assert sha((ROOT/name).read_bytes())==digest,name
    meta=load(HERE/'experiment.json')
    parent=load(ROOT/meta['parent']/'experiment.json')
    assert len(parent['harness_sha256'])==187
    for name,digest in parent['harness_sha256'].items():assert sha((ROOT/name).read_bytes())==digest,name
    assert meta['variants']['control']['input_sha256']==parent['variants']['origins']['input_sha256']
    for name,variant in meta['variants'].items():
        assert set(variant['input_sha256'])==set(variant['source_paths'])
        assert len(variant['input_sha256'])==(35 if name=='origins'else 34)
        for source,digest in variant['input_sha256'].items():assert sha((ROOT/variant['source_paths'][source]).read_bytes())==digest,source
        launch=load(HERE/f'builds/{name}-launch.json');result=load(HERE/f'builds/{name}-result.json')
        assert launch['inputs']==variant['input_sha256']and result['source_unchanged']and result['exit_code']==0
        assert launch['rustc_sha256']=='c8807b7ebede8578ac5a257ea333780f9d89bd356064fd8184af7e996cb71a97'
        assert 'sbpf-solana-solana'in launch['command']and '-e'in launch['command']and 'RUSTFLAGS=-Zremap-cwd-prefix='in launch['command']
        log=(HERE/f'builds/{name}-build.log').read_bytes()
        assert sha(log)==result['log_sha256']and log.count(b'--crate-name pump_fees_candidate ')==1
        assert result['candidate_sha256']==variant['files']['candidate']['sha256']and result['symbols_sha256']==variant['files']['symbols']['sha256']
    for kind in ['candidate','symbols']:
        assert all(meta['variants']['control']['files'][kind][k]==parent['variants']['origins']['files'][kind][k]for k in ['sha256','bytes'])
    source='programs/pump-fees/src/lib.rs'
    old=(ROOT/meta['variants']['control']['source_paths'][source]).read_text()
    remove='''    // The original aborts on addition overflow before comparing the total.
    let total = fees.lp_fee_bps.checked_add(fees.protocol_fee_bps).unwrap()
        .checked_add(fees.creator_fee_bps).unwrap();
    require!(total <= 10_000, FeeError::InvalidFeeTotal);'''
    assert old.count(remove)==1
    expected=old.replace(remove,'    require!(fee_total_is_valid(fees), FeeError::InvalidFeeTotal);').replace('fn validate_fees(fees: &Fees)','''#[inline(never)]
fn fee_total_is_valid(fees: &Fees) -> bool {
    fees.lp_fee_bps + fees.protocol_fee_bps + fees.creator_fee_bps <= 10_000
}

fn validate_fees(fees: &Fees)''')
    assert (ROOT/meta['variants']['predicate']['source_paths'][source]).read_text()==expected
    expected=old.replace(remove,'    require!(fees.is_valid(), FeeError::InvalidFeeTotal);').replace('fn validate_fees(fees: &Fees)','''#[path = "../../../pump-fees-math/src/lib.rs"]
mod fee_math;

fn validate_fees(fees: &Fees)''')
    assert (ROOT/meta['variants']['origins']['source_paths'][source]).read_text()==expected
    for name in ['predicate','origins']:
        assert {k for k,v in meta['variants']['control']['input_sha256'].items()if meta['variants'][name]['input_sha256'][k]!=v}=={source}
        receipt=json.loads(gzip.decompress((HERE/f'receipts/{name}-full.json.gz').read_bytes()))
        assert receipt['candidate_sha256']==meta['variants'][name]['files']['candidate']['sha256']and receipt['case_count']==17331 and not receipt['mismatches']and len(receipt['suites'])==18
        for suite in receipt['suites'].values():
            assert suite['original_sha256']==receipt['original_sha256']and suite['candidate_sha256']==receipt['candidate_sha256']
            assert not suite.get('mismatches',suite.get('failures',[]))
        flags=json.loads(gzip.decompress((HERE/f'receipts/{name}-flags.json.gz').read_bytes()))
        assert flags['candidate_sha256']==receipt['candidate_sha256']and flags['original_sha256']==receipt['original_sha256']
        assert flags['case_count']==len(flags['cases'])==1542 and not flags['failures']and not flags['compute_differences']
        assert all(row['original']==row['candidate']for row in flags['cases'])
        assert {(r['cap'],r['pool'],r['flag_hex'])for r in flags['cases']}=={(cap,pool,flag)for cap in (0,1000,2**128-1)for pool in (0,1)for flag in ['']+[bytes([b]).hex()for b in range(256)]}
    spec=importlib.util.spec_from_file_location('integration_analysis',HERE/'analyze.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    report=module.analyze();assert report==json.loads(gzip.decompress((HERE/'analysis.json.gz').read_bytes()))
    for label,expect in meta['expected'].items():
        r=report['variants'][label]
        assert len(r['unique_pairs'])==expect['unique']and len(r['unmatched_original'])==expect['unmatched']and r['candidate_windows']==expect['windows']
        assert r['unique_raw_pairs']==58 and not r['equals_original_capture']and not r['equals_original_elf_extent']
    for label in ['predicate','origins']:
        assert report['deltas'][label]==dict(added_original_windows=[700568],lost_original_windows=[])
        assert report['predicates'][label]['panic_callee']['signature']==report['predicates']['original']['panic_callee']['signature']
        assert report['predicates'][label]['panic_callee']['message']=='attempt to add with overflow'
        assert len(report['predicates'][label]['callers'])==1
    assert len(report['predicates']['original']['callers'])==4
    assert report['predicates']['origins']['location']==report['predicates']['original']['location']==meta['source_location']
    receipt=json.loads(gzip.decompress((HERE/'receipts/origins-full.json.gz').read_bytes()))
    expected=[]
    for name,suite in receipt['suites'].items():
        for i,row in enumerate(suite.get('cases',[])):
            if isinstance(row.get('original'),dict):
                logs=[s for s in row['original'].get('logs',[])if 'panicked at pump-fees-math/src/lib.rs:28:9'in s]
                if logs:
                    assert logs==[s for s in row['candidate'].get('logs',[])if 'panicked at pump-fees-math/src/lib.rs:28:9'in s]
                    expected.append(dict(suite=name,index=i,case=row['case'],panic=logs))
    assert expected==load(HERE/'diagnostic-cases.json')and expected
    print(f'PASS: 357 unique pairs; 81 unmatched; one new helper and no losses; {len(expected)} recovered overflow diagnostics; 34,662 suite cases and 3,084 exact focused comparisons')

if __name__=='__main__':main()

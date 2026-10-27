"""Validate the source experiments and full-body/callee evidence without a compiler."""
from pathlib import Path
import difflib,gzip,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(p.read_text())
def main():
    manifest=load(HERE/'manifest.json');actual={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()and p.name!='manifest.json'and '__pycache__'not in p.parts};assert actual==set(manifest)
    for n,h in manifest.items():
        p=HERE/n;assert not p.is_symlink()and p.resolve().is_relative_to(HERE)and sha(p.read_bytes())==h,n
    for n,h in load(HERE/'parents.json').items():assert sha((ROOT/n).read_bytes())==h,n
    e=load(HERE/'experiment.json');parent=load(ROOT/e['parent']/'experiment.json');assert e['control_reused']and e['variants']['control']['input_sha256']==parent['variants']['origins']['input_sha256']
    for k in ['candidate','symbols']:assert all(e['variants']['control']['files'][k][x]==parent['variants']['origins']['files'][k][x]for x in ['sha256','bytes'])
    diffs={}
    for name,v in e['variants'].items():
        assert len(v['input_sha256'])==35 and set(v['input_sha256'])==set(v['source_paths'])
        for n,h in v['input_sha256'].items():assert sha((ROOT/v['source_paths'][n]).read_bytes())==h,n
        launch=load(HERE/f'builds/{name}-launch.json');result=load(HERE/f'builds/{name}-result.json');log=(HERE/f'builds/{name}-build.log').read_bytes()
        assert launch['inputs']==v['input_sha256']and result['source_unchanged']and result['exit_code']==0
        assert launch['rustc_sha256']=='c8807b7ebede8578ac5a257ea333780f9d89bd356064fd8184af7e996cb71a97'
        assert 'sbpf-solana-solana'in launch['command']and 'RUSTFLAGS=-Zremap-cwd-prefix='in launch['command']
        assert sha(log)==result['log_sha256']and log.count(b'--crate-name pump_fees_candidate ')==1
        assert result['candidate_sha256']==v['files']['candidate']['sha256']and result['symbols_sha256']==v['files']['symbols']['sha256']
        if name!='control':
            diffs[name]={}
            for n,h in e['variants']['control']['input_sha256'].items():
                if v['input_sha256'][n]!=h:
                    old=(ROOT/e['variants']['control']['source_paths'][n]).read_text().splitlines(True);new=(ROOT/v['source_paths'][n]).read_text().splitlines(True)
                    diffs[name][n]=''.join(difflib.unified_diff(old,new,fromfile='control/'+n,tofile=name+'/'+n))
    assert diffs==load(HERE/'source-diffs.json')
    paths=lambda name: {n:(ROOT/p).read_text()for n,p in e['variants'][name]['source_paths'].items()if n.endswith('.rs')}
    variants={n:paths(n)for n in e['variants']};types='programs/pump-fees/src/types.rs';state='programs/pump-fees/src/state.rs';root='programs/pump-fees/src/lib.rs'
    assert variants['copy'][types]==variants['clone'][types].replace('#[derive(AnchorSerialize, AnchorDeserialize, Clone)]\npub struct FeeTier','#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy)]\npub struct FeeTier')
    assert variants['usize'][state]==variants['copy'][state].replace('require_gte!(50,','require_gte!(50usize,')
    changed={n for n,h in e['variants']['control']['input_sha256'].items()if e['variants']['origins']['input_sha256'][n]!=h};assert changed=={types,state,root}
    spec=importlib.util.spec_from_file_location('tier_analysis',HERE/'analyze.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);r=a.analyze();assert r==json.loads(gzip.decompress((HERE/'analysis.json.gz').read_bytes()))
    for name,expect in e['expected'].items():
        row=r['variants'][name];assert len(row['unique_pairs'])==expect['unique']and len(row['unmatched_original'])==expect['unmatched']and row['candidate_windows']==expect['windows'];assert not row['equals_original_capture']and not row['equals_original_elf_extent']
    expected={'clone':[54864],'copy':[54864,784168],'usize':[54864,784168],'all':[54864,261816,784168],'origins':[54864,261816,265976,784168]}
    for name,gains in expected.items():assert r['deltas'][name]==dict(added_original_windows=gains,lost_original_windows=[])
    assert sum(len(x['calls'])for x in r['recovered'])==57
    for row,lines,stores in [(r['recovered'][1],[383,385,405,411,418],[16,8,0]),(r['recovered'][2],[436,438,458,464,471],[40,32,24])]:
        assert row['bytes']==4160 and row['origins']['error_lines']==lines and row['origins']['error_codes']==[6002,6004,6003,6006,6005]and row['origins']['final_vector_stores']==stores
    full=json.loads(gzip.decompress((HERE/'receipts/origins-full.json.gz').read_bytes()));assert full['candidate_sha256']==e['variants']['origins']['files']['candidate']['sha256']and full['case_count']==17331 and len(full['suites'])==18 and not full['mismatches']
    for s in full['suites'].values():assert s['candidate_sha256']==full['candidate_sha256']and s['original_sha256']==full['original_sha256']and not s.get('mismatches',s.get('failures',[]))
    flags=json.loads(gzip.decompress((HERE/'receipts/origins-flags.json.gz').read_bytes()));assert flags['case_count']==len(flags['cases'])==1542 and flags['candidate_sha256']==full['candidate_sha256']and flags['original_sha256']==full['original_sha256']and not flags['failures']and not flags['compute_differences'];assert all(x['original']==x['candidate']for x in flags['cases']);assert {(x['cap'],x['pool'],x['flag_hex'])for x in flags['cases']}=={(cap,pool,flag)for cap in (0,1000,2**128-1)for pool in (0,1)for flag in ['']+[bytes([b]).hex()for b in range(256)]}
    for name,count in [('config',625),('upsert',578)]:
        receipt=json.loads(gzip.decompress((HERE/f'receipts/clone-{name}.json.gz').read_bytes()));assert receipt['candidate_sha256']==e['variants']['clone']['files']['candidate']['sha256']and receipt['case_count']==count and not receipt['mismatches']
    for n,h in load(ROOT/'research/fees-sharing-owned-legacy/experiment.json')['harness_sha256'].items():assert sha((ROOT/n).read_bytes())==h,n
    print('PASS: 366 unique pairs; 72 unmatched; four gains and no losses; 57 callee bindings; 17,331 suite and 1,542 exact focused comparisons')
if __name__=='__main__':main()

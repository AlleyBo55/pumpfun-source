"""Exercise precedence-receipt integrity, literal flags and false size matches."""
from pathlib import Path
import copy,gzip,importlib.util,json,struct,unittest
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('precedence_verify',HERE/'verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
s=importlib.util.spec_from_file_location('precedence_analysis',HERE/'analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
class ScopeTests(unittest.TestCase):
    def test_changed_result_is_not_hidden_by_match_flag(self):
        r=json.loads(gzip.decompress((HERE/'receipts/origins-precedence.json.gz').read_bytes()));r['cases'][0]['candidate']['error']='changed'
        with self.assertRaises(AssertionError):v.check_boundary(r)
    def test_same_length_is_not_a_body_match(self):
        e=json.loads((HERE/'experiment.json').read_text());o=(a.ROOT/'evidence/original/pump_fees/deployed.so').read_bytes();c=gzip.decompress((HERE/e['variants']['argument_order']['files']['symbols']['path']).read_bytes());f=next(f for f in a.wm.windows(o)if f['address']==88552);g=next(f for f in a.wm.windows(c)if '19pump_fees_candidate20set_exotic_flat_fees'in f['name']);self.assertEqual(f['bytes'],g['bytes']);self.assertNotEqual(f['signature'],g['signature'])
    def test_realloc_flag_read_tracks_changed_instruction(self):
        e=json.loads((HERE/'experiment.json').read_text());c=gzip.decompress((HERE/e['variants']['origins']['files']['symbols']['path']).read_bytes());fs=a.wm.windows(c);f=next(f for f in fs if '19pump_fees_candidate20set_exotic_flat_fees'in f['name']);targets={k:next(x['address']for x in fs if term in x['name'])for k,term in [('data_len','8data_len'),('realloc','7realloc'),('validate','20set_exotic_flat_fees')] if k!='validate'};targets['validate']=next(x['address']for x in fs if 'types..FeeConfig' in x['name']and '20set_exotic_flat_fees'in x['name']);site=a.behavior_sites(c,f,targets);self.assertEqual(site['realloc_zero_init'],0);address=f['address']+site['calls']['realloc']-4;sec=next(s for s in a.wm.m.elf_layout(c)['sections']if s['type']!=8 and s['address']<=address< s['address']+s['size']);off=sec['offset']+address-sec['address'];changed=bytearray(c);changed[off:off+4]=struct.pack('<i',1);self.assertEqual(a.behavior_sites(bytes(changed),f,targets)['realloc_zero_init'],1)
if __name__=='__main__':unittest.main()

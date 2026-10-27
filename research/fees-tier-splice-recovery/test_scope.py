"""Make sure the full-body check does not substitute for call/data checks."""
from pathlib import Path
import gzip,importlib.util,json,struct,unittest
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('tier_scope',HERE/'analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
class ScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        e=json.loads((HERE/'experiment.json').read_text());cls.original=(a.ROOT/'evidence/original/pump_fees/deployed.so').read_bytes();cls.image=gzip.decompress((HERE/e['variants']['origins']['files']['symbols']['path']).read_bytes());cls.left=a.wm.windows(cls.original);cls.right=a.wm.windows(cls.image);r=a.wm.compare(cls.left,cls.right);cls.pair=next(p for p in r['unique_pairs']if p['original']['address']==261816)
    def replace(self,address,raw):
        s=next(s for s in a.wm.m.elf_layout(self.image)['sections']if s['type']!=8 and s['address']<=address and address+len(raw)<=s['address']+s['size']);off=s['offset']+address-s['address'];b=bytearray(self.image);b[off:off+len(raw)]=raw;return bytes(b)
    def test_call_target_is_checked_beyond_mask(self):
        p=self.pair;f=p['candidate'];off=next(iter(a.local_calls(self.image,f)));image=self.replace(f['address']+off+4,struct.pack('<i',-(off+8)//8));windows=a.wm.windows(image);changed=next(x for x in windows if x['address']==f['address']);self.assertEqual(changed['signature'],f['signature'])
        with self.assertRaises(AssertionError):a.calls(self.original,image,p['original'],changed,self.left,windows)
    def test_source_line_is_not_masked(self):
        f=self.pair['candidate'];r=next(r for r in a.wm.m.instructions(self.image,f['address'],f['bytes'])if r['opcode']==0x62 and r['displacement']==-256);image=self.replace(f['address']+r['offset']+4,struct.pack('<i',382));changed=next(x for x in a.wm.windows(image)if x['address']==f['address']);self.assertNotEqual(changed['signature'],f['signature'])
    def test_vector_field_offset_is_not_masked(self):
        f=self.pair['candidate'];r=next(r for r in a.wm.m.instructions(self.image,f['address'],f['bytes'])if r['opcode']==0x7b and r['destination']==2);image=self.replace(f['address']+r['offset']+2,struct.pack('<h',17));changed=next(x for x in a.wm.windows(image)if x['address']==f['address']);self.assertNotEqual(changed['signature'],f['signature'])
if __name__=='__main__':unittest.main()

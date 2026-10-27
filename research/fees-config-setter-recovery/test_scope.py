"""Check the call/data details that body normalization alone cannot prove."""
from pathlib import Path
import gzip,importlib.util,json,struct,unittest
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('setter_scope',HERE/'analyze.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class ScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        e=json.loads((HERE/'experiment.json').read_text());cls.original=(a.ROOT/'evidence/original/pump_fees/deployed.so').read_bytes();cls.image=gzip.decompress((HERE/e['variants']['origins']['files']['symbols']['path']).read_bytes());cls.left=a.wm.windows(cls.original);cls.right=a.wm.windows(cls.image);r=a.wm.compare(cls.left,cls.right);cls.pair=next(p for p in r['unique_pairs']if p['original']['address']==260568)
    def replace(self,address,raw):
        s=next(s for s in a.wm.m.elf_layout(self.image)['sections']if s['type']!=8 and s['address']<=address and address+len(raw)<=s['address']+s['size']);offset=s['offset']+address-s['address'];image=bytearray(self.image);image[offset:offset+len(raw)]=raw;return bytes(image)
    def test_retargeted_call_still_normalizes_but_fails_binding(self):
        p=self.pair;right=p['candidate'];offset=next(iter(a.local_calls(self.image,right)));image=self.replace(right['address']+offset+4,struct.pack('<i',-(offset+8)//8));windows=a.wm.windows(image);changed=next(f for f in windows if f['address']==right['address']);self.assertEqual(changed['signature'],right['signature'])
        with self.assertRaises(AssertionError):a.paired_calls(self.original,image,p['original'],changed,self.left,windows)
    def test_error_line_is_not_masked(self):
        right=self.pair['candidate'];row=next(r for r in a.wm.m.instructions(self.image,right['address'],right['bytes'])if r['opcode']==0x62 and r['displacement']==-248);image=self.replace(right['address']+row['offset']+4,struct.pack('<i',364));changed=next(f for f in a.wm.windows(image)if f['address']==right['address']);self.assertNotEqual(changed['signature'],right['signature'])
    def test_origin_string_requires_separate_read(self):
        right=self.pair['candidate'];address=next(r['lddw_value']for r in a.wm.m.instructions(self.image,right['address'],right['bytes'])if r['offset']==480);image=self.replace(address,b'q');changed=next(f for f in a.wm.windows(image)if f['address']==right['address']);self.assertEqual(changed['signature'],right['signature']);self.assertNotEqual(a.origin_and_fields(image,changed)['file'],a.origin_and_fields(self.image,right)['file'])
if __name__=='__main__':unittest.main()

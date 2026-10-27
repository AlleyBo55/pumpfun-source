"""Check that duplicate-body attribution depends on actual callee targets."""
from pathlib import Path
import gzip,importlib.util,json,struct,unittest
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('event_scope',HERE/'analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
class ScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        e=json.loads((HERE/'experiment.json').read_text());cls.original=(a.ROOT/'evidence/original/pump_fees/deployed.so').read_bytes();cls.image=gzip.decompress((HERE/e['variants']['origins']['files']['symbols']['path']).read_bytes());cls.left=a.wm.windows(cls.original);cls.right=a.wm.windows(cls.image);cls.report=json.loads(gzip.decompress((HERE/'analysis.json.gz').read_bytes()));cls.row=cls.report['callers'][2];cls.l=next(x for x in cls.left if x['address']==cls.row['original']);cls.r=next(x for x in cls.right if x['address']==cls.row['candidate'])
    def replace(self,address,raw):
        sec=next(s for s in a.wm.m.elf_layout(self.image)['sections']if s['type']!=8 and s['address']<=address and address+len(raw)<=s['address']+s['size']);off=sec['offset']+address-sec['address'];b=bytearray(self.image);b[off:off+len(raw)]=raw;return bytes(b)
    def test_same_body_wrong_upsert_has_different_callees(self):
        wrong=next(x for x in self.right if x['address']==self.row['rejected'][0]['candidate']);self.assertEqual(self.r['signature'],wrong['signature']);rows=a.compare_calls(self.original,self.image,self.l,wrong,self.left,self.right);self.assertEqual([x['offset']for x in rows if not x['equal']],[120,448,912])
    def test_mutated_call_survives_mask_but_not_check(self):
        off=next(iter(a.local_calls(self.image,self.r)));image=self.replace(self.r['address']+off+4,struct.pack('<i',-(off+8)//8));windows=a.wm.windows(image);r=next(x for x in windows if x['address']==self.r['address']);self.assertEqual(r['signature'],self.r['signature']);self.assertTrue(any(not x['equal']for x in a.compare_calls(self.original,image,self.l,r,self.left,windows)))
    def test_admin_field_offset_is_not_masked(self):
        row=next(x for x in a.wm.m.instructions(self.image,self.r['address'],self.r['bytes'])if x['opcode']==0x79 and x['source']==7 and x['displacement']==72);image=self.replace(self.r['address']+row['offset']+2,struct.pack('<h',80));r=next(x for x in a.wm.windows(image)if x['address']==self.r['address']);self.assertNotEqual(r['signature'],self.r['signature'])
if __name__=='__main__':unittest.main()

"""A raw-equal instruction section must not hide an altered source pathname."""
from pathlib import Path
import gzip,importlib.util,json,unittest
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('origin_analysis',P/'analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
class OriginScope(unittest.TestCase):
 def test_path_mutation_survives_text_comparison_but_is_rejected(self):
  e=json.loads((P/'experiment.json').read_text());image=gzip.decompress((P/e['variants']['origins']['files']['symbols']['path']).read_bytes());original=(a.ROOT/'evidence/original/pump_fees/deployed.so').read_bytes();target=next(x for x in a.wm.windows(original)if x['address']==358312);f=next(x for x in a.wm.windows(image)if x['signature']==target['signature']);ins={i['offset']:i for i in a.wm.m.instructions(image,f['address'],f['bytes'])};address=ins[2400]['lddw_value'];section=next(s for s in a.wm.m.elf_layout(image)['sections']if s['name']=='.rodata'and s['address']<=address<s['address']+s['size']);offset=section['offset']+address-section['address'];changed=bytearray(image);changed[offset]^=0x20
  self.assertEqual(a.wm.m.section_data(image,'.text'),a.wm.m.section_data(changed,'.text'))
  a.check_origin(a.error_origin(image,f))
  with self.assertRaises(AssertionError):a.check_origin(a.error_origin(changed,f))
if __name__=='__main__':unittest.main()

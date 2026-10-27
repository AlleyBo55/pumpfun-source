"""Changing a referenced owner ID leaves the normalized helper body unchanged."""
from pathlib import Path
import gzip,importlib.util
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('prefix_scope',P/'analyze.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 b=gzip.decompress((P/'artifacts/origins-symbols.so.gz').read_bytes());o=(m.ROOT/'evidence/original/pump_fees/deployed.so').read_bytes();original=next(x for x in m.wm.windows(o)if x['address']==18384);f=next(x for x in m.wm.windows(b)if x['signature']==original['signature']);ins={i['offset']:i for i in m.wm.m.instructions(b,f['address'],f['bytes'])};address=ins[96]['lddw_value'];sec=next(s for s in m.wm.m.elf_layout(b)['sections']if s['address']<=address<s['address']+s['size']);changed=bytearray(b);changed[sec['offset']+address-sec['address']]^=1;changed=bytes(changed)
 assert m.wm.m.section_data(changed,'.text')==m.wm.m.section_data(b,'.text')and m.pointers(changed,f)!=m.pointers(b,f)
 assert next(x for x in m.wm.windows(changed)if x['address']==f['address'])['signature']==f['signature']
 print('PASS: owner-ID mutation preserves instructions and fails the separate data contract')
if __name__=='__main__':main()

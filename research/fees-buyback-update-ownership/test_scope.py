"""Instruction equality does not establish an instruction-message payload."""
from pathlib import Path
import gzip,importlib.util
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('update_scope',P/'analyze.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 b=gzip.decompress((P/'artifacts/origins-symbols.so.gz').read_bytes());f=next(f for f in m.wm.windows(b)if'__global'in(f['name']or'')and'update_buyback_authority'in f['name']);ins={i['offset']:i for i in m.wm.m.instructions(b,f['address'],f['bytes'])};address=ins[40]['lddw_value'];sec=next(s for s in m.wm.m.elf_layout(b)['sections']if s['address']<=address<s['address']+s['size']);changed=bytearray(b);changed[sec['offset']+address-sec['address']]=ord('x');changed=bytes(changed)
 assert m.wm.m.section_data(changed,'.text')==m.wm.m.section_data(b,'.text')
 assert m.constant_data(changed,f,652592)!=m.constant_data(b,f,652592)
 assert next(x for x in m.wm.windows(changed)if x['address']==f['address'])['signature']==f['signature']
 print('PASS: message mutation preserves instructions but fails separate data contract')
if __name__=='__main__':main()

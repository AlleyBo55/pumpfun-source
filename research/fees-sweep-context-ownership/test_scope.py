"""An equal exit instruction body does not establish its referenced labels."""
from pathlib import Path
import gzip,importlib.util
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('sweep_scope',P/'analyze.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 b=gzip.decompress((P/'artifacts/origins-symbols.so.gz').read_bytes());f=next(f for f in m.wm.windows(b)if'SweepBuyback'in(f['name']or'')and'AccountsExit'in f['name']);ins={i['offset']:i for i in m.wm.m.instructions(b,f['address'],f['bytes'])};address=ins[312]['lddw_value'];sec=next(s for s in m.wm.m.elf_layout(b)['sections']if s['address']<=address<s['address']+s['size']);changed=bytearray(b);changed[sec['offset']+address-sec['address']]=ord('x');changed=bytes(changed)
 assert m.wm.m.section_data(changed,'.text')==m.wm.m.section_data(b,'.text')
 assert m.exit_data(changed,f)!=m.exit_data(b,f)
 assert next(x for x in m.wm.windows(changed)if x['address']==f['address'])['signature']==f['signature']
 print('PASS: field-label mutation preserves instructions but fails separate data contract')
if __name__=='__main__':main()

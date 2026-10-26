from pathlib import Path
import argparse,gzip,json
from elf_reader import Elf
from layer_inventory import analyze_images
P=Path(__file__).resolve().parent

def run():
 o=Elf(P/'static-inputs/original.so');before=analyze_images(o,Elf(P/'static-inputs/candidate.so'),Elf(P/'static-inputs/symbols.so'));after=analyze_images(o,Elf(P/'candidate.so'),Elf(P/'unstripped.so'))
 return {'scope':'Both measured here using exactly the same pass01 normalized+relocation-pattern, actual call-fixed-point algorithm. Prior published pass01 used an older Pump candidate and cannot be compared numerically without this new baseline. No data-semantic closure implied.','before':before,'after':after}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();r=run();out=P/'full-before-after-inventory.json.gz'
 if a.check:assert json.loads(gzip.decompress(out.read_bytes()))==r
 else:out.write_bytes(gzip.compress((json.dumps(r,separators=(',',':'))+'\n').encode(),mtime=0))
 print(json.dumps({k:r[k]['summary']for k in ['before','after']},indent=2))

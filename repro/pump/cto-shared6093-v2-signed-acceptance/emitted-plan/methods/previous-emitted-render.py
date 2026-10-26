"""Saved complete candidate-only instruction rendering; no collector entrypoint."""
import struct
def render(O,start,end):
 lines=[];pc=start
 while pc<end:
  op,reg,off,imm=struct.unpack_from('<BBhi',O,pc);dst=reg&15;src=reg>>4;step=8
  if op==24:step=16;t=f'r{dst}=LDDW '+str((imm&0xffffffff)|(struct.unpack_from('<I',O,pc+12)[0]<<32))
  elif op==133:t='CALL '+str(pc+8+imm*8)
  elif op==149:t='EXIT'
  elif op&7 in[1,2,3]:
   w={0:32,8:16,16:8,24:64}[op&24];t=f'r{dst}=u{w}[r{src}{off:+}]'if op&7==1 else f'u{w}[r{dst}{off:+}]='+('r'+str(src)if op&7==3 else str(imm))
  elif op&7 in[5,6]:t=f'JUMP op={op:x} r{dst},'+('r'+str(src)if op&8 else str(imm))+' ->'+str(pc+8+off*8)
  else:t=f'ALU op={op:x} r{dst},'+('r'+str(src)if op&8 else str(imm))
  lines.append(f'{pc}: {O[pc:pc+step].hex():32} {t}');pc+=step
 return '\n'.join(lines)+'\n'

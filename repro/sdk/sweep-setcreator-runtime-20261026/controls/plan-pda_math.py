import hashlib
ALPHABET='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def decode(s):
 n=0
 for c in s:n=n*58+ALPHABET.index(c)
 return b'\0'*(len(s)-len(s.lstrip('1')))+n.to_bytes((n.bit_length()+7)//8,'big')
def encode(b):
 n=int.from_bytes(b,'big');s=''
 while n:n,r=divmod(n,58);s=ALPHABET[r]+s
 return '1'*(len(b)-len(b.lstrip(b'\0')))+s
def on_curve(b):
 # Ed25519 compressed-point decompression: y and the sign of x.
 q=2**255-19;v=int.from_bytes(b,'little');sign=v>>255;y=v&((1<<255)-1)
 if y>=q:return False
 d=(-121665*pow(121666,q-2,q))%q;den=(d*y*y+1)%q
 if den==0:return False
 x2=((y*y-1)*pow(den,q-2,q))%q;x=pow(x2,(q+3)//8,q)
 if x*x%q!=x2:x=x*pow(2,(q-1)//4,q)%q
 return x*x%q==x2 and not(x==0 and sign)
def pda(seeds,program):
 assert len(program)==32 and len(seeds)<16 and all(len(s)<=32 for s in seeds)
 for bump in range(255,-1,-1):
  h=hashlib.sha256(b''.join(seeds)+bytes([bump])+program+b'ProgramDerivedAddress').digest()
  if not on_curve(h):return encode(h)
 raise AssertionError('no PDA bump')

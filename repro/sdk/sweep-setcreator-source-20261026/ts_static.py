"""Small bounded TS lexical reader; data/source only, never execute JavaScript."""
import re

def tokens(source):
 out=[];i=0;n=len(source)
 while i<n:
  c=source[i]
  if c.isspace():i+=1;continue
  if source.startswith('//',i):j=source.find('\n',i);i=n if j<0 else j;continue
  if source.startswith('/*',i):j=source.find('*/',i+2);assert j>=0;i=j+2;continue
  start=i
  if c in "\"'`":
   quote=c;i+=1
   while i<n:
    if source[i]=='\\':i+=2;continue
    if source[i]==quote:i+=1;break
    i+=1
   else:raise ValueError('unclosed literal')
   out.append((source[start:i],start,i));continue
  if c.isalpha()or c in '_$':
   i+=1
   while i<n and(source[i].isalnum()or source[i]in'_$'):i+=1
   out.append((source[start:i],start,i));continue
  if c.isdigit():
   i+=1
   while i<n and(source[i].isalnum()or source[i]in'._'):i+=1
   out.append((source[start:i],start,i));continue
  if c=='/'and(out[-1][0]if out else '')in['(','=',':',',','return','=>','[','!']:
   i+=1;inside=False
   while i<n:
    if source[i]=='\\':i+=2;continue
    if source[i]=='[':inside=True
    elif source[i]==']':inside=False
    elif source[i]=='/'and not inside:
     i+=1
     while i<n and source[i].isalpha():i+=1
     break
    i+=1
   out.append((source[start:i],start,i));continue
  if source.startswith('...',i):i+=3
  elif source.startswith('=>',i)or source.startswith('?.',i):i+=2
  else:i+=1
  out.append((source[start:i],start,i))
 return out

def pairs(ts):
 stack=[];result={};depth={};close={')':'(',']':'[','}':'{'}
 for i,(v,_,_)in enumerate(ts):
  depth[i]=len(stack)
  if v in'([{':stack.append((v,i))
  elif v in')]}':
   assert stack and stack[-1][0]==close[v],('unbalanced',i,v,stack[-1:] )
   _,j=stack.pop();result[j]=i;result[i]=j
 assert not stack,stack[-3:]
 return result,depth

def class_methods(source,ts,ps,depth):
 out=[];classes=[]
 for i,t in enumerate(ts):
  if t[0]!='class'or i+1>=len(ts):continue
  name=ts[i+1][0];j=i+2
  while j<len(ts)and ts[j][0]!='{':j+=1
  if j==len(ts):continue
  classes.append((name,j,ps[j]))
 for owner,start,end in classes:
  # The indentation is a documented bounded extraction convention, not a TS AST.
  regex=r'^  (?P<mods>(?:(?:public|private|protected|static|async|override|readonly)\s+)*)(?P<name>[A-Za-z_$][\w$]*)\s*(?:<[^;{}]*?>\s*)?\('
  lookup={t[1]:i for i,t in enumerate(ts)}
  for m in re.finditer(regex,source,re.M):
   pos=m.start('name');idx=lookup.get(pos)
   if idx is None or not start<idx<end or depth[idx]!=depth[start]+1:continue
   op=next((k for k in range(idx,end)if ts[k][0]=='('),None)
   if op is None:continue
   cp=ps[op];j=cp+1;angle=0;body=None
   while j<end:
    v=ts[j][0]
    if v==';'and angle==0:break
    if v=='<':angle+=1
    elif v=='>':angle=max(0,angle-1)
    elif v=='{':
     if angle==0 and ts[j-1][0]!=':':body=j;break
     j=ps[j]
    elif v in['(', '[']:j=ps[j]
    j+=1
   if body is not None:
    out.append(dict(owner=owner,name=m.group('name'),visibility='private'if'private'in m.group('mods')else'protected'if'protected'in m.group('mods')else'public',declaration_token=idx,body_open=body,body_close=ps[body],start=ts[idx][1],end=ts[ps[body]][2],line=source.count('\n',0,pos)+1))
 return out

def split_items(ts,ps,start,end):
 items=[];last=start;i=start
 while i<end:
  if ts[i][0]in['(','[','{']:i=ps[i]+1;continue
  if ts[i][0]==',':
   if last<i:items.append((last,i))
   last=i+1
  i+=1
 if last<end:items.append((last,end))
 return items

def slice_text(source,ts,a,b):return source[ts[a][1]:ts[b-1][2]]if a<b else''

def object_fields(source,ts,ps,op):
 end=ps[op];fields=[];unknown=[]
 for a,b in split_items(ts,ps,op+1,end):
  key=ts[a][0]
  if key=='...':unknown.append(slice_text(source,ts,a,b));continue
  if not re.fullmatch(r'[A-Za-z_$][\w$]*',key):unknown.append(slice_text(source,ts,a,b));continue
  value=slice_text(source,ts,a+2,b)if a+1<b and ts[a+1][0]==':'else key
  fields.append(dict(key=key,expression=value))
 return fields,unknown

def named_functions(source,ts,ps):
 out=[]
 for i,t in enumerate(ts):
  if t[0]!='function'or i+2>=len(ts)or not re.fullmatch(r'[A-Za-z_$][\w$]*',ts[i+1][0]):continue
  name=ts[i+1][0];j=i+2
  while j<len(ts)and ts[j][0]not in['(',';','{']:j+=1
  if j==len(ts)or ts[j][0]!='(':continue
  j=ps[j]+1;angle=0;body=None
  while j<len(ts):
   v=ts[j][0]
   if v==';'and not angle:break
   if v=='<':angle+=1
   elif v=='>':angle=max(0,angle-1)
   elif v=='{':
    if not angle and ts[j-1][0]!=':':body=j;break
    j=ps[j]
   elif v in['(','[']:j=ps[j]
   j+=1
  if body is not None:out.append(dict(name=name,body_open=body,body_close=ps[body],line=source.count('\n',0,t[1])+1,start=t[1],end=ts[ps[body]][2]))
 return out


def exported_const_declarations(source,ts=None):
 """Top-level semicolon-terminated export const declarations, balanced lexically.

 Strings/templates/comments use tokens() masking; parentheses/brackets/braces
 are skipped via pairs(). No ASI or arbitrary TS AST completeness is claimed.
 """
 ts=tokens(source)if ts is None else ts
 ps,depth=pairs(ts);out=[]
 for i in range(len(ts)-3):
  if depth[i]!=0 or [t[0]for t in ts[i:i+2]]!=['export','const']:continue
  name=ts[i+2][0];assert re.fullmatch(r'[A-Za-z_$][\w$]*',name)
  j=i+3
  while j<len(ts):
   if depth[j]==0 and ts[j][0]=='export':raise ValueError('Next export before declaration terminator: '+name)
   if ts[j][0]in['(','[','{']:j=ps[j]+1;continue
   if ts[j][0]==';'and depth[j]==0:break
   j+=1
  if j==len(ts):raise ValueError('No top-level declaration terminator: '+name)
  out.append(dict(name=name,start=ts[i][1],end=ts[j][2],line=source.count('\n',0,ts[i][1])+1))
 return out

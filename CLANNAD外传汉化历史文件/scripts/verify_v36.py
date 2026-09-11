# -*- coding:utf-8 -*-
import re,struct,csv,hashlib,base64,json,collections,os
R=r'D:\clannad_nsw';orig=open(R+r'\romfs\SCRIPT.PAK','rb').read();cur=open(R+r'\out_zh_v36\SCRIPT.PAK','rb').read();v25=open(R+r'\out_zh_v25\SCRIPT.PAK','rb').read()
print('=== FILE ===')
print('size',len(cur),'orig',len(orig),'equal',len(cur)==len(orig));print('header485',cur[:485]==orig[:485]);print('sha256',hashlib.sha256(cur).hexdigest())
# titles
s25=open(R+r'\build_v25.py',encoding='utf-8').read();m=re.search(r'TITLE_TR\s*=\s*json\.loads\(base64\.b64decode\("([A-Za-z0-9+/=]+)"\)',s25);titles=json.loads(base64.b64decode(m.group(1)).decode())
keep=bad=miss=0
for jp in titles:
 p=orig.find(jp.encode('utf-16-le'))
 if p<2:miss+=1;continue
 L=struct.unpack_from('<H',orig,p-2)[0];sl=slice(p-2,p+2*L)
 if cur[sl]==v25[sl]:keep+=1
 else:bad+=1
print('titles preserved',keep,'bad',bad,'missing',miss)
# body blocks
DECOR=[(b'\xe2\x9d\x9d',b'"'),(b'\xe2\x9d\x9e',b'"'),(b'\xe2\x80\x9c',b'"'),(b'\xe2\x80\x9d',b'"'),(b'\xe2\x80\x98',b"'"),(b'\xe2\x80\x99',b"'"),(b'\xe2\x80\xa6',b'...'),(b'\xc2\xa0',b' '),(b'\xef\xbd\x9e',b'~')]
def isjp(ch):return (0x3040<=ch<=0x30ff) or (0x4e00<=ch<=0x9fff) or (0x3000<=ch<=0x303f) or (0xff00<=ch<=0xff60) or ch in (0x2019,0x201c,0x201d,0x2026,0x3005)
blocks=[];i=0
while i<len(orig)-4:
 L=struct.unpack_from('<H',orig,i)[0]
 if 2<=L<=400 and i+2+2*L<=len(orig):
  ok=0
  for k in range(L):
   ch=struct.unpack_from('<H',orig,i+2+2*k)[0]
   if isjp(ch):ok+=1
   else:break
  if ok>=max(2,L-1):
   je=i+2+2*L;m2=re.search(rb'[\x20-\x7e]{4,}',orig[je:je+90])
   if m2 and m2.start()<=8:blocks.append((i,L,i+2,je));i=je;continue
 i+=1
unch=[];badlen=[];ctrl=[];rep=[];empty=[]
for off,cap,js,je in blocks:
 if cur[off:je]==orig[off:je]:unch.append((off,cap))
 L=struct.unpack_from('<H',cur,off)[0]
 if L<1 or L>cap:badlen.append((off,cap,L));continue
 txt=cur[off+2:off+2+2*L].decode('utf-16-le','replace')
 if not txt:empty.append(off)
 if '\ufffd' in txt:rep.append((off,txt))
 cc=[ord(c) for c in txt if ord(c)<32 and c not in '\t\r\n']
 if cc:ctrl.append((off,cc,txt))
print('body blocks',len(blocks),'unchanged',len(unch),'badlen',len(badlen),'empty',len(empty),'controls',len(ctrl),'replacement',len(rep))
# exact v36 repair checks
fix=list(csv.DictReader(open(R+r'\v36_trunc_fixes.tsv',encoding='utf-8'),delimiter='\t'));mismatch=[]
for r in fix:
 o=int(r['offset']);cap=int(r['cap']);L=struct.unpack_from('<H',cur,o)[0];txt=cur[o+2:o+2+2*L].decode('utf-16-le','replace')
 if txt!=r['chinese'] or L!=len(r['chinese']) or L>cap:mismatch.append((o,cap,L,r['chinese'],txt))
print('former trunc fixes',len(fix),'mismatch',len(mismatch),'punct',sum(r['kind']=='punct' for r in fix),'manual',sum(r['kind']=='manual' for r in fix))
# check no old smart-cut ending U+2026 can be proven? report candidate endings only
print('fix ending ellipsis',sum(r['chinese'].endswith('…') for r in fix),'ending punctuation',collections.Counter(r['chinese'][-1:] for r in fix).most_common(12))
# top-level diff byte count
print('bytes changed vs v35',sum(a!=b for a,b in zip(cur,open(R+r'\out_zh_v35\SCRIPT.PAK','rb').read())))

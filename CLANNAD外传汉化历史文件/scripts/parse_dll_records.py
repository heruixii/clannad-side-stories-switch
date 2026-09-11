# -*- coding:utf-8 -*-
from pathlib import Path
import re,collections
root=Path(r'D:\switch游戏\个人汉化\clannad 外传\pc汉化版\《Clannad》外传——《被光守望着的坡道》\CLANNAD被光守望着的坡道（CLANNAD 光見守る坂道で）')
d=(root/'CJXHook.dll').read_bytes()
# opcode record: 0A <pc u16> 40 <resource_index u16> 22 <payload> 22 0A
pat=re.compile(rb'\x0a(..)\x40(..)\x22(.*?)\x22\x0a',re.S)
recs=[]
for m in pat.finditer(d):
 pc=int.from_bytes(m.group(1),'little'); idx=int.from_bytes(m.group(2),'little'); raw=m.group(3)
 # Keep plausible text record: short, no NUL/control except tabs, decodes GBK
 if len(raw)>1000 or b'\x00' in raw: continue
 try: txt=raw.decode('gbk')
 except: continue
 # payload is padded with ASCII spaces
 txt=txt.rstrip(' ')
 # reject implausible raw binary pretending to be a string
 if any(ord(c)<32 and c not in '\t\r\n' for c in txt):continue
 recs.append((m.start(),pc,idx,txt,raw))
print('total plausible opcode-text records',len(recs))
print('first 60:')
for r in recs[:60]: print(hex(r[0]),'pc',r[1],'idx',r[2],r[3].encode('unicode_escape').decode('ascii'))
# detect index resets/decreases
resets=[]
prev=None
for i,r in enumerate(recs):
 if prev is not None and r[2] <= prev:resets.append((i,prev,r[2],r[0]))
 prev=r[2]
print('\nresets/decreases',len(resets));print(resets[:80])
# segments by decreases, summarize idx coverage and likely Chinese density
bounds=[0]+[x[0] for x in resets]+[len(recs)]
print('\nsegments',len(bounds)-1)
for si,(a,b) in enumerate(zip(bounds,bounds[1:])):
 seg=recs[a:b]; inds=[x[2] for x in seg];
 if not seg:continue
 han=sum(sum('\u4e00'<=c<='\u9fff' for c in x[3]) for x in seg)
 print(si,'n',len(seg),'idx',min(inds),max(inds),'firstpos',hex(seg[0][0]),'lastpos',hex(seg[-1][0]),'han',han,'first=',seg[0][3][:50].encode('unicode_escape').decode('ascii'))
# duplicate idx within each segment

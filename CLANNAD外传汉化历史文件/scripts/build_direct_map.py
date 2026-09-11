# -*- coding:utf-8 -*-
from pathlib import Path
import re,collections,csv
PC=Path(r'D:\switch游戏\个人汉化\clannad 外传\pc汉化版\《Clannad》外传——《被光守望着的坡道》\CLANNAD被光守望着的坡道（CLANNAD 光見守る坂道で）')
WORK=Path(r'D:\switch游戏\个人汉化\clannad 外传\work\pc_seen_src')
d=(PC/'CJXHook.dll').read_bytes()
pat=re.compile(rb'\x0a(..)\x40(..)\x22(.*?)\x22\x0a',re.S)
recs=[]
for m in pat.finditer(d):
 pc=int.from_bytes(m.group(1),'little');kid=int.from_bytes(m.group(2),'little');raw=m.group(3)
 if len(raw)>1000 or b'\x00' in raw:continue
 try:txt=raw.decode('gbk').rstrip(' ')
 except:continue
 if any(ord(c)<32 and c not in '\t\r\n' for c in txt):continue
 recs.append((m.start(),pc,kid,txt))
# segment at kidoku resets/decreases
cuts=[0]
for i in range(1,len(recs)):
 if recs[i][2] <= recs[i-1][2]:cuts.append(i)
cuts.append(len(recs));segs=[recs[a:b] for a,b in zip(cuts,cuts[1:])]
assert len(segs)==16,len(segs)
allout=[];summary=[];unmapped=[];dupres=[]
for ep in range(1,17):
 org=(WORK/f'SEEN{ep:04d}.org').read_text(encoding='utf-8',errors='replace')
 # kidoku -> res; allow whitespace/newlines between marker and resource
 km={int(k):int(r) for k,r in re.findall(r'\{-\s*kidoku\s+(\d+)\s+line\s+\d+\s*-\}\s*#res<(\d+)>',org)}
 # English resource map
 utf=(WORK/f'SEEN{ep:04d}.utf').read_text(encoding='utf-8',errors='replace')
 em={int(i):t.rstrip('\r') for i,t in re.findall(r'^<(\d+)>\s?(.*)$',utf,re.M)}
 seenres=collections.defaultdict(list); mapped=0
 for pos,pc,kid,cn in segs[ep-1]:
  rid=km.get(kid)
  if rid is None:
   unmapped.append((ep,pos,kid,cn));continue
  mapped+=1;seenres[rid].append((kid,cn,pos));allout.append((ep,rid,kid,em.get(rid,''),cn,pos))
 for rid,arr in seenres.items():
  if len(arr)>1:dupres.append((ep,rid,arr))
 missing=sorted(set(em)-set(seenres)); extra=sorted(set(seenres)-set(em))
 summary.append((ep,len(em),len(segs[ep-1]),mapped,len(seenres),len(missing),len(extra),min(km) if km else None,max(km) if km else None))
 print(f'EP{ep:02d}: EN={len(em)} DLLrec={len(segs[ep-1])} mapped={mapped} uniqueRes={len(seenres)} missingCN={len(missing)} extraRes={len(extra)}')
 print('  missing rid',missing[:40])
print('\nTOTAL direct',len(allout),'unique scene/res',len({(x[0],x[1]) for x in allout}),'unmapped kid',len(unmapped),'dup res groups',len(dupres))
print('TOTAL EN',sum(x[1] for x in summary),'missingCN',sum(x[5] for x in summary))
if unmapped:
 print('\nUNMAPPED KID examples')
 for x in unmapped[:50]:print(x[0],hex(x[1]),x[2],x[3].encode('unicode_escape').decode('ascii'))
if dupres:
 print('\nDUP RES examples')
 for x in dupres[:20]:print(x[0],x[1],[(a,b.encode('unicode_escape').decode('ascii')) for a,b,_ in x[2]])
# export deterministic table
out=Path(r'D:\clannad_nsw\pc_dll_direct_map.tsv')
with out.open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['episode','resource_id','kidoku','english','chinese','dll_offset'])
 for x in sorted(allout,key=lambda z:(z[0],z[1],z[2])):w.writerow(x)
print('\nwrote',out,out.stat().st_size)

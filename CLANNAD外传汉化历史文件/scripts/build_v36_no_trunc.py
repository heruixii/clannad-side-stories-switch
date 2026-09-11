# -*- coding:utf-8 -*-
import csv,struct,os,hashlib,re,base64,json,collections
R=r'D:\clannad_nsw'; orig=open(R+r'\romfs\SCRIPT.PAK','rb').read(); base=bytearray(open(R+r'\out_zh_v35\SCRIPT.PAK','rb').read())
# collect all 336 replacement candidates
cand={}; meta={}
# punctuation-only 110
with open(R+r'\trunc_punct_fit.tsv',encoding='utf-8') as f:
 for r in csv.DictReader(f,delimiter='\t'):
  o=int(r['offset']); cand[o]=r['candidate']; meta[o]=('punct',int(r['episode']),int(r['rid']),r['switch_en'])
# manual 226
for fn in ['trunc_manual_batch1.tsv','trunc_manual_batch2.tsv','trunc_manual_batch3.tsv']:
 with open(R+'\\'+fn,encoding='utf-8') as f:
  for r in csv.DictReader(f,delimiter='\t'):
   o=int(r['offset'])
   if o in cand: raise RuntimeError(('duplicate',o,fn))
   cand[o]=r['candidate_cn']; meta[o]=('manual',int(r['episode']),int(r['rid']),r['switch_en'])
# original trunc set
trunc={int(r['offset']):r for r in csv.DictReader(open(R+r'\trunc_v35_all.tsv',encoding='utf-8'),delimiter='\t')}
print('candidate total',len(cand),'trunc total',len(trunc),'missing',len(set(trunc)-set(cand)),'extra',len(set(cand)-set(trunc)))
assert set(cand)==set(trunc)
# write, strict capacity
rows=[]
for o,t in sorted(cand.items()):
 cap=struct.unpack_from('<H',orig,o)[0]
 if len(t)>cap: raise ValueError((o,cap,len(t),t))
 st=o+2;en=st+2*cap;zb=t.encode('utf-16-le');base[st:en]=zb+bytes(2*cap-len(zb));struct.pack_into('<H',base,o,len(t))
 kind,ep,rid,swen=meta[o];rows.append((o,ep,rid,cap,kind,swen,t))
outdir=R+r'\out_zh_v36';os.makedirs(outdir,exist_ok=True);op=outdir+r'\SCRIPT.PAK';open(op,'wb').write(base)
with open(R+r'\v36_trunc_fixes.tsv','w',encoding='utf-8',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['offset','episode','rid','cap','kind','switch_en','chinese']);w.writerows(rows)
print('wrote',op,'size',len(base),'same',len(base)==len(orig),'header485',bytes(base[:485])==orig[:485])
print('sha256',hashlib.sha256(base).hexdigest())

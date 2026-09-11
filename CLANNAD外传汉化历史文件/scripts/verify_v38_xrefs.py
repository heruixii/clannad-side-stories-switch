from pathlib import Path
import struct,hashlib,zipfile
R=Path(r'D:\clannad_nsw')
b=(R/'ui_main_zh_v38'/'main_ui_zh_uncompressed.nso').read_bytes(); text_fo=0x100;text_sz=0x25c950
old={'Help':0x28be05-0x100,'No':0x28c2cd-0x100,'On':0x28cee9-0x100}
new={'Help':0x29453d-0x100,'No':0x294544-0x100,'On':0x294548-0x100}
def sx(v,n): return v-(1<<n) if v&(1<<(n-1)) else v
def adrp(ins,pc):
 immlo=(ins>>29)&3;immhi=(ins>>5)&0x7ffff;imm=sx((immhi<<2)|immlo,21)<<12;return (pc&~0xfff)+imm
refs={k:{'old':0,'new':0} for k in old}
for i in range(text_fo,text_fo+text_sz-4,4):
 ins=struct.unpack_from('<I',b,i)[0]
 if (ins&0x9f000000)!=0x90000000: continue
 pc=i-text_fo; reg=ins&31; page=adrp(ins,pc)
 for j in range(i+4,min(i+4*13,text_fo+text_sz),4):
  x=struct.unpack_from('<I',b,j)[0]
  if (x&0xff000000)==0x91000000 and ((x>>5)&31)==reg:
   val=((x>>10)&0xfff) << (12 if ((x>>22)&1) else 0); tgt=page+val
   for k in refs:
    if tgt==old[k]: refs[k]['old']+=1
    if tgt==new[k]: refs[k]['new']+=1
for k,v in refs.items(): print(k,v)
assert refs['Help']=={'old':0,'new':1}
assert refs['No']=={'old':0,'new':1}
assert refs['On']=={'old':0,'new':2}
print('xref_audit=PASS')

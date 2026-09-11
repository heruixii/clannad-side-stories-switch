from pathlib import Path
import struct,hashlib
R=Path(r'D:\clannad_nsw')
orig=(R/'exefs'/'main.nso.uncompressed').read_bytes()
base=bytearray((R/'ui_main_zh'/'main_ui_zh_uncompressed.nso').read_bytes())
# Use zero tail of already-shortened Blue Level string slot.
host=0x294515; zhbytes=39
assert base[host+zhbytes]==0
help_fo=host+zhbytes+1
help_b='帮助'.encode('utf-8')+b'\0'
no_fo=help_fo+len(help_b)
no_b='否'.encode('utf-8')+b'\0'
on_fo=no_fo+len(no_b)
on_b='开'.encode('utf-8')+b'\0'
end=on_fo+len(on_b)
assert end <= host+108
assert all(x==0 for x in base[help_fo:end])
base[help_fo:help_fo+len(help_b)]=help_b
base[no_fo:no_fo+len(no_b)]=no_b
base[on_fo:on_fo+len(on_b)]=on_b

# file->memory for rodata in this NSO is -0x100
new_targets={'Help':help_fo-0x100,'No':no_fo-0x100,'On':on_fo-0x100}
xrefs={
 'Help':[(0x5848,0x584c)],
 'No':[(0x2ac4,0x2ac8)],
 'On':[(0x214094,0x214098),(0x215884,0x215888)],
}

def sx(v,b): return v-(1<<b) if v&(1<<(b-1)) else v

def enc_adrp(old, pc, target):
 page=target & ~0xfff; pcpage=pc & ~0xfff
 imm=(page-pcpage)>>12
 if not (-(1<<20)<=imm<(1<<20)): raise ValueError('ADRP range')
 u=imm & ((1<<21)-1); immlo=u&3; immhi=(u>>2)&0x7ffff
 return (old & ~((3<<29)|(0x7ffff<<5))) | (immlo<<29) | (immhi<<5)

def enc_add(old,target):
 imm=target&0xfff
 return (old & ~((1<<22)|(0xfff<<10))) | (imm<<10)

def dec_adrp(ins,pc):
 immlo=(ins>>29)&3; immhi=(ins>>5)&0x7ffff; imm=sx((immhi<<2)|immlo,21)<<12
 return (pc&~0xfff)+imm

def dec_add(ins): return ((ins>>10)&0xfff) << (12 if ((ins>>22)&1) else 0)

for name,pairs in xrefs.items():
 tgt=new_targets[name]
 for adrp_fo,add_fo in pairs:
  olda=struct.unpack_from('<I',base,adrp_fo)[0]; oldb=struct.unpack_from('<I',base,add_fo)[0]
  pc=adrp_fo-0x100
  na=enc_adrp(olda,pc,tgt); nb=enc_add(oldb,tgt)
  struct.pack_into('<I',base,adrp_fo,na); struct.pack_into('<I',base,add_fo,nb)
  got=dec_adrp(na,pc)+dec_add(nb)
  print(name,'xref',hex(adrp_fo),hex(add_fo),'target',hex(tgt),'decoded',hex(got),'ok',got==tgt)
  assert got==tgt

# Verify relocated strings.
for name,fo in [('Help',help_fo),('No',no_fo),('On',on_fo)]:
 e=base.index(0,fo); print(name,'file',hex(fo),'mem',hex(fo-0x100),'bytes',base[fo:e], 'text',base[fo:e].decode())

final=bytes(base)
outdir=R/'ui_main_zh_v38';outdir.mkdir(exist_ok=True)
(outdir/'main_ui_zh_uncompressed.nso').write_bytes(final)
# Build IPS from contiguous byte diffs, splitting at 65535.
ips=bytearray(b'PATCH'); i=0; rec=0
while i<len(orig):
 if orig[i]==final[i]: i+=1; continue
 start=i
 while i<len(orig) and orig[i]!=final[i] and i-start<65535: i+=1
 data=final[start:i]
 assert start<0x1000000 and len(data)>0
 ips+=start.to_bytes(3,'big')+len(data).to_bytes(2,'big')+data; rec+=1
ips+=b'EOF'
bid='AB53346DF8D55798AB3304D1712F9966C3999D1D'
(outdir/(bid+'.ips')).write_bytes(ips)
# Apply IPS back.
chk=bytearray(orig);p=5;rr=0
while ips[p:p+3]!=b'EOF':
 off=int.from_bytes(ips[p:p+3],'big');n=int.from_bytes(ips[p+3:p+5],'big');p+=5
 if n: chk[off:off+n]=ips[p:p+n];p+=n
 else:
  rlen=int.from_bytes(ips[p:p+2],'big');v=ips[p+2];p+=3;chk[off:off+rlen]=bytes([v])*rlen
 rr+=1
assert bytes(chk)==final
print('diff_records',rec,'apply_records',rr,'ips_bytes',len(ips),'verify=PASS')
print('final_sha256',hashlib.sha256(final).hexdigest())
print('ips_sha256',hashlib.sha256(ips).hexdigest())
print('ips',outdir/(bid+'.ips'))

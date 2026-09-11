# -*- coding:utf-8 -*-
import csv,struct,os,hashlib,ast
R=r'D:\clannad_nsw'; ORIG=R+r'\romfs\SCRIPT.PAK'; BASE=R+r'\out_zh_v34\SCRIPT.PAK'
orig=open(ORIG,'rb').read(); base=bytearray(open(BASE,'rb').read())
# Remaining set from v35 table
remaining={}
with open(R+r'\v35_local_candidates.tsv',encoding='utf-8') as f:
    for r in csv.DictReader(f,delimiter='\t'):
        remaining[int(r['offset'])]=(int(r['episode']),int(r['cap']),r['switch_en'])
assert len(remaining)==128,len(remaining)
# Direct DLL CN
D={}
with open(R+r'\pc_dll_direct_map.tsv',encoding='utf-8') as f:
    for r in csv.DictReader(f,delimiter='\t'):
        D[(int(r['episode']),int(r['resource_id']))]=r['chinese']
# One Switch slot -> one deterministic PC resource
ONE={
 9254:(1,61),24332:(1,164),27914:(1,188),34406:(1,228),
 62400:(2,163),65666:(2,183),
 147190:(4,156),155942:(4,228),162924:(4,280),
 177768:(5,1),179580:(5,16),
 286776:(6,154),289250:(6,173),289920:(6,179),
 354396:(7,1),358326:(7,29),
 475722:(8,262),
 511938:(10,153),
 531654:(11,0),551518:(11,141),558282:(11,180),560462:(11,198),
 326092:(12,106),349838:(12,254),
 412332:(13,79),412632:(13,80),
 616658:(14,225),618716:(14,237),
 707346:(16,109),
}
# One PC resource -> multiple Switch slots. Chinese is distributed across capacities.
SPLIT={
 (62706,62816):(2,165),
 (288876,288944):(6,171),
 (293092,293274):(6,197),
 (295508,295612,295748):(6,212),
 (295986,296160):(6,214),
 (303316,303430):(6,258),
 (442576,442646):(8,23),
 (445850,446008):(8,46),
 (474592,474680,474732):(8,254),
 (480142,480230):(8,291),
 (491286,491444):(10,16),
 (493574,493656):(10,32),
 (507712,507824):(10,127),
 (550236,550304):(11,135),
 (556260,556352):(11,170),
 (569358,569408):(11,259),
 (583810,583862):(14,7),
 (592544,592596):(14,65),
 (604282,604328):(14,140),
 (630798,630996):(14,334),
}
# Switch-specific / PC-fragment / semantic-version corrections. Must fit original slot.
MANUAL={
 # EP1
 6048:'啊……',33520:'咚！',36342:'别向困难低头。GLHF留。',
 # EP2
 52632:'啊啊啊！',58816:'我又开始走了。',61022:'啊啊啊！',
 # EP3
 118730:'什么？',118844:'呀啊！',
 # EP5
 206704:'铮！',
 # EP6
 277028:'周日一大早，我就拉着哥哥来到市体育场。',305688:'我继续注视着哥哥。',
 # EP8
 465918:'我没空站在这里教训她。',469208:'我想让今晚成为他愿望成真的夜晚！',
 475132:'不，是',475186:'女生。',476406:'她是谁？',
 # EP10
 494736:'喜欢、被喜欢、甩掉、被甩…',494834:'喜欢、被喜欢、甩掉、被甩…',494928:'喜欢、被喜欢、甩掉、被甩…',
 499194:'哦哦！',499944:'呃……',504036:'放学后的资料室…',
 506052:'我是《生死时速》的基努·李维斯…',506146:'我是《生死时速》的基努·李维斯…',506236:'我是《生死时速》的基努·李维斯…',
 518050:'哇啊！',520434:'咚！',
 # EP11
 539908:'哇、哇啊！',551234:'我正不知该去哪儿时，看见一名像在找人的田径赛工作人员。',
 559618:'呀！喂！喂！你为什么脱衣服……？',569880:'他不能',569984:'交往。',
 # EP12
 315866:'我来到轻音部。',325104:'间奏时，这家伙又开始讲疯狂往事和发胖的事。',346060:'哦，对了，佐川先生。',
 # EP14
 599252:'…呜哇啊！',605058:'啊啊啊啊！',622316:'咚！',622722:'一个身影出现，随意转过身来。',622906:'参上！',625132:'咚！',625360:'参上！',
 631842:'但我不知道现在告诉他们会怎样。',633608:'我拿起手套走向一垒，很多孩子正在那里等我。',
 # EP15
 639456:'还得至少往身上浇三次热水，这是规矩。',645288:'嗯？',646190:'呀！呀！',
 649738:'我和家人来过几次。爸爸喜欢能伸直腿的大浴池。',655428:'好，从今天开始我要多吃点。',675236:'哗啦！',
 # EP16
 692576:'一切始于我和汐、渚的对话。',709726:'渚的爆炸发言PART…',709812:'PART几来着？我也记不住了。',
 719016:'汐系紧鞋带，又调整好帽子。',719162:'她背着一个比自己身体大得多的背包。',
 723240:'我们与许多人相遇又离别，并在其中一步步成长。',723550:'她眼中的小镇，也会与别的小镇相遇、离别。',
}
# Additional direct mappings better handled manually to preserve Switch wording/context.
MANUAL.update({
 9254:'一句话就把我卖了！', # same source meaning, concise
 36342:'别向困难低头。GLHF留。',
 58816:'我又开始走了。',
 62400:'他在祈求你陪伴他一生！',
 65666:'这姐姐是真的。',
 277028:'周日一大早，我就拉着哥哥来到市体育场。',
 286776:'连胸罩都还穿不了！',
 305688:'我继续注视着哥哥。',
 315866:'我来到轻音部。',325104:'间奏时，这家伙又开始讲疯狂往事和发胖的事。',
 346060:'哦，对了，佐川先生。',
})
# If a slot is manual, manual overrides ONE.
for off in list(ONE):
    if off in MANUAL: ONE.pop(off)
# Fill a few one-to-one version changes manually rather than source wording.
MANUAL.update({
 36342:'别向困难低头。GLHF留。',
 277028:'周日一大早，我就拉着哥哥来到市体育场。',
 286776:'连胸罩都还穿不了！',
 305688:'我继续注视着哥哥。',
 315866:'我来到轻音部。',
 325104:'间奏时，这家伙又开始讲疯狂往事和发胖的事。',
 346060:'哦，对了，佐川先生。',
})
# Helpers
PUNC='。！？；，、…!?;,'
def cap(off): return struct.unpack_from('<H',orig,off)[0]
def write(off,txt,kind,meta,audit):
    L=cap(off)
    if len(txt)>L:
        raise ValueError(f'MANUAL/FINAL overflow off={off} cap={L} len={len(txt)} txt={txt!r}')
    zb=txt.encode('utf-16-le'); start=off+2; end=start+2*L
    base[start:end]=zb+bytes(2*L-len(zb)); struct.pack_into('<H',base,off,len(txt))
    audit.append((off,remaining[off][0],L,kind,meta,remaining[off][2],txt))
def smart_cut(txt,L):
    if len(txt)<=L:return txt
    # keep natural boundary if possible, otherwise hard concise ellipsis
    lo=max(1,L-10); candidates=[i for i in range(lo,L+1) if txt[i-1] in PUNC]
    cut=max(candidates) if candidates else max(1,L-1)
    return txt[:cut].rstrip(PUNC)+'…'
def distribute(txt,offs):
    caps=[cap(o) for o in offs]; total=sum(caps)
    truncated=False
    if len(txt)>total:
        txt=smart_cut(txt,total);truncated=True
    remain=txt;parts=[];consumed=0
    for idx,o in enumerate(offs[:-1]):
        L=caps[idx]; remcap=sum(caps[idx+1:]); remslots=len(offs)-idx-1
        desired=round(len(txt)*sum(caps[:idx+1])/total)-consumed
        lower=max(0,len(remain)-remcap); upper=min(L,len(remain))
        if len(remain)>=remslots: upper=min(upper,len(remain)-remslots)
        if lower>upper: lower=upper
        target=max(lower,min(upper,desired)); lo=max(lower,target-7); hi=min(upper,target+7)
        cands=[i for i in range(lo,hi+1) if i>0 and remain[i-1] in PUNC]
        cut=min(cands,key=lambda i:abs(i-target)) if cands else target
        parts.append(remain[:cut]); remain=remain[cut:]; consumed+=cut
    parts.append(remain)
    assert len(parts)==len(offs)
    assert all(len(p)<=c for p,c in zip(parts,caps)),(txt,offs,caps,parts)
    return parts,truncated
# coverage check before writing
planned=set(MANUAL)|set(ONE)
for offs in SPLIT: planned.update(offs)
missing=set(remaining)-planned; extra=planned-set(remaining); dup_count=(len(MANUAL)+len(ONE)+sum(len(k) for k in SPLIT)-len(planned))
print('PLAN remaining',len(remaining),'planned unique',len(planned),'missing',len(missing),'extra',len(extra),'dup_count',dup_count)
if missing:
    for o in sorted(missing): print(' MISSING',o,remaining[o])
if extra:
    for o in sorted(extra): print(' EXTRA',o)
assert not missing and not extra
# write manual
audit=[]
badmanual=[(off,cap(off),len(txt),txt) for off,txt in sorted(MANUAL.items()) if len(txt)>cap(off)]
print('manual overflow count',len(badmanual))
for x in badmanual: print(' MANUAL_OVERFLOW',x)
assert not badmanual
for off,txt in sorted(MANUAL.items()): write(off,txt,'manual','',audit)
# write direct one
one_trunc=0
for off,(ep,rid) in sorted(ONE.items()):
    src=D.get((ep,rid))
    if src is None: raise KeyError(('missing direct',off,ep,rid))
    out=smart_cut(src,cap(off)); one_trunc += out!=src
    write(off,out,'direct' if out==src else 'direct_trunc',f'{ep}:{rid}',audit)
# split resources
split_trunc=0
for offs,(ep,rid) in SPLIT.items():
    src=D.get((ep,rid))
    if src is None: raise KeyError(('missing split direct',offs,ep,rid))
    parts,tr=distribute(src,offs);split_trunc+=tr
    for off,part in zip(offs,parts): write(off,part,'split' if not tr else 'split_trunc',f'{ep}:{rid}',audit)
# final coverage uniqueness
assert len({a[0] for a in audit})==128,len({a[0] for a in audit})
# output
outdir=R+r'\out_zh_v35';os.makedirs(outdir,exist_ok=True);op=outdir+r'\SCRIPT.PAK';open(op,'wb').write(base)
with open(R+r'\v35_added.tsv','w',encoding='utf-8',newline='') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['offset','episode','cap','kind','meta','switch_en','chinese']);w.writerows(audit)
print('v35 added',len(audit),'manual',sum(a[3]=='manual' for a in audit),'direct',sum(a[3].startswith('direct') for a in audit),'split_slots',sum(a[3].startswith('split') for a in audit))
print('new direct trunc',one_trunc,'split-resource trunc',split_trunc)
print('size',len(base),'same',len(base)==len(orig),'header485',bytes(base[:485])==orig[:485])
print('sha256',hashlib.sha256(base).hexdigest())



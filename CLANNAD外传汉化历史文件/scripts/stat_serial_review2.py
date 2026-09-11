from pathlib import Path
import csv,re,difflib,collections,json
R=Path(r'D:\clannad_nsw'); out=R/'stat_serial_audit_v38'

def canon(s):
 s=(s or '').replace('❝','"').replace('❞','"').replace('“','"').replace('”','"').replace('’',"'").replace('‘',"'").lower()
 s=re.sub(r'[^a-z0-9]+',' ',s); return ' '.join(s.split())
# reload universe by importing generated script namespace without rerunning prints
ns={}; src=(R/'stat_serial_audit_v38.py').read_text(encoding='utf-8-sig')
# execute only before sampling output creation would be messy; instead reconstruct from sample file + all known audit using same functions simply import via runpy redirects omitted
# Use exec and temporarily suppress print
import builtins
op=builtins.print; builtins.print=lambda *a,**k:None
exec(compile(src,str(R/'stat_serial_audit_v38.py'),'exec'),ns)
builtins.print=op
U=ns['U']; sample=ns['sample']; flags=ns['flags']; D=ns['D']
# group all slots by ep,rid, preserving offset
G=collections.defaultdict(list)
for x in U:
 if x['rid'] is not None and x['switch_en']: G[(x['episode'],x['rid'])].append(x)
review=[]
for x in flags:
 rows=G[(x['episode'],x['rid'])]
 concat=' '.join(r['switch_en'] for r in rows)
 pc=x['pc_en']
 sim=difflib.SequenceMatcher(None,canon(concat),canon(pc)).ratio()
 review.append((x,sim,concat,len(rows)))
print('sample flags',len(flags))
print('group sim >=.90',sum(sim>=.90 for _,sim,_,_ in review),'>=.80',sum(sim>=.80 for _,sim,_,_ in review),'<.80',sum(sim<.80 for _,sim,_,_ in review))
print('\n=== unresolved group sim < .80 ===')
for x,sim,concat,n in review:
 if sim<.80:
  print('OFF',x['offset'],'EP',x['episode'],'RID',x['rid'],'kind',x['kind'],'groupn',n,'sim',round(sim,3))
  print(' SWGROUP:',repr(concat))
  print(' PC     :',repr(x['pc_en']))
  print(' CN     :',repr(x['cn_final']))
# all sample manual no rid as UTF-8 file for semantic review
manual=[x for x in sample if x['rid'] is None]
print('\nmanual count',len(manual))
for x in manual:
 print('MAN',x['offset'],x['episode'],repr(x['switch_en']),'->',repr(x['cn_final']))
# inspect 3 population inversions neighborhoods
print('\n=== inversion neighborhoods ===')
for ep,po,pr,off,rid in ns['inversions']:
 rows=[x for x in U if x['episode']==ep]
 idx=next(i for i,z in enumerate(rows) if z['offset']==off)
 print('INV ep',ep,'at',off,pr,'->',rid)
 for z in rows[max(0,idx-3):idx+4]: print(' ',z['offset'],z['rid'],z['kind'],repr(z['switch_en'])[:160])

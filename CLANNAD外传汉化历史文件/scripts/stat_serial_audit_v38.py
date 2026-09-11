from pathlib import Path
import csv,re,random,math,difflib,collections,json
R=Path(r'D:\clannad_nsw')

def canon(s):
    s=s or ''
    s=s.replace('❝','"').replace('❞','"').replace('“','"').replace('”','"').replace('’',"'").replace('‘',"'")
    s=s.lower()
    s=re.sub(r'[^a-z0-9]+',' ',s)
    return ' '.join(s.split())

# direct PC resource map
D={}
with open(R/'pc_dll_direct_map.tsv',encoding='utf-8') as f:
    for r in csv.DictReader(f,delimiter='\t'):
        D[(int(r['episode']),int(r['resource_id']))]=r

U=[]
# v32: 4400 slots
with open(R/'v32_audit.tsv',encoding='utf-8') as f:
    for r in csv.DictReader(f,delimiter='\t'):
        U.append(dict(offset=int(r['offset']),episode=int(r['episode']),rid=int(r['resource_id']),kind='v32',switch_en=r['switch_en'],pc_en=r['pc_en'],cn=r['chinese'],group=''))
# v33: 3 group lines -> 8 slots; group is deterministic resource split
with open(R/'v33_special.tsv',encoding='utf-8') as f:
    for line in f:
        if not line.strip():continue
        ep,rid,offs,caps,parts,full=line.rstrip('\n').split('\t')
        ep=int(ep);rid=int(rid); offs=eval(offs); parts=eval(parts)
        for off,part in zip(offs,parts):
            U.append(dict(offset=int(off),episode=ep,rid=rid,kind='v33_split',switch_en='',pc_en=D[(ep,rid)]['english'],cn=part,group=f'{ep}:{rid}'))
# v34 direct additions
with open(R/'v34_added.tsv',encoding='utf-8') as f:
    for r in csv.DictReader(f,delimiter='\t'):
        ep=int(r['episode']);rid=int(r['resource_id'])
        U.append(dict(offset=int(r['offset']),episode=ep,rid=rid,kind='v34',switch_en=r['switch_en'],pc_en=D[(ep,rid)]['english'],cn=r['written_cn'],group=''))
# v35 remaining additions
with open(R/'v35_added.tsv',encoding='utf-8') as f:
    for r in csv.DictReader(f,delimiter='\t'):
        rid=None; ep=int(r['episode']);meta=r['meta'].strip();kind='v35_'+r['kind']
        if meta and ':' in meta:
            e,rr=meta.split(':',1); rid=int(rr); assert int(e)==ep
        U.append(dict(offset=int(r['offset']),episode=ep,rid=rid,kind=kind,switch_en=r['switch_en'],pc_en=(D[(ep,rid)]['english'] if rid is not None and (ep,rid) in D else ''),cn=r['chinese'],group=(meta if r['kind'].startswith('split') else '')))

# Sanity universe
U.sort(key=lambda x:x['offset'])
assert len(U)==4573,len(U)
assert len({x['offset'] for x in U})==4573

# Overlay final v36 shortened Chinese (mapping remains same)
fix={}
with open(R/'v36_trunc_fixes.tsv',encoding='utf-8') as f:
    for r in csv.DictReader(f,delimiter='\t'): fix[int(r['offset'])]=r
for x in U:
    if x['offset'] in fix:
        x['cn_final']=fix[x['offset']]['chinese']; x['v36fix']=fix[x['offset']]['kind']
    else:
        x['cn_final']=x['cn']; x['v36fix']=''

# Similarity checks for resource-backed one-to-one rows
for x in U:
    if x['rid'] is not None and x['switch_en']:
        a,b=canon(x['switch_en']),canon(x['pc_en'])
        x['exact']=(a==b)
        x['sim']=difflib.SequenceMatcher(None,a,b).ratio() if a or b else 1.0
    else:
        x['exact']=None;x['sim']=None

# Fixed seed random sample 650 without replacement
seed=202609112310
rng=random.Random(seed)
sample=rng.sample(U,650)
sample.sort(key=lambda x:x['offset'])

# gross-risk flags: only flag potential SERIAL mismatch, not wording/translation quality
# resource-backed rows with wildly different source English (<0.72); split rows are reviewed at group level separately.
flags=[]
for x in sample:
    if x['rid'] is not None and x['switch_en'] and not x['kind'].endswith('split') and x['sim']<0.72:
        flags.append(x)

# sample category counts
cats=collections.Counter(x['kind'] for x in sample)
eps=collections.Counter(x['episode'] for x in sample)
manual=[x for x in sample if x['rid'] is None]
splits=[x for x in sample if 'split' in x['kind']]
exact=sum(1 for x in sample if x['exact'] is True)
resource=sum(1 for x in sample if x['rid'] is not None)
resource_with_en=sum(1 for x in sample if x['rid'] is not None and x['switch_en'])

# whole population structural diagnostics for context
pop_flags=[x for x in U if x['rid'] is not None and x['switch_en'] and 'split' not in x['kind'] and x['sim']<0.72]
# monotonic rid inversions within each episode, ignoring duplicate/split ids; useful for gross serial shifts
inversions=[]
for ep in sorted(set(x['episode'] for x in U)):
    rows=[x for x in U if x['episode']==ep and x['rid'] is not None]
    prev=None
    for x in rows:
        if prev is not None and x['rid']<prev['rid']:
            inversions.append((ep,prev['offset'],prev['rid'],x['offset'],x['rid']))
        if prev is None or x['rid']!=prev['rid']: prev=x

# one-sided 95% zero-failure binomial upper bound
upper=1-math.pow(0.05,1/650)

out=R/'stat_serial_audit_v38';out.mkdir(exist_ok=True)
fields=['offset','episode','rid','kind','switch_en','pc_en','cn_final','sim','exact','v36fix','group']
with open(out/'sample_650.tsv','w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();
    for x in sample:w.writerow({k:x.get(k,'') for k in fields})
with open(out/'potential_serial_flags.tsv','w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();
    for x in flags:w.writerow({k:x.get(k,'') for k in fields})
with open(out/'sample_manual_no_rid.tsv','w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();
    for x in manual:w.writerow({k:x.get(k,'') for k in fields})
summary={
 'population':len(U),'sample_n':650,'seed':seed,'confidence':0.95,'zero_failure_upper_rate':upper,
 'resource_backed_sample':resource,'resource_with_english_sample':resource_with_en,'exact_normalized_sample':exact,
 'sample_potential_flags':len(flags),'sample_manual_no_rid':len(manual),'sample_split_slots':len(splits),
 'population_low_similarity_flags':len(pop_flags),'population_rid_inversions':len(inversions),
 'episode_sample_counts':dict(sorted(eps.items())),'kind_counts':dict(cats)
}
(out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
print('\n=== sample low-sim flags ===')
for x in flags[:80]:print(x['offset'],x['episode'],x['rid'],x['kind'],f"sim={x['sim']:.3f}",repr(x['switch_en']),'=>',repr(x['pc_en']),'CN',repr(x['cn_final']))
print('\n=== sample manual no-rid ===')
for x in manual:print(x['offset'],x['episode'],x['kind'],repr(x['switch_en']),'CN',repr(x['cn_final']))
print('\n=== sample split slots ===')
for x in splits:print(x['offset'],x['episode'],x['rid'],x['kind'],x['group'],repr(x['switch_en']),'CN',repr(x['cn_final']))
print('\n=== population low-sim first 60 ===')
for x in pop_flags[:60]:print(x['offset'],x['episode'],x['rid'],x['kind'],f"sim={x['sim']:.3f}",repr(x['switch_en']),'=>',repr(x['pc_en']))
print('\nRID inversions',len(inversions),inversions[:40])

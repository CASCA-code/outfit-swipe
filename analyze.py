#!/usr/bin/env python3
"""Analiza resultados de Outfit Swipe.
Uso:  python3 analyze.py results.json        (o)   pbpaste | python3 analyze.py -
Entrada: JSON [{id, verdict: like|nope|super, note?}, ...] pegado desde la app.
Salida: like-rate global, like-rate por tag, tags strong-YES / strong-NO,
tags compartidos (venn LIKE ∩ NOPE), exclusivos, resumen por faceta y notas.
Opciones: --min N (mín. apariciones por tag, default 3)  --json (salida máquina)
"""
import json,sys,os,collections,math,argparse
ap=argparse.ArgumentParser();ap.add_argument('results');ap.add_argument('--data',default=os.path.join(os.path.dirname(os.path.abspath(__file__)),'data.json'))
ap.add_argument('--min',type=int,default=3);ap.add_argument('--json',action='store_true');a=ap.parse_args()
raw=sys.stdin.read() if a.results=='-' else open(a.results).read()
R=json.loads(raw[raw.find('['):raw.rfind(']')+1])
D={x['id']:x for x in json.load(open(a.data))}
SKIP=('garment:','tuck:n/a')
votes=[r for r in R if r['id'] in D]
n=len(votes); 
if not n: sys.exit('Sin votos válidos')
pos=lambda v:v in('like','super')
L=sum(pos(r['verdict']) for r in votes); base=L/n
C=collections.defaultdict(lambda:{'n':0,'like':0,'super':0,'nope':0})
for r in votes:
    for t in D[r['id']]['tags']:
        if t.startswith(SKIP): continue
        c=C[t]; c['n']+=1; c[r['verdict']]+=1
rows=[]
for t,c in C.items():
    y=c['like']+c['super']; rate=y/c['n']
    sm=(y+2*base)/(c['n']+2)          # tasa suavizada (prior = base)
    lift=sm-base
    # z-score binomial vs base
    z=(rate-base)/math.sqrt(max(base*(1-base),1e-9)/c['n'])
    rows.append(dict(tag=t,n=c['n'],likes=y,supers=c['super'],nopes=c['nope'],rate=round(rate,3),lift=round(lift,3),z=round(z,2)))
ok=[r for r in rows if r['n']>=a.min]
yes=sorted([r for r in ok if r['z']>=1.0],key=lambda r:-r['z'])
no=sorted([r for r in ok if r['z']<=-1.0],key=lambda r:r['z'])
liked_tags={t for r in votes if pos(r['verdict']) for t in D[r['id']]['tags'] if not t.startswith(SKIP)}
noped_tags={t for r in votes if r['verdict']=='nope' for t in D[r['id']]['tags'] if not t.startswith(SKIP)}
shared=sorted([r for r in ok if r['tag'] in liked_tags&noped_tags and abs(r['z'])<1.0],key=lambda r:-r['n'])
only_like=sorted([r for r in rows if r['tag'] in liked_tags-noped_tags],key=lambda r:-r['n'])
only_nope=sorted([r for r in rows if r['tag'] in noped_tags-liked_tags],key=lambda r:-r['n'])
facet=collections.defaultdict(list)
for r in ok: facet[r['tag'].split(':')[0]].append(r)
out=dict(n=n,likes=L,supers=sum(r['verdict']=='super' for r in votes),nopes=n-L,base_like_rate=round(base,3),
 strong_yes=yes,strong_no=no,shared_neutral=shared,only_in_likes=only_like,only_in_nopes=only_nope,
 by_facet={f:sorted(v,key=lambda r:-r['rate']) for f,v in facet.items()},
 notes=[dict(id=r['id'],verdict=r['verdict'],note=r['note'],lanes=D[r['id']]['lanes']) for r in votes if r.get('note')])
if a.json: print(json.dumps(out,ensure_ascii=False,indent=1)); sys.exit()
def tab(title,rs,k=20):
    print(f'\n== {title} ==')
    for r in rs[:k]: print(f"  {r['tag']:<38} {r['likes']:>3}/{r['n']:<3} {r['rate']*100:5.0f}%  z={r['z']:+.1f}")
    if not rs: print('  (nada)')
print(f"Votos: {n} | sí {L} (super {out['supers']}) | no {n-L} | like-rate base {base*100:.0f}%")
tab('STRONG YES (z≥+1)',yes); tab('STRONG NO (z≤−1)',no)
tab('COMPARTIDOS LIKE∩NOPE (neutros, no deciden)',shared,15)
tab('SOLO EN LIKES',only_like,12); tab('SOLO EN NOPES',only_nope,12)
print('\n== POR FACETA (like-rate) ==')
for f in ['lane','region','top','bottom','shoes','layer','palette','texture','collar','fit','leg','tuck','formality','weather','setting','photo','vibe','pattern']:
    if f in facet: print(f'  {f:<10} '+' · '.join(f"{r['tag'].split(':',1)[1]} {r['rate']*100:.0f}%({r['n']})" for r in out['by_facet'][f][:8]))
if out['notes']:
    print('\n== NOTAS ==')
    for x in out['notes']: print(f"  {x['id']} [{x['verdict']}] {x['note']}  ({', '.join(x['lanes'])})")

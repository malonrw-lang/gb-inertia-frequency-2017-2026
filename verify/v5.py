import json, numpy as np, pandas as pd, statsmodels.formula.api as smf
v=json.load(open('data/grid_dc.json'))
rows=[]
for k,a in v.items():
    if k.startswith('__'): continue
    rows+=a
dc=pd.DataFrame([r.split(',') for r in rows],columns=['bin_utc','n2','sumG','n100']).astype({'bin_utc':'int64','n2':int,'sumG':float,'n100':int})
b=pd.read_csv('./out/analysis_halfhours_adj.csv')
m=b.merge(dc,on='bin_utc',how='inner'); m=m[m.n2>=1700].copy()
m['Y5']=np.log1p(m.sumG); m['Y6']=np.log1p(m.n100)
ctrl="C(year) + C(moy) + C(hour) + weekend + lognd + ewsh + essh"
d=m.dropna(subset=['Y5','lognd','ewsh','essh'])
print('n',len(d), 'post median sumG', d[d.era=='post'].sumG.median(), 'post mean n100', d[d.era=='post'].n100.mean(), 'post median n100', d[d.era=='post'].n100.median())
k=np.log(102/120); f=lambda x:100*(np.exp(x*k)-1)
for y in ['Y5','Y6']:
  for a,c in [('logH_pre','logH_post'),('logHa_pre','logHa_post')]:
    mm=smf.ols(f"{y} ~ {a} + {c} + {ctrl}",data=d).fit(cov_type='cluster',cov_kwds={'groups':d['date']})
    ci=mm.conf_int().loc[c]; bp=mm.params[c]
    print(y,c,'pre',mm.params[a],'post',bp,ci.values,'floor',f(bp),f(ci[1]),f(ci[0]))

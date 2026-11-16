import pandas as pd, numpy as np, json, statsmodels.formula.api as smf
G='.'
b=pd.read_csv(G+'/out/analysis_halfhours_adj.csv')
ctrl="C(year) + C(moy) + C(hour) + weekend + lognd + ewsh + essh"
d=b.dropna(subset=['Y1','lognd','ewsh','essh']).copy()
k=np.log(102/120); f=lambda x:100*(np.exp(x*k)-1)
m=smf.ols(f"Y1 ~ logHa_pre + logHa_post + {ctrl}",data=d).fit(cov_type='cluster',cov_kwds={'groups':d['date']})
ci=m.conf_int().loc['logHa_post']; bp=m.params['logHa_post']
print('adj post', bp, ci.values, 'floor', f(bp), f(ci[1]), f(ci[0]))
print('adj pre', m.params['logHa_pre'])
res={}
for e in ['pre','post']:
    s=d[d.era==e]; mm=smf.ols(f"Y1 ~ logH + {ctrl}",data=s).fit(cov_type='cluster',cov_kwds={'groups':s['date']})
    res[e]=(mm.params['logH'],mm.bse['logH']); print('sep',e,mm.params['logH'],mm.bse['logH'],mm.conf_int().loc['logH'].values)
dd=res['post'][0]-res['pre'][0]; se=np.sqrt(res['post'][1]**2+res['pre'][1]**2); print('sep diff',dd,dd-1.96*se,dd+1.96*se)
print('sep post floor', f(res['post'][0]))

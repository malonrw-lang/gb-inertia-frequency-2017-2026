# Sensitivity (not pre-registered): era-by-era fits for Y1, Y5, Y6; Figure 1 binscatter; gate excluding transition events; floor effects on both inertia bases.
import json, numpy as np, pandas as pd, statsmodels.formula.api as smf
ctrl = "C(year) + C(moy) + C(hour) + weekend + lognd + ewsh + essh"
k = np.log(102/120)
R = {}
b = pd.read_csv('out/analysis_halfhours.csv').dropna(subset=['Y1','lognd','ewsh','essh'])
for era in ['pre','post']:
    d = b[b.era==era]; m = smf.ols(f"Y1 ~ logH + {ctrl}", d).fit(cov_type='cluster', cov_kwds={'groups': d['date']})
    R[f'Y1_sep_{era}'] = [float(m.params['logH']), float(m.bse['logH'])]
d_ = R['Y1_sep_post'][0]-R['Y1_sep_pre'][0]; se = np.hypot(R['Y1_sep_post'][1], R['Y1_sep_pre'][1])
R['Y1_sep_diff'] = [d_, d_-1.96*se, d_+1.96*se]
# binscatter
out=[]
for era in ['pre','post']:
    d = b[b.era==era].copy()
    ry = smf.ols(f"Y1 ~ {ctrl}", d).fit().resid; rx = smf.ols(f"logH ~ {ctrl}", d).fit().resid
    d['rx']=rx; d['ry']=ry; d['bin']=pd.qcut(d.rx,20,labels=False)
    g = d.groupby('bin').agg(x=('rx','mean'), y=('ry','mean'))
    for _,r in g.iterrows(): out.append(dict(era=era, x=round(100*(np.exp(r.x)-1),2), y=round(100*(np.exp(r.y)-1),2)))
pd.DataFrame(out).to_csv('out/binscatter.csv', index=False)
# A1 floor precise
a1 = json.load(open('out/a1_pathfinder.json'))
# recompute A1 unrounded
ba = pd.read_csv('out/analysis_halfhours_adj.csv').dropna(subset=['Y1','lognd','ewsh','essh'])
m = smf.ols(f"Y1 ~ logHa_pre + logHa_post + {ctrl}", ba).fit(cov_type='cluster', cov_kwds={'groups': ba['date']})
bp, (lo, hi) = m.params['logHa_post'], m.conf_int().loc['logHa_post']
R['A1_floor_pct'] = [100*(np.exp(bp*k)-1), 100*(np.exp(hi*k)-1), 100*(np.exp(lo*k)-1)]
R['A1_share_pf_post'] = float((ba.loc[ba.era=='post','pf_GVAs']>0).mean())
R['A1_share_pf_since_2023_09'] = float((ba.loc[pd.to_datetime(ba.settlement_date)>='2023-09-04','pf_GVAs']>0).mean())
# A2 floor on unadjusted basis
a2 = json.load(open('out/a2_dc.json'))
for y in ['Y5','Y6']:
    p = a2[f'{y}_H']['post']
    R[f'{y}_floor_pct_unadj'] = [100*(np.exp(p[0]*k)-1), 100*(np.exp(p[2]*k)-1), 100*(np.exp(p[1]*k)-1)]
# gate excluding transition events
e = pd.read_csv('out/analysis_events.csv'); e = e[e.era!='trans']
g = smf.ols("logK ~ logH + C(era) + C(moy) + C(hour)", e).fit(cov_type='cluster', cov_kwds={'groups': e['date']})
R['gate_excl_trans'] = [float(g.params['logH']), *map(float, g.conf_int().loc['logH']), int(g.nobs)]
for v in ['rocof_mHz','depth_mHz']:
    g = smf.ols(f"np.log({v}) ~ logH + C(era) + C(moy) + C(hour)", e).fit(cov_type='cluster', cov_kwds={'groups': e['date']})
    R[f'gate_excl_trans_{v}'] = [float(g.params['logH']), *map(float, g.conf_int().loc['logH'])]
print(json.dumps({k_: (np.round(v,3).tolist() if isinstance(v,list) else round(v,3)) for k_,v in R.items()}, indent=1))
json.dump(R, open('out/sens_eras_binscatter.json','w'), indent=1)

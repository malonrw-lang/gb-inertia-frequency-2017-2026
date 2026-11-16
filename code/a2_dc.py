# Addendum A2: DC delivery proxy (Y5) and seconds beyond 0.1 Hz (Y6) vs inertia. Model identical to main.
import json, numpy as np, pandas as pd, statsmodels.formula.api as smf, sys
v = json.load(open(sys.argv[1]))
rows = []
for k, arr in v.items():
    if k.startswith('__'): continue
    rows += arr
dc = pd.DataFrame([r.split(',') for r in rows], columns=['bin_utc', 'n2', 'sumG', 'n100']).astype({'bin_utc': 'int64', 'n2': int, 'sumG': float, 'n100': int})
b = pd.read_csv('out/analysis_halfhours_adj.csv')
m = b.merge(dc, on='bin_utc', how='inner')
m = m[m.n2 >= 1700].copy()
m['Y5'] = np.log1p(m.sumG); m['Y6'] = np.log1p(m.n100)
ctrl = "C(year) + C(moy) + C(hour) + weekend + lognd + ewsh + essh"
d = m.dropna(subset=['Y5', 'lognd', 'ewsh', 'essh'])
R = {'n_merged': int(len(m)), 'n_used': int(len(d)),
     'descr': {e: dict(sumG_median=float(g.sumG.median()), sumG_mean=float(g.sumG.mean()), n100_mean=float(g.n100.mean()), share_any_n100=float((g.n100 > 0).mean())) for e, g in d.groupby('era')}}
def q(m, k): return [round(m.params[k], 3), round(m.conf_int().loc[k, 0], 3), round(m.conf_int().loc[k, 1], 3)]
for y in ['Y5', 'Y6']:
    for nm, (a, c) in {'H': ('logH_pre', 'logH_post'), 'H_adj': ('logHa_pre', 'logHa_post')}.items():
        mm = smf.ols(f"{y} ~ {a} + {c} + {ctrl}", data=d).fit(cov_type='cluster', cov_kwds={'groups': d['date']})
        cv = mm.cov_params(); df_ = mm.params[c] - mm.params[a]; se = float(np.sqrt(cv.loc[c, c] + cv.loc[a, a] - 2 * cv.loc[c, a]))
        R[f'{y}_{nm}'] = dict(pre=q(mm, a), post=q(mm, c), diff=[round(df_, 3), round(df_ - 1.96 * se, 3), round(df_ + 1.96 * se, 3)])
    # separate eras
    for e in ['pre', 'post']:
        s = d[d.era == e]; mm = smf.ols(f"{y} ~ logH + {ctrl}", data=s).fit(cov_type='cluster', cov_kwds={'groups': s['date']})
        R[f'{y}_sep_{e}'] = q(mm, 'logH')
k = np.log(102 / 120)
for y in ['Y5', 'Y6']:
    bp = R[f'{y}_H_adj']['post']
    # approx % change in (1+X): exp(beta*k)-1
    R[f'{y}_floor_pct'] = [round(100 * (np.exp(bp[0] * k) - 1), 1), round(100 * (np.exp(bp[2] * k) - 1), 1), round(100 * (np.exp(bp[1] * k) - 1), 1)]
p = R['Y5_H']['post']; R['H4_post'] = 'supported' if p[2] < 0 else ('reversed' if p[1] > 0 else 'not supported')
p = R['Y5_H']['pre']; R['H4_pre'] = 'supported' if p[2] < 0 else ('reversed' if p[1] > 0 else 'not supported')
print(json.dumps(R, indent=1)); json.dump(R, open('out/a2_dc.json', 'w'), indent=1)

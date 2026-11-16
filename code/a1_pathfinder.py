# Addendum A1: add Stability Pathfinder (+ mid-term Y-1) inertia to NESO outturn inertia; rerun Y1 main model & H2.
import json, numpy as np, pandas as pd, statsmodels.formula.api as smf, io
v = json.load(open('data/grid_pathfinder.json'))
pf = pd.read_csv(io.StringIO(v['pf']))
pf['bin_utc'] = pf.sp_start_utc.astype('int64'); pf['pf_GVAs'] = pf.pf_MVAs / 1000
mt = pd.read_csv(io.StringIO(v['midterm'])); mt.columns = [c.strip() for c in mt.columns]
mt = mt.dropna(subset=['Utilisation Start Datetime'])
add = {}
for _, r in mt.iterrows():
    s = pd.Timestamp(pd.to_datetime(r['Utilisation Start Datetime'], dayfirst=True)).tz_localize('Europe/London', ambiguous='NaT', nonexistent='shift_forward').tz_convert('UTC')
    e = pd.Timestamp(pd.to_datetime(r['Utilisation End Datetime'], dayfirst=True)).tz_localize('Europe/London', ambiguous='NaT', nonexistent='shift_forward').tz_convert('UTC')
    if pd.isna(s) or pd.isna(e): continue
    t0 = int(s.timestamp()); t1 = int(e.timestamp()); b = t0 // 1800 * 1800
    while b < t1:
        ov = min(t1, b + 1800) - max(t0, b)
        if ov > 0: add[b] = add.get(b, 0) + float(r['Inertia']) / 1000 * ov / 1800
        b += 1800
mtd = pd.Series(add, name='mt_GVAs')
b = pd.read_csv('out/analysis_halfhours.csv')
b = b.merge(pf[['bin_utc', 'pf_GVAs']], on='bin_utc', how='left').merge(mtd.rename_axis('bin_utc').reset_index(), on='bin_utc', how='left')
b[['pf_GVAs', 'mt_GVAs']] = b[['pf_GVAs', 'mt_GVAs']].fillna(0)
b['H_adj'] = b.H + b.pf_GVAs + b.mt_GVAs
b['logHa'] = np.log(b.H_adj); b['logHa_pre'] = b.logHa * b.pre; b['logHa_post'] = b.logHa * b.post
ctrl = "C(year) + C(moy) + C(hour) + weekend + lognd + ewsh + essh"
d = b.dropna(subset=['Y1', 'lognd', 'ewsh', 'essh']).copy()
def run(f, df, a='logH_pre', c='logH_post'):
    m = smf.ols(f, data=df).fit(cov_type='cluster', cov_kwds={'groups': df['date']})
    cv = m.cov_params(); diff = m.params[c] - m.params[a]
    se = float(np.sqrt(cv.loc[c, c] + cv.loc[a, a] - 2 * cv.loc[c, a]))
    q = lambda k: [round(m.params[k], 3), round(m.conf_int().loc[k, 0], 3), round(m.conf_int().loc[k, 1], 3)]
    return dict(pre=q(a), post=q(c), diff=[round(diff, 3), round(diff - 1.96 * se, 3), round(diff + 1.96 * se, 3)], n=int(m.nobs))
R = {}
R['descr'] = dict(share_halfhours_with_pf=float((d.pf_GVAs > 0).mean()), pf_median_when_on=float(d.loc[d.pf_GVAs > 0, 'pf_GVAs'].median()),
                  pf_over_H_median_when_on=float((d.pf_GVAs / d.H)[d.pf_GVAs > 0].median()), mt_halfhours=int((d.mt_GVAs > 0).sum()),
                  first_pf=str(pd.to_datetime(d.loc[d.pf_GVAs > 0, 'bin_utc'].min(), unit='s')))
R['orig'] = run(f"Y1 ~ logH_pre + logH_post + {ctrl}", d)
R['adj'] = run(f"Y1 ~ logHa_pre + logHa_post + {ctrl}", d, 'logHa_pre', 'logHa_post')
s = d[pd.to_datetime(d.settlement_date) >= '2023-09-04'].copy()
for nm, x in [('H', 'logH'), ('H_adj', 'logHa')]:
    m = smf.ols(f"Y1 ~ {x} + C(year) + C(moy) + C(hour) + weekend + lognd + ewsh + essh", data=s).fit(cov_type='cluster', cov_kwds={'groups': s['date']})
    R[f'since_2023_09_{nm}'] = [round(m.params[x], 3), round(m.conf_int().loc[x, 0], 3), round(m.conf_int().loc[x, 1], 3), int(m.nobs)]
k = np.log(102 / 120); bp = R['adj']['post']
R['H3_adj_pct'] = [round(100 * (np.exp(bp[0] * k) - 1), 1), round(100 * (np.exp(bp[2] * k) - 1), 1), round(100 * (np.exp(bp[1] * k) - 1), 1)]
c = R['adj']['diff']; R['H2_rule'] = 'stands' if (c[1] <= 0 <= c[2] and abs(c[0] - R['orig']['diff'][0]) <= 0.05) else 'changes'
print(json.dumps(R, indent=1)); json.dump(R, open('out/a1_pathfinder.json', 'w'), indent=1)
b.to_csv('out/analysis_halfhours_adj.csv', index=False)

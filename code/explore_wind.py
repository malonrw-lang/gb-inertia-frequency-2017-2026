# EXPLORATORY (not pre-registered): does inertia predict 1-s volatility beyond transmission wind/solar/imports share?
import pandas as pd, numpy as np, statsmodels.formula.api as smf, json, sys
b = pd.read_csv('out/analysis_halfhours.csv')
g = pd.read_csv('data/genmix_2017on.csv')
g['dt'] = pd.to_datetime(g.DATETIME)
d = g.dt.dt.date.value_counts()
print('rows/day distribution:', d.value_counts().head().to_dict())
g['bin_utc'] = (g.dt - pd.Timestamp('1970-01-01')).dt.total_seconds().astype('int64')
for c in ['WIND','SOLAR','IMPORTS','STORAGE','NUCLEAR','GAS','GENERATION','BIOMASS','HYDRO','COAL']:
    g[c] = pd.to_numeric(g[c], errors='coerce')
g['wsh'] = g.WIND/g.GENERATION; g['ssh']=g.SOLAR/g.GENERATION; g['ish']=g.IMPORTS/g.GENERATION
g['nsh'] = g.NUCLEAR/g.GENERATION; g['gsh']=g.GAS/g.GENERATION; g['stsh']=g.STORAGE/g.GENERATION
m = b.merge(g[['bin_utc','wsh','ssh','ish','nsh','gsh','stsh']], on='bin_utc', how='inner').dropna(subset=['Y1','wsh','ssh','ish','lognd','ewsh','essh'])
print('merged', len(m), 'of', len(b))
base = "C(year) + C(moy) + C(hour) + weekend + lognd + ewsh + essh"
out = {}
for name, extra in [('prereg', ''), ('+wind_solar_imports', ' + wsh + ssh + ish'), ('+full_mix', ' + wsh + ssh + ish + nsh + gsh + stsh')]:
    f = f"Y1 ~ logH_pre + logH_post + {base}{extra}"
    r = smf.ols(f, data=m).fit(cov_type='cluster', cov_kwds={'groups': m['date']})
    out[name] = {k: [round(r.params[k],3), round(r.conf_int().loc[k,0],3), round(r.conf_int().loc[k,1],3)] for k in ['logH_pre','logH_post'] + (['wsh'] if 'wsh' in extra else [])}
    r2 = smf.ols(f"logH ~ {base}{extra}", data=m).fit().rsquared
    out[name]['R2_logH_on_controls'] = round(r2,3)
print(json.dumps(out, indent=1))
json.dump(out, open('out/explore_wind.json','w'), indent=1)

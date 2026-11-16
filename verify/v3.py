import pandas as pd, numpy as np, json
G='.'
e=pd.read_csv(G+'/out/analysis_events.csv')
print(len(e), e.era.value_counts().to_dict())
print('median rocof', e.rocof_mHz.median(), e.groupby('era').rocof_mHz.median().to_dict(), 'share rocof<=25', (e.rocof_mHz<=25).mean())
print('median depth', e.depth_mHz.median(), 'min rocof', e.rocof_mHz.min(), 'min depth', e.depth_mHz.min())
raw=pd.read_csv(G+'/data/grid_events.csv'); print('raw events', len(raw), 'raw min rocof', raw.rocof_mHz.min(), 'raw min depth', raw.depth_mHz.min())
bs=pd.read_csv(G+'/out/binscatter.csv')
for era,g in bs.groupby('era'):
    s=np.polyfit(g.x,g.y,1)[0]; print(era,'binscatter slope',s, 'xrange', g.x.min(), g.x.max())
v=json.load(open('data/grid_pathfinder.json'))
print(v.keys())
import io
pf=pd.read_csv(io.StringIO(v['pf'])); print(pf.head(3)); print(pf.columns.tolist())
pf['t']=pd.to_datetime(pf.sp_start_utc,unit='s'); print('pf rows',len(pf),pf.t.min(),pf.t.max(),'first >0',pf.loc[pf.pf_MVAs>0,'t'].min())

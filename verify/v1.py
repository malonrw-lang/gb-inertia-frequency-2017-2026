import pandas as pd, numpy as np, glob, json
G='.'
# inertia by financial year
fr=[]
for f in sorted(glob.glob(G+'/data/inertia_*.csv')):
    x=pd.read_csv(f); x.columns=[c.strip().lower().replace(' ','_') for c in x.columns]; x['file']=f.split('-_')[-1]; fr.append(x)
x=pd.concat(fr)
print(x.groupby('file').agg(mean_out=('outturn_inertia','mean'),median_out=('outturn_inertia','median'),mean_mkt=('market_provided_inertia','mean'),n=('outturn_inertia','size'),first=('settlement_date','first'),last=('settlement_date','last')))
# parse dates
s=x.settlement_date.astype(str)
d=pd.to_datetime(s,format='%Y-%m-%d',errors='coerce')
for fmt in ('%d-%b-%Y','%d-%b-%y'):
    m=d.isna(); d[m]=pd.to_datetime(s[m],format=fmt,errors='coerce')
x['d']=d; print('date range',d.min(),d.max(), d.isna().sum())
x['fy']=np.where(x.d.dt.month>=4,x.d.dt.year,x.d.dt.year-1)
print(x.drop_duplicates(['d','settlement_period']).groupby('fy').outturn_inertia.agg(['mean','median','size']))
# min/max of floor-ish
q=pd.read_csv(G+'/data/grid_qc.csv'); q['cov']=q.rows/(q.month.apply(lambda m: pd.Period(m,'M').days_in_month)*86400)
print(q[['month','cov']].sort_values('cov').head(5)); print('months',len(q),q.month.min(),q.month.max())

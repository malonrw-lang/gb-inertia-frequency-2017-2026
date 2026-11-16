import pandas as pd, numpy as np
G='.'
b=pd.read_csv(G+'/out/analysis_halfhours_adj.csv')
b['sd_']=pd.to_datetime(b.settlement_date)
print('N',len(b), b.era.value_counts().to_dict())
for e,g in b.groupby('era'): print(e, g.sd_.min(), g.sd_.max())
z=b[b.Y1.isna()]; print('Y1 NaN', len(z)); print(z[['settlement_date','sp','n','sd','p999_mHz','min','max']])
print('sd==0 count', (b.sd==0).sum())
# n>=1700
print('min n', b.n.min())
# PF share
post=b[b.era=='post']; d=b.dropna(subset=['Y1','lognd','ewsh','essh'])
print('pf share all d', (d.pf_GVAs>0).mean(), 'post', (d[d.era=='post'].pf_GVAs>0).mean(), 'post incl mt', ((d[d.era=='post'].pf_GVAs+d[d.era=='post'].mt_GVAs)>0).mean())
print('pf>0 first', d.loc[d.pf_GVAs>0,'settlement_date'].min(), 'mt>0 first', d.loc[d.mt_GVAs>0,'settlement_date'].min(), d.loc[d.mt_GVAs>0,'settlement_date'].max())
on=d[d.pf_GVAs>0]; print('pf median',on.pf_GVAs.median(),'pf/H median',(on.pf_GVAs/on.H).median(),'pf/Hadj',(on.pf_GVAs/on.H_adj).median())
since=d[d.sd_>='2023-09-04']; print('since sep23 n',len(since),'pf share since', (since.pf_GVAs>0).mean(), 'any adj share', ((since.pf_GVAs+since.mt_GVAs)>0).mean())
tot=d.pf_GVAs+d.mt_GVAs; print('pf+mt>0 post share', (tot[d.era=='post']>0).mean(), 'median add when on', tot[tot>0].median(), (tot/d.H)[tot>0].median())
# DC proxy: mean of n100, median sumG from a2 description ok; inertia means by era
print(b.groupby('era').H.describe())
# 10% fall
for bb in [-0.3483179,-0.3257036]: print('10% fall', 100*(np.exp(bb*np.log(0.9))-1))
k=np.log(102/120)
f=lambda bb: 100*(np.exp(bb*k)-1)
print('Y1 unadj post', f(-0.3257036), f(-0.26889706), f(-0.38251015))
print('Y1 adj post', f(-0.321), f(-0.262), f(-0.379))
print('Y5 unadj', f(-0.051), f(-0.021), f(-0.081), 'adj', f(-0.045), f(-0.014), f(-0.075))
print('Y6 unadj', f(-0.279), f(-0.138), f(-0.421), 'adj', f(-0.253), f(-0.107), f(-0.4))
print('Y1 pre unadj', f(-0.348), 'sep post', f(-0.33))
print('cut', 1-102/120)

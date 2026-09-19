"""Compute exact 4-method x 3-bin residual-q sensitivity source for Fig06.
Non-visual Python preprocessing only; R remains exclusive renderer."""
import os
import numpy as np
import pandas as pd
import jenkspy
from pathlib import Path

BASE=Path(os.environ.get("YUEXI_BASE") or r"C:\Users\han\Desktop\粤西论文文件夹\YueXi0518\YueXi0518")
ROOT=BASE.parent.parent
BASE=ROOT/"YueXi0518"/"YueXi0518"
OUT=ROOT/"_YUEXI_FIGURE_REBUILD_20260912"/"04_figures"/"source_data"
FACTORS=["slope","DEM","TEM"]
ALL=["slope","DEM","TEM","soiltype","NDVI","NLI","POP","roads","GDP","railways","water","PRE","aspect"]
HQ=np.load(BASE/'gd_HQ.npy').ravel(); LU=np.load(BASE/'gd_LUCC.npy').ravel()
def load(n): return np.load(BASE/f'gd_{n}.npy').ravel()
data={n:load(n) for n in ALL}
m=np.isfinite(HQ)&np.isin(LU,[1,2,3,4,5,6])
for v in data.values():m &= np.isfinite(v)
y=HQ[m]; lu=LU[m].astype(int); resid=y.copy()
for c in range(1,7): resid[lu==c]-=y[lu==c].mean()
def qstat(y,z):
 sst=((y-y.mean())**2).sum(); ssw=sum(((a-a.mean())**2).sum() for a in (y[z==i] for i in np.unique(z)) if len(a));return 1-ssw/sst
rows=[]
rng=np.random.default_rng(20260912)
for method in ['Quantile','Equal interval','Jenks','Standard deviation']:
 for bins in [5,8,10]:
  for f in FACTORS:
   x=data[f][m]
   if method=='Quantile':
    e=np.unique(np.quantile(x,np.linspace(0,1,bins+1)));e[0]-=1e-9;e[-1]+=1e-9;z=np.digitize(x,e[1:-1])
   elif method=='Equal interval':
    e=np.linspace(x.min(),x.max(),bins+1);z=np.digitize(x,e[1:-1])
   elif method=='Jenks':
    # deterministic 2,000-point sample for computationally stable documented approximation
    ix=rng.choice(len(x),size=min(2000,len(x)),replace=False);e=np.array(jenkspy.jenks_breaks(x[ix],n_classes=bins));e[0]-=1e-9;e[-1]+=1e-9;z=np.digitize(x,e[1:-1])
   else:
    e=np.linspace(x.mean()-(bins/2)*x.std(),x.mean()+(bins/2)*x.std(),bins+1);z=np.digitize(x,e[1:-1])
   rows.append({'method':method,'bins':bins,'factor':f,'q_residual':qstat(resid,z),'n_complete':int(m.sum())})
pd.DataFrame(rows).to_csv(OUT/'fig6_discretization_sensitivity.csv',index=False)
print(pd.DataFrame(rows).to_string(index=False))

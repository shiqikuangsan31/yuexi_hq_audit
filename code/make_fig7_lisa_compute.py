# -*- coding: utf-8 -*-
# Step A: compute LISA clusters of forest within-class HQ residuals (real data, esda)
# and export point coords (UTM) + cluster class to CSV for ArcGIS map rendering.
import os, numpy as np, csv
BASE=os.environ.get("YUEXI_BASE") or r"C:/Users/han/Desktop/粤西论文文件夹/YueXi0518/YueXi0518"
XMIN,YMAX,CELL,STEP=361151.0,2511101.0,30.0,33
def gd(n): return np.load(os.path.join(BASE,f"gd_{n}.npy"))
HQ,LUCC=gd("HQ").ravel(),gd("LUCC").ravel(); ncol=283
ii,jj=np.divmod(np.arange(HQ.size),ncol)
X=XMIN+(jj*STEP+0.5)*CELL; Y=YMAX-(ii*STEP+0.5)*CELL
f=(LUCC==2)&np.isfinite(HQ); xf,yf,hf=X[f],Y[f],HQ[f]; resid=hf-hf.mean()
from libpysal.weights import KNN
from esda.moran import Moran, Moran_Local
w=KNN.from_array(np.column_stack([xf,yf]),k=8); w.transform="r"
gI=Moran(resid,w,permutations=999).I
lm=Moran_Local(resid,w,permutations=999,seed=42)
sig=lm.p_sim<0.05; q=lm.q
cls=np.zeros(resid.size,int)
cls[sig&(q==1)]=1  # HH eco-core
cls[sig&(q==3)]=2  # LL threat hotspot
cls[sig&(q==4)]=3  # HL stepping stone
cls[sig&(q==2)]=4  # LH edge
pct={k:100*(cls==k).sum()/cls.size for k in range(5)}
out=os.path.join(BASE,"code","lisa_points.csv")
with open(out,"w",newline="") as fcsv:
    wr=csv.writer(fcsv); wr.writerow(["x_utm","y_utm","cls"])
    for a,b,c in zip(xf,yf,cls): wr.writerow([f"{a:.1f}",f"{b:.1f}",int(c)])
import json
meta={"global_moran":round(float(gI),3),"n":int(resid.size),
      "pct":{k:round(v,1) for k,v in pct.items()}}
json.dump(meta,open(os.path.join(BASE,"code","lisa_meta.json"),"w"))
print("global Moran I =",round(gI,3),"n=",resid.size)
print("pct:",{k:round(v,1) for k,v in pct.items()})
print("CSV ->",out)

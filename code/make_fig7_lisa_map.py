# -*- coding: utf-8 -*-
# Fig 7 (LISA) map rendered in ArcGIS Pro python env from real esda clusters.
import arcpy, json, numpy as np, csv
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.family"]="Times New Roman"; plt.rcParams["axes.unicode_minus"]=False
B=os.environ.get("YUEXI_BASE") or r"C:/Users/han/Desktop/粤西论文文件夹/YueXi0518/YueXi0518"
OUT=B+r"\code\figures_hires\Fig7_lisa_arcgis.png"
meta=json.load(open(B+r"\code\lisa_meta.json"))
gI=meta["global_moran"]; pct=meta["pct"]

xs=[];ys=[];cs=[]
with open(B+r"\code\lisa_points.csv") as f:
    rd=csv.reader(f); next(rd)
    for a,b,c in rd: xs.append(float(a)/1000); ys.append(float(b)/1000); cs.append(int(c))
xs=np.array(xs);ys=np.array(ys);cs=np.array(cs)

# study-area boundary (UTM km)
rings=[]
with arcpy.da.SearchCursor(B+r"\BJ\BJ.shp",["SHAPE@"]) as cur:
    for (shp,) in cur:
        if shp is None: continue
        for part in shp:
            r=[(p.X/1000,p.Y/1000) for p in part if p]
            if len(r)>2: rings.append(np.array(r))

ST={0:("#cfd8dc","Not significant",4),1:("#d32f2f","HH (eco-core)",9),
    2:("#1565c0","LL (threat hotspot)",9),3:("#fb8c00","HL (stepping stone)",12),
    4:("#4dd0e1","LH (edge)",12)}
fig,ax=plt.subplots(figsize=(8.6,7.4),dpi=600)
for r in rings: ax.plot(r[:,0],r[:,1],color="#222",lw=0.9,zorder=2)
for k in [0,2,1,4,3]:
    m=cs==k; c,l,s=ST[k]
    ax.scatter(xs[m],ys[m],s=s,c=c,marker="s",lw=0,alpha=0.85,zorder=3,
               label=f"{l} ({pct.get(str(k),0):.1f}%)")
ax.set_aspect("equal")
ax.set_xlabel("UTM Easting (km)",fontsize=10); ax.set_ylabel("UTM Northing (km)",fontsize=10)
ax.tick_params(labelsize=9); ax.grid(True,ls=":",lw=0.4,color="#666",alpha=0.5)
ax.set_title(f"LISA clusters of forest within-class HQ residuals\n(global Moran's $I$ = {gI:.3f}, p < 0.001; KNN k = 8, 999 permutations)",
             fontsize=10.5,fontweight="bold")
# scale bar + north arrow
x0=xs.min()+5; y0=ys.min()+5
ax.plot([x0,x0+50],[y0,y0],color="k",lw=2.5,solid_capstyle="butt",zorder=6)
ax.plot([x0,x0],[y0,y0+2.5],"k",lw=1.2);ax.plot([x0+50,x0+50],[y0,y0+2.5],"k",lw=1.2)
ax.text(x0+25,y0+4,"50 km",ha="center",fontsize=8,zorder=6)
ax.annotate("N",xy=(xs.max()-6,ys.max()-6),xytext=(xs.max()-6,ys.max()-24),ha="center",
            fontsize=11,fontweight="bold",arrowprops=dict(arrowstyle="-|>",color="k",lw=1.6),zorder=6)
ax.legend(loc="center left",bbox_to_anchor=(1.02,0.5),fontsize=9,title="LISA cluster",title_fontsize=9.5,framealpha=0.95)
fig.savefig(OUT,bbox_inches="tight",facecolor="white",dpi=600); plt.close(fig)
import os; from PIL import Image
print("SAVED",OUT,os.path.getsize(OUT),"px",Image.open(OUT).size,"| Moran",gI,"n",len(xs))

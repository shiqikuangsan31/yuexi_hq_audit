# -*- coding: utf-8 -*-
# Fig 2: (a) LUCC 2020 + (b) InVEST HQ 2020, redrawn in ArcGIS Pro python env.
# Real full-res rasters (UTM 49N), study-area boundary, scale bar, grid, legend/colorbar.
import arcpy, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
plt.rcParams["font.family"]="Times New Roman"; plt.rcParams["axes.unicode_minus"]=False

B=r"C:/Users/han/Desktop/粤西论文文件夹/YueXi0518/YueXi0518"
OUT=B+r"\code\figures_hires\Fig2_lucc_hq_arcgis.png"
LUCC=B+r"\lucc\lucc2020.tif"
HQ=B+r"\生境质量结果输出\SJ2020\quality_c_SJ2020.tif"
BND=B+r"\BJ\BJ.shp"

NAME={1:"Cropland",2:"Forest",3:"Grassland",4:"Water",5:"Built-up",6:"Unused"}
COL ={1:"#f4e04d",2:"#2e7d32",3:"#9ccc65",4:"#1e88e5",5:"#e53935",6:"#9e9e9e"}

def read_ras(path, step):
    d=arcpy.Describe(path); ext=d.extent
    a=arcpy.RasterToNumPyArray(path, nodata_to_value=-9999).astype(float)
    a[a==-9999]=np.nan
    a=a[::step,::step]
    return a,(ext.XMin,ext.YMin,ext.XMax,ext.YMax)

lucc,ext=read_ras(LUCC,5)
hq,_=read_ras(HQ,5)
print("LUCC uniq:", np.unique(lucc[np.isfinite(lucc)])[:12])
print("HQ range:", np.nanmin(hq), np.nanmax(hq), "shape",hq.shape)
W,S,E,N=ext
# to km
extkm=[W/1000,E/1000,S/1000,N/1000]

# study-area boundary (UTM) -> km
rings=[]
with arcpy.da.SearchCursor(BND,["SHAPE@"]) as cur:
    for (shp,) in cur:
        if shp is None: continue
        for part in shp:
            r=[(p.X/1000,p.Y/1000) for p in part if p]
            if len(r)>2: rings.append(np.array(r))
print("boundary rings:",len(rings))

def add_common(ax):
    for r in rings: ax.plot(r[:,0],r[:,1],color="#222",lw=0.8,zorder=4)
    ax.set_xlim(extkm[0],extkm[1]); ax.set_ylim(extkm[2],extkm[3])
    ax.set_aspect("equal")
    ax.set_xlabel("UTM Easting (km)",fontsize=9); ax.set_ylabel("UTM Northing (km)",fontsize=9)
    ax.tick_params(labelsize=8); ax.grid(True,ls=":",lw=0.4,color="#666",alpha=0.5)
    # scale bar 50 km
    x0=extkm[0]+8; y0=extkm[2]+8
    ax.plot([x0,x0+50],[y0,y0],color="k",lw=2.5,solid_capstyle="butt",zorder=6)
    ax.plot([x0,x0],[y0,y0+2.5],"k",lw=1.2); ax.plot([x0+50,x0+50],[y0,y0+2.5],"k",lw=1.2)
    ax.text(x0+25,y0+4,"50 km",ha="center",fontsize=8,zorder=6)
    # north arrow
    ax.annotate("N",xy=(extkm[1]-10,extkm[3]-10),xytext=(extkm[1]-10,extkm[3]-28),
                ha="center",fontsize=11,fontweight="bold",
                arrowprops=dict(arrowstyle="-|>",color="k",lw=1.6),zorder=6)

fig,axes=plt.subplots(1,2,figsize=(13,6.6),dpi=600)
# (a) LUCC
vals=sorted(NAME.keys())
cmap=ListedColormap([COL[v] for v in vals])
norm=BoundaryNorm([v-0.5 for v in vals]+[vals[-1]+0.5],cmap.N)
axes[0].imshow(np.where(np.isfinite(lucc),lucc,np.nan),extent=extkm,origin="upper",cmap=cmap,norm=norm,zorder=1)
add_common(axes[0])
axes[0].set_title("(a) Land use / land cover, 2020",fontsize=10.5,fontweight="bold")
leg=[Patch(facecolor=COL[v],edgecolor="#333",label=NAME[v]) for v in vals]
axes[0].legend(handles=leg,loc="upper right",fontsize=8,framealpha=0.9,title="LULC",title_fontsize=8.5)
# (b) HQ
im=axes[1].imshow(np.where(np.isfinite(hq),hq,np.nan),extent=extkm,origin="upper",cmap="YlGn",vmin=0,vmax=0.8,zorder=1)
add_common(axes[1])
axes[1].set_title("(b) InVEST habitat quality, 2020 (mean = 0.405)",fontsize=10.5,fontweight="bold")
cb=fig.colorbar(im,ax=axes[1],fraction=0.046,pad=0.02); cb.set_label("Habitat quality",fontsize=9); cb.ax.tick_params(labelsize=8)

plt.tight_layout()
fig.savefig(OUT,bbox_inches="tight",facecolor="white",dpi=600); plt.close(fig)
import os; from PIL import Image
print("SAVED",OUT,os.path.getsize(OUT),"px",Image.open(OUT).size)

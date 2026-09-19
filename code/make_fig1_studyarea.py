# -*- coding: utf-8 -*-
# Fig 1 study-area map, redrawn in the ArcGIS Pro python env (arcpy + matplotlib).
# Standard SCI "overview + detail" layout, real data, complete China territory.
import arcpy, json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly, Rectangle, FancyArrow
from matplotlib.collections import PatchCollection
import matplotlib.font_manager as fm

plt.rcParams["font.family"]="Times New Roman"
plt.rcParams["axes.unicode_minus"]=False

B=os.environ.get("YUEXI_BASE") or r"C:/Users/han/Desktop/粤西论文文件夹/YueXi0518/YueXi0518"
BD=os.environ.get("YUEXI_BOUNDARIES") or r"C:\Users\han\yuexi_fmt\boundaries"
OUT=B+r"\code\figures_hires\Fig1_studyarea_arcgis.png"

# ---------- read GeoJSON polygons ----------
def load_polys(path):
    d=json.load(open(path,encoding="utf-8")); feats=[]
    for f in d["features"]:
        g=f.get("geometry")
        if not g: continue
        t=g["type"]; coords=g["coordinates"]
        polys=[coords] if t=="Polygon" else coords
        rings=[]
        for poly in polys:
            if poly and poly[0]:
                rings.append(np.array(poly[0]))
        feats.append((f["properties"].get("name",""), rings))
    return feats
china=load_polys(BD+r"\china_100000.json")
gd=load_polys(BD+r"\guangdong_440000.json")

# ---------- read DEM (lat/lon clipped) downsampled ----------
dem_path=B+r"\过程文件\DEMcj.tif"
d=arcpy.Describe(dem_path); ext=d.extent
ras=arcpy.Raster(dem_path)
nd=ras.noDataValue
arr=arcpy.RasterToNumPyArray(dem_path, nodata_to_value=-9999).astype(float)
arr[arr<=-9999]=np.nan; arr[arr<-1000]=np.nan
# downsample for plotting
step=max(1, arr.shape[0]//1600)
arr=arr[::step,::step]
W,S,E,N=ext.XMin,ext.YMin,ext.XMax,ext.YMax
print("DEM arr",arr.shape,"ext",round(W,2),round(S,2),round(E,2),round(N,2),"elev",np.nanmin(arr),np.nanmax(arr))

# ---------- study-area boundary from shp (lat/lon) ----------
sa_rings=[]
with arcpy.da.SearchCursor(B+r"\过程文件\研究区RH.shp",["SHAPE@"]) as cur:
    for (shp,) in cur:
        if shp is None: continue
        for part in shp:
            ring=[(p.X,p.Y) for p in part if p]
            if len(ring)>2: sa_rings.append(np.array(ring))
print("study-area rings:",len(sa_rings))

# ============ FIGURE ============
fig=plt.figure(figsize=(13,6.4),dpi=600)
gs=fig.add_gridspec(1,2,width_ratios=[1.0,1.5],wspace=0.16)

# ---- (a) China locator ----
axl=fig.add_subplot(gs[0,0])
for nm,rings in china:
    for r in rings:
        axl.plot(r[:,0],r[:,1],color="#888",lw=0.3,zorder=1)
# highlight Guangdong
for nm,rings in china:
    if nm=="广东省":
        for r in rings:
            axl.add_patch(MplPoly(r,closed=True,facecolor="#d24b4b",edgecolor="#7a1f1f",lw=0.5,alpha=0.85,zorder=2))
# study-area red box
axl.add_patch(Rectangle((109.7,20.2),112.4-109.7,22.7-20.2,fill=False,edgecolor="red",lw=1.6,zorder=5))
axl.annotate("Study area",xy=(111.0,21.4),xytext=(118,15),fontsize=10,color="red",
             arrowprops=dict(arrowstyle="->",color="red",lw=1.2),zorder=6)
axl.text(103,52,"China",fontsize=12,fontweight="bold")
axl.set_xlim(72,136); axl.set_ylim(2,55)
axl.set_aspect(1/np.cos(np.deg2rad(30)))
axl.set_xticks([80,100,120]); axl.set_yticks([10,25,40,55])
axl.set_xticklabels([f"{v}\u00b0E" for v in [80,100,120]],fontsize=8)
axl.set_yticklabels([f"{v}\u00b0N" for v in [10,25,40,55]],fontsize=8)
axl.set_title("(a) Location in China",fontsize=11,fontweight="bold")
for s in axl.spines.values(): s.set_linewidth(0.8)

# ---- (b) DEM main map ----
axm=fig.add_subplot(gs[0,1])
im=axm.imshow(arr,extent=[W,E,S,N],origin="upper",cmap="terrain",
              vmin=0,vmax=float(np.nanpercentile(arr,99)),zorder=1)
# study-area boundary
for r in sa_rings:
    axm.plot(r[:,0],r[:,1],color="#222",lw=1.0,zorder=3)
# Guangdong-coast context: plot study-area cities outline lightly (optional skip)
axm.set_xlim(W,E); axm.set_ylim(S,N)
axm.set_aspect(1/np.cos(np.deg2rad(21.5)))
# graticule
xt=[110,111,112]; yt=[20.5,21.0,21.5,22.0,22.5]
axm.set_xticks(xt); axm.set_yticks(yt)
axm.set_xticklabels([f"{v}\u00b0E" for v in xt],fontsize=9)
axm.set_yticklabels([f"{v}\u00b0N" for v in yt],fontsize=9)
axm.grid(True,ls=":",lw=0.4,color="#555",alpha=0.6)
axm.set_title("(b) Topography of the Yuexi region (DEM, Copernicus GLO-30, 30 m)",fontsize=10.5,fontweight="bold")
# place-name labels with white bbox, in empty spots (no overlap)
bb=dict(boxstyle="round,pad=0.2",fc="white",ec="none",alpha=0.8)
axm.text(110.5,22.35,"Tianlu\u2013Yunwu\nforest core",fontsize=8.5,ha="center",bbox=bb,zorder=5)
axm.text(111.5,21.25,"Coastal urban\ncorridor",fontsize=8.5,ha="center",color="#7a1f1f",bbox=bb,zorder=5)
axm.text(111.7,20.45,"South China Sea",fontsize=8.5,style="italic",color="#1f4e79",bbox=bb,zorder=5)
# scale bar (~50 km).  1 deg lon at 21.5N ~ 103.6 km -> 50 km = 0.4827 deg
km=50; dlon=km/(111.32*np.cos(np.deg2rad(21.5)))
x0=W+0.12; y0=S+0.10
axm.plot([x0,x0+dlon],[y0,y0],color="k",lw=2.5,zorder=6,solid_capstyle="butt")
axm.plot([x0,x0],[y0,y0+0.03],color="k",lw=1.2); axm.plot([x0+dlon,x0+dlon],[y0,y0+0.03],color="k",lw=1.2)
axm.text(x0+dlon/2,y0+0.05,f"{km} km",ha="center",fontsize=8,zorder=6)
# north arrow (top-right, small)
axm.annotate("N",xy=(E-0.12,N-0.12),xytext=(E-0.12,N-0.34),ha="center",fontsize=11,fontweight="bold",
             arrowprops=dict(arrowstyle="-|>",color="k",lw=1.6),zorder=6)
# colorbar
cb=fig.colorbar(im,ax=axm,fraction=0.040,pad=0.02)
cb.set_label("Elevation (m)",fontsize=9); cb.ax.tick_params(labelsize=8)

fig.savefig(OUT,bbox_inches="tight",facecolor="white",dpi=600)
plt.close(fig)
import os
print("SAVED",OUT,os.path.getsize(OUT),"bytes")
from PIL import Image
print("px:",Image.open(OUT).size)

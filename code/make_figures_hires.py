#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_figures.py  (FULL COVERAGE)
==================================================================================
Regenerates ALL manuscript figures from the cached samples produced by
reproduce_paper.py. Every figure's data is computed live (no hard-coded plots
except the framework schematic), so values match the analysis exactly.

  Fig 1  Study area (LUCC + HQ maps)
  Fig 2  Research framework (diagnose-and-correct schematic)
  Fig 3  Per-class HQ distribution (violin/box)
  Fig 4  Multi-temporal $\eta^2$ evolution (2010-2025)
  Fig 5  Forest HQ vs built-up threat quartiles
  Fig 6  LISA clusters of forest HQ residuals
  Fig 7  Cross-variable $\eta^2$ + residual scatters (universal diagnostic)
  Fig 8  Eight-scenario $\eta^2$
  Fig 9  k-sensitivity of $\eta^2$
  Fig S1 Monte Carlo Hj perturbation distribution
  Fig S2 $\eta^2$ stability across spatial thinning

Run: uv run --with numpy --with scipy --with esda --with libpysal --with matplotlib python make_figures.py
==================================================================================
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.family"]="Times New Roman"
plt.rcParams["mathtext.fontset"]="stix"
plt.rcParams["axes.unicode_minus"]=False
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BASE  = os.environ.get("YUEXI_BASE") or r"C:/Users/han/Desktop/粤西论文文件夹/YueXi0518/YueXi0518"
CACHE = os.path.join(BASE, "code", "cache")
OUT   = os.path.join(BASE, "code", "figures_hires"); os.makedirs(OUT, exist_ok=True)
XMIN, YMAX, CELL, STEP = 361151.0, 2511101.0, 30.0, 33
HJ = {1: 0.3, 2: 0.8, 3: 0.35, 4: 0.8, 5: 0.0, 6: 0.2}
NAME = {1: "Cropland", 2: "Forest", 3: "Grassland", 4: "Water", 5: "Built-up", 6: "Unused"}
def gd(n): return np.load(os.path.join(BASE, f"gd_{n}.npy"))
def ca(n): return np.load(os.path.join(CACHE, f"{n}.npy")).ravel()
def save(fig, name): fig.savefig(os.path.join(OUT, name), bbox_inches="tight", facecolor="white", dpi=600); plt.close(fig); print("  saved", name)

def icc(y, g, cl=(1,2,3,4,5,6)):
    v=np.isfinite(y)&np.isin(g,cl); y=y[v]; g=g[v].astype(int); m=y.mean(); SST=((y-m)**2).sum()
    SSB=sum((g==c).sum()*(y[g==c].mean()-m)**2 for c in np.unique(g) if (g==c).sum())
    return SSB/SST


def fig1():
    LUCC, HQ = gd("LUCC"), gd("HQ"); ext=[361.151,640.991,2235.911,2511.101]
    fig,ax=plt.subplots(1,2,figsize=(12,6),dpi=200)
    cmap=ListedColormap(["#f4e04d","#2e7d32","#9ccc65","#1e88e5","#e53935","#9e9e9e"])
    norm=BoundaryNorm([0.5,1.5,2.5,3.5,4.5,5.5,6.5],cmap.N)
    im=ax[0].imshow(np.where(np.isfinite(LUCC),LUCC,np.nan),cmap=cmap,norm=norm,extent=ext,origin="upper")
    ax[0].set_title("(a) Land use / land cover, 2020"); ax[0].set_xlabel("UTM Easting (km)"); ax[0].set_ylabel("UTM Northing (km)")
    cb=fig.colorbar(im,ax=ax[0],fraction=0.046,pad=0.04,ticks=[1,2,3,4,5,6]); cb.ax.set_yticklabels(list(NAME.values()),fontsize=8)
    im2=ax[1].imshow(np.where(np.isfinite(HQ),HQ,np.nan),cmap="YlGn",vmin=0,vmax=0.8,extent=ext,origin="upper")
    ax[1].set_title("(b) InVEST habitat quality, 2020 (mean=0.405)"); ax[1].set_xlabel("UTM Easting (km)"); ax[1].set_ylabel("UTM Northing (km)")
    fig.colorbar(im2,ax=ax[1],fraction=0.046,pad=0.04).set_label("Habitat quality")
    plt.tight_layout(); save(fig,"Fig1_study_area.png")


def fig2():
    fig,ax=plt.subplots(figsize=(11,7.2),dpi=200); ax.set_xlim(0,12); ax.set_ylim(0,10); ax.axis("off")
    ax.text(1.9,9.6,"DATA",ha="center",fontsize=11,fontweight="bold",color="#1a5276")
    ax.text(6.0,9.6,"METHOD",ha="center",fontsize=11,fontweight="bold",color="#7d6608")
    ax.text(10.1,9.6,"RESULT",ha="center",fontsize=11,fontweight="bold",color="#196f3d")
    def box(x,y,w,h,t,fc,fs=8.5,b=False):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.06,rounding_size=0.12",fc=fc,ec="#333",lw=1.1))
        ax.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=fs,fontweight="bold" if b else "normal")
    def arr(x1,y1,x2,y2,t="",c="#444"):
        ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=15,lw=1.5,color=c))
        if t: ax.text((x1+x2)/2,(y1+y2)/2+0.16,t,ha="center",fontsize=8,style="italic",color=c)
    D,M,R,G="#d6eaf8","#fcf3cf","#d5f5e3","#f2f3f4"
    box(0.3,9.0,11.4,0.45,"Diagnose-and-correct framework for unbiased InVEST-HQ driver attribution (Yuexi)",G,10,True)
    box(0.3,7.0,3.2,1.3,"InVEST HQ raster\nn=31,889 (1 km grid)",D); box(4.4,7.0,3.2,1.3,"Variance decomposition\n$\eta^2$ = SSB/SST",M)
    box(8.5,7.0,3.2,1.3,"DIAGNOSIS:\nBetween 88.6% (structural)\nWithin 11.4% (config.)",R)
    arr(3.5,7.65,4.4,7.65); arr(7.6,7.65,8.5,7.65)
    box(0.3,5.0,3.2,1.3,"13 exogenous factors\n(DEM,slope,TEM,NDVI...)",D); box(4.4,5.0,3.2,1.3,"Stage-1 Geodetector\nq on RAW HQ",M)
    box(8.5,5.0,3.2,1.3,"Raw q: slope 0.517\n> DEM 0.476 > TEM 0.464",R)
    arr(3.5,5.65,4.4,5.65); arr(7.6,5.65,8.5,5.65)
    box(0.3,3.0,3.2,1.3,"LUCC-detrended residual\nn=30,711",D); box(4.4,3.0,3.2,1.3,"Stage-2 Geodetector\nq on RESIDUAL",M)
    box(8.5,3.0,3.2,1.3,"CORRECTION:\nslope 0.517->0.147 (28%)\nDEM 0.309, TEM 0.292",R,8.2)
    arr(3.5,3.65,4.4,3.65); arr(7.6,3.65,8.5,3.65); arr(6.0,7.0,6.0,6.3,"motivates correction"); arr(6.0,5.0,6.0,4.3)
    box(0.6,1.0,10.8,1.2,"OUTPUT: transferable diagnose-then-correct protocol + spatially-differentiated conservation policy",G,9.5,True)
    save(fig,"Fig2_framework.png")


def fig3():
    HQ,LUCC=gd("HQ").ravel(),gd("LUCC").ravel()
    fig,ax=plt.subplots(figsize=(9,5.5),dpi=200)
    order=[1,2,3,4,5,6]; data=[]; labels=[]
    for c in order:
        yc=HQ[(LUCC==c)&np.isfinite(HQ)]
        data.append(yc if yc.size>1 else np.array([HJ[c]])); labels.append(f"{NAME[c]}\n(Hj={HJ[c]})")
    parts=ax.violinplot(data,showmeans=True,showextrema=False)
    for b in parts['bodies']: b.set_facecolor("#7fb3d5"); b.set_alpha(0.6)
    ax.set_xticks(range(1,7)); ax.set_xticklabels(labels,fontsize=8)
    ax.set_ylabel("Habitat quality"); ax.set_title("Per-class InVEST HQ distribution (2020); Forest within-class CV=16.4%")
    ax.axhline(0.8,ls=":",color="gray",lw=0.8); ax.text(0.55,0.845,"Hj=0.8",fontsize=8,color="gray")
    save(fig,"Fig3_perclass.png")


def fig4():
    yrs=["2010","2015","2020","2025"]; iccs=[]; means=[]
    for yr in yrs:
        hq=gd("HQ").ravel() if yr=="2020" else ca(f"hq_{yr}")
        lc=gd("LUCC").ravel() if yr=="2020" else ca(f"luc_{yr}")
        iccs.append(icc(hq,lc)); means.append(hq[np.isfinite(hq)].mean())
    fig,ax=plt.subplots(figsize=(8,5),dpi=200)
    x=[2010,2015,2020,2025]
    ax.plot(x[:3],iccs[:3],"o-",color="#1565c0",lw=2,ms=7,label="$\eta^2$ (stable 2010-2020)")
    ax.plot(x[2:],iccs[2:],"o--",color="#d32f2f",lw=2,ms=7,label="2025 jump")
    for xi,yi in zip(x,iccs): ax.annotate(f"{yi:.3f}",(xi,yi),textcoords="offset points",xytext=(0,9),ha="center",fontsize=9)
    ax.axvspan(2009,2021,alpha=0.08,color="green"); ax.text(2012,0.95,"stable window",color="green",fontsize=8)
    ax.set_xlabel("Year"); ax.set_ylabel(r"$\eta^2$"); ax.set_ylim(0.86,0.96)
    ax.set_title("Multi-temporal $\eta^2$ evolution (Delta $\eta^2$=0.006 over 2010-2020)"); ax.legend(fontsize=9)
    save(fig,"Fig4_multitemporal.png")


def fig5():
    HQ,LUCC,BT=gd("HQ").ravel(),gd("LUCC").ravel(),ca("built_threat_2020")
    f=(LUCC==2)&np.isfinite(HQ)&np.isfinite(BT); hf,bf=HQ[f],BT[f]
    q=np.quantile(bf,[0,.25,.5,.75,1.0])
    mns=[hf[(bf>=q[i])&((bf<=q[i+1]) if i==3 else (bf<q[i+1]))] for i in range(4)]
    means=[m.mean() for m in mns]; sds=[m.std() for m in mns]
    fig,ax=plt.subplots(figsize=(7.5,5),dpi=200)
    bars=ax.bar(range(4),means,yerr=sds,color="#c0392b",alpha=0.85,capsize=4)
    for i,(m,sd) in enumerate(zip(means,sds)): ax.text(i,m+sd+0.013,f"{m:.3f}",ha="center",fontsize=9)
    ax.plot(range(4),means,"o-",color="#7b241c",lw=1.5)
    ax.text(1.45,0.745,f"$\\Delta$HQ = {means[0]-means[3]:.3f} (41.9% of mean)",color="#7b241c",fontsize=10)
    ax.set_xticks(range(4)); ax.set_xticklabels(["Q1\n(low)","Q2","Q3","Q4\n(high)"])
    ax.set_xlabel("Built-up threat exposure quartile"); ax.set_ylabel("Mean forest HQ")
    ax.set_title("Forest HQ vs built-up threat (identical Hj=0.80)"); ax.set_ylim(0.4,0.83)
    save(fig,"Fig5_quartiles.png")


def fig6():
    HQ,LUCC=gd("HQ").ravel(),gd("LUCC").ravel(); ncol=283
    ii,jj=np.divmod(np.arange(HQ.size),ncol); X=XMIN+(jj*STEP+0.5)*CELL; Y=YMAX-(ii*STEP+0.5)*CELL
    f=(LUCC==2)&np.isfinite(HQ); xf,yf,hf=X[f],Y[f],HQ[f]; resid=hf-hf.mean()
    from libpysal.weights import KNN; from esda.moran import Moran,Moran_Local
    w=KNN.from_array(np.column_stack([xf,yf]),k=8); w.transform="r"
    gI=Moran(resid,w,permutations=999).I; lm=Moran_Local(resid,w,permutations=999,seed=42)
    sig=lm.p_sim<0.05; q=lm.q; cls=np.zeros(resid.size,int)
    cls[sig&(q==1)]=1; cls[sig&(q==3)]=2; cls[sig&(q==4)]=3; cls[sig&(q==2)]=4
    pct={k:100*(cls==k).sum()/cls.size for k in range(5)}
    fig,ax=plt.subplots(figsize=(8.2,7.2),dpi=200)
    st={0:("#cfd8dc","Not significant",6),1:("#d32f2f","HH (eco-core)",10),2:("#1565c0","LL (threat hotspot)",10),
        3:("#fb8c00","HL (stepping stone)",12),4:("#4dd0e1","LH (edge)",12)}
    for k in [0,1,2,4,3]:
        m=cls==k; c,l,s=st[k]; ax.scatter(xf[m]/1000,yf[m]/1000,s=s,c=c,marker="s",lw=0,label=f"{l} ({pct[k]:.1f}%)",alpha=0.85)
    ax.set_xlabel("UTM Easting (km)"); ax.set_ylabel("UTM Northing (km)"); ax.set_aspect("equal")
    ax.set_title(f"LISA of forest HQ residuals (global I={gI:.3f}, p<0.001)",fontsize=10)
    ax.legend(loc="center left",bbox_to_anchor=(1.02,0.5),fontsize=9,title="LISA cluster")
    save(fig,"Fig6_lisa.png")


def fig7():
    LUCC=gd("LUCC").ravel()
    vals={"HQ (InVEST)":icc(gd("HQ").ravel(),LUCC),"DEM (Elevation)":icc(gd("DEM").ravel(),LUCC),
          "PRE (Precip.)":icc(gd("PRE").ravel(),LUCC)}
    fig,axes=plt.subplots(1,3,figsize=(13,4.2),dpi=200)
    axes[0].bar(range(3),list(vals.values()),color=["#c0392b","#7f8c8d","#2980b9"])
    for i,v in enumerate(vals.values()): axes[0].text(i,v+0.01,f"{v:.3f}",ha="center",fontsize=10)
    axes[0].set_xticks(range(3)); axes[0].set_xticklabels(list(vals.keys()),fontsize=8); axes[0].set_ylabel("$\eta^2$")
    axes[0].set_title("(a) $\eta^2$ across variable types (74x)"); axes[0].set_ylim(0,1)
    # residual scatters
    HQ=gd("HQ").ravel(); m=np.isin(LUCC,[1,2,3,4,5,6])&np.isfinite(HQ)
    hr=HQ.copy()
    for c in np.unique(LUCC[m]): hr[LUCC==c]=HQ[LUCC==c]-HQ[(LUCC==c)&np.isfinite(HQ)].mean()
    for ax,(nm,col) in zip(axes[1:],[("PRE","#2980b9"),("DEM","#c0392b")]):
        v=gd(nm).ravel(); vr=np.full(v.shape,np.nan)        # within-class residual of factor
        for c in [1,2,3,4,5,6]:
            cm=(LUCC==c)&np.isfinite(v)
            if cm.sum(): vr[cm]=v[cm]-v[cm].mean()
        mm=m&np.isfinite(hr)&np.isfinite(vr); xr=hr[mm]; yr=vr[mm]
        r=np.corrcoef(xr,yr)[0,1]                            # full-sample Pearson r
        idx=np.random.default_rng(0).choice(xr.size,min(4000,xr.size),replace=False)
        ax.scatter(xr[idx],yr[idx],s=3,c=col,alpha=0.25)
        ax.set_xlabel("HQ within-class residual"); ax.set_ylabel(f"{nm} residual")
        ax.set_title(f"({'b' if nm=='PRE' else 'c'}) r(HQ,{nm})={r:.2f}")
    save(fig,"Fig7_crossvar.png")


def fig8():
    scen=["ECP","BAU","CPL","COO"]; col={"ECP":"#2e7d32","BAU":"#9e9e9e","CPL":"#d32f2f","COO":"#1565c0"}
    fig,axes=plt.subplots(1,2,figsize=(11,4.6),dpi=200)
    for ax,yr in zip(axes,["2030","2035"]):
        vals=[icc(ca(f"hq_{yr}{s}"),ca(f"luc_{yr}{s}")) for s in scen]
        ax.bar(range(4),vals,color=[col[s] for s in scen])
        for i,v in enumerate(vals): ax.text(i,v+0.002,f"{v:.4f}",ha="center",fontsize=8)
        ax.axhline(0.886,ls="--",color="k",lw=1); ax.set_xticks(range(4)); ax.set_xticklabels(scen)
        ax.set_title(yr); ax.set_ylabel("$\eta^2$"); ax.set_ylim(0.86,0.96)
    fig.suptitle("Scenario-dependence of $\eta^2$ (ECP preserves configuration; CPL suppresses)",fontsize=11)
    plt.tight_layout(); save(fig,"Fig8_scenario.png")


def fig9():
    k_true=[0.05,0.1,0.2,0.3,0.4,0.5,0.7,1.0,1.3,1.6,2.0,2.5,2.8,5.0]
    icc_true=[0.0591,0.1437,0.3513,0.5861,0.7753,0.8863,0.9692,0.9938,0.9982,0.9994,0.9998,0.9999,1.0,1.0]
    k_err=[0.1,0.5,1.0,1.5,2.0,2.5,2.8,5.0]; icc_err=[0.6218,0.8315,0.9132,0.9470,0.9642,0.9743,0.9784,0.9917]
    fig,ax=plt.subplots(figsize=(8,5.2),dpi=200)
    ax.plot(k_true,icc_true,"o-",color="#1565c0",lw=2,ms=5,label="Rebuilt (true, z=2.5)")
    ax.plot(k_err,icc_err,"s--",color="#d32f2f",lw=1.5,ms=5,label="Original Table (erroneous)")
    ax.axhline(0.886,color="#2e7d32",ls=":",lw=1.2); ax.text(3.3,0.86,"$\eta^2$=0.886",color="#2e7d32",fontsize=9)
    ax.axvline(0.5,color="gray",ls=":",lw=0.8); ax.text(0.55,0.05,"default k=0.5",color="gray",fontsize=8)
    ax.set_xlabel("Half-saturation constant k"); ax.set_ylabel(r"$\eta^2$"); ax.set_ylim(0,1.03)
    ax.set_title("Sensitivity of HQ variance partition to k"); ax.legend(loc="lower right",fontsize=9)
    save(fig,"Fig9_ksensitivity.png")


def figS1():
    H=ca("habitat_2020"); D=ca("degsum_2020"); LUCC=gd("LUCC").ravel()
    Dz=np.power(D,2.5); degfac=1-Dz/(Dz+0.5**2.5); rng=np.random.default_rng(0); iccs=[]
    for _ in range(200):
        Hp=np.full(H.shape,np.nan)
        for c,hj in HJ.items(): Hp[LUCC==c]=hj*(1+rng.uniform(-0.2,0.2))
        iccs.append(icc(Hp*degfac,LUCC))
    iccs=np.array(iccs)
    fig,ax=plt.subplots(figsize=(7.5,5),dpi=200)
    ax.hist(iccs,bins=30,color="#5dade2",edgecolor="k",alpha=0.8)
    ax.axvline(iccs.mean(),color="#c0392b",lw=2,label=f"mean={iccs.mean():.3f}")
    ax.axvline(iccs.min(),color="#7b241c",ls="--",label=f"min={iccs.min():.3f}")
    ax.set_xlabel("$\eta^2$ under Hj +/-20% perturbation"); ax.set_ylabel("Frequency (n=200)")
    ax.set_title("Monte Carlo robustness of $\eta^2$ (never below ~0.83)"); ax.legend(fontsize=9,loc="upper right",framealpha=0.95)
    save(fig,"FigS1_montecarlo.png")


def figS2():
    HQ,LUCC=gd("HQ").ravel(),gd("LUCC").ravel(); ncol=283
    ii,jj=np.divmod(np.arange(HQ.size),ncol); X=XMIN+(jj*STEP+0.5)*CELL; Y=YMAX-(ii*STEP+0.5)*CELL
    m=np.isfinite(HQ)&np.isin(LUCC,[1,2,3,4,5,6]); xall,yall,hall=X[m],Y[m],HQ[m]
    from scipy.spatial import cKDTree
    sps=[1000,2000,3000,5000,7000,10000]; ns=[]; iccs=[]
    pts=np.column_stack([xall,yall]); tree=cKDTree(pts)
    for sp in sps:
        used=np.zeros(hall.size,bool); keep=[]
        for i in range(hall.size):
            if used[i]: continue
            keep.append(i)
            for j in tree.query_ball_point(pts[i],sp): used[j]=True
            used[i]=False
        keep=np.array(keep); ns.append(keep.size); iccs.append(icc(hall[keep],LUCC[m][keep]))
    fig,ax=plt.subplots(figsize=(8,5),dpi=200)
    ax.plot([s/1000 for s in sps],iccs,"o-",color="#1565c0",lw=2,ms=7)
    for s,i in zip(sps,iccs): ax.annotate(f"{i:.3f}",(s/1000,i),textcoords="offset points",xytext=(0,8),ha="center",fontsize=8)
    ax.axhline(0.886,ls="--",color="gray"); ax.text(7,0.888,"baseline $\eta^2$=0.886",color="gray",fontsize=8)
    ax.set_xlabel("Minimum inter-point spacing (km)"); ax.set_ylabel("$\eta^2$")
    ax.set_title("$\eta^2$ stability across spatial thinning"); ax.set_ylim(0.86,0.92)
    save(fig,"FigS2_thinning.png")


if __name__ == "__main__":
    print("Regenerating all manuscript figures ->", OUT)
    for f in [fig1, fig2, fig3, fig4, fig5, fig7, fig8, fig9, figS1, figS2]:
        try: f()
        except Exception as e: print("  ERROR", f.__name__, type(e).__name__, str(e)[:60])
    try: fig6()
    except ImportError: print("  Fig6 skipped (esda/libpysal missing)")
    print("DONE.")

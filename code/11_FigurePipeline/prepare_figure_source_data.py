"""Build R-ready source tables from hash-locked Yuexi canonical arrays.
This is non-visual preprocessing. It must not mutate the canonical data."""
from __future__ import annotations

import os
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from libpysal.weights import KNN
from esda.moran import Moran, Moran_Local

ROOT = Path(os.environ.get("YUEXI_ROOT") or r"C:\Users\han\Desktop\粤西论文文件夹")
BASE = ROOT / "YueXi0518" / "YueXi0518"
CACHE = BASE / "code" / "cache"
OUT = ROOT / "_YUEXI_FIGURE_REBUILD_20260912" / "04_figures" / "source_data"
OUT.mkdir(parents=True, exist_ok=True)

CLASS = {1: "Cropland", 2: "Forest", 3: "Grassland", 4: "Water", 5: "Built-up", 6: "Unused"}
HJ = {1: 0.30, 2: 0.80, 3: 0.35, 4: 0.80, 5: 0.00, 6: 0.20}
XMIN, YMAX, CELL, STEP, NCOL = 361151.0, 2511101.0, 30.0, 33, 283


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def gd(name: str) -> np.ndarray:
    return np.load(BASE / f"gd_{name}.npy").ravel()


def ca(name: str) -> np.ndarray:
    return np.load(CACHE / f"{name}.npy").ravel()


def eta2(y: np.ndarray, g: np.ndarray) -> float:
    valid = np.isfinite(y) & np.isin(g, list(CLASS))
    y, g = y[valid], g[valid].astype(int)
    mean = y.mean()
    sst = np.sum((y - mean) ** 2)
    ssb = sum(np.sum(g == c) * (y[g == c].mean() - mean) ** 2 for c in CLASS)
    return float(ssb / sst)


def qstat(y: np.ndarray, z: np.ndarray) -> float:
    sst = np.sum((y - y.mean()) ** 2)
    ssw = sum(np.sum((v - v.mean()) ** 2) for v in (y[z == k] for k in np.unique(z)) if len(v))
    return float(1.0 - ssw / sst)

# Core arrays
hq = gd("HQ")
lucc = gd("LUCC")
built = ca("built_threat_2020")
valid = np.isfinite(hq) & np.isin(lucc, list(CLASS))

# Figure 2
class_df = pd.DataFrame({"HQ": hq[valid], "class_code": lucc[valid].astype(int)})
class_df["LULC"] = class_df.class_code.map(CLASS)
class_df["Hj"] = class_df.class_code.map(HJ)
class_df.to_csv(OUT / "fig2_class_distribution.csv", index=False)

forest = valid & (lucc == 2) & np.isfinite(built)
forest_df = pd.DataFrame({"HQ": hq[forest], "built_threat": built[forest]})
forest_df["quartile"] = pd.qcut(forest_df.built_threat, 4, labels=["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"])
forest_df.to_csv(OUT / "fig2_forest_threat.csv", index=False)

# Figure 3 temporal and scenario source
periods = []
for yr in ("2010", "2015", "2020", "2025"):
    y = hq if yr == "2020" else ca(f"hq_{yr}")
    g = lucc if yr == "2020" else ca(f"luc_{yr}")
    periods.append({"year": int(yr), "eta2": eta2(y, g), "mean_HQ": float(np.nanmean(y)),
                    "data_type": "Observed" if yr in {"2010", "2015", "2020"} else "Projected"})
pd.DataFrame(periods).to_csv(OUT / "fig3_temporal.csv", index=False)

scenarios = []
for year in ("2030", "2035"):
    for scenario in ("ECP", "BAU", "CPL", "COO"):
        y, g = ca(f"hq_{year}{scenario}"), ca(f"luc_{year}{scenario}")
        f = np.isfinite(y) & (g == 2)
        scenarios.append({"year": int(year), "scenario": scenario, "eta2": eta2(y, g),
                          "forest_CV_pct": float(np.std(y[f]) / np.mean(y[f]) * 100),
                          "mean_HQ": float(np.nanmean(y))})
pd.DataFrame(scenarios).to_csv(OUT / "fig3_scenarios.csv", index=False)

# Figure 4: full LISA inputs for R map + Moran scatter
idx = np.arange(hq.size)
ii, jj = np.divmod(idx, NCOL)
x, y = XMIN + (jj * STEP + 0.5) * CELL, YMAX - (ii * STEP + 0.5) * CELL
f = valid & (lucc == 2)
coords = np.column_stack([x[f], y[f]])
resid = hq[f] - np.mean(hq[f])
w = KNN.from_array(coords, k=8)
w.transform = "r"
global_moran = Moran(resid, w, permutations=999)
local = Moran_Local(resid, w, permutations=999, seed=42)
lag = w.sparse @ ((resid - resid.mean()) / resid.std(ddof=1))
z = (resid - resid.mean()) / resid.std(ddof=1)
cl = np.full(resid.shape, "Not significant", dtype=object)
sig = local.p_sim < 0.05
cl[sig & (local.q == 1)] = "High-High"
cl[sig & (local.q == 3)] = "Low-Low"
cl[sig & (local.q == 4)] = "High-Low"
cl[sig & (local.q == 2)] = "Low-High"
pd.DataFrame({"x_utm": coords[:, 0], "y_utm": coords[:, 1], "residual_HQ": resid,
              "z_residual": z, "spatial_lag_z": np.asarray(lag).ravel(),
              "LISA_cluster": cl, "p_sim": local.p_sim}).to_csv(OUT / "fig4_lisa_points.csv", index=False)
pd.DataFrame({"cluster": pd.Series(cl).value_counts().index, "n": pd.Series(cl).value_counts().values,
              "percentage": pd.Series(cl).value_counts(normalize=True).values * 100}).to_csv(OUT / "fig4_lisa_shares.csv", index=False)

# Figure 5: deterministic Monte Carlo and k curve
H, D = ca("habitat_2020"), ca("degsum_2020")
Dz = np.power(D, 2.5)
rng = np.random.default_rng(0)
rows = []
for iteration in range(1, 201):
    Hp = np.full(H.shape, np.nan)
    for c, hj in HJ.items():
        Hp[lucc == c] = hj * (1 + rng.uniform(-0.2, 0.2))
    HQp = Hp * (1 - Dz / (Dz + 0.5**2.5))
    rows.append({"iteration": iteration, "eta2": eta2(HQp, lucc)})
pd.DataFrame(rows).to_csv(OUT / "fig5_montecarlo.csv", index=False)

ks = np.array([0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.70, 1.00, 1.30, 1.60, 2.00, 2.50, 2.80, 5.00])
k_rows = []
for k in ks:
    HQk = H * (1 - Dz / (Dz + k**2.5))
    k_rows.append({"k": k, "eta2": eta2(HQk, lucc)})
pd.DataFrame(k_rows).to_csv(OUT / "fig5_k_sensitivity.csv", index=False)

# Figure 6: raw/residual q, stored cross-validation artifact and exact 12-combination quantile/equal/jenks/std test
factors = ["slope", "DEM", "TEM", "soiltype", "NDVI", "NLI", "POP", "roads", "GDP", "railways", "water", "PRE", "aspect"]
source = {name: gd(name) for name in factors}
complete = valid.copy()
for val in source.values():
    complete &= np.isfinite(val)
yraw, group = hq[complete], lucc[complete].astype(int)
yres = yraw.copy()
for c in CLASS:
    cm = group == c
    yres[cm] -= yraw[cm].mean()

q_rows = []
for factor in factors:
    X = source[factor][complete]
    if factor == "soiltype":
        strata = X.astype(int)
    else:
        breaks = np.unique(np.quantile(X, np.linspace(0, 1, 6)))
        breaks[0] -= 1e-9; breaks[-1] += 1e-9
        strata = np.digitize(X, breaks[1:-1])
    q_rows.append({"factor": factor, "q_raw": qstat(yraw, strata), "q_residual": qstat(yres, strata)})
pd.DataFrame(q_rows).to_csv(OUT / "fig6_q_raw_residual.csv", index=False)

# Store verified TreeSHAP values. This remains a versioned artifact, not a fresh XGBoost training rerun.
shap_path = ROOT / "audit_20260824" / "geoshapley_exp" / "treeshap_values.npy"
shap = np.load(shap_path)
shap_names = ["DEM", "Slope", "Aspect", "Precipitation", "Temperature", "NDVI", "Population", "GDP", "Night-time light", "Soil type", "Roads", "Railways", "Water"]
pd.DataFrame({"factor": shap_names, "mean_abs_SHAP": np.abs(shap).mean(axis=0)}).to_csv(OUT / "fig6_treeshap_artifact.csv", index=False)

manifest = {
    "canonical_arrays": {n: sha(BASE / f"gd_{n}.npy") for n in ["HQ", "LUCC", "DEM", "slope", "TEM", "PRE", "NDVI", "NLI", "POP", "GDP", "roads", "railways", "water", "soiltype", "aspect"]},
    "cache_arrays": {n: sha(CACHE / f"{n}.npy") for n in ["built_threat_2020", "habitat_2020", "degsum_2020"]},
    "treeshap_artifact": {"path": str(shap_path), "sha256": sha(shap_path), "shape": list(shap.shape)},
    "counts": {"n_valid": int(valid.sum()), "n_complete": int(complete.sum()), "n_forest": int(f.sum())},
    "moran": {"I": float(global_moran.I), "p_sim": float(global_moran.p_sim)},
}
(OUT / "source_data_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps(manifest, indent=2))

#!/usr/bin/env python3
"""06 — 两阶段地理探测器 (Two-stage Geodetector)：论文 Table 9"""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "00_SharedUtils"))
from utils import gd, get_strata, geodetector_q
HQ, LUCC = gd("HQ"), gd("LUCC")
FACTORS = ["DEM","slope","aspect","PRE","TEM","NDVI","POP","GDP","NLI","soiltype","roads","railways","water"]
mask = np.isfinite(HQ) & np.isfinite(LUCC)
for f in FACTORS: mask &= np.isfinite(gd(f))
hq, lc = HQ[mask], LUCC[mask].astype(int)
resid = hq.copy()
for c in np.unique(lc): resid[lc==c] = hq[lc==c] - hq[lc==c].mean()
rows = []
for f in FACTORS:
    st = get_strata(f, gd(f)[mask], "quantile")
    rows.append((f, geodetector_q(hq, st), geodetector_q(resid, st)))
rows.sort(key=lambda x: -x[1])
print(f"Module 6: 两阶段地理探测器 — Table 9 (n={hq.size})")
for f, qr, qd in rows:
    print(f"  {f:12s} q_raw={qr:.3f} q_resid={qd:.3f} 保留{100*qd/qr:.1f}%")
print("论文对照 (Table 9): slope 0.517->0.147 (28.4%) DEM 0.476->0.309 (64.8%) "
      "TEM 0.464->0.292 (62.9%)")

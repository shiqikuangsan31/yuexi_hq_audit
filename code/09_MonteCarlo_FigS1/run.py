#!/usr/bin/env python3
"""09 — 蒙特卡洛稳健性检验 (Monte Carlo)：Fig 5c"""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "00_SharedUtils"))
from utils import gd, ca, variance_decomposition, HJ
LUCC = gd("LUCC").ravel(); H = ca("habitat_2020"); D = ca("degsum_2020")
Dz = np.power(D, 2.5); degfac = 1 - Dz/(Dz+0.5**2.5)
rng = np.random.default_rng(0); iccs = []
for _ in range(200):
    Hp = np.full(H.shape, np.nan)
    for c,hj in HJ.items(): Hp[LUCC==c] = hj*(1+rng.uniform(-0.2,0.2))
    iccs.append(variance_decomposition(Hp*degfac, LUCC)["ICC"])
iccs = np.array(iccs)
print("Module 9: 蒙特卡洛检验 — Fig 5c")
print(f"  mean={iccs.mean():.3f} SD={iccs.std():.3f} min={iccs.min():.3f} max={iccs.max():.3f}")
print("论文对照: mean=0.883 SD=0.018 range [0.826, 0.914]")

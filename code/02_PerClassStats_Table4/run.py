#!/usr/bin/env python3
"""02 — 各地类统计 (Per-class Statistics)：论文 Table 6"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "00_SharedUtils"))
from utils import gd, variance_decomposition, CLASS_NAME, HJ
HQ, LUCC = gd("HQ"), gd("LUCC")
r = variance_decomposition(HQ, LUCC)
print("Module 2: 各地类统计 — Table 6")
for c in [2,1,4,3,6,5]:
    if c in r["per"]:
        p = r["per"][c]
        print(f"  {CLASS_NAME[c]:12s} Hj={HJ[c]:.1f} n={p['n']:5d} mean={p['mean']:.3f} SD={p['sd']:.4f} CV={p['cv']:.1f}% %SSW={100*p['ssw']/r['SSW']:.1f}")
print("论文对照: Forest 0.595/0.0974/16.4%/94.8% ; Cropland 0.228/0.0173/7.6%/2.8%")

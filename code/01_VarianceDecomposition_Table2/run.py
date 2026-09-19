#!/usr/bin/env python3
"""01 — 方差分解 (Variance Decomposition)：论文 Table 4"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "00_SharedUtils"))
from utils import gd, variance_decomposition, CLASS_NAME

HQ, LUCC = gd("HQ"), gd("LUCC")
r = variance_decomposition(HQ, LUCC)

print("Module 1: 方差分解 2020 — Table 4")
print(f"  n={r['n']} SSB={r['SSB']:.2f} SSW={r['SSW']:.2f} SST={r['SST']:.2f}")
print(f"  ICC(eta2)={r['ICC']:.4f} 类内占比={r['within_pct']:.1f}% meanHQ={r['mean']:.4f}")
for c in [2,1,4,3,6,5]:
    if c in r["per"]:
        p = r["per"][c]
        print(f"  {CLASS_NAME[c]}: n={p['n']} mean={p['mean']:.3f} SD={p['sd']:.4f} CV={p['cv']:.1f}% %SSW={100*p['ssw']/r['SSW']:.1f}")
print(f"论文对照: SSB=1203.23 SSW=154.43 SST=1357.67 ICC=0.886 n=31,889")

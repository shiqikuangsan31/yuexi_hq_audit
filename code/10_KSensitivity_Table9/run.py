#!/usr/bin/env python3
"""10 — k 敏感性分析 (k-sensitivity)：Table 11 + Fig 5d"""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "00_SharedUtils"))
from utils import gd, ca, variance_decomposition
LUCC = gd("LUCC").ravel(); H = ca("habitat_2020"); D = ca("degsum_2020")
ks = [0.05,0.1,0.2,0.3,0.4,0.5,0.7,1.0,1.3,1.6,2.0,2.5,2.8,5.0]
print("Module 10: k 敏感性 — Table 11")
for k in ks:
    hq_k = H * (1 - np.power(D,2.5)/(np.power(D,2.5)+k**2.5))
    r = variance_decomposition(hq_k, LUCC)
    print(f"  k={k:<5.2f} ICC={r['ICC']:.4f} 类间={100-r['within_pct']:.1f}% 类内={r['within_pct']:.1f}%")
print("论文对照: k=0.5 ICC=0.886 ; k=2.8 ICC=1.000 (已修正)")

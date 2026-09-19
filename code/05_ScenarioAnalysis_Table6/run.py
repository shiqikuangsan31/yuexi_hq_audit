#!/usr/bin/env python3
"""05 — 八情景分析 (8-scenario ICC)：论文 Table 8"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "00_SharedUtils"))
from utils import ca, variance_decomposition, SCEN
for sc in SCEN:
    print(f"  {sc}: ICC={variance_decomposition(ca(f'hq_{sc}'), ca(f'luc_{sc}'))['ICC']:.4f}")
print("论文对照: 2030 .877/.920/.925/.919 ; 2035 .892/.946/.947/.942")

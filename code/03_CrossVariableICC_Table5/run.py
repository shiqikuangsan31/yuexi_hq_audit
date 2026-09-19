#!/usr/bin/env python3
"""03 — 跨变量 ICC 对比 (Cross-variable ICC)：论文 Table 7

对照串校正记录 2026-09-17 (M23)：
  手稿 §4.3 正文与 Table 7 题注已统一为 DEM η² = 0.212、HQ/PRE = 77×
  （见改19/改21）。原对照串残留旧值 0.211 与 74×，与手稿不符，已按手稿校正。
  比值必须用未舍入值、且与同表 DEM 同口径（逐变量掩膜）计算：
    0.886250 / 0.011549 = 76.74 -> 77×
  （complete-case n=30,711 会给 0.884401 / 0.011918 = 74.21，非本表口径。）
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "00_SharedUtils"))
from utils import gd, variance_decomposition
LUCC = gd("LUCC")
icc = {}
for nm in ["HQ", "DEM", "PRE"]:
    icc[nm] = variance_decomposition(gd(nm), LUCC)["ICC"]
    print(f"  {nm}: ICC={icc[nm]:.4f} (3 dp {icc[nm]:.3f})")
ratio = icc["HQ"] / icc["PRE"]
print(f"  HQ/PRE ratio (unrounded) = {ratio:.2f} -> {round(ratio)}x")
print("论文对照 (Table 7): HQ 0.886 ; DEM 0.212 ; PRE 0.012 ; HQ/PRE = 77x")

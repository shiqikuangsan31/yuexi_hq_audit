#!/usr/bin/env python3
"""08 — 森林 HQ vs 建设用地威胁四分位 (Threat Quartiles)：Fig 2b

分箱约定校正记录 2026-09-17 (M20)：
  原实现用左闭右开 [lo, hi)，与手稿 Fig.2 题注不符
  （给出 Q3=0.543、n=[3859, 3858, 3827, 3896]）。
  手稿采用右闭 (lo, hi]（首箱并入最小值），等价于 pandas.qcut 的默认右闭约定，
  可精确复现题注 n=[3864, 3857, 3870, 3849] 与 mean=[0.732, 0.621, 0.542, 0.483]。
  按「规范文本优先于代码实现」，代码改为右闭以对齐手稿。
  8 种分位实现的独立穷举见外审脚本 phase52_m20_quartile.py。
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "00_SharedUtils"))
from utils import gd, ca
HQ, LUCC = gd("HQ").ravel(), gd("LUCC").ravel()
BT = ca("built_threat_2020")
f = (LUCC == 2) & np.isfinite(HQ) & np.isfinite(BT); hf, bf = HQ[f], BT[f]
qv = np.quantile(bf, [0, .25, .5, .75, 1.0])
# 右闭分箱 (qv[i], qv[i+1]]；首箱并入最小值 —— 与 pandas.qcut 默认约定一致
masks = [((bf >= qv[i]) if i == 0 else (bf > qv[i])) & (bf <= qv[i + 1]) for i in range(4)]
mns = [hf[m].mean() for m in masks]
nns = [int(m.sum()) for m in masks]
print("Module 8: 森林威胁四分位 — Fig 2b")
for i in range(4):
    print(f"  Q{i+1} n={nns[i]:5d} mean={mns[i]:.3f}")
print(f"  dHQ={mns[0]-mns[3]:.3f}  占森林均值 {(mns[0]-mns[3])/(hf.mean())*100:.1f}%")
print("论文对照: 0.732/0.621/0.542/0.483  dHQ=0.249 (41.9%)  n=3864/3857/3870/3849")

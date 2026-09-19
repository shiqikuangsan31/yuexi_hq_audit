#!/usr/bin/env python3
"""04 — 多时相分析 (Multi-temporal ICC)：论文 Table 5

精度口径 2026-09-17 (M25)：
  手稿 Table 5 / Fig.3 题注 / 正文三处的 η² 均以 3 位小数报告
  （2010 = 0.880, 2015 = 0.885, 2020 = 0.886, 2025 = 0.943）。
  2010 的未舍入值为 0.8804857399（SSB=1212.950964 / SST=1377.592969），
  3 dp 舍入即 0.880；原对照串手写为 0.881，与手稿不符，已按手稿校正。
  故本模块统一以 3 dp 打印，避免 4 dp 显示值 0.8805 造成歧读。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "00_SharedUtils"))
from utils import gd, ca, variance_decomposition


def _row(yr, hq, luc):
    r = variance_decomposition(hq, luc)
    print(f"  {yr}: meanHQ={r['mean']:.4f} ICC={r['ICC']:.3f} forestCV={r['forest_cv']:.1f}%")


_row("2010", ca("hq_2010"), ca("luc_2010"))
_row("2015", ca("hq_2015"), ca("luc_2015"))
_row("2020", gd("HQ"), gd("LUCC"))
_row("2025", ca("hq_2025"), ca("luc_2025"))
print("论文对照 (Table 5): 0.880 / 0.885 / 0.886 / 0.943")

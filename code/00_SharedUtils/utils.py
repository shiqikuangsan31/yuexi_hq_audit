#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共享工具模块 — 所有分析模块公用的常量和函数
BASE路径、数据加载、方差分解、地理探测器辅助函数等
"""
import os, glob
import numpy as np

# ===================== 路径配置 =====================
# 可移植性说明 2026-09-17 (M17)：
#   原实现把 BASE 硬编码为某台机器的绝对路径，复现者在其他机器上无法直接运行，
#   与稿件 Data Availability 的「脚本公开可复现」声明冲突。
#   现将 BASE 改为「按序解析 + 数据哨兵校验」：
#     ① 环境变量 YUEXI_BASE
#     ② 由本文件位置自动推导的若干上游目录（覆盖 <BASE>/code/… 与
#        <root>/code/code/… + <root>/YueXi0518/YueXi0518/… 两种布局）
#     ③ 已知的固定候选路径（含原硬编码路径，向后兼容）
#   每个候选都必须含哨兵文件 gd_HQ.npy 才算命中，避免"目录存在但数据不在"的假命中。
_SENTINEL = "gd_HQ.npy"


def _has_data(d):
    return bool(d) and os.path.isfile(os.path.join(d, _SENTINEL))


BASE = os.environ.get("YUEXI_BASE")
if not _has_data(BASE):
    _here = os.path.dirname(os.path.abspath(__file__))          # …/<…>/code/00_SharedUtils
    _code = os.path.dirname(_here)                              # …/code
    _root = os.path.dirname(_code)                              # …（code 的父目录）
    _cands = [
        _root,                                                  # <BASE>/code/00_SharedUtils 布局
        os.path.join(_root, "YueXi0518", "YueXi0518"),          # <root>/code/code + <root>/YueXi0518/YueXi0518
        os.path.join(os.path.dirname(_root), "YueXi0518", "YueXi0518"),
        r"C:/Users/han/Desktop/粤西论文文件夹/YueXi0518/YueXi0518",  # 本机数据包
        os.path.join(os.path.expanduser("~"), "Desktop", "粤西论文文件夹",
                     "YueXi0518", "YueXi0518"),                 # 同结构的其他用户
        r"C:\baidunetdiskdownload\YueXi0518\YueXi0518",         # 历史路径（向后兼容）
    ]
    BASE = next((c for c in _cands if _has_data(c)), None)
    if BASE is None:
        raise RuntimeError(
            "无法定位数据根目录 BASE（需含 %s）。请设置环境变量 YUEXI_BASE 指向该目录。"
            % _SENTINEL
        )
CACHE = os.path.join(BASE, "code", "cache")

# ===================== 空间参数 =====================
XMIN, YMAX, CELL = 361151.0, 2511101.0, 30.0
STEP = 33  # 系统采样步长（≈1km）

# ===================== InVEST 参数 =====================
LUCC_VALID = (1, 2, 3, 4, 5, 6)         # 有效地类代码
HJ = {1: 0.3, 2: 0.8, 3: 0.35, 4: 0.8, 5: 0.0, 6: 0.2}  # 生境适宜性
CLASS_NAME = {1: "Cropland", 2: "Forest", 3: "Grassland",
              4: "Water", 5: "Built-up", 6: "Unused"}
# 多情景名称
SCEN = ["2030ECP", "2030BAU", "2030CPL", "2030COO",
        "2035ECP", "2035BAU", "2035CPL", "2035COO"]

# ===================== 数据加载 =====================
def gd(name):
    """加载gd_前缀的因子采样数组 (.npy)"""
    return np.load(os.path.join(BASE, f"gd_{name}.npy"))

def ca(name):
    """加载cache目录中的缓存数组 (.npy)，展平为一维"""
    return np.load(os.path.join(CACHE, f"{name}.npy")).ravel()

def sj_path(*parts):
    """生境质量结果输出目录下的文件路径"""
    return os.path.join(BASE, "生境质量结果输出", *parts)

def first_file(pattern):
    """返回匹配pattern的第一个文件"""
    g = glob.glob(pattern)
    return g[0] if g else None

# ===================== 方差分解核心函数 =====================
def variance_decomposition(y, g, classes=LUCC_VALID):
    """
    单因素方差分解：计算 SST = SSB + SSW
    
    参数:
        y: 数值数组（如 HQ）
        g: 分组数组（如 LUCC 编码）
    返回:
        dict: n, SSB, SSW, SST, ICC(=SSB/SST), within_pct, forest_cv, mean, per(各地类统计)
    """
    v = np.isfinite(y) & np.isin(g, classes)
    y = y[v]
    g = g[v].astype(int)
    gm = y.mean()
    SST = ((y - gm) ** 2).sum()
    SSB = SSW = 0.0
    fcv = np.nan
    perc = {}

    for c in classes:
        yc = y[g == c]
        if yc.size:
            mc = yc.mean()
            b = yc.size * (mc - gm) ** 2
            w = ((yc - mc) ** 2).sum()
            SSB += b
            SSW += w
            perc[c] = dict(
                n=int(yc.size), mean=mc, sd=float(yc.std()),
                cv=(float(yc.std() / mc * 100) if mc > 0 else 0),
                ssw=w
            )
            if c == 2 and mc > 0:
                fcv = float(yc.std() / mc * 100)

    return dict(
        n=int(y.size), SSB=SSB, SSW=SSW, SST=SST,
        ICC=SSB/SST, within_pct=100*SSW/SST,
        forest_cv=fcv, mean=float(gm), per=perc
    )

# ===================== 地理探测器辅助函数 =====================
def _stratify_quantile(x, k=5):
    """分位数分层"""
    qs = np.unique(np.quantile(x, np.linspace(0, 1, k + 1)))
    qs[0] -= 1e-9
    qs[-1] += 1e-9
    return np.digitize(x, qs[1:-1])

def _stratify_equal(x, k=5):
    """等距分层"""
    e = np.linspace(x.min(), x.max(), k + 1)
    return np.clip(np.digitize(x, e[1:-1]), 0, k - 1)

def _aspect_strata(x):
    """坡向分层（4方位）"""
    s = np.zeros(x.shape, dtype=int)
    s[x >= 0] = 1 + (((x[x >= 0] + 45) // 90).astype(int) % 4)
    return s

def geodetector_q(y, strata):
    """计算地理探测器 q 值"""
    SST = ((y - y.mean()) ** 2).sum()
    if SST == 0:
        return 0.0
    SSW = sum(((y[strata == h] - y[strata == h].mean()) ** 2).sum()
              for h in np.unique(strata))
    return 1 - SSW / SST

def get_strata(name, x, scheme="quantile"):
    """获取因子分层结果"""
    if name == "soiltype":
        return x.astype(int)
    elif name == "aspect":
        return _aspect_strata(x)
    elif scheme == "quantile":
        return _stratify_quantile(x)
    else:
        return _stratify_equal(x)

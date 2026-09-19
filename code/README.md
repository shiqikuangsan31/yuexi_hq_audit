# 粤西 InVEST 生境质量论文 — 可复现代码包

**论文**: Decomposing the InVEST Habitat Quality Index: Variance-Partitioning and Two-Stage Geodetector Framework for the Yuexi Region, South China

本包为稿件 Data Availability 所声明的分析脚本。`python MASTER_RUN.py` 可一键复现
稿件全部表格与图注数值（10 个模块，确定性算法，无需 ArcGIS）。

---

## 运行前置

```bash
pip install -r requirements.txt      # numpy 等
```

**数据根目录解析**（`00_SharedUtils/utils.py`）：脚本按下列顺序自动定位含 `gd_HQ.npy` 的目录，
因此不依赖任何硬编码绝对路径：

1. 环境变量 `YUEXI_BASE`
2. 由脚本自身位置推导的上游目录（兼容 `<BASE>/code/…` 与 `<root>/code/code/…` 两种布局）
3. 内置候选路径（向后兼容旧路径）

若均未命中，脚本会抛出明确错误并提示设置 `YUEXI_BASE`。

---

## 目录结构与稿件编号对照

> **重要**：子文件夹名中的 `Table n` / `Fig n` 后缀沿用**早期编号**，与稿件终稿编号不同。
> 下表左列为实际文件夹，右列为**稿件终稿中的对应编号**（以各模块 `run.py` 的 docstring 为准）。

| 文件夹 | 稿件终稿对应 | 内容 |
|---|---|---|
| `00_SharedUtils/` | — | 共享工具：路径解析、方差分解、地理探测器函数 |
| `01_VarianceDecomposition_Table2/` | **Table 4** | 方差分解 η² = 0.886（SSB/SSW/SST） |
| `02_PerClassStats_Table4/` | **Table 6** | 各地类组内统计（n / mean / SD / CV / %SSW） |
| `03_CrossVariableICC_Table5/` | **Table 7** | 跨变量 η² 对比（HQ / DEM / PRE，HQ/PRE = 77×） |
| `04_MultiTemporal_Table3/` | **Table 5** | 多时相 η²（2010–2025） |
| `05_ScenarioAnalysis_Table6/` | **Table 8** | 八情景 η²（2030 / 2035） |
| `06_Geodetector_Table7/` | **Table 9** | 两阶段地理探测器 q_raw / q_resid |
| `07_SpatialAutocorrelation_Table8/` | **Table 10** | 空间自相关 Moran's I + 贪婪空间抽稀阶梯 |
| `08_ForestThreat_Fig5/` | **Fig. 2b** | 森林 HQ vs 建设用地威胁四分位 |
| `09_MonteCarlo_FigS1/` | **Fig. 5c** | 蒙特卡洛 Hj 扰动稳健性（n = 200, ±20%） |
| `10_KSensitivity_Table9/` | **Table 11** + **Fig. 5d** | k 半饱和常数敏感性 |

其他文件：

```
├── MASTER_RUN.py                 ← 一键执行全部 10 个模块（本包入口）
├── 11_FigurePipeline/            ← 稿件 Fig. 1–6 的 R 绘图管线（150 mm 栏宽设计）
├── reproduce_paper.py            ← 原始整合版脚本（模块→稿件编号注释见文件头）
├── make_figures.py / make_figures_hires.py   ← 图表生成脚本
├── make_fig1_studyarea.py        ← Fig. 1 研究区图（arcpy + matplotlib）
├── make_fig2_lucc_hq.py          ← Fig. 2 底图（LUCC + HQ）
├── make_fig7_lisa_compute.py / make_fig7_lisa_map.py  ← Fig. 4 LISA 计算与成图
├── cache/                        ← 多时相/多情景采样缓存
├── figures/ , figures_hires/     ← 图表输出
├── lisa_meta.json / lisa_points.csv  ← LISA 分析结果
└── requirements.txt
```

### 图件生成脚本（`11_FigurePipeline/`）

稿件 Fig. 1–6 的**最终印刷版**由 R 管线生成，设计宽度锁定为正文栏宽 150.0 mm
（A4 − 左右各 30 mm），因此 Word 内嵌时不做缩放，图内文字实际尺寸等于脚本设定磅值。
`11_FigurePipeline/README.md` 给出逐图设计尺寸、rId 对照、运行方式，
以及两个必须保留的实现细节（Fig. 4 不依赖 `sf`；Fig. 5 的 n 标注使用 `ggrepel`）。

---

## 用法

```bash
# 一键复现所有表格/图注数值（无需 ArcGIS）
python MASTER_RUN.py

# 单独运行某个模块
python "01_VarianceDecomposition_Table2/run.py"

# 生成图表（需 matplotlib）
python make_figures.py
```

---

## 可复现性说明

- ✅ **完全可复现**：全部模块为确定性算法（固定随机种子 0、固定采样步长 STEP = 33 ≈ 1 km）
- ✅ **无硬编码路径**：数据根目录按 `YUEXI_BASE` → 自推导 → 候选列表解析（见上）
- ✅ **独立验证**：10 个模块全部通过稿件数值对照（`MASTER_RUN.py` 末尾输出 `10 PASS / 0 FAIL`）
- ✅ **两条实现路径**：有 ArcGIS 时可从原始栅格采样；无 ArcGIS 时使用 `cache/` 缓存
- ✅ **口径一致**：CV 用总体标准差（ddof = 0，稿件 Methods 明文）；四分位用右闭区间 `(lo, hi]`
  （等价 `pandas.qcut` 默认，与稿件 Fig. 2b 题注 n = 3,864 / 3,857 / 3,870 / 3,849 逐位一致）
- ✅ **图件脚本齐备**：Fig. 1–6 的 R 绘图脚本随包公开于 `11_FigurePipeline/`（2026-09-17 补录，
  此前缺失，见审计编号 M26）

## 验证结果（2026-09-17 复核）

| 模块 | 稿件数值 | 复现结果 | 判定 |
|------|---------|---------|------|
| Table 4 方差分解 | SSB 1203.23 / SSW 154.43 / SST 1357.67 / η² 0.886 / n 31,889 | 精确命中 | ✅ |
| Table 6 各地类 | Forest 0.595 / 0.0974 / 16.4% / 94.8%；Cropland 0.228 / 0.0173 / 7.6% / 2.8% | 精确命中 | ✅ |
| Table 7 跨变量 | HQ 0.886 / DEM 0.212 / PRE 0.012；HQ/PRE = 77× | 精确命中 | ✅ |
| Table 5 多时相 | 0.880 / 0.885 / 0.886 / 0.943 | 精确命中 | ✅ |
| Table 8 八情景 | 2030 .877/.920/.925/.919；2035 .892/.946/.947/.942 | 精确命中 | ✅ |
| Table 9 地理探测器 | slope 0.517→0.147 (28.4%)；DEM 0.476→0.309 (64.8%)；TEM 0.464→0.292 (62.9%) | 精确命中 | ✅ |
| Table 10 空间自相关 | 全样本 Moran 0.622 / η² 0.886；1 km 0.585；10 km 0.348 | 精确命中 | ✅ |
| Fig. 2b 威胁四分位 | 0.732 / 0.621 / 0.542 / 0.483；dHQ 0.249 (41.9%)；n 3864/3857/3870/3849 | 精确命中 | ✅ |
| Fig. 5c 蒙特卡洛 | mean 0.883 / SD 0.018 / range [0.826, 0.914] | 精确命中 | ✅ |
| Table 11 k 敏感性 | k = 0.5 → 0.886；k = 2.8 → 1.000 | 精确命中 | ✅ |

> 复核记录：全样本 Moran's I 的确定性 KNN (k = 8, 行标准化) 实现给出 0.62148；
> 参考实现 `libpysal` + `esda` 给出 0.62151 → 3 dp 即 0.622（稿件 Table 10 所记）。

## 数据来源

见稿件 Table 3（数据来源表）。核心数据文件：

- `gd_*.npy` — 13 个驱动因子 + HQ + LUCC 的 1 km 系统采样
- `cache/*.npy` — 多时相 / 多情景 HQ + LUCC 采样
- `生境质量结果输出/` — InVEST 原始栅格输出
- `factors/` — 驱动因子 TIF 栅格
- `lucc/` — LUCC 栅格

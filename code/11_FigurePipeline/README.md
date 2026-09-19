# 11_FigurePipeline — R 图件生成管线（稿件 Fig. 1–6）

本目录使稿件 **Data Availability** 中「图件生成脚本随文公开」的声明成立。
在本次补录之前，Fig. 1–6 的绘制脚本（R）并未进入代码包，与声明不符（审计编号 **M26**）。

## 版面契约

稿件为 A4、左右页边距各 30 mm，正文栏宽 = 210 − 30 − 30 = **150.0 mm**。
全部 6 张图按 **150.0 mm 设计宽度**渲染，因此 Word 内嵌时**不做任何缩放**，
图内文字的实际印刷尺寸即脚本设定的磅值（最小 6.0 pt）。

| 图 | 设计尺寸 (mm) | 输出像素 @600 dpi | 对应稿件 rId / media |
|---|---|---|---|
| Fig. 1 | 150.0 × 136.24 | 3543 × 3218 | rId8 / image2.png |
| Fig. 2 | 150.0 × 76.97 | 3543 × 1818 | rId10 / image4.png |
| Fig. 3 | 150.0 × 67.19 | 3543 × 1587 | rId9 / image3.png |
| Fig. 4 | 150.0 × 67.19 | 3543 × 1587 | rId13 / image7.png |
| Fig. 5 | 150.0 × 95.09 | 3543 × 2246 | rId14 / image8.png |
| Fig. 6 | 150.0 × 63.89 | 3543 × 1509 | rId20 / image11.png |

## 运行

```
# 1) 由确定性数据源生成绘图输入表（Python）
python prepare_figure_source_data.py
python compute_fig06_discretization.py

# 2) 渲染 6 张图（R >= 4.5，需 ggplot2 / patchwork / dplyr / tidyr / ggrepel /
#    svglite / ragg；ragg 不可用时自动回退到 cairo 设备）
cd r_scripts
Rscript fig01_study_area.R
Rscript fig02_class_configuration.R
Rscript fig03_temporal_scenarios.R
Rscript fig04_forest_residual_LISA.R
Rscript fig05_sensitivity_diagnostics.R
Rscript fig06_driver_diagnostics.R
```

输出目录由环境变量 `YUEXI_FIG_ROOT` 决定（缺省为脚本内建的 ASCII 路径）。
**注意**：R 的 `normalizePath()` 在 `LC_CTYPE` 不可用的 Windows 上会损坏非 ASCII 路径，
故管线路径应保持纯 ASCII，或在脚本中显式设置 UTF-8 的 `LC_CTYPE`
（`yuexi_r_style_150mm.R` 已内置该保护）。

## 两个必须保留的实现细节

1. **Fig. 4 不依赖 `sf`。** 部分 Windows 环境下 `r-sf` 的动态库损坏
   （`Mingw-w64 runtime failure: 32 bit pseudo relocation`）。`export_fig4_boundary.py`
   用 geopandas 把 `BJ.shp`（EPSG:32649）边界导出为顶点表 `source_data/fig4_boundary.csv`，
   `geom_polygon()` 直接绘制，几何内容与 `geom_sf()` 完全一致。
2. **Fig. 5 的 n 标注使用 `ggrepel`。** 6 个稀疏化间距的标注在 150 mm 面板下相互碰撞或
   被面板边界裁切（原始 183 mm 设计中首个标注的 `n` 即已被裁掉）。`ggrepel` 保证标注
   全部落在面板内；`seed = 20260912` 保证可复现。

## 源数据

`source_data/*.csv` 为上述 Python 脚本产出的确定性中间表，包含每张图的作图数值。
其中 `provenance` 列注明该表的来源（如 Table 10）。

`source_data/source_data_manifest.json` 记录 15 个正典栅格数组的 SHA-256、
TreeSHAP 产物的来源与形状、样本计数（31,889 / 30,711 / 15,440）以及森林残差的
全局 Moran's I（0.7516 → 3 位小数 0.752）。

> ⚠️ **`source_data/*.csv` 必须是纯数据表，不得加入 `#` 注释行。**
> R 的 `read.csv()` 默认 `comment.char = ""`，注释行会被当作数据行，
> 导致 `more columns than column names` 而使整条图件管线中断。

### 分层口径说明（aspect 与其余因子的差异）

`fig6_q_raw_residual.csv` 中**除 `aspect` 外**所有因子均采用统一的 **5 分位（quintile）** 分层；
`aspect` 在本表中按 **4 分位** 分层，以与 Fig. 6 管线保持一致。

这与稿件 **Table 9** 不同：Table 9 对 `aspect` 采用 **四个基本方位（four cardinal sectors）**
分层，因此 Table 9 中 `aspect` 的 q 统计量与本表的数值**不可直接比较**。
稿件 Table 9 题注已就此显式声明。


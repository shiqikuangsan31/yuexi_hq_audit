# Auditing Land-Cover-Structured Variance in InVEST Habitat Quality

This repository provides canonical spatial coordinates, reproduction scripts, and challenger econometric evidence for:
**"Auditing land-cover-structured variance in InVEST habitat quality: implications for stratified driver analyses"**

---

## 1. Canonical Coordinate Datasets

- `yuexi_points_all_31889.csv`: Full territorial sample points (N = 31,889, SHA-256: `a56c88e03a330697daf00342f6af79e817d894e6e4d21652a3010382c146a4b1`)
- `yuexi_points_complete_30711.csv`: Complete cases across all 13 exogenous drivers (N = 30,711, SHA-256: `bf2275a3ce726fb86e7e833b50484a351398384c8281e91e5aa9815d3861705d`)
- `yuexi_grid_canonical.csv`: Full 278 × 283 sampling grid (SHA-256: `85c727ea67eb8cf1639422b886420b8bcd1469360336fde55a885ff68852bdf2`)

Coordinates are mathematically reconstructed from systematic grid sampling (33 × 30 m ≈ 1 km spacing)
under **CGCS2000 / 3-degree Gauss-Kruger CM 111°E (EPSG:4546)**.

Reconstruction formula (also in `canonical_meta.json`):

```
X = XMIN + (jj*STEP + 0.5) * CELL
Y = YMAX - (ii*STEP + 0.5) * CELL
ii, jj = divmod(arange(n), 283)
XMIN = 361151.0   YMAX = 2511101.0   CELL = 30.0   STEP = 33
```

> **Note on the CRS code**: `EPSG:4546` (CM 111°E, *without* zone prefix) is the correct code for these
> coordinates. `EPSG:4525` is the *zone-prefixed* variant of the same projection (false easting 37,500,000)
> and does **not** match the values in this repository.

---

## 2. Reproduction Code

R and Python scripts for variance decomposition, two-stage Geodetector, spatial autocorrelation,
Monte-Carlo perturbation, and visualization are provided under **`code/`**:

```
code/
├── 00_SharedUtils/                    # shared constants + variance_decomposition()
├── 01_VarianceDecomposition_Table2/   # η² decomposition (Table 4)
├── 02_PerClassStats_Table4/           # per-class statistics (Table 5)
├── 03_CrossVariableICC_Table5/        # cross-variable η² (Table 7)
├── 04_MultiTemporal_Table3/           # multi-temporal η² (Table 5)
├── 05_ScenarioAnalysis_Table6/        # scenario η² (Table 8)
├── 06_Geodetector_Table7/             # two-stage Geodetector (Table 9)
├── 07_SpatialAutocorrelation_Table8/  # Moran's I + spatial thinning (Table 10)
├── 08_ForestThreat_Fig5/              # forest threat index (Fig. 2)
├── 09_MonteCarlo_FigS1/               # Monte-Carlo perturbation (Fig. 5c)
├── 10_KSensitivity_Table9/            # k-sensitivity (Table 11)
├── 11_FigurePipeline/                 # figure source data + R scripts
├── MASTER_RUN.py                      # runs all modules end-to-end
├── reproduce_paper.py                 # single-entry reproduction of paper tables
└── requirements.txt
```

> **`07_SpatialAutocorrelation_Table8/run.py`** prints `Δη²` in **two calibers**:
> the raw (unrounded) difference and the **three-decimal difference**.
> The manuscript's Table 10 uses the **three-decimal** caliber (stated in the Methods).

---

## 3. InVEST Model Parameters

Threat-source parameter tables (`wxy.csv`) for all eight scenarios are provided under
`invest_parameters/`:

```
invest_parameters/
├── wxy_2030_ECP.csv   wxy_2030_BAU.csv   wxy_2030_CPL.csv   wxy_2030_COO.csv
└── wxy_2035_ECP.csv   wxy_2035_BAN.csv   wxy_2035_CPL.csv   wxy_2035_COO.csv
```

---

## 4. Challenger Model Evidence

- **Variation partitioning (`vegan::varpart`)**:
  - Pure LUCC fraction [a]: **34.30%**
  - Pure environmental fraction [b]: **6.05%**  (F = 3060.7, p = 0.001, 999 permutations)
  - Shared fraction [c]: **54.14%**
  - Residual [d]: 5.52%
  - OLS cross-check: 34.29% / 6.05% / 54.15% / 5.51%
- **Spatial Error Model (SEM, N = 30,711)**:
  - OLS residual Moran's I = **0.5062**
  - Spatial error coefficient λ = **0.8567** (p < 0.001)
  - Temperature effect flips sign from OLS +0.0012 (p = 0.45) to SEM **−0.0150** (p < 0.001)
  - AIC improves by **19,860** over non-spatial OLS

---

## 5. Manuscript

`manuscript/` contains the current submission candidate:

- `改34_V9_FINAL.docx` / `.pdf` — the manuscript with the two-stage Geodetector
  audit-and-sensitivity workflow, including the variation-partitioning and
  spatial-error cross-checks reported in Section 4.7 (Robustness Verification).

---

## 6. Environment

See `code/requirements.txt`. Core Python dependencies: `numpy`, `scipy`, `pandas`, `geopandas`,
`python-docx`. Optional: `libpysal` + `esda` (used for an independent cross-check of Moran's I).

---

*Last updated: 2026-09-19*

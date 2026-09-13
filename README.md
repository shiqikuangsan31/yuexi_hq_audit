# Auditing Land-Cover-Structured Variance in InVEST Habitat Quality

This repository provides canonical spatial coordinates, reproduction scripts, and challenger econometric evidence for:
**"Auditing land-cover-structured variance in InVEST habitat quality: implications for stratified driver analyses"**

## 1. Canonical Coordinate Datasets
- `yuexi_points_all_31889.csv`: Full territorial sample points (N = 31,889, SHA-256: `80f331cf113cf7ba837bcf7047f6cf5ce9a8ca6a5416fa9c803f295b9d3ce6b2`)
- `yuexi_points_complete_30711.csv`: Complete cases across all 13 exogenous drivers (N = 30,711, SHA-256: `bb113f8c0507a24e75685710aa0570b5501869e5d799014be349ef8f566dd1ff`)

Coordinates are mathematically reconstructed from systematic grid sampling ($33 \times 30\text{ m} \approx 1\text{ km}$ spacing) under CGCS2000 / 3-degree Gauss-Kruger zone 37 (EPSG:4525).

## 2. Challenger Model Evidence
- **Variation Partitioning (`vegan::varpart`)**:
  - Pure LUCC fraction [a]: **34.3%**
  - Pure Environmental fraction [b]: **6.05%**
  - Shared fraction [c]: **54.1%**
- **Spatial Error Model (SEM, N = 30,711)**:
  - Spatial error coefficient $\lambda = 0.8567$ ($p < 0.001$)
  - Temperature effect flips sign from OLS $+0.0012$ to SEM $-0.0150$ ($p < 0.001$)
  - AIC improves by 19,860 over non-spatial OLS.

## 3. Reproduction Code
- R and Python scripts for variation partitioning, spatial autoregressive estimation, and visualization are documented under `scripts/`.

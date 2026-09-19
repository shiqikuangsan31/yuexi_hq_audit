# Export the study-area boundary as a flat vertex table so that Fig. 4 can be
# rendered in R WITHOUT the `sf` package (this machine's r-sf build crashes with
# "Mingw-w64 runtime failure: 32 bit pseudo relocation").
#
# Output: source_data/fig4_boundary.csv  columns = ring, hole, order, x, y
#   ring  -> polygon ring id (exterior and each interior hole of every part)
#   hole  -> 1 for interior rings, 0 for exterior rings
#   order -> vertex order within the ring
# CRS of BJ.shp is EPSG:32649 (UTM 49N); the LISA point table is in the same CRS.
import warnings

import geopandas as gpd
import pandas as pd

warnings.filterwarnings("ignore")

SHP = r"C:\Users\han\Desktop\粤西论文文件夹\YueXi0518\YueXi0518\BJ\BJ.shp"
OUT = r"C:\yuexi_r\_YUEXI_FIGURE_REBUILD_20260912\04_figures\source_data\fig4_boundary.csv"

g = gpd.read_file(SHP)
print("source_crs:", g.crs, "| parts:", len(g), "| types:", g.geom_type.value_counts().to_dict())

rows = []
ring_id = 0
for geom in g.geometry:
    if geom is None:
        continue
    polys = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
    for poly in polys:
        rings = [(0, poly.exterior)] + [(1, r) for r in poly.interiors]
        for is_hole, ring in rings:
            ring_id += 1
            xs, ys = ring.xy
            for k, (x, y) in enumerate(zip(xs, ys)):
                rows.append(
                    {
                        "ring": ring_id,
                        "hole": is_hole,
                        "order": k,
                        "x": round(float(x), 4),
                        "y": round(float(y), 4),
                    }
                )

df = pd.DataFrame(rows)
df.to_csv(OUT, index=False)
print("rings_written:", df["ring"].nunique(), "| vertices:", len(df))
print("x_range:", (df.x.min(), df.x.max()))
print("y_range:", (df.y.min(), df.y.max()))
print("out:", OUT)

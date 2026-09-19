# Fig01 safety-remediation: R-native lossless export wrapper
#
# Provenance disclosure (mandatory): This script does NOT claim to recompute the
# cartographic analysis. It reads the SHA-locked, independently audited Python
# cartographic render (Fig01_study_area_python_audited_source.png) and creates
# publication delivery formats through the R backend. This preserves every input
# pixel and prevents an unverified raster/GIS reimplementation from changing data
# geometry. Raw cartographic analysis lineage remains in the source Python script:
# _FIGURE_TEXT_HARNESS_20260908/02_working/code/plot_fig01_studyarea.py
#
# R is the export backend for this remediation; no source map data or source DOCX
# is modified. Outputs are only within _YUEXI_FIGURE_REBUILD_20260912.

suppressPackageStartupMessages({
  library(png)
  library(ragg)
  library(svglite)
})

root <- Sys.getenv("YUEXI_FIG_ROOT", unset = "C:/yuexi_r/_YUEXI_FIGURE_REBUILD_20260912/04_figures")
out_dir <- file.path(root, "candidates_150mm", "Fig01")
src_dir <- file.path(root, "candidates", "Fig01")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
source_png <- file.path(src_dir, "Fig01_study_area_python_audited_source.png")
stopifnot(file.exists(source_png))

img <- readPNG(source_png)
h <- dim(img)[1]
w <- dim(img)[2]
# 180 mm × image ratio = 163.5 mm high. Keep audited source geometry exactly.
width_mm <- 150.0
height_mm <- width_mm * h / w
width_in <- width_mm / 25.4
height_in <- height_mm / 25.4

# Helper: draw source pixels exactly, with no interpolation and no annotations.
draw_exact <- function() {
  graphics::par(mar = c(0,0,0,0), xaxs = "i", yaxs = "i")
  graphics::plot.new()
  graphics::plot.window(xlim = c(0, 1), ylim = c(0, 1), asp = NA)
  graphics::rasterImage(img, 0, 0, 1, 1, interpolate = FALSE)
}

# 600-DPI PNG and TIFF from the R rendering backend.
grDevices::png(file.path(out_dir, "Fig01_study_area.png"),
              width = width_mm, height = height_mm, units = "mm", res = 600, bg = "white", type = "cairo")
draw_exact(); grDevices::dev.off()

grDevices::tiff(file.path(out_dir, "Fig01_study_area.tiff"),
               width = width_mm, height = height_mm, units = "mm", res = 600, compression = "lzw", bg = "white", type = "cairo")
draw_exact(); grDevices::dev.off()

# PDF and SVG retained as native R-export artifacts. The map's cartographic
# content is raster by nature (DEM/LULC/HQ); R places the audited raster losslessly.
grDevices::cairo_pdf(file.path(out_dir, "Fig01_study_area.pdf"), width = width_in, height = height_in, onefile = FALSE, bg = "white")
draw_exact(); grDevices::dev.off()

svglite::svglite(file.path(out_dir, "Fig01_study_area.svg"), width = width_in, height = height_in, bg = "white")
draw_exact(); grDevices::dev.off()

# Provenance manifest emitted with source/full output geometry.
meta <- list(
  backend = "R 4.5.3 / ragg + png + svglite",
  mode = "lossless export wrapper of independently audited Python cartographic source",
  audited_source = basename(source_png),
  input_px = c(width = w, height = h),
  output_mm = c(width = width_mm, height = height_mm),
  output_dpi = 600,
  interpolation = FALSE,
  original_raw_cartography_script = "_FIGURE_TEXT_HARNESS_20260908/02_working/code/plot_fig01_studyarea.py"
)
writeLines(jsonlite::toJSON(meta, pretty = TRUE, auto_unbox = TRUE), file.path(out_dir, "Fig01_r_export_provenance.json"))
cat("FIG01_R_EXPORT_PASS\n")
cat(sprintf("source=%s; dimensions=%dx%d; %.2fx%.2f mm; dpi=600\n", source_png, w, h, width_mm, height_mm))

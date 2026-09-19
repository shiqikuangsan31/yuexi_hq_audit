# R publication style contract — Yuexi English SCI figures
# 150 mm variant: designed for the 150.0 mm text column of the A4 + 30 mm-margin
# manuscript so that Word performs no scaling on the embedded rasters.

# --- Locale guard (M31) -------------------------------------------------------
# The conda R session starts with LC_CTYPE=C because the startup default
# "C.UTF-8" is not a valid Windows locale. Under a C locale the cairo devices
# mis-encode multi-byte characters in plot text: an en-dash (U+2013) inside a
# label was observed to swallow the remainder of that label ("Low–High" rendered
# as "Low" + a missing-glyph box). Setting a real UTF-8 CTYPE locale repairs text
# shaping for cairo_pdf/png/tiff. ragg is locale-independent but is still run
# under the corrected locale for consistent metrics.
local({
  if (!grepl("UTF-8|utf8", Sys.getlocale("LC_CTYPE"))) {
    for (loc in c("English_United States.utf8", "Chinese (Simplified)_China.utf8", "en_US.UTF-8")) {
      ok <- suppressWarnings(tryCatch(Sys.setlocale("LC_CTYPE", loc), error = function(e) ""))
      if (nzchar(ok)) break
    }
  }
  cat("LC_CTYPE =", Sys.getlocale("LC_CTYPE"), "\n")
})

suppressPackageStartupMessages({
  library(ggplot2)
  library(patchwork)
  library(dplyr)
  library(tidyr)
  library(ggrepel)
  library(svglite)
})

YUEXI <- list(
  forest = "#2D6A4F",
  cropland = "#D4A373",
  grassland = "#74A57F",
  water = "#1F78B4",
  built_up = "#A85A55",
  unused = "#9A8F7A",
  dem = "#0F4D92",
  temperature = "#B64342",
  slope = "#767676",
  teal = "#42949E",
  neutral_dark = "#343434",
  neutral_mid = "#737373",
  neutral_light = "#D9D9D9",
  projection = "#9A4D8E"
)

label_lulc <- c(
  "Cropland" = "Cropland", "Forest" = "Forest", "Grassland" = "Grassland",
  "Water" = "Water", "Built-up" = "Built-up", "Unused" = "Unused"
)

figure_theme <- function(base_size = 7) {
  theme_classic(base_size = base_size, base_family = "Arial") +
    theme(
      text = element_text(colour = "#202020"),
      axis.line = element_line(linewidth = 0.40, colour = "#202020"),
      axis.ticks = element_line(linewidth = 0.35, colour = "#202020"),
      axis.ticks.length = grid::unit(1.4, "mm"),
      axis.title = element_text(size = base_size, margin = margin(t = 4, r = 4, b = 4, l = 4)),
      axis.text = element_text(size = base_size - 0.5),
      legend.title = element_text(size = base_size - 0.1, face = "bold"),
      legend.text = element_text(size = base_size - 0.5),
      legend.key.height = grid::unit(3.5, "mm"),
      legend.key.width = grid::unit(4.5, "mm"),
      panel.grid = element_blank(),
      plot.margin = margin(4, 5, 4, 5),
      plot.tag = element_text(size = base_size + 1, face = "bold", hjust = 0, vjust = 1),
      plot.title = element_blank()
    )
}

# Close every device above the null device; used before a backend fallback so a
# half-written device cannot leak into the next attempt.
.close_open_devices <- function() {
  while (grDevices::dev.cur() > 1) grDevices::dev.off()
}

# Raster export backend: ragg first (identical to the reviewed 183 mm render
# set), cairo as a documented fallback for hosts where the agg device cannot
# open the output file.
.save_raster_pair <- function(draw, stem, width_in, height_in, dpi) {
  try_ragg <- function() {
    ragg::agg_tiff(paste0(stem, ".tiff"), width = width_in, height = height_in,
                   units = "in", res = dpi, compression = "lzw")
    draw(); grDevices::dev.off()
    ragg::agg_png(paste0(stem, ".png"), width = width_in, height = height_in,
                  units = "in", res = dpi)
    draw(); grDevices::dev.off()
    TRUE
  }
  ok <- tryCatch(try_ragg(), error = function(e) {
    .close_open_devices()
    cat("ragg backend failed (", conditionMessage(e), ") -> cairo fallback\n", sep = "")
    FALSE
  })
  if (!ok) {
    grDevices::tiff(paste0(stem, ".tiff"), width = width_in, height = height_in,
                    units = "in", res = dpi, compression = "lzw", type = "cairo", bg = "white")
    draw(); grDevices::dev.off()
    grDevices::png(paste0(stem, ".png"), width = width_in, height = height_in,
                   units = "in", res = dpi, type = "cairo", bg = "white")
    draw(); grDevices::dev.off()
  }
}

save_r_figure <- function(plot, stem, width_mm = 150, height_mm = 112, dpi = 600) {
  dir.create(dirname(stem), recursive = TRUE, showWarnings = FALSE)
  width_in <- width_mm / 25.4
  height_in <- height_mm / 25.4
  draw <- function() print(plot)

  svglite::svglite(paste0(stem, ".svg"), width = width_in, height = height_in)
  draw(); dev.off()

  grDevices::cairo_pdf(paste0(stem, ".pdf"), width = width_in, height = height_in, family = "Arial")
  draw(); dev.off()

  .save_raster_pair(draw, stem, width_in, height_in, dpi)
}

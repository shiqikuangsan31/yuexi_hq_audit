# Candidate Figure 4 — forest HQ residual LISA clusters and composition
# R-only rendering from the lock-derived LISA source table.
#
# NOTE (2026-09-17): the `sf` package cannot load on this machine
# ("Mingw-w64 runtime failure: 32 bit pseudo relocation"), so the study-area
# boundary is read from a flat vertex table exported from BJ.shp by
# `export_fig4_boundary.py` (geopandas, EPSG:32649) and drawn with geom_polygon.
# Geometry content is identical to the previous geom_sf() call; `coord_fixed(1)`
# reproduces the coord_sf() aspect for projected data.
source("yuexi_r_style_150mm.R")

root <- Sys.getenv("YUEXI_FIG_ROOT", unset = "C:/yuexi_r/_YUEXI_FIGURE_REBUILD_20260912/04_figures")
data_dir <- file.path(root, "source_data")
out_dir <- file.path(root, "candidates_150mm", "Fig04")
points <- read.csv(file.path(data_dir, "fig4_lisa_points.csv"), check.names = FALSE)
shares <- read.csv(file.path(data_dir, "fig4_lisa_shares.csv"), check.names = FALSE)
boundary <- read.csv(file.path(data_dir, "fig4_boundary.csv"), check.names = FALSE)
boundary$ring <- factor(boundary$ring)

cluster_levels <- c("Not significant", "High-High", "Low-Low", "High-Low", "Low-High")
points$LISA_cluster <- factor(points$LISA_cluster, levels = cluster_levels)
shares$cluster <- factor(shares$cluster, levels = cluster_levels)
cluster_palette <- c(
  "Not significant" = "#D6D6D6",
  "High-High" = "#B64342",
  "Low-Low" = "#0F4D92",
  "High-Low" = "#9A4D8E",
  "Low-High" = "#42949E"
)
cluster_labels <- c(
  "Not significant" = "Not significant", "High-High" = "High–High",
  "Low-Low" = "Low–Low", "High-Low" = "High–Low", "Low-High" = "Low–High"
)

# Hero: no cartographic furniture here because Fig. 1 supplies orientation/scale.
p_a <- ggplot() +
  geom_polygon(data = boundary, aes(x = x, y = y, group = ring),
               fill = "#FAFAF8", colour = YUEXI$neutral_dark, linewidth = 0.50) +
  geom_point(data = subset(points, LISA_cluster == "Not significant"),
             aes(x = x_utm, y = y_utm, colour = LISA_cluster),
             size = 0.035, alpha = 0.20, show.legend = FALSE) +
  geom_point(data = subset(points, LISA_cluster != "Not significant"),
             aes(x = x_utm, y = y_utm, colour = LISA_cluster),
             size = 0.095, alpha = 0.62, show.legend = FALSE) +
  geom_polygon(data = boundary, aes(x = x, y = y, group = ring),
               fill = NA, colour = YUEXI$neutral_dark, linewidth = 0.38) +
  scale_colour_manual(values = cluster_palette, guide = "none") +
  coord_fixed(ratio = 1, expand = FALSE) +
  figure_theme() +
  theme(axis.title = element_blank(), axis.text = element_blank(), axis.ticks = element_blank(), axis.line = element_blank(),
        legend.position = c(0.80, 0.18), legend.background = element_rect(fill = "white", colour = NA),
        legend.key.height = grid::unit(3, "mm"))

# Supporting composition panel: exact cluster shares, not an unstable second spatial geometry.
shares$label <- sprintf("%.1f%%", shares$percentage)
p_b <- ggplot(shares, aes(x = percentage, y = cluster, fill = cluster)) +
  geom_col(width = 0.68, colour = NA) +
  geom_text(aes(label = label), hjust = -0.15, size = 2.55, colour = YUEXI$neutral_dark) +
  scale_fill_manual(values = cluster_palette, labels = cluster_labels, guide = "none") +
  scale_y_discrete(labels = cluster_labels) +
  coord_cartesian(xlim = c(0, 52), clip = "on") +
  labs(x = "Share of forest residual points (%)", y = NULL) +
  figure_theme() +
  theme(axis.text.y = element_text(size = 6.2), axis.title.x = element_text(size = 6.3))

fig <- p_a + p_b + plot_layout(widths = c(1.50, 0.82)) +
  plot_annotation(tag_levels = "a") & theme(plot.tag = element_text(size = 8.3, face = "bold"))

save_r_figure(fig, file.path(out_dir, "Fig04_forest_residual_LISA"), width_mm = 150, height_mm = 67.2, dpi = 600)
write.csv(shares, file.path(out_dir, "Fig04_source_cluster_shares.csv"), row.names = FALSE)

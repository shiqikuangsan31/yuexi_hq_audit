# Candidate Figure 2 — class identity and within-class configuration
# R-only rendering script. Inputs are produced by prepare_figure_source_data.py.
source("yuexi_r_style_150mm.R")

root <- Sys.getenv("YUEXI_FIG_ROOT", unset = "C:/yuexi_r/_YUEXI_FIGURE_REBUILD_20260912/04_figures")
data_dir <- file.path(root, "source_data")
out_dir <- file.path(root, "candidates_150mm", "Fig02")
class_df <- read.csv(file.path(data_dir, "fig2_class_distribution.csv"), check.names = FALSE)
forest_df <- read.csv(file.path(data_dir, "fig2_forest_threat.csv"), check.names = FALSE)

class_levels <- c("Cropland", "Forest", "Grassland", "Water", "Built-up", "Unused")
class_df$LULC <- factor(class_df$LULC, levels = class_levels)
class_palette <- c(
  "Cropland" = YUEXI$cropland, "Forest" = YUEXI$forest,
  "Grassland" = YUEXI$grassland, "Water" = YUEXI$water,
  "Built-up" = YUEXI$built_up, "Unused" = YUEXI$unused
)
summary_class <- class_df |>
  group_by(LULC, Hj) |>
  summarise(n = n(), cv = ifelse(mean(HQ) == 0, 0, sd(HQ) / mean(HQ) * 100), .groups = "drop") |>
  mutate(x_lab = paste0(LULC, "\nn = ", format(n, big.mark = ",")))

# Panel a: categories establish structural context. Raw points avoid misleading KDE for n=22/n=5 classes.
p_a <- ggplot(class_df, aes(x = LULC, y = HQ, fill = LULC)) +
  geom_violin(data = subset(class_df, LULC %in% c("Cropland", "Forest", "Water")),
              scale = "width", alpha = 0.68, linewidth = 0.25, colour = NA, trim = TRUE) +
  geom_boxplot(data = subset(class_df, LULC %in% c("Cropland", "Forest", "Water")),
               width = 0.17, outlier.shape = NA, linewidth = 0.35, fill = "white", colour = YUEXI$neutral_dark) +
  geom_point(data = subset(class_df, LULC %in% c("Grassland", "Built-up", "Unused")),
             position = position_jitter(width = 0.10, height = 0, seed = 20260912),
             shape = 21, size = 1.6, stroke = 0.35, colour = YUEXI$neutral_dark) +
  scale_fill_manual(values = class_palette, guide = "none") +
  scale_x_discrete(labels = setNames(summary_class$x_lab, summary_class$LULC), expand = expansion(add = 0.50)) +
  coord_cartesian(ylim = c(0, 0.84), clip = "on") +
  labs(x = NULL, y = "InVEST habitat quality") +
  figure_theme(base_size = 7.2) +
  theme(axis.text.x = element_text(size = 6.3, lineheight = 0.95, margin = margin(t = 5)))

# Panel b: same forest observations, but the distinct inferential unit is pre-defined built-up-threat quartiles.
forest_df$quartile <- factor(forest_df$quartile, levels = c("Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"))
quartile_stats <- forest_df |>
  group_by(quartile) |>
  summarise(n = n(), mean_HQ = mean(HQ), sd_HQ = sd(HQ), .groups = "drop") |>
  mutate(x_lab = paste0(quartile, "\nn = ", format(n, big.mark = ",")))
quartile_palette <- c("Q1 (lowest)" = "#DDF3DE", "Q2" = "#AADCA9", "Q3" = "#6FAF78", "Q4 (highest)" = "#2D6A4F")

p_b <- ggplot(forest_df, aes(x = quartile, y = HQ, fill = quartile)) +
  geom_violin(scale = "width", alpha = 0.72, linewidth = 0.25, colour = NA, trim = TRUE) +
  geom_boxplot(width = 0.18, outlier.shape = NA, linewidth = 0.35, fill = "white", colour = YUEXI$neutral_dark) +
  geom_point(position = position_jitter(width = 0.13, height = 0, seed = 20260912),
             shape = 16, size = 0.28, alpha = 0.16, colour = YUEXI$neutral_dark, show.legend = FALSE) +
  geom_point(data = quartile_stats, aes(x = quartile, y = mean_HQ), inherit.aes = FALSE,
             shape = 21, size = 2.2, stroke = 0.45, fill = "white", colour = YUEXI$neutral_dark) +
  scale_fill_manual(values = quartile_palette, guide = "none") +
  scale_x_discrete(labels = setNames(quartile_stats$x_lab, quartile_stats$quartile), expand = expansion(add = 0.50)) +
  coord_cartesian(ylim = c(0.38, 0.86), clip = "on") +
  labs(x = "Descriptive built-up threat-index quartile", y = "Forest habitat quality") +
  figure_theme(base_size = 7.2) +
  theme(axis.text.x = element_text(size = 6.3, lineheight = 0.95, margin = margin(t = 5)))

fig <- p_a + p_b + plot_layout(widths = c(1.45, 1.15)) +
  plot_annotation(tag_levels = "a") &
  theme(plot.tag = element_text(size = 7.9, face = "bold"))

save_r_figure(fig, file.path(out_dir, "Fig02_class_configuration"), width_mm = 150, height_mm = 77, dpi = 600)
write.csv(summary_class, file.path(out_dir, "Fig02_source_class_summary.csv"), row.names = FALSE)
write.csv(quartile_stats, file.path(out_dir, "Fig02_source_quartile_summary.csv"), row.names = FALSE)

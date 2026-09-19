# Candidate Figure 3 — observed temporal stability and scenario divergence
source("yuexi_r_style_150mm.R")
root <- Sys.getenv("YUEXI_FIG_ROOT", unset = "C:/yuexi_r/_YUEXI_FIGURE_REBUILD_20260912/04_figures")
data_dir <- file.path(root, "source_data")
out_dir <- file.path(root, "candidates_150mm", "Fig03")
temporal <- read.csv(file.path(data_dir, "fig3_temporal.csv"))
scenarios <- read.csv(file.path(data_dir, "fig3_scenarios.csv"))

# Panel a: only four date-specific outputs; observed and projected status encoded redundantly.
p_a <- ggplot(temporal, aes(year, eta2)) +
  geom_line(data = subset(temporal, data_type == "Observed"), colour = YUEXI$neutral_dark, linewidth = 0.75) +
  geom_point(data = subset(temporal, data_type == "Observed"), shape = 21, size = 2.8, stroke = 0.55, fill = "white", colour = YUEXI$neutral_dark) +
  geom_line(data = subset(temporal, year >= 2020), colour = YUEXI$projection, linewidth = 0.75, linetype = "dashed") +
  geom_point(data = subset(temporal, data_type == "Projected"), shape = 24, size = 3, stroke = 0.55, fill = YUEXI$projection, colour = YUEXI$projection) +
  geom_text(aes(label = sprintf("%.3f", eta2)), vjust = -1.45, size = 2.60, colour = YUEXI$neutral_dark) +
  annotate("text", x = 2014.7, y = 0.901, label = "Observed land cover", size = 2.60, colour = YUEXI$neutral_dark) +
  annotate("text", x = 2020.0, y = 0.869, label = "Observed anchor", size = 2.45, colour = YUEXI$neutral_dark, hjust = 0.5) +
  annotate("text", x = 2024.5, y = 0.927, label = "Projected", size = 2.60, colour = YUEXI$projection, hjust = 1) +
  scale_x_continuous(breaks = temporal$year) +
  coord_cartesian(ylim = c(0.872, 0.956), clip = "off") +
  labs(x = NULL, y = "η²") + figure_theme(base_size = 7.2)

# Panel b: 2030 and 2035 are modelled scenarios, no invented uncertainty.
scenarios$scenario <- factor(scenarios$scenario, levels = c("ECP", "BAU", "CPL", "COO"))
scenario_palette <- c("ECP" = YUEXI$forest, "BAU" = YUEXI$neutral_mid, "CPL" = YUEXI$cropland, "COO" = YUEXI$teal)
base_eta <- 0.8863
p_b <- ggplot(scenarios, aes(x = eta2, y = scenario, colour = scenario)) +
  geom_segment(aes(x = base_eta, xend = eta2, yend = scenario), linewidth = 0.7, colour = YUEXI$neutral_light) +
  geom_point(size = 2.8) +
  geom_vline(xintercept = base_eta, linetype = "dashed", linewidth = 0.35, colour = YUEXI$neutral_mid) +
  geom_text(aes(label = sprintf("%.3f", eta2)), hjust = -0.35, size = 2.45, colour = YUEXI$neutral_dark, show.legend = FALSE) +
  facet_wrap(~year, nrow = 1) +
  scale_colour_manual(values = scenario_palette, guide = "none") +
  coord_cartesian(xlim = c(0.86, 0.965), clip = "off") +
  labs(x = "η² of modelled scenario", y = NULL) +
  figure_theme(base_size = 7.2) +
  theme(axis.title.x = element_text(size = 6.5, margin = margin(t = 4)), strip.background = element_blank(), strip.text = element_text(face = "bold", size = 7.2))

# Supporting bottom strip has a different inferential role: forest within-class CV response.
p_c <- ggplot(scenarios, aes(x = scenario, y = forest_CV_pct, fill = scenario)) +
  geom_col(width = 0.68, colour = NA) +
  geom_text(aes(label = sprintf("%.1f%%", forest_CV_pct)), vjust = -0.45, size = 2.45, colour = YUEXI$neutral_dark) +
  facet_wrap(~year, nrow = 1) +
  scale_fill_manual(values = scenario_palette, guide = "none") +
  coord_cartesian(ylim = c(0, 18.3), clip = "off") +
  # Two-line y title: a single long line extends to the top of this short panel
  # and collides with the panel tag "c" once the figure is fitted to 150 mm.
  labs(x = NULL, y = "Forest CV\n(%)") + figure_theme(base_size = 7.2) +
  theme(strip.text = element_blank())

right <- p_b / p_c + plot_layout(heights = c(2.3, 1))
fig <- p_a + right + plot_layout(widths = c(0.9, 1.35)) +
  plot_annotation(tag_levels = "a") &
  theme(plot.tag = element_text(size = 7.9, face = "bold"))

save_r_figure(fig, file.path(out_dir, "Fig03_temporal_scenarios"), width_mm = 150, height_mm = 67.2, dpi = 600)
write.csv(temporal, file.path(out_dir, "Fig03_source_temporal.csv"), row.names = FALSE)
write.csv(scenarios, file.path(out_dir, "Fig03_source_scenarios.csv"), row.names = FALSE)

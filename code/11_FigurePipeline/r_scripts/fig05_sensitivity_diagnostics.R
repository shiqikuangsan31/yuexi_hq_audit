# Candidate Figure 5 — 2x2 sensitivity diagnostics
source("yuexi_r_style_150mm.R")
root <- Sys.getenv("YUEXI_FIG_ROOT", unset = "C:/yuexi_r/_YUEXI_FIGURE_REBUILD_20260912/04_figures")
data_dir <- file.path(root, "source_data")
out_dir <- file.path(root, "candidates_150mm", "Fig05")
thin <- read.csv(file.path(data_dir, "fig5_spatial_thinning_table10.csv"), stringsAsFactors = FALSE)
mc <- read.csv(file.path(data_dir, "fig5_montecarlo.csv"))
ks <- read.csv(file.path(data_dir, "fig5_k_sensitivity.csv"))
thin <- subset(thin, spacing_m != "Full set")
thin$spacing_km <- as.numeric(thin$spacing_m) / 1000
thin$n_retained <- as.numeric(thin$n_retained)
thin$moran_I <- as.numeric(thin$moran_I)
thin$eta2 <- as.numeric(thin$eta2)

p_a <- ggplot(thin, aes(x = spacing_km, y = eta2)) +
  geom_hline(yintercept = 0.886, colour = YUEXI$neutral_mid, linetype = "dashed", linewidth = 0.35) +
  geom_line(colour = YUEXI$dem, linewidth = 1.0) + geom_point(colour = YUEXI$dem, size = 2.2) +
  # ggrepel: at 150 mm the spacing-1 km and -2 km labels are only ~6.3 mm apart
  # and "0.887"/"0.887" touch, so labels are separated automatically instead of
  # being stacked at a fixed offset.
  ggrepel::geom_text_repel(aes(label = sprintf("%.3f", eta2)), size = 2.2, colour = YUEXI$neutral_dark,
                           direction = "y", nudge_y = 0.0012, box.padding = 0.10, point.padding = 0.10,
                           min.segment.length = 0.12, segment.size = 0.25, segment.colour = YUEXI$neutral_mid,
                           bg.color = "white", bg.r = 0.10,
                           ylim = c(0.8785, 0.9045), seed = 20260912, max.overlaps = Inf) +
  scale_x_continuous(breaks = thin$spacing_km) +
  coord_cartesian(ylim = c(0.878, 0.906), clip = "on") +
  labs(x = "Minimum inter-point spacing (km)", y = "η²") + figure_theme(base_size = 6.6)

p_b <- ggplot(thin, aes(x = spacing_km, y = moran_I)) +
  geom_line(colour = YUEXI$neutral_dark, linewidth = 0.85) + geom_point(colour = YUEXI$neutral_dark, size = 2.0) +
  ggrepel::geom_text_repel(aes(label = sprintf("n = %s", format(n_retained, big.mark = ","))), size = 2.2,
                           colour = YUEXI$neutral_mid, direction = "y", nudge_y = 0.006,
                           box.padding = 0.10, point.padding = 0.10, min.segment.length = 0.12,
                           segment.size = 0.25, segment.colour = YUEXI$neutral_mid,
                           bg.color = "white", bg.r = 0.10,
                           ylim = c(0.345, 0.595), seed = 20260912, max.overlaps = Inf) +
  scale_x_continuous(breaks = thin$spacing_km) +
  coord_cartesian(ylim = c(0.34, 0.60), clip = "on") +
  labs(x = "Minimum inter-point spacing (km)", y = "Global Moran's I") + figure_theme(base_size = 6.6)

mc_q <- quantile(mc$eta2, c(0.025, 0.50, 0.975))
p_c <- ggplot(mc, aes(x = eta2)) +
  geom_density(fill = "#AADCA9", colour = YUEXI$forest, linewidth = 0.95, alpha = 0.60) +
  geom_vline(xintercept = 0.886250156078105, colour = YUEXI$dem, linetype = "dotted", linewidth = 0.75) +
  geom_vline(xintercept = mean(mc$eta2), colour = YUEXI$neutral_dark, linewidth = 0.65) +
  geom_vline(xintercept = mc_q[c(1,3)], colour = YUEXI$neutral_mid, linetype = "dashed", linewidth = 0.40) +
  # Two-line annotations anchored clear of their reference lines: as single
  # lines they crossed the 0.844 / 0.883 / 0.910 verticals at 150 mm.
  annotate("text", x = mean(mc$eta2) - 0.0016, y = 25, label = sprintf("mean\n= %.3f", mean(mc$eta2)), size = 2.2, colour = YUEXI$neutral_dark, hjust = 1, lineheight = 0.95) +
  annotate("text", x = 0.812, y = 9, label = sprintf("2.5%%\n= %.3f", mc_q[1]), size = 2.2, hjust = 0, colour = YUEXI$neutral_mid, lineheight = 0.95) +
  annotate("text", x = 0.9285, y = 9, label = sprintf("97.5%%\n= %.3f", mc_q[3]), size = 2.2, hjust = 1, colour = YUEXI$neutral_mid, lineheight = 0.95) +
  coord_cartesian(xlim = c(0.81, 0.93), ylim = c(0, 28), clip = "on") +
  labs(x = "η² under independent ±20% Hj perturbations (n = 200)", y = "Density") + figure_theme(base_size = 6.6)

p_d <- ggplot(ks, aes(x = k, y = eta2)) +
  geom_line(colour = YUEXI$temperature, linewidth = 1.05) + geom_point(colour = YUEXI$temperature, size = 2.0) +
  geom_vline(xintercept = 0.30, colour = YUEXI$neutral_mid, linetype = "dashed", linewidth = 0.45) +
  geom_vline(xintercept = 0.50, colour = YUEXI$neutral_dark, linetype = "dashed", linewidth = 0.45) +
  annotate("text", x = 0.30, y = 0.13, label = "reference\nk = 0.30", size = 2.2, colour = YUEXI$neutral_mid) +
  annotate("text", x = 0.50, y = 0.49, label = "model run\nk = 0.50", size = 2.2, colour = YUEXI$neutral_dark, hjust = 0) +
  coord_cartesian(xlim = c(0.02, 1.55), ylim = c(0, 1.05), clip = "on") +
  labs(x = "InVEST half-saturation constant (k)", y = "η²") + figure_theme(base_size = 6.6)

fig <- (p_a | p_b) / (p_c | p_d) +
  plot_annotation(tag_levels = "a") & theme(plot.tag = element_text(size = 7.9, face = "bold"))
save_r_figure(fig, file.path(out_dir, "Fig05_sensitivity_diagnostics"), width_mm = 150, height_mm = 95.1, dpi = 600)
write.csv(thin, file.path(out_dir, "Fig05_source_thinning_table10.csv"), row.names = FALSE)
write.csv(mc, file.path(out_dir, "Fig05_source_montecarlo.csv"), row.names = FALSE)
write.csv(ks, file.path(out_dir, "Fig05_source_k_sensitivity.csv"), row.names = FALSE)

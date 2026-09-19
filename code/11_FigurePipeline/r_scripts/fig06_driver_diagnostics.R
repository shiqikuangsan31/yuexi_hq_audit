# Candidate Figure 6 — two-stage Geodetector and predictive-attribution diagnostics
source("yuexi_r_style_150mm.R")
root <- Sys.getenv("YUEXI_FIG_ROOT", unset = "C:/yuexi_r/_YUEXI_FIGURE_REBUILD_20260912/04_figures")
data_dir <- file.path(root, "source_data")
out_dir <- file.path(root, "candidates_150mm", "Fig06")
q <- read.csv(file.path(data_dir, "fig6_q_raw_residual.csv"))
disc <- read.csv(file.path(data_dir, "fig6_discretization_sensitivity.csv"))
shap <- read.csv(file.path(data_dir, "fig6_treeshap_artifact.csv"))
label_map <- c(slope="Slope", DEM="Elevation", TEM="Temperature", soiltype="Soil type", NDVI="NDVI", NLI="Night-time light", POP="Population", roads="Road distance", GDP="GDP", railways="Railway distance", water="Water distance", PRE="Precipitation", aspect="Aspect")
q$label <- label_map[q$factor]
q$label <- factor(q$label, levels = q$label[order(q$q_raw)])
top3 <- c("Slope", "Elevation", "Temperature")
q$is_top <- q$label %in% top3
q_delta <- sapply(top3, function(nm) {
  i <- which(as.character(q$label) == nm)
  q$q_raw[i] - q$q_residual[i]
})
q_long <- rbind(data.frame(label=q$label, stage="Raw HQ", q=q$q_raw, is_top=q$is_top), data.frame(label=q$label, stage="LUCC-detrended residual", q=q$q_residual, is_top=q$is_top))
p_a <- ggplot(q_long, aes(x=q, y=label, colour=stage, group=label)) +
 geom_line(data=subset(q_long, !is_top), colour=YUEXI$neutral_light, linewidth=0.7) + geom_point(data=subset(q_long, !is_top), size=2.0) +
 geom_line(data=subset(q_long, is_top), colour=YUEXI$neutral_light, linewidth=0.9) + geom_point(data=subset(q_long, is_top), size=3.1, shape=21, stroke=0.8, fill="white") +
 scale_colour_manual(values=c("Raw HQ"=YUEXI$slope,"LUCC-detrended residual"=YUEXI$temperature)) +
  annotate("text", x=0.50, y="Slope", label=sprintf("Δq = %.3f", q_delta["Slope"]), size=2.2, hjust=0, colour=YUEXI$neutral_dark) +
  annotate("text", x=0.50, y="Elevation", label=sprintf("Δq = %.3f", q_delta["Elevation"]), size=2.2, hjust=0, colour=YUEXI$neutral_dark) +
  annotate("text", x=0.50, y="Temperature", label=sprintf("Δq = %.3f", q_delta["Temperature"]), size=2.2, hjust=0, colour=YUEXI$neutral_dark) +
  # x limit widened from 0.86: at the fitted 150 mm panel width (17.4 mm) the
  # single-line Δq annotation ran past the panel edge and was truncated.
  scale_x_continuous(breaks=c(0, 0.25, 0.50, 0.75)) +
  coord_cartesian(xlim=c(0, 0.95), clip="on") +
  labs(x="Geodetector q-statistic (n = 30,711 complete cases)",y=NULL,colour=NULL)+figure_theme(base_size = 6.6)+theme(legend.position="top", legend.text=element_text(size=6.2))

disc$factor <- factor(disc$factor, levels=c("slope","DEM","TEM"), labels=c("Slope","Elevation","Temperature"))
p_b <- ggplot(disc,aes(x=factor,y=interaction(method,bins,sep=" | "),fill=q_residual))+
 geom_tile(colour="white",linewidth=0.35)+geom_text(aes(label=sprintf("%.3f",q_residual)),size=2.15,colour="white")+
 scale_fill_gradient(low="#DDEAF5",high=YUEXI$dem,name="Residual q")+
 labs(x=NULL,y="Discretization method | bins")+figure_theme(base_size = 6.6)+theme(axis.text.x=element_text(face="bold",size=6.2,angle=25,hjust=1),axis.text.y=element_text(size=6.0),axis.title.y=element_text(size=6.2),legend.position="right")+
 # Displayed method names are abbreviated so the y-label block fits the 150 mm
 # column; the full names appear in the manuscript table and caption.
 scale_y_discrete(labels=function(v) sub("^Equal interval", "Equal int.", sub("^Standard deviation", "Std. dev.", v)))

shap$factor <- factor(shap$factor,levels=shap$factor[order(shap$mean_abs_SHAP)])
p_c <- ggplot(shap,aes(x=mean_abs_SHAP,y=factor))+
 geom_segment(aes(x=0,xend=mean_abs_SHAP,yend=factor),colour=YUEXI$neutral_light,linewidth=0.85)+
 geom_point(colour=YUEXI$forest,size=2.25)+
 # Three ticks instead of five: the 23 mm panel cannot carry 0.00/0.02/.../0.08
 # at >= 6 pt without the tick labels touching. Three-line title keeps the
 # centred title inside the panel width so it is not cut by the canvas edge.
 scale_x_continuous(breaks=c(0, 0.04, 0.08)) +
 labs(x="Mean |TreeSHAP|\n(predictive;\nn = 30,711)",y=NULL)+figure_theme(base_size = 6.6)

fig <- p_a + p_b + p_c + plot_layout(widths=c(1.55,1.00,0.90)) + plot_annotation(tag_levels="a") & theme(plot.tag=element_text(size=7.9,face="bold"))
save_r_figure(fig,file.path(out_dir,"Fig06_driver_diagnostics"),width_mm = 150, height_mm = 63.9,dpi=600)
write.csv(q,file.path(out_dir,"Fig06_source_q.csv"),row.names=FALSE)
write.csv(disc,file.path(out_dir,"Fig06_source_discretization.csv"),row.names=FALSE)
write.csv(shap,file.path(out_dir,"Fig06_source_treeshap.csv"),row.names=FALSE)

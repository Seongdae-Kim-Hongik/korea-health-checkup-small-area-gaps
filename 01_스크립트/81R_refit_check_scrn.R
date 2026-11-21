suppressPackageStartupMessages({library(INLA);library(jsonlite)})
TAG<-"SCRN";VER<-"std3";ROOT<-Sys.getenv("ST_ROOT",normalizePath("."));OUTD<-file.path(ROOT,"04_분석",TAG);RES<-file.path(OUTD,"results_std3")
inla.setOption(num.threads="1:1")
S<-fromJSON(file.path(OUTD,"config_SCRN_std3.json"));DD<-read.csv(file.path(OUTD,"panel_SCRN_std3.csv"),fileEncoding="UTF-8-BOM",stringsAsFactors=FALSE)
g<-inla.read.graph(file.path(RES,"nb_SCRN.graph"));G<-sf::st_read(paste0(Sys.getenv("ST_DATA_ROOT"), "/기타/R_Studio/FBD_DATA_ZIP/final.shp",quiet=TRUE)
DD$area<-match(enc2utf8(DD$fbd_region),enc2utf8(G$region));DD$time<-DD$year-min(DD$year)+1;DD$yiid<-DD$time;DD$obs<-seq_len(nrow(DD));stopifnot(!anyNA(DD$area))
MAINFAM<-sub(".*main_family=([a-z_]+).*","\\1",paste(readLines(file.path(OUTD,"HM_best_SCRN_std3.txt")),collapse=" "))
V<-unique(c(S$sets_after_vif$S1_narrative_full,S$forced))
pc<-list(prec=list(prior="pc.prec",param=c(0.5,0.01)),phi=list(prior="pc",param=c(0.5,2/3)));pcp<-list(prec=list(prior="pc.prec",param=c(0.5,0.01)))
rhs<-c("1",sprintf("`%s`",V),"f(area,model='bym2',graph=g,scale.model=TRUE,constr=TRUE,hyper=pc)","f(time,model='rw1',scale.model=TRUE,hyper=pcp)","f(yiid,model='iid',hyper=pcp)",if(MAINFAM=="binomial_olre")"f(obs,model='iid',hyper=pcp)","offset(off)")
fm<-as.formula(paste("cases ~",paste(rhs,collapse="+")));fam<-if(MAINFAM=="binomial_olre")"binomial" else MAINFAM
fit<-function(){inla(fm,family=fam,data=DD,Ntrials=DD$Ntr,control.fixed=list(mean=0,prec=4,mean.intercept=0,prec.intercept=0.001),control.compute=list(waic=TRUE,dic=TRUE),control.inla=list(control.vb=list(emergency=50)),verbose=FALSE)}
m1<-fit();m2<-fit()
for(m in list(m1,m2)){pp<-m$summary.fitted.values$mean[seq_len(nrow(DD))];stopifnot(all(pp>0&pp<1))}
d<-data.frame(cov=rownames(m1$summary.fixed),OR1=exp(m1$summary.fixed$mean),OR2=exp(m2$summary.fixed$mean));d$absdiff<-abs(d$OR1-d$OR2)
write.csv(d,file.path(RES,"S90_refit_twice_fixed.csv"),row.names=FALSE)
meta<-data.frame(INLA=as.character(packageVersion("INLA")),R=R.version.string,threads="1:1",family=MAINFAM,WAIC1=m1$waic$waic,WAIC2=m2$waic$waic,WAIC_diff=m1$waic$waic-m2$waic$waic,max_OR_absdiff=max(d$absdiff),seeds="81 S7 set.seed(20261019); Moran set.seed(1)/(2); 88k 원본 seed",date=as.character(Sys.time()))
write.csv(meta,file.path(RES,"S90_repro_meta.csv"),row.names=FALSE);print(meta)

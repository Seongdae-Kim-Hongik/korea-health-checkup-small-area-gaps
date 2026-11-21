#!/bin/bash
set -x
S="${ST_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"; cd "$S"; export SK_RSLOTS=7; RS="nice -n 10 $S/01_스크립트/rslot.sh"
T=SCRN; GR="$S/04_분석/$T/graph_593.graph"; D=261118; NW=2; NMV=200; L="$S/04_분석/$T"
wl(){ while true; do l5=$(sysctl -n vm.loadavg | awk '{print $3}'); awk -v l=$l5 'BEGIN{exit !(l>=14)}' || break; echo "load5=$l5 ≥14 wait 10m $(date +%H:%M)"; sleep 600; done; }
q(){ while [ "$(jobs -rp | wc -l)" -ge 2 ]; do sleep 15; done; }
export ST_VER=std3 ST_THREADS=1 ST_GRAPH="$GR" ST_FAMS=binomial,binomial_olre   # 11/19 00:16: betabinomial 61분 미수렴(INLA 1스레드) → 후보에서 제외, 기록 results_std3/S1_betabinomial_note.txt
wl; (cd 01_스크립트 && ST_MV_STOP=1 $RS Rscript 81_fit_inla_binom_scrn.R $T) > $L/run_std3_81a.log 2>&1 || exit 1
FAM=$(grep -o "main_family=[a-z_]*" $L/HM_best_${T}_std3.txt | cut -d= -f2); echo "FAM=$FAM"
wl; $RS Rscript 01_스크립트/81R_refit_check_scrn.R > $L/run_std3_81R.log 2>&1 &
STEP=$(( (NMV + NW - 1) / NW ))
for k in $(seq 0 $((NW-1))); do a=$(( k*STEP+1 )); b=$(( (k+1)*STEP )); [ $b -gt $NMV ] && b=$NMV; wl; (cd 01_스크립트 && ST_MV_RANGE=$a-$b $RS Rscript 81_fit_inla_binom_scrn.R $T) > $L/run_std3_81_mv_$a.log 2>&1 & sleep 20; done
wait
wl; (cd 01_스크립트 && $RS Rscript 81_fit_inla_binom_scrn.R $T) > $L/run_std3_81b.log 2>&1 || exit 1
python3 01_스크립트/82L_core_report_nwin.py $T $D > $L/run_std3_82.log 2>&1; echo "82 rc=$?"
for V in s577 s2 s8; do wl; ST_VER=$V python3 01_스크립트/80_build_disease_panel_v.py $T > $L/run_${V}_80.log 2>&1 && python3 01_스크립트/99SC2_attach_binom_scrn.py $T $V && (cd 01_스크립트 && ST_FAMS=$FAM ST_VER=$V ST_THREADS=1 ST_MV_N=2 ST_GRAPH=$([ $V = s577 ] || echo "$GR") $RS Rscript 81_fit_inla_binom_scrn.R $T) > $L/run_${V}_81.log 2>&1; echo "$V rc=$?"; done
python3 01_스크립트/87_window_grid.py $T std3; (cd 01_스크립트 && TAG=$T ST_VER=std3 $RS Rscript 85_window_maps.R $T std3); python3 01_스크립트/86_yearly_maps_ehsa.py $T std3
python3 01_스크립트/88g_sens_prep.py $T std3 || exit 1
cd 01_스크립트; export TAG=$T
for G in 1 2 3 4 5 6; do q; wl; GROUP=$G $RS Rscript 88g_sens_suite_binom.R > $L/run_std3_88g_$G.log 2>&1 & sleep 5; done
q; wl; $RS Rscript 88h_ppc_varpart_binom.R > $L/run_std3_88h.log 2>&1 &
for G in nb struct review kh; do q; wl; $RS Rscript 88k_struct_kh_binom_scrn.R $G > $L/run_std3_88k_$G.log 2>&1 & sleep 5; done
wait
$RS Rscript 88k_struct_kh_binom_scrn.R combine > $L/run_std3_88k_combine.log 2>&1
cd ..; TAG=$T ST_VER=std3 python3 01_스크립트/89g_sens_combine.py $T std3 > $L/run_std3_89g.log 2>&1
echo "ALL rc=$?"; grep -l "FAILED\|Error" $L/run_std3_8*.log; true

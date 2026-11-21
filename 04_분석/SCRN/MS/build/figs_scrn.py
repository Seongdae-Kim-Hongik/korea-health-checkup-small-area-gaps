# -*- coding: utf-8 -*-
#  Fig 1 (A) 14년 표준화 수검비(SUR) 지도 + Gi* 핫·콜드 윤곽 (B) 주모형 잔차 시군구 효과(오즈비) 지도 (C) 전국 수검률 남녀 2011-24
#  Fig 2 독거노인·대졸·걷기·공공체육시설의 모형별 오즈비(1 SD)
import os, json, numpy as np, pandas as pd, geopandas as gpd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, Rectangle, Polygon
from matplotlib.lines import Line2D
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
SHP = os.environ.get("ST_SHP", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "data", "boundary", "final.shp"))
HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, "figs"); OUTF = os.path.join(os.path.dirname(HERE), "out", "Figures"); os.makedirs(FIG, exist_ok=True); os.makedirs(OUTF, exist_ok=True)
N = json.load(open(os.path.join(HERE, "numbers_scrn.json"))); GI = pd.read_csv(os.path.join(HERE, "gi_scrn.csv"), dtype={"sigungu_cd": str})
MM = 1 / 25.4; W = 170 * MM; LW = 0.3
plt.rcParams.update({"font.family": "Arial", "font.size": 8, "legend.fontsize": 7.5, "legend.title_fontsize": 8, "axes.linewidth": 1.0, "xtick.major.width": 1.0, "ytick.major.width": 1.0, "lines.linewidth": 1.0, "pdf.fonttype": 42})
G = gpd.read_file(SHP); G["cd"] = G.sigungu_cd.astype(str); G["sido"] = G.cd.str[:2]; SIDO = G.dissolve("sido"); XL = (G.total_bounds[0], G.total_bounds[2]); YL = (G.total_bounds[1], G.total_bounds[3])
def letter(ax, ch, dx=0.0, dy=1.03, fs=28): ax.text(dx, dy, ch.upper(), transform=ax.transAxes, fontsize=fs, fontweight="bold", va="bottom", ha="left", clip_on=False)
def mapax(ax):
    SIDO.boundary.plot(ax=ax, color="#404040", linewidth=1.0); ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_axis_off(); ax.set_aspect("equal")
    x0, x1 = XL; y0, y1 = YL; W_ = x1 - x0; H_ = y1 - y0; bx, by = x0 + 0.62 * W_, y0 + 0.04 * H_; hh = 0.012 * H_
    ax.add_patch(Rectangle((bx, by), 50000, hh, facecolor="black", edgecolor="black", linewidth=1.0)); ax.add_patch(Rectangle((bx + 50000, by), 50000, hh, facecolor="white", edgecolor="black", linewidth=1.0))
    for xx, lab in ((0, "0"), (50000, "50"), (100000, "100")): ax.text(bx + xx, by + hh + 0.008 * H_, lab, ha="center", va="bottom", fontsize=7)
    ax.text(bx + 108000, by + 0.5 * hh, "km", ha="left", va="center", fontsize=7)
    nx, ny = x0 + 0.90 * W_, y0 + 0.70 * H_
    ax.add_patch(Polygon([[nx - 0.036 * W_, ny], [nx + 0.036 * W_, ny], [nx, ny + 0.21 * H_]], closed=True, facecolor="black", edgecolor="none")); ax.text(nx, ny + 0.225 * H_, "N", ha="center", va="bottom", fontsize=24)
def save(fig, k, dpi):
    p = os.path.join(FIG, f"Fig{k}.png"); fig.savefig(p, dpi=dpi, facecolor="white"); plt.close(fig)
    im = Image.open(p).convert("RGB"); im.save(p, dpi=(dpi, dpi)); im.save(os.path.join(OUTF, f"Figure_{k}.tif"), dpi=(dpi, dpi), compression="tiff_lzw"); return im.size
PAL = ["#2166AC", "#67A9CF", "#D1E5F0", "#FDDBC7", "#F4A582", "#D6604D", "#B2182B"]
# Fig 1
fig = plt.figure(figsize=(W, 6.6))
gg = G.merge(GI[["sigungu_cd", "SUR", "cls", "RR"]], left_on="cd", right_on="sigungu_cd", how="left"); assert gg.SUR.notna().all() and len(gg) == 229
ax = fig.add_axes([0.0, 0.40, 0.48, 0.56])
BR = [0, 0.92, 0.95, 0.98, 1.02, 1.05, 1.08, 9]; LB = ["<0.92", "0.92–0.94", "0.95–0.97", "0.98–1.01", "1.02–1.04", "1.05–1.07", "≥1.08"]
gg.plot(ax=ax, column="SUR", cmap=ListedColormap(PAL), norm=BoundaryNorm(BR, len(PAL)), edgecolor="#a0a0a0", linewidth=LW); mapax(ax)
gg[gg.cls == "cold"].boundary.plot(ax=ax, color="#08306B", linewidth=1.0, linestyle=(0, (2.0, 1.2))); gg[gg.cls == "hot"].boundary.plot(ax=ax, color="black", linewidth=1.1); letter(ax, "A", dy=0.95)
h = [Patch(facecolor=c, edgecolor="#777777", linewidth=0.5, label=l) for c, l in zip(PAL, LB)] + [Patch(facecolor="none", edgecolor="black", linewidth=1.1, label="Hot spot"), Patch(facecolor="none", edgecolor="#08306B", linewidth=1.0, linestyle="--", label="Cold spot")]
ax.legend(handles=h, title="Standardised uptake ratio, 2011–2024", loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False, columnspacing=0.8, handlelength=1.3)
bx = fig.add_axes([0.52, 0.40, 0.48, 0.56])
BR2 = [0, 0.75, 0.85, 0.95, 1.05, 1.15, 1.25, 9]; LB2 = ["<0.75", "0.75–0.84", "0.85–0.94", "0.95–1.04", "1.05–1.14", "1.15–1.24", "≥1.25"]
gg.plot(ax=bx, column="RR", cmap=ListedColormap(PAL), norm=BoundaryNorm(BR2, len(PAL)), edgecolor="#a0a0a0", linewidth=LW); mapax(bx); letter(bx, "B", dy=0.95)
bx.legend(handles=[Patch(facecolor=c, edgecolor="#777777", linewidth=0.5, label=l) for c, l in zip(PAL, LB2)], title="Residual district odds ratio, principal model", loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=4, frameon=False, columnspacing=0.8, handlelength=1.3)
c = fig.add_axes([0.10, 0.05, 0.86, 0.20]); ys = sorted(int(k) for k in N["uptake"])
c.plot(ys, [N["uptake_men"][str(y)] for y in ys], color="#2166AC", marker="o", ms=3, lw=1.2, label="Men")
c.plot(ys, [N["uptake_women"][str(y)] for y in ys], color="#B2182B", marker="s", ms=3, lw=1.2, label="Women")
c.plot(ys, [N["uptake"][str(y)] for y in ys], color="black", marker="D", ms=2.6, lw=1.0, ls="--", label="All")
for x0 in (2017.5, 2018.5, 2019.5): c.axvline(x0, color="#404040", lw=1.0, ls=":")
c.set_ylim(60, 85); c.set_xticks(ys[::1]); c.set_xticklabels([str(y) if y % 2 == 1 else "" for y in ys]); c.set_ylabel("Uptake, %"); c.set_xlabel("Year")
c.legend(frameon=False, ncol=3, loc="lower left", fontsize=7); c.spines[["top", "right"]].set_visible(False); letter(c, "C", dx=-0.09, dy=1.0)
s1 = save(fig, 1, 600)
# Fig 2 — 모형별 오즈비
LAB = {"alone_elderly": "Older adults\nliving alone", "tertiary": "Tertiary-educated\nadults", "walking": "Walking\nrate", "public_fac": "Public sports\nfacilities"}
COL = {"alone_elderly": "ext__living_alone_elderly", "tertiary": "tertiary_educated_share", "walking": "ext__walking_rate", "public_fac": "ext__public_sport_fac_per100k"}
ORD = list(LAB); PH = N["ph"]
def p(a, v, s=""): return PH.get(f"{a}|{COL[v]}{s}")
MOD = [("Principal model", lambda v: N["main"][v], "#000000", "o"),
       ("Knorr-Held type II", lambda v: N["KH_typeII"][v], "#E08214", "P"),
       ("Knorr-Held type IV", lambda v: N["KH_typeIV"][v], "#B2182B", "D"),
       ("Spatial+", lambda v: N["D1_spatial_plus"][v], "#1B7837", "h"),
       ("Restricted spatial regression", lambda v: N["RSR"][v], "#6a3d9a", "X"),
       ("Between-district component", lambda v: p("P4_between_within", v, "__B"), "#7f7f7f", "^"),
       ("Within-district component", lambda v: p("P4_between_within", v, "__W"), "#67A9CF", "v"),
       ("2019–2024 only", lambda v: p("P6_2019_2024_only", v), "#2166AC", "s")]
vals = [t for v in ORD for j in range(len(MOD)) for t in [MOD[j][1](v)] if t]; lo_all = min(t[1] for t in vals); hi_all = max(t[2] for t in vals)
fig, ax = plt.subplots(figsize=(W, 4.6)); fig.subplots_adjust(left=0.20, right=0.98, top=0.98, bottom=0.28)
off = np.linspace(-0.36, 0.36, len(MOD))
for i, v in enumerate(ORD):
    for (lab, f, col, mk), o in zip(MOD, off):
        r = f(v)
        if not r: continue
        e, lo, hi = r; ax.plot([lo, hi], [i + o] * 2, color=col, lw=1.0); ax.plot(e, i + o, marker=mk, color=col, ms=3.6, mew=0, ls="none")
ax.axvline(1, color="#404040", lw=1.0, ls=":"); ax.set_yticks(range(len(ORD))); ax.set_yticklabels([LAB[v] for v in ORD]); ax.invert_yaxis()
xt = [0.84, 0.88, 0.92, 0.96, 1.00, 1.04, 1.08]; assert xt[0] <= lo_all and hi_all <= xt[-1], (lo_all, hi_all)
ax.set_xlim(xt[0], xt[-1]); ax.set_xticks(xt); ax.set_xticklabels([f"{x:.2f}" for x in xt]); ax.minorticks_off()
ax.set_xlabel("Odds ratio of uptake per 1 standard deviation (95% credible interval)"); ax.spines[["top", "right"]].set_visible(False)
ax.legend(handles=[Line2D([0], [0], color=c_, marker=m, lw=1.0, ms=3.6, mew=0, label=l) for l, _, c_, m in MOD], loc="upper center", bbox_to_anchor=(0.40, -0.13), ncol=3, frameon=False)
s2 = save(fig, 2, 1000)
for k, s, d in ((1, s1, 600), (2, s2, 1000)): print(f"Fig{k}: {s[0]}x{s[1]} px = {s[0]/d*25.4:.0f} x {s[1]/d*25.4:.0f} mm @ {d} dpi")

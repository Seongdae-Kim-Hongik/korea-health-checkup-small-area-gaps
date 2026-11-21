#  산출 = numbers_scrn.json, gi_scrn.csv. 원고 숫자의 유일한 출처. 효과 = 오즈비(OR, 결과 csv의 IRR 열 이름은 이항 사본에서 그대로 유지).
import os, json, unicodedata, numpy as np, pandas as pd
from scipy.stats import spearmanr, norm
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.abspath(os.path.join(HERE, "..", "..")); AN = os.path.dirname(B); ROOT = os.path.dirname(AN); PAN = os.path.join(ROOT, "02_패널")
RS = lambda v="std3": os.path.join(B, f"results_{v}"); NFC = lambda s: unicodedata.normalize("NFC", str(s))
SHP = os.environ.get("ST_SHP", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "data", "boundary", "final.shp"))
VARS = {"walking": "ext__walking_rate", "mpa": "moderate_pa_rate", "public_fac": "ext__public_sport_fac_per100k", "village_fac": "ext__village_sport_fac_per100k",
        "smoking": "ext__smoking_rate", "drinking": "ext__high_risk_drinking", "obesity": "obesity_rate",
        "im_spec": "im_specialists_per_100k", "unmet": "ext__unmet_need_rate",
        "livelihood": "basic_livelihood_rate", "tertiary": "tertiary_educated_share", "alone_elderly": "ext__living_alone_elderly",
        "urban": "urban_population_share", "physicians": "physicians_per_1000", "sex_ratio": "sex_ratio", "fiscal": "fiscal_independence", "pop80": "pop80_share"}
HYP = list(VARS)[:12]
def tab(f, v="std3"):
    d = pd.read_csv(os.path.join(RS(v), f)); d["cov"] = d["cov"].astype(str); return d
def get(d, c, col="IRR"):
    r = d[d["cov"] == c].iloc[0]; return [round(float(r[col]), 3), round(float(r.lo), 3), round(float(r.hi), 3)]
N = {}
P = pd.read_csv(os.path.join(B, "panel_SCRN_std3.csv"), encoding="utf-8-sig"); P["fbd_region"] = P.fbd_region.map(NFC)
EB = pd.read_csv(os.path.join(PAN, "SCRN_Ebinom.csv"), encoding="utf-8-sig"); EB["fbd_region"] = EB.fbd_region.map(NFC)
N["n_rows"] = len(P); N["n_districts"] = P.fbd_region.nunique(); N["elig_total_m"] = round(P.Ntr.sum() / 1e6, 1); N["scr_total_m"] = round(P.cases.sum() / 1e6, 1)
g = EB.groupby("year"); up = g.cases.sum() / g.Ntr.sum()
N["uptake"] = {int(k): round(100 * v, 1) for k, v in up.items()}; N["elig_m"] = {int(k): round(v / 1e6, 1) for k, v in g.Ntr.sum().items()}
for s, lab in (("남자", "men"), ("여자", "women")):
    u = g[f"scr_{s}"].sum() / g[f"elig_{s}"].sum(); N[f"uptake_{lab}"] = {int(k): round(100 * v, 1) for k, v in u.items()}
N["elig_growth_2017_2019_pct"] = round(100 * (N["elig_m"][2019] / N["elig_m"][2017] - 1), 1)
L = P.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E.sum(), include_groups=False)   # 표준화 수검비(SUR, 관측/기대)
U = P.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.Ntr.sum(), include_groups=False)
N["sur_min"], N["sur_max"] = round(L.min(), 2), round(L.max(), 2); N["sur_p10"], N["sur_p90"] = round(L.quantile(.1), 2), round(L.quantile(.9), 2); N["p90p10"] = round(L.quantile(.9) / L.quantile(.1), 2)
N["up_p10"], N["up_p90"] = round(100 * U.quantile(.1), 1), round(100 * U.quantile(.9), 1); N["up_min"], N["up_max"] = round(100 * U.min(), 1), round(100 * U.max(), 1)
N["sur_top"] = [[r, round(v, 3)] for r, v in L.sort_values(ascending=False).head(10).items()]; N["sur_bottom"] = [[r, round(v, 3)] for r, v in L.sort_values().head(10).items()]
YS = P.pivot_table(index="fbd_region", columns="year", values="SIR"); N["p90p10_year"] = {int(y): round(YS[y].quantile(.9) / YS[y].quantile(.1), 3) for y in YS.columns}
N["rho_2011_2024"] = round(spearmanr(YS[2011], YS[2024]).correlation, 2)
N["rho_sur_up"] = round(spearmanr(L, U.reindex(L.index)).correlation, 2)
# 기술(Table 1)
WIN = {"2011-2017": (2011, 2017), "2018-2024": (2018, 2024), "2011-2024": (2011, 2024)}
T1 = {}
for w, (a, b) in WIN.items():
    s = P[P.year.between(a, b)]; sw = s.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E.sum(), include_groups=False)
    T1[w] = dict(n=len(s), elig=float(s.Ntr.sum()), scr=float(s.cases.sum()), rate=float(s.cases.sum() / s.Ntr.sum()), sur_med=float(sw.median()), sur_p10=float(sw.quantile(.1)), sur_p90=float(sw.quantile(.9)),
                 cov={k: [float(s[VARS[k] + "_raw"].mean()), float(s[VARS[k] + "_raw"].std())] for k in VARS})
N["T1"] = T1
mo = pd.read_csv(os.path.join(RS(), "S6_moran_year.csv")); N["moran_min"], N["moran_max"] = round(mo.moran_I.min(), 2), round(mo.moran_I.max(), 2)
N["moran_2011"], N["moran_2024"] = round(float(mo[mo.year == 2011].moran_I.iloc[0]), 2), round(float(mo[mo.year == 2024].moran_I.iloc[0]), 2)
N["kendall_w"] = round(float(pd.read_csv(os.path.join(RS(), "S12_persistence.csv")).iloc[0].kendall_W), 2)
# Gi*(593 그래프, 자기 포함) — 14년 log SUR
import geopandas as gpd
G = open(os.path.join(B, "graph_593.graph")).read().split("\n"); nreg = int(G[0]); nb = {}
for line in G[1:]:
    t = line.split()
    if len(t) >= 2: nb[int(t[0])] = [int(x) for x in t[2:]]
area = pd.DataFrame({"fbd_region": gpd.read_file(SHP)["region"].values}); area["fbd_region"] = area.fbd_region.map(NFC); assert len(area) == nreg
id2r = dict(zip(range(1, nreg + 1), area.fbd_region))
x = np.log(L.reindex([id2r[i] for i in range(1, nreg + 1)]).values); assert not np.isnan(x).any(); xb, sd = x.mean(), x.std(); gi = []
for i in range(1, nreg + 1):
    w = np.zeros(nreg); w[i - 1] = 1; w[[j - 1 for j in nb.get(i, [])]] = 1; W = w.sum()
    gi.append(((w * x).sum() - xb * W) / (sd * np.sqrt((nreg * (w ** 2).sum() - W ** 2) / (nreg - 1))))
GI = pd.DataFrame({"fbd_region": [id2r[i] for i in range(1, nreg + 1)], "SUR": np.exp(x), "z": gi}); GI["p"] = 2 * norm.sf(GI.z.abs())
GI["cls"] = np.where((GI.p < 0.05) & (GI.z > 0), "hot", np.where((GI.p < 0.05) & (GI.z < 0), "cold", "other"))
S6 = pd.read_csv(os.path.join(RS(), "S6_spatial_RR.csv")); S6["fbd_region"] = S6.fbd_region.map(NFC); GI = GI.merge(S6[["fbd_region", "sigungu_cd", "RR", "class"]], on="fbd_region", validate="one_to_one")
SIDO = {"서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon", "광주": "Gwangju", "대전": "Daejeon", "울산": "Ulsan", "세종": "Sejong", "경기": "Gyeonggi", "강원": "Gangwon", "충청북": "Chungbuk",
        "충청남": "Chungnam", "전라북": "Jeonbuk", "전라남": "Jeonnam", "경상북": "Gyeongbuk", "경상남": "Gyeongnam", "제주": "Jeju"}
GI["sido"] = GI.fbd_region.map(lambda r: next(v for k, v in SIDO.items() if r.startswith(k)))
GI.to_csv(os.path.join(HERE, "gi_scrn.csv"), index=False, encoding="utf-8-sig")
for c in ("hot", "cold"):
    s = GI[GI.cls == c]; N[f"gi_{c}"] = len(s); N[f"gi_{c}_sido"] = s.sido.value_counts().to_dict(); N[f"gi_{c}_sur_med"] = round(s.SUR.median(), 3)
for c in ("hotspot", "coldspot"):
    s = GI[GI["class"] == c]; N[f"bym_{c}"] = len(s); N[f"bym_{c}_sido"] = s.sido.value_counts().to_dict()
N["seoul_cold_bym"] = int(((GI.sido == "Seoul") & (GI["class"] == "coldspot")).sum()); N["seoul_n"] = int((GI.sido == "Seoul").sum())
N["rr_min"], N["rr_max"] = round(GI.RR.min(), 2), round(GI.RR.max(), 2)
N["rr_bottom"] = [[r, v] for r, v in GI.sort_values("RR").head(6)[["fbd_region", "RR"]].values.tolist()]; N["rr_top"] = [[r, v] for r, v in GI.sort_values("RR", ascending=False).head(6)[["fbd_region", "RR"]].values.tolist()]
# 모형
LK = pd.read_csv(os.path.join(RS(), "S1_likelihood.csv")); N["lik"] = {r.family: float(r.WAIC) for r in LK.itertuples()}
M = tab("S3_main_IRR.csv"); N["main"] = {k: get(M, VARS[k]) for k in VARS}
F = pd.read_csv(os.path.join(RS(), "S3_main_fit.csv")).iloc[0]; N["waic_main"] = float(F.WAIC); N["phi"] = float(F.phi); N["n_hot_bym"] = int(F.n_hotspot); N["n_cold_bym"] = int(F.n_coldspot)
RM = pd.read_csv(os.path.join(RS(), "S8_residual_moran.csv")).set_index("quantity")
N["resid_moran"] = [float(RM.loc["pearson_residual_area_mean", "moran_I"]), float(RM.loc["pearson_residual_area_mean", "expected_I"]), float(RM.loc["pearson_residual_area_mean", "p_perm"])]
N["obs_moran"] = [float(RM.loc["observed_logSIR_pooled", "moran_I"]), float(RM.loc["observed_logSIR_pooled", "p_perm"])]
hy = pd.read_csv(os.path.join(RS(), "S3_main_hyper.csv")).set_index("hyperpar"); N["phi_ci"] = [round(float(hy.loc["Phi for area", c]), 2) for c in ("mean", "X0.025quant", "X0.975quant")]
NC = tab("S3_negcontrol.csv"); N["nc"] = {c: get(NC, c) for c in NC["cov"]}
MV = pd.read_csv(os.path.join(RS(), "S7_multiverse_summary.csv")); MV["cov"] = MV["cov"].astype(str)
N["mv"] = {k: [round(float(MV[MV["cov"] == VARS[k]].cred_frac.iloc[0]), 3), round(float(MV[MV["cov"] == VARS[k]].sign_agree.iloc[0]), 3), int(MV[MV["cov"] == VARS[k]].n_specs.iloc[0])] for k in HYP}
d = tab("S9_typeI_IRR.csv"); N["KH_typeI"] = {k: get(d, VARS[k]) for k in VARS}
for t in ("KH_typeII", "KH_typeIII", "KH_typeIV", "icar_besag", "iid_only", "no_spatial", "knn4"):
    d = tab(f"S43_part_{t}.csv"); N[t] = {k: get(d, VARS[k]) for k in VARS if (d["cov"] == VARS[k]).any()}
SF = pd.read_csv(os.path.join(RS(), "S43_sensitivity_fit.csv")).set_index("analysis"); N["waic_spec"] = {a: float(SF.loc[a, "WAIC"]) for a in SF.index}
for a in ("D1_spatial_plus", "C4_sido_year_iid", "E1_lag1", "E2_lag2", "G1_kchs_ma3", "H4_even_years", "H4_odd_years"):
    d = tab(f"S41_part_{a}.csv"); N[a] = {k: get(d, VARS[k]) for k in VARS if (d["cov"] == VARS[k]).any()}
f = os.path.join(RS(), "S43_part_RSR.csv")
if os.path.exists(f): d = tab("S43_part_RSR.csv"); N["RSR"] = {k: get(d, VARS[k]) for k in VARS if (d["cov"] == VARS[k]).any()}
rs = pd.read_csv(os.path.join(RS(), "S50_resid_moran_by_spec.csv")).set_index("spec"); N["rm_spec"] = {s: [round(float(rs.loc[s, "resid_moran_I"]), 3), float(rs.loc[s, "p_perm"])] for s in rs.index}
W4 = tab("S4_window_IRR.csv"); N["win"] = {w: {k: get(W4[W4.window == w], VARS[k]) for k in VARS} for w in W4.window.unique()}
CV = tab("S5_covid.csv"); N["covid_x"] = {k: get(CV[CV.term == "var_x_post"], VARS[k]) for k in HYP}
for v in ("s577", "s2", "s8"):
    d = tab("S3_main_IRR.csv", v); N["sens_" + v] = {k: get(d, VARS[k]) for k in VARS if (d["cov"] == VARS[k]).any()}
d = tab("S10_offset_sensitivity_IRR.csv"); N["E_pop"] = {k: get(d, VARS[k]) for k in VARS}
PH = pd.read_csv(os.path.join(RS(), "S46_scrn_posthoc.csv")); PH["cov"] = PH["cov"].astype(str)
N["ph"] = {f"{r.analysis}|{r.cov}": [round(r.OR, 3), round(r.lo, 3), round(r.hi, 3)] for r in PH.itertuples()}
VP = pd.read_csv(os.path.join(RS(), "S42_variance_partition.csv")).set_index("component"); N["vp"] = {c: round(float(VP.loc[c, "share_of_linear_predictor_var"]), 3) for c in VP.index if c != "linear_predictor_total"}
PP = pd.read_csv(os.path.join(RS(), "S42_ppc.csv")).iloc[0]; N["ppc"] = {"cov95": round(float(PP.coverage95), 4), "cov50": round(float(PP.coverage50), 4), "pit_sd": round(float(PP.pit_sd), 3)}
N["repro"] = pd.read_csv(os.path.join(RS(), "S90_repro_meta.csv")).iloc[0][["INLA", "threads", "WAIC_diff", "max_OR_absdiff"]].astype(str).to_dict()
json.dump(N, open(os.path.join(HERE, "numbers_scrn.json"), "w"), ensure_ascii=False, indent=1, default=float)
print({k: N[k] for k in ("n_districts", "elig_total_m", "scr_total_m", "sur_p10", "sur_p90", "p90p10", "up_p10", "up_p90", "gi_hot", "gi_cold", "gi_hot_sido", "gi_cold_sido", "bym_coldspot_sido", "seoul_cold_bym", "moran_2011", "moran_2024", "kendall_w", "rho_2011_2024", "uptake")})

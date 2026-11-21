#!/usr/bin/env python3
#  분자 cases = 1차검진 수검인원, 시행 Ntr = 1차검진 대상인원 (KOSIS DT_35007_N001 2011-17 '1차검진', DT_35007_N001_1 2018-24; 시군구×성).
#  분모 = 검진 '대상자'(수검자 아님). 대상자 연령 분포는 시군구에서 공표되지 않음 → 주 기대 비율 pE = Σ_성 대상_성 × 전국 성별 수검률 / Ntr (성 간접표준화).
#   민감도 off_pop = 주민등록 성×16연령 인구 × 전국 성·연령 수검 율(N099 계 ÷ 전국 인구)로 만든 기대 수검자 ÷ Ntr(연도별 재척도) → 연령 구조 반영 대안.
#   off_age(s8용) = 전국 연도 수검률(성 무시), off_crude = 같음.
#  세종: 시군구 행 없는 해 → 원표 시도 머리행(세종) 사용. 일반구 시 = 구 합(분모 가중, 단순평균 아님). 군위 2023 = 대구 편입 키 매핑(m50.map_region).
#  산출: 02_패널/SCRN_Ebinom.csv, 04_분석/SCRN/gate/*.csv(게이트 표)
import os, sys, importlib.util, unicodedata
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); AN = os.path.join(ROOT, "04_분석"); PAN = os.path.join(ROOT, "02_패널")
SRC = os.path.join(ROOT, "00_원천", "C_NHIS_검진보험"); GATE = os.path.join(AN, "SCRN", "gate"); os.makedirs(GATE, exist_ok=True)
def _load(nm, f):
    s = importlib.util.spec_from_file_location(nm, os.path.join(HERE, f)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
m38 = _load("m38", "38_build_Estd_all.py"); cw = _load("cw", "40_region_crosswalk.py"); m50 = _load("m50", "50_build_master_panel.py")
NFC = lambda s: unicodedata.normalize("NFC", str(s))
YEARS = list(range(2011, 2025)); SEXES = ["남자", "여자"]
BANDS = ["0-19"] + [f"{lo}-{lo+4}" for lo in range(20, 85, 5)] + ["85+"]
assert os.environ.get("ST_FBDZIP"), "ST_FBDZIP(창원 2023 교정 인구 폴더)를 지정"
SJ = NFC("세종시세종시")

# ── 원표 N001/N001_1 직접 읽기(시군구·시도·전국, 성별) ──
R = []
for f in ["DT_35007_N001.csv", "DT_35007_N001_1.csv"]:
    d = pd.read_csv(os.path.join(SRC, f), encoding="utf-8-sig", low_memory=False)
    if "C3_NM" in d.columns: d = d[d.C3_NM == "1차검진"]
    d = d[d.PRD_DE.isin(YEARS)][["PRD_DE", "C1", "C1_NM", "C2_NM", "ITM_NM", "DT"]].copy(); d["src"] = f; R.append(d)
R = pd.concat(R); R["DT"] = pd.to_numeric(R.DT.astype(str).str.replace(",", ""), errors="coerce")
R.columns = ["year", "c1", "c1_nm", "sex", "item", "value", "src"]
print("[99SC] 원표 값 결측(-·빈칸):", int(R.value.isna().sum()), "칸; 0 값:", int((R.value == 0).sum()), "칸")
R.to_csv(os.path.join(GATE, "raw_N001_rows.csv"), index=False, encoding="utf-8-sig")

# 장기 long csv(시군구 이름 정규화 완료본) 사용 — 같은 원표의 정리본
L = pd.read_csv(os.path.join(PAN, "NHIS검진_시군구_연도_long.csv"), usecols=["year", "sido", "sigungu", "level", "sex", "topic", "category", "measure", "value", "tbl_id"], engine="pyarrow")
L = L[(L.topic == "일반검진_대상수검") & (L.category == "1차검진") & L.year.isin(YEARS)].copy()
L["v"] = L.measure.map({"대상인원": "elig", "수검인원": "scr"})
NAT = L[L.level == "전국"].pivot_table(index="year", columns=["v", "sex"], values="value", aggfunc="sum")
# 전국 성별 수검률
pnat = {s: NAT[("scr", s)] / NAT[("elig", s)] for s in SEXES + ["합계"]}
g = pd.DataFrame({"elig_total": NAT[("elig", "합계")], "scr_total": NAT[("scr", "합계")], "uptake_total": pnat["합계"],
                  "uptake_men": pnat["남자"], "uptake_women": pnat["여자"], "elig_men": NAT[("elig", "남자")], "elig_women": NAT[("elig", "여자")]})
g["elig_yoy"] = g.elig_total.pct_change(); g["uptake_diff_pp"] = g.uptake_total.diff() * 100
print("[99SC] 전국 대상·수검:\n", g.round(4).to_string()); g.to_csv(os.path.join(GATE, "G1_national_eligible_uptake.csv"), encoding="utf-8-sig")
assert (NAT[("elig", "합계")] - NAT[("elig", "남자")] - NAT[("elig", "여자")]).abs().max() <= 1

base = pd.read_csv(os.path.join(AN, "PERIO", "panel_PERIO.csv"), encoding="utf-8-sig"); base["fbd_region"] = base.fbd_region.map(NFC); base["key"] = base.key.map(NFC)
base = base[["year", "key", "fbd_region"]].drop_duplicates(); base = base[base.year.isin(YEARS)].reset_index(drop=True)
PKEYS = set(base.key); assert base.fbd_region.nunique() == 229 and len(base) == 229 * 14
S = L[(L.level == "시군구") & L.sex.isin(SEXES)].copy()
pairs = S[["sido", "sigungu"]].drop_duplicates(); mp = {(a, b): m50.map_region(a, b, PKEYS) for a, b in zip(pairs.sido, pairs.sigungu)}
S["key"] = [mp[(a, b)]["key"] for a, b in zip(S.sido, S.sigungu)]; S["role"] = [mp[(a, b)]["role"] for a, b in zip(S.sido, S.sigungu)]
unm = S[S.key.isna()][["sido", "sigungu"]].drop_duplicates(); print("[99SC] 키 미매칭 원표 지역(제외):", unm.values.tolist())
S = S[S.key.notna()]; S["key"] = S.key.map(NFC)
hasprim = S[S.role == "primary"].groupby(["key", "year"]).size().index
nsub = int(((S.role == "sub") & S.set_index(["key", "year"]).index.isin(hasprim)).sum())
S = S[~((S.role == "sub") & S.set_index(["key", "year"]).index.isin(hasprim))]
print(f"[99SC] 일반구 하위 행 중 상위 시 행이 있어 버린 행 {nsub}; 나머지 일반구는 구 합(인원 합 = 분모 가중)")
X = S.pivot_table(index=["year", "key"], columns=["v", "sex"], values="value", aggfunc="sum")
# 세종: 시도 머리행
SJr = L[(L.level == "시도") & (L.sido == "세종") & L.sex.isin(SEXES)].pivot_table(index="year", columns=["v", "sex"], values="value", aggfunc="sum")
sjkey = base.loc[base.fbd_region == SJ, "key"].iat[0]
P = base.copy(); Xr = X.reindex(pd.MultiIndex.from_frame(P[["year", "key"]]))
sjm = (P.fbd_region == SJ).values
src_note = np.where(sjm & P.year.isin(SJr.index).values, "세종 시도 머리행", "시군구 행")
for v in ["elig", "scr"]:
    for s in SEXES:
        col = Xr[(v, s)].values.astype(float) if (v, s) in Xr.columns else np.full(len(P), np.nan)
        sjv = P.year.map(SJr[(v, s)]).values
        had = ~np.isnan(col[sjm]); print(f"[99SC] 세종 {v}{s}: 시군구 행 있는 해 {int(had.sum())}/14 (시도 머리행으로 대체)")
        cs = col[sjm]; col[sjm] = np.where(np.isnan(sjv[sjm]), cs, sjv[sjm]); P[f"{v}_{s}"] = col   # 시도 행 없는 해(2011 연기군)는 시군구 행
P["src"] = src_note
miss = P[[c for c in P.columns if c.startswith(("elig_", "scr_"))]].isna().any(axis=1)
print("[99SC] 결측 칸:", P.loc[miss, ["fbd_region", "year"]].values.tolist())
zero = (P[[f"elig_{s}" for s in SEXES]] <= 0).any(axis=1); print("[99SC] 대상 0 칸:", P.loc[zero, ["fbd_region", "year"]].values.tolist())
assert not miss.any() and not zero.any()
P["Ntr"] = P.elig_남자 + P.elig_여자; P["cases"] = P.scr_남자 + P.scr_여자
assert (P.cases <= P.Ntr).all()
chk = P.groupby("year")[["Ntr", "cases"]].sum(); chk["Ntr_ratio_nat"] = chk.Ntr / NAT[("elig", "합계")]; chk["cases_ratio_nat"] = chk.cases / NAT[("scr", "합계")]
print("[99SC] 시군구 합 / 전국:\n", chk.round(5).to_string()); chk.to_csv(os.path.join(GATE, "G2_district_sum_vs_national.csv"), encoding="utf-8-sig")

# ── 기준 SQLite 대조(chk__수검률) ──
import sqlite3
DB = os.path.expandvars("$ST_GPT_DATASET") + "/02_체육건강_시공간_GPT버전/02_체육건강_시공간_GPT버전.sqlite"
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
SQ = pd.read_sql('select year, fbd_region, "chk__수검률" as up_sq from region_year where year between 2011 and 2024', con); SQ["fbd_region"] = SQ.fbd_region.map(NFC)
c = P.merge(SQ, on=["year", "fbd_region"], how="left", validate="one_to_one"); c["up"] = c.cases / c.Ntr * 100; dd = (c.up - c.up_sq).abs()
print(f"[99SC] SQLite chk__수검률 대조: 겹침 {int(dd.notna().sum())}칸, 최대차 {dd.max():.4f}%p, SQLite 빈칸 {int(c.up_sq.isna().sum())}칸 → {c.loc[c.up_sq.isna(), ['fbd_region','year']].values.tolist()[:20]}")
c[["year", "fbd_region", "up", "up_sq"]].to_csv(os.path.join(GATE, "G3_sqlite_crosscheck.csv"), index=False, encoding="utf-8-sig")

# ── 주민등록 성×16연령 인구(99H 규칙 그대로) → 인구 기반 민감도 ──
SIDO_HDR = {k for k in cw.SIDO_STD if len(k) >= 3 and (k.endswith("시") or k.endswith("도"))}
FIVE = [f"{lo}-{lo+4}세" for lo in range(0, 85, 5)]; OLD85 = ["85-89세", "90-94세", "95-99세", "100세 이상"]
EXTRA = {("충청북도", "청원군"): "충청북도|청주시"}; rows = []
for y in YEARS:
    d = pd.read_csv(os.path.join(m38.FBDZIP, f"{y}.csv"), encoding="cp949", dtype=str)
    d["행정구역별"] = d["행정구역별"].map(NFC).str.strip(); d["연령별"] = d["연령별"].map(NFC).str.strip()
    for s in ["전체"] + SEXES: d[s] = pd.to_numeric(d[s].str.replace(",", ""), errors="coerce")
    sido = None; city = None; blocks = (d["행정구역별"] != d["행정구역별"].shift()).cumsum()
    for _, gg in d.groupby(blocks, sort=False):
        nm = gg["행정구역별"].iat[0]
        if nm == "전국": continue
        if nm in SIDO_HDR:
            sido = nm; city = None
            if nm != "세종특별자치시": continue
            gg = gg.drop_duplicates("연령별")
        sg = nm.split("-")[-1]
        if sg.endswith("시"): city = sg
        elif sg.endswith("구") and city is not None and cw.sido_std(sido) not in ("서울시", "부산시", "대구시", "인천시", "광주시", "대전시", "울산시"): continue
        else: city = None
        key = EXTRA.get((cw.sido_std(sido), sg), cw.make_key(sido, sg))
        if key not in PKEYS and key.endswith("군") and key[:-1] + "시" in PKEYS: key = key[:-1] + "시"
        for s in SEXES:
            a = gg.set_index("연령별")[s]; tot = a.get("계", np.nan)
            if pd.isna(tot): continue
            f5 = a.reindex(FIVE); o = a.reindex(OLD85).fillna(0); assert f5.notna().all(), (y, nm, s)
            rows.append({"year": y, "sex": s, "key": NFC(key), "tot": tot, "0-19": f5["15-19세"], **{b: f5[b + "세"] for b in BANDS[1:-1]}, "85+": o.sum()})
G = pd.DataFrame(rows).groupby(["year", "key", "sex"], as_index=False)[["tot"] + BANDS].sum()
def nb_band(a):
    a = str(a).replace(" ", "")
    if a == "19세이하": return "0-19"
    if a == "85세이상": return "85+"
    if a.endswith("세") and "~" in a:
        lo, hi = a[:-1].split("~"); return f"{lo}-{hi}"
    return None
A = pd.read_csv(os.path.join(SRC, "DT_35007_N099_national_long.csv"), encoding="utf-8-sig"); A = A[(A.grp == "계") & A.year.isin(YEARS)]; A["band"] = A.age.map(nb_band)
EX = A[A.band.notna() & A.sex.isin(SEXES)].set_index(["year", "sex", "band"]).value.unstack()[BANDS]
NATPOP = G.groupby(["year", "sex"])[BANDS].sum(); UPT = EX / NATPOP
exn = EX.groupby(level="year").sum().sum(1); print("[99SC] 판정 수검자(N099 계) ÷ 1차 수검인원(N001):", (exn / NAT[("scr", "합계")]).round(4).to_dict())
EP = np.zeros(len(P))
for s in SEXES:
    Z = P[["year", "key"]].merge(G[G.sex == s], on=["year", "key"], how="left", validate="one_to_one"); assert Z.tot.notna().all(), s
    EP += (Z[BANDS].values * UPT.xs(s, level="sex").loc[Z.year.values].values).sum(1)
    P[f"pop_{s}"] = Z.tot.values
P["pop"] = P.pop_남자 + P.pop_여자
P["E_pop"] = EP * P.groupby("year").cases.transform("sum").values / pd.Series(EP).groupby(P.year.values).transform("sum").values
P["elig_per_pop"] = P.Ntr / P["pop"]
lg = lambda p: np.log(p / (1 - p))
pE = sum(P[f"elig_{s}"] * P.year.map(pnat[s]) for s in SEXES) / P.Ntr
P["pE"] = pE; P["off"] = lg(pE)
P["off_age"] = lg(P.year.map(pnat["합계"])); P["off_crude"] = P.off_age
pp = (P.E_pop / P.Ntr).clip(0.02, 0.98); P["pE_pop"] = pp; P["off_pop"] = lg(pp)
P["E"] = P.Ntr * P.pE; P["E"] = P.E * P.groupby("year").cases.transform("sum") / P.groupby("year").E.transform("sum")
P["uptake"] = P.cases / P.Ntr; P["SUR"] = P.cases / P.E
H = pd.read_csv(os.path.join(PAN, "HTND_Estd2.csv"), encoding="utf-8-sig"); H["fbd_region"] = H.fbd_region.map(NFC)
P = P.merge(H[["year", "fbd_region", "pop80_share_raw"]], on=["year", "fbd_region"], how="left", validate="one_to_one"); assert P.pop80_share_raw.notna().all()
cols = ["year", "fbd_region", "key", "src", "elig_남자", "elig_여자", "scr_남자", "scr_여자", "Ntr", "cases", "pE", "off", "off_age", "off_pop", "off_crude", "pE_pop", "E", "E_pop", "uptake", "SUR", "pop", "elig_per_pop", "pop80_share_raw"]
fp = os.path.join(PAN, "SCRN_Ebinom.csv"); P[cols].to_csv(fp, index=False, encoding="utf-8-sig")
print(f"[99SC] {fp}: {len(P)}행 {P.fbd_region.nunique()}곳, 수검 합 {int(P.cases.sum()):,} / 대상 합 {int(P.Ntr.sum()):,}")
print(f"[99SC] 수검률 칸 {P.uptake.min():.3f}~{P.uptake.max():.3f} (중앙 {P.uptake.median():.3f}); pE {P.pE.min():.3f}~{P.pE.max():.3f}; pE_pop {P.pE_pop.min():.3f}~{P.pE_pop.max():.3f} (clip 칸 {int(((P.E_pop/P.Ntr)<0.02).sum()+((P.E_pop/P.Ntr)>0.98).sum())})")
print(f"[99SC] 대상/인구 {P.elig_per_pop.min():.3f}~{P.elig_per_pop.max():.3f}; Spearman(SUR, uptake) {P.SUR.corr(P.uptake, method='spearman'):.3f}")

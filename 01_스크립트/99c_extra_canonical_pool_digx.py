#!/usr/bin/env python3







import os, sqlite3, unicodedata, numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); PAN = os.path.join(ROOT, "02_패널")
DB = os.path.expandvars("$ST_GPT_DATASET") + "/02_체육건강_시공간_GPT버전/02_체육건강_시공간_GPT버전.sqlite"
E = pd.read_csv(os.path.join(PAN, "DIGX_Estd25.csv"), encoding="utf-8-sig", dtype={"sigungu_cd": str}); E["fbd_region"] = E.fbd_region.map(NFC)
MC = pd.read_csv(os.path.join(PAN, "DIGX_mort_counts_2011_2025.csv"), encoding="utf-8-sig", dtype={"sigungu_cd": str}); MC["fbd_region"] = MC.fbd_region.map(NFC)
assert len(E) == 229 * 15 and (E.sigungu_cd == "29010").sum() == 15
out = E[["year", "fbd_region", "sigungu_cd", "offset", "cases"]].rename(columns={"offset": "population", "cases": "digx_deaths"})
out = out.merge(MC[["year", "fbd_region", "ill_defined_share"]], on=["year", "fbd_region"], how="left", validate="one_to_one")
RULE = [dict(variable="ill_defined_share", source="DT_1B34E13 불명확 사인(R00-R99)/전체 사망 2025 원값", n2025_observed=229, n2025_locf=0)]
def locf(col, src):
    m25 = (out.year == 2025) & out[col].isna(); v24 = out[out.year == 2024].set_index("fbd_region")[col]
    out.loc[m25, col] = out.loc[m25, "fbd_region"].map(v24).values
    RULE.append(dict(variable=col, source=src, n2025_observed=int(229 - m25.sum()), n2025_locf=int(m25.sum())))
WARD_CITIES = ["고양", "성남", "수원", "안산", "안양", "용인", "창원", "포항", "전주", "천안", "청주"]
def gate(col, fix=True):
    o = out.sort_values(["fbd_region", "year"]); g = o.groupby("fbd_region")[col]; nb = (g.shift(1) + g.shift(-1)) / 2
    lo_ = (nb > 0) & (o[col] < 0.2 * nb); hi_ = (nb > 0) & (o[col] > 5 * nb)
    ward = o.fbd_region.str.contains("|".join(WARD_CITIES))
    print(f"[99c-digx] gate {col}: <=0 {int((o[col] <= 0).sum())}, below 20% of neighbours {int(lo_.sum())} (ward cities {int((lo_ & ward).sum())}), above 5 times {int(hi_.sum())} (ward cities {int((hi_ & ward).sum())})")
    bad = lo_ | hi_
    if fix and bad.any():
        print(f"   -> set missing and interpolated {o.loc[bad, ['fbd_region', 'year', col]].values.tolist()[:20]}")
        out.loc[bad[bad].index, col] = np.nan
        out[col] = out.sort_values(["fbd_region", "year"]).groupby("fbd_region")[col].transform(lambda s: s.interpolate(limit_area="inside"))
        RULE.append(dict(variable=col, source=f"게이트: 이웃 연도 평균 20% 미만·5배 초과 {int(bad.sum())}칸 → 결측 → 시군구 안 선형 보간", n2025_observed=None, n2025_locf=None))
# ② region_year
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
RY = {"urban_pop": "eloc__DT_1YL20421E__1인당도시지역면적현황__도시지역인구", "physicians_per_1000": "eloc__DT_1YL20981__인구천명당의료기관종사의사수＜br＞(A÷B×1000)",
      "sex_ratio": "eloc__DT_1YL20701__남녀성비＜br＞(A÷B×100)", "fiscal_independence": "eloc__DT_1YL20891__재정자주도(세입과목개편전)",
      "walking_rate": "kchs__DT_H_EX_WALK__SR", "moderate_pa_rate": "kchs__DT_H_EX_PHY__SR", "fac_n": "fac__total", "vil_n": "vil__계",
      "chewing_discomfort_65": "kchs__DT_H_OR_INCONV__SR", "smoking_rate": "kchs__DT_H_SM__SR", "high_risk_drinking": "kchs__DT_H_DR_HIGH__SR", "obesity_rate": "kchs__DT_H_OBE_OBE__SR",
      "medicaid1_n": "nhis__의료급여1종__진료실인원수", "genhosp_n": "chk__요양기관_종합병원",
      "hit_and_run_rate": "eloc__DT_1YL13901__뺑소니교통사고율＜br＞(A÷B×100)", "traffic_culture_index": "eloc__DT_1YL20331__지수__계",
      "fires_per_10000": "eloc__DT_1YL21081__주민만명당화재발생건수＜br＞(A÷B×10000)", "ry_population": "population"}
q = ", ".join(f'"{c}" as "{k}"' for k, c in RY.items())
R = pd.read_sql(f"select year, fbd_region, {q} from region_year where year between 2011 and 2025", con); R["fbd_region"] = R.fbd_region.map(NFC)
out = out.merge(R, on=["year", "fbd_region"], how="left", validate="one_to_one")
d = (out.population - out.ry_population).abs(); print("[99c-digx] population (E denominator) vs region_year, largest difference (2011-24, FBDZIP basis, including the Changwon 2023 correction):", float(d.max()), "· largest difference in 2025", float(d[out.year == 2025].max()))
out["urban_population_share"] = 100 * out.urban_pop / out.ry_population
out["genhosp_per100k"] = 1e5 * out.genhosp_n / out.ry_population
out["public_sport_fac_per100k"] = 1e5 * out.fac_n / out.ry_population
out["village_sport_fac_per100k"] = 1e5 * out.vil_n / out.ry_population
out["medicaid1_share"] = 100 * out.medicaid1_n / out.ry_population
for c in ["public_sport_fac_per100k", "village_sport_fac_per100k", "medicaid1_share", "chewing_discomfort_65", "walking_rate"]: gate(c)
gate("genhosp_per100k", fix=False)
for c in ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "walking_rate", "moderate_pa_rate", "chewing_discomfort_65", "smoking_rate",
          "high_risk_drinking", "obesity_rate", "genhosp_per100k", "hit_and_run_rate", "traffic_culture_index", "fires_per_10000"]:
    if out[out.year == 2025][c].notna().sum() < 229: locf(c, "region_year 2025 결측 칸 → 2024 이월")
    else: RULE.append(dict(variable=c, source="region_year 2025 원값", n2025_observed=229, n2025_locf=0))
for c in ["public_sport_fac_per100k", "village_sport_fac_per100k"]: locf(c, "체육시설 현황 2025 미공표 → 2024 이월")
locf("medicaid1_share", "NHIS 의료급여 1종 2025 미공표 → 2024 이월")

S = pd.read_csv(os.path.join(PAN, "SCRT_Estd25.csv"), encoding="utf-8-sig"); S["fbd_region"] = S.fbd_region.map(NFC)
out = out.merge(S[["year", "fbd_region", "pop80_share_raw"]].rename(columns={"pop80_share_raw": "pop80_share"}), on=["year", "fbd_region"], how="left", validate="one_to_one")
RULE.append(dict(variable="pop80_share", source="SCRT_Estd25(2011–24 시리즈 값, 2025 KOSIS DT_1B04005N 2025-12 원값)", n2025_observed=229, n2025_locf=0))

A = pd.read_csv(os.path.join(PAN, "EXT_canonical_pool_ALLD_261112.csv"), encoding="utf-8-sig"); A["fbd_region"] = A.fbd_region.map(NFC)
out = out.merge(A[["year", "fbd_region", "basic_livelihood_rate", "tertiary_educated_share"]], on=["year", "fbd_region"], how="left")
r = out.fbd_region.map(out[out.year.isin([2020, 2024])].groupby("fbd_region").basic_livelihood_rate.mean())
assert not (out.year.isin([2021, 2022, 2023]) & ((out.basic_livelihood_rate < 0.2 * r) | (out.basic_livelihood_rate > 5 * r))).any(), "livelihood-rate correction violated"
locf("basic_livelihood_rate", "ALLD 풀 2024까지 → 2025 이월"); locf("tertiary_educated_share", "ALLD 풀 2024까지 → 2025 이월")
keep = ["year", "fbd_region", "sigungu_cd", "population", "digx_deaths", "pop80_share", "urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence",
        "walking_rate", "moderate_pa_rate", "public_sport_fac_per100k", "village_sport_fac_per100k", "chewing_discomfort_65", "smoking_rate", "high_risk_drinking", "obesity_rate",
        "medicaid1_share", "genhosp_per100k", "ill_defined_share", "basic_livelihood_rate", "tertiary_educated_share", "hit_and_run_rate", "traffic_culture_index", "fires_per_10000"]
out = out[keep].sort_values(["fbd_region", "year"]).reset_index(drop=True)
miss = out.isna().sum(); print("[99c-digx] missing before interpolation", miss[miss > 0].to_dict())
for c in keep[5:]:
    n = int(out[c].isna().sum())
    if n:
        out[c] = out.groupby("fbd_region")[c].transform(lambda s: s.interpolate(limit_direction="both")); n2 = int(out[c].isna().sum())
        if n2: out[c] = out[c].fillna(out.groupby("year")[c].transform("mean"))
        RULE.append(dict(variable=c, source=f"결측 {n}칸: 시군구 안 선형 보간(양끝 이월) {n - n2}칸, 전 연도 결측 시군구 {n2}칸 = 그해 전국 평균", n2025_observed=None, n2025_locf=None))
assert out.notna().all().all() and len(out) == 3435 and out.groupby("year").fbd_region.nunique().eq(229).all() and (out.sigungu_cd == "29010").sum() == 15
cw = out[(out.fbd_region == NFC("경상남도창원시")) & out.year.isin([2021, 2022, 2023])].basic_livelihood_rate; assert cw.between(1.5, 3.5).all(), cw.tolist()
pd.DataFrame(RULE).to_csv(os.path.join(PAN, "EXT_canonical_pool_DIGX_2025rule.csv"), index=False, encoding="utf-8-sig")
out.to_csv(os.path.join(PAN, "EXT_canonical_pool_DIGX_261114.csv"), index=False, encoding="utf-8-sig")
print("[99c-digx] saved", out.shape); print(pd.DataFrame(RULE).to_string(index=False))
print(out[keep[5:]].describe().T[["mean", "std", "min", "max"]].round(3).to_string())

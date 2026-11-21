#!/usr/bin/env python3
#
import os, json, hashlib, unicodedata
import numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); PAN = os.path.join(ROOT, "02_패널")
POOL = "EXT_canonical_pool_SCRN_261118.csv"
D = pd.read_csv(os.path.join(PAN, "EXT_canonical_pool_LIPS_261116.csv")).drop(columns=["lips_cases", "lips_examinees", "screening_uptake"]); D["fbd_region"] = D.fbd_region.map(NFC)
B = pd.read_csv(os.path.join(PAN, "SCRN_Ebinom.csv"), encoding="utf-8-sig"); B["fbd_region"] = B.fbd_region.map(NFC)
P = D.merge(B[["year", "fbd_region", "cases", "Ntr"]].rename(columns={"cases": "scrn_cases", "Ntr": "scrn_eligible"}), on=["year", "fbd_region"], how="left", validate="one_to_one")
assert len(P) == 229 * 14 and P.notna().all().all(), P.isna().sum()[lambda s: s > 0]
P.to_csv(os.path.join(PAN, POOL), index=False, encoding="utf-8-sig")
FORCED = ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"]
NEG = ["hit_and_run_rate", "traffic_culture_index", "fires_per_10000"]
SENS = ["medicaid1_share", "genhosp_per100k"]
HYP = ["walking_rate", "moderate_pa_rate", "public_sport_fac_per100k", "village_sport_fac_per100k",
       "smoking_rate", "high_risk_drinking", "obesity_rate",
       "im_specialists_per100k", "unmet_need_rate",
       "basic_livelihood_rate", "tertiary_educated_share", "living_alone_elderly"]
OBES = "kchs__DT_H_OBE_OBE__SR"
X = lambda L: [OBES if v == "obesity_rate" else "ext__" + v for v in L]; XK = lambda v: OBES if v == "obesity_rate" else "ext__" + v
EXPECT = {
 "walking_rate": "+ (걷기 실천율: 건강 관여 행동의 군집 → 예방 서비스 이용 증가; 체육 경로 주 가설)",
 "moderate_pa_rate": "+ (중강도 이상 신체활동 실천율: 건강 관여 행동 군집; 체육 경로 주 가설)",
 "public_sport_fac_per100k": "+ (공공체육시설 인구 10만 명당: 지역 건강 기반 시설·생활권 건강 관여 기회; 체육 경로 주 가설)",
 "village_sport_fac_per100k": "+ (마을체육시설 인구 10만 명당: 농촌 생활권 건강 관여 기회)",
 "smoking_rate": "- (현재흡연율: 건강 위험 행동 군집 → 예방 서비스 이용 저하)",
 "high_risk_drinking": "- (고위험음주율: 건강 위험 행동 군집)",
 "obesity_rate": "± (자가보고 비만율: 건강 우려 → 이용 증가 또는 낙인·회피 → 저하)",
 "im_specialists_per100k": "+ (내과 전문의 10만 명당: 검진기관·의료 공급 접근)",
 "unmet_need_rate": "- (미충족 의료 경험률: 의료 접근 장벽)",
 "basic_livelihood_rate": "- (기초생활 수급률, 2021-23 양쪽 규칙 정정: 박탈 → 예방 서비스 이용 저하; 역의 돌봄 법칙)",
 "tertiary_educated_share": "+ (대졸 이상 비율: 건강 문해력·예방 행동)",
 "living_alone_elderly": "- (독거노인 비율: 사회적 고립 → 이용 저하)",
}
SETS = {"S1_narrative_full": X(HYP),
        "S2_core": X(["walking_rate", "moderate_pa_rate", "public_sport_fac_per100k", "smoking_rate", "unmet_need_rate", "basic_livelihood_rate"]),
        "S3_physical_activity": X(["walking_rate", "moderate_pa_rate", "public_sport_fac_per100k", "village_sport_fac_per100k"]),
        "S4_health_behaviour": X(["smoking_rate", "high_risk_drinking", "obesity_rate"]),
        "S5_care_access": X(["im_specialists_per100k", "unmet_need_rate"]),
        "S6_socioeconomic": X(["basic_livelihood_rate", "tertiary_educated_share", "living_alone_elderly"])}
pov = [{"year": 2023, "fbd_region": "경상남도창원시", "population": 1009038, "source": "KOSIS DT_1YL20651E 2023 통합창원시 계(유방암 11/4 population_final_audit)"}]
allv = ["scrn_cases", "scrn_eligible"] + FORCED + NEG + SENS + [v for v in HYP if v != "obesity_rate"]
LAB = ("expected first-stage examinees E = eligible x pE, pE = sex-standardised expected uptake (district eligible persons by sex x national sex-specific uptake of the same year, KOSIS DT_35007_N001/N001_1); "
       "binomial models use Ntrials = eligible persons and offset logit(pE); eligible persons by age are not published for districts (age enters through forced 80+ share and the population-based sensitivity)")
def make(ver):
    return {
     "tag": "SCRN", "outcome_column": "ext__scrn_cases",
     "outcome_label_en": "First-stage National General Health Screening uptake: examinees among eligible persons (NHIS health screening statistics DT_35007_N001 2011-2017 and DT_35007_N001_1 2018-2024, annual)",
     "disease_en": "General health screening uptake (use of a preventive service, not a disease)",
     "disease_ko": "일반건강검진 1차 수검(수검인원 ÷ 대상인원)",
     "offset": "ext__scrn_eligible", "exclude_years": [],
     "forced": X(FORCED), "negative_controls": X(NEG),
     "offset_E_column": "E", "offset_E_file": "SCRN_Ebinom.csv", "offset_E_label": LAB,
     "offset_E_sensitivity_column": "E_pop", "offset_E_label_sensitivity": "population-based age-and-sex standardisation (resident population 2 sexes x 16 age bands x national age-sex uptake per resident; binomial offset logit(E_pop/eligible))",
     "graph": "593-edge contact graph, ST_GRAPH=04_분석/SCRN/graph_593.graph",
     "population_override": pov, "sensitivity_only_extra": X(SENS),
     "version": "std3 physical-activity pathway (general health screening uptake: physical activity and sport facilities, health behaviours, care access, socioeconomic), 2011-2024",
     "sets": SETS, "transform": {XK(v): "none" for v in FORCED + NEG + SENS + HYP},
     "expected_direction": {XK(k): v for k, v in EXPECT.items()},
     "rules": {"likelihood": "forced-only 모형 WAIC 낮은 쪽(binomial/betabinomial/binomial_olre)", "set_choice": "WAIC 최소, 4 이내면 변수 적은 세트", "credible": "95% CrI 1 제외", "vif_drop": 10, "multiverse_specs": 200,
               "main_model_note": "주모형 = S1_narrative_full(가설 12 + 강제통제 5). 세트를 다시 바꾸지 않음. VIF>10 유지·보고. 효과 = 오즈비.",
               "years": [2011, 2024], "windows": {"W1_2011-17": [2011, 2017], "W2_2018-24": [2018, 2024]}, "covid_post_from": 2020,
               "windows_note": "2018 표 개편(N001→N001_1)·대상 확대(2018 +10%, 2019 20-30대 피부양자·세대원 편입 +11%)를 가로지르지 않는 2011-17·2018-24 창(결과 전 고정)."},
     "note": "SCRN = 일반건강검진 1차 수검인원 ÷ 대상인원(KOSIS DT_35007_N001·N001_1, 시군구×성). 세종은 원표 시도 머리행(2012-24), 2011은 연기군 시군구 행. 시군구 합/전국 1.000(14년), 기준 SQLite chk__수검률 겹침 3,186칸 차이 0, SQLite 빈칸 20칸(세종 13·부천 2016·용인/창원/천안 2011-12)은 원표 값. 이항 BYM2(Ntrials = 대상인원, offset = logit 성 표준화 기대 수검률). 연도별 전국 성별 수검률로 기대치 → 추정 대상 = 그해 전국 대비 상대 오즈. 단절: 2018·2019 대상 확대, 2020 COVID(전국 67.8%)·2020/2021 검진 기간 연장.",
     "extra_columns": {"ext__" + v: [POOL, v] for v in allv}}
out = {}
for ver in ["std3", "s577", "s2", "s8"]:
    j = make(ver)
    if ver == "s577": j["sens_note"] = "민감도: 그래프만 queen 577"
    if ver == "s2": j["sens_note"] = "민감도: 80세 이상 비율 강제통제 없음"; j["forced"] = X(FORCED[:4])
    if ver == "s8": j["sens_note"] = "민감도: 성 무시 기대치(offset = logit 전국 연도 수검률)"
    fp = os.path.join(HERE, f"sets_SCRN_{ver}.json"); json.dump(j, open(fp, "w"), ensure_ascii=False, indent=1)
    out[ver] = hashlib.sha256(open(fp, "rb").read()).hexdigest()
pd.Series(out, name="sha256").to_csv(os.path.join(HERE, "sets_SCRN_sha256_261118.csv"))
print("sets 저장·해시:", out)

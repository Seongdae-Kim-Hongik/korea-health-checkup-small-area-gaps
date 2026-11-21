# esm_scrn.py — 65호 SCRN Supplementary material(Supporting Methods·Table S1–S5) + STROBE 체크리스트 단독 파일(2026-11-19).
#  수치는 numbers_scrn.json·결과 CSV에서만. 영국식 철자, 표 제목 쌍점 금지, 사후 분석은 post hoc 표기. Spatial+·RSR·KH 전부 게재.
import os, sys, json, subprocess, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import content_scrn as C
from build_manuscript_base_scrn import TX, foot_row, LABEL, GROUPS
MSD = os.path.dirname(HERE); OUT = os.path.join(MSD, os.environ.get("ESM_OUT", "out")); JRN = os.environ.get("ESM_JOURNAL", ""); B = os.path.dirname(MSD); RS = os.environ.get("ESM_RS") or os.path.join(B, "results_std3"); PAN = os.environ.get("ESM_PAN") or os.path.join(os.path.dirname(os.path.dirname(B)), "02_패널")
N = C.N; f3 = lambda t: f"{t[0]:.3f} ({t[1]:.3f}–{t[2]:.3f})" if t else "–"
HYP = [v for _, vs in GROUPS[:4] for v in vs]
J = TX(cite="bracket")
def TF(title, header, rows, foot="", fs=8, land=False, port=False):
    J.new_page("landscape") if land else (J.new_page("portrait") if port else J.page_break()); J.table_fit(title, header, rows, "", fs_max=fs, title_bold=True)
    if foot: foot_row(J, foot, 8, 12)
J.para("<b>Supplementary material</b>"); J.para(f"Supplementary material for the manuscript entitled \"{C.TITLE}\"" + (f", {JRN}. Seongdae Kim, Department of Biohealth Convergence Open Sharing System, Hongik University, Seoul, Republic of Korea (kimsd@hongik.ac.kr)" if JRN else ""))
J.para("Contents. Supporting Methods; Table S1 (district characteristics); Table S2 (structural alternatives); Table S3 (other alternative specifications); Table S3b (separate periods); Table S4 (prespecified and post hoc analyses); Table S5 (national eligible persons and attendees, residual autocorrelation and negative controls).")
J.head("Supporting Methods", 1)
SM = [
 ("Data checks", f"First-stage eligible persons and attendees by district and sex were read from the published tables (DT_35007_N001 for 2011–2017 and DT_35007_N001_1 for 2018–2024). District sums equalled the national totals in all 14 years for both eligible persons and attendees (ratio 1.000), no published cell was missing or zero, and attendees never exceeded eligible persons. Sejong is published only as a province row from 2012 and was taken from that row; in 2011 the district row for Yeongi-gun was used. The analysis dataset (a fixed copy of the series database) gave identical uptake in all 3,186 overlapping district-years, and its 20 empty cells (Sejong 2012–2024, Bucheon 2016, and Yongin, Changwon and Cheonan 2011–2012) were taken from the published tables. National first-stage attendees equalled the national examinees with judgement results (DT_35007_N099) in every year."),
 ("Eligibility and screening periods", "Eligibility follows the National Health Insurance Service general health screening rules: employees (non-office workers every year, office workers every 2 years), heads of self-employed households, household members and dependants aged 40 years or older, and Medical Aid beneficiaries, mostly invited by birth-year parity. Dependants and household members aged 20–39 years became eligible on 1 January 2019. The 2020 and 2021 screening periods were extended to June of the following year during the COVID-19 pandemic. National eligible persons rose by 10.0% in 2018 and 10.8% in 2019; the ratio of eligible persons to residents rose almost uniformly across districts in both years (10th–90th percentile of district change 7–12% and 6–13%)."),
 ("Likelihood and model checks", f"Binomial, beta-binomial and binomial with an observation-level independent random effect were compared with the forced adjustments only. The beta-binomial model did not converge within 61 minutes with eligible counts in the tens of thousands per cell and was abandoned; the binomial with an observation-level effect had WAIC {N['lik']['binomial_olre']:,.1f} against {N['lik']['binomial']:,.1f} for the plain binomial. With an observation-level effect, WAIC favoured models without a spatial term or with an intrinsic conditional autoregressive term and disfavoured Knorr-Held interactions, because the observation-level effect absorbs structured variation; WAIC was therefore not used to choose among spatial structures, and all 4 interaction types are reported. Fitted values were checked to lie on the probability scale in every model. Refitting the principal model twice with 1 thread gave identical WAIC and odds ratios (INLA {N['repro']['INLA']}). The characteristic sets and robustness rules were fixed before fitting (SHA-256 745b71c8…). Priors: penalised complexity priors on precisions (P(σ > 0.5) = 0.01) and on the Besag-York-Mollié 2 mixing parameter (P(φ < 0.5) = 2/3); fixed effects N(0, 0.25)."),
 ("Variance and calibration", f"In the principal model, the variance of the structured district effect was {100*N['vp']['spatial_structured']:.0f}% and that of the characteristics {100*N['vp']['fixed_covariates']:.0f}% of the variance of the linear predictor (the components are correlated, so the shares do not sum to 100%); posterior predictive 95% intervals contained {100*N['ppc']['cov95']:.2f}% of observations and the standard deviation of probability integral transform values was {N['ppc']['pit_sd']:.2f} (0.29 expected under calibration), indicating wide predictive intervals."),
]
for h, t in SM: J.head(h, 2); J.para(t)
META = pd.read_csv(os.path.join(B, "panel_META_SCRN_std3.csv"))
COLM = {"walking": "ext__walking_rate", "mpa": "moderate_pa_rate", "public_fac": "ext__public_sport_fac_per100k", "village_fac": "ext__village_sport_fac_per100k", "smoking": "ext__smoking_rate", "drinking": "ext__high_risk_drinking",
        "obesity": "obesity_rate", "im_spec": "im_specialists_per_100k", "unmet": "ext__unmet_need_rate", "livelihood": "basic_livelihood_rate", "tertiary": "tertiary_educated_share", "alone_elderly": "ext__living_alone_elderly",
        "urban": "urban_population_share", "physicians": "physicians_per_1000", "sex_ratio": "sex_ratio", "fiscal": "fiscal_independence", "pop80": "pop80_share"}
SRC = {"walking": "KCHS, age-standardised", "mpa": "KCHS, age-standardised", "public_fac": "Ministry of Culture, Sports and Tourism", "village_fac": "Ministry of Culture, Sports and Tourism", "smoking": "KCHS, age-standardised",
       "drinking": "KCHS, age-standardised", "obesity": "KCHS, age-standardised (not surveyed 2019)", "im_spec": "HIRA health resources", "unmet": "KCHS", "livelihood": "Ministry of Health and Welfare",
       "tertiary": "Census", "alone_elderly": "Statistics Korea, local indicators", "urban": "Statistics Korea, local indicators", "physicians": "Statistics Korea, local indicators", "sex_ratio": "Resident registration",
       "fiscal": "Ministry of the Interior and Safety", "pop80": "Resident registration"}
rows = []
for g, vs in GROUPS:
    rows.append(["__H__", g])
    for v in vs:
        r = META[META.variable == COLM[v]].iloc[0]; t = N["T1"]["2011-2024"]["cov"][v]
        rows.append([f"  {LABEL[v]}", SRC[v], f"{int(r.obs_year_min)}–{int(r.obs_year_max)}", f"{t[0]:.2f} ({t[1]:.2f})", str(int(r.n_imputed_interp + r.n_imputed_sgg_mean + r.n_imputed_year_mean)), f"{r.vif_final:.1f}"])
TF("Table S1. District characteristics, sources, years, means, imputed district-years and variance inflation factors", ["Characteristic (expected direction)", "Source", "Years", "Mean (SD)", "Imputed district-years", "VIF"], rows, land=True, fs=7,
   foot="KCHS, Korea Community Health Survey; HIRA, Health Insurance Review and Assessment Service; VIF, variance inflation factor. Implausible basic livelihood rates in 2021–2023 in cities with general wards were set to missing and interpolated within districts. Characteristics with VIF above 10 were retained and reported. The general screening uptake covariate of the series was excluded because it is the outcome.")
def spec_table(title, cols, foot):
    rows = []
    for g, vs in GROUPS[:4]:
        rows.append(["__H__", g])
        for v in vs: rows.append([f"  {LABEL[v]}"] + [f3(N[k].get(v)) if isinstance(N.get(k), dict) else "–" for k, _ in cols])
    TF(title, ["Characteristic"] + [h for _, h in cols], rows, land=True, fs=7, foot=foot)
spec_table("Table S2. Odds ratios per 1 SD (95% CrI) under alternative district and space-time structures",
           [("main", "Principal"), ("KH_typeI", "Knorr-Held type I"), ("iid_only", "Independent district effect only"), ("icar_besag", "Intrinsic CAR only"), ("no_spatial", "No district effect"), ("knn4", "4 nearest neighbours")],
           "CAR, conditional autoregressive. Knorr-Held types II–IV, Spatial+ and restricted spatial regression are shown in Table 2 of the manuscript.")
spec_table("Table S3. Odds ratios per 1 SD (95% CrI) under other alternative specifications",
           [("C4_sido_year_iid", "Province-by-year effects"), ("E1_lag1", "Lag 1 year"), ("E2_lag2", "Lag 2 years"), ("sens_s577", "Queen graph (577 pairs)"), ("sens_s2", "Without 80-or-over adjustment"), ("sens_s8", "Expected uptake ignoring sex"), ("E_pop", "Population-based age-sex expected")],
           "Population-based expected attendees: resident population by sex and 16 age groups multiplied by national attendees per resident of each sex and age group, rescaled each year.")
WN = [w for w in N["win"]]
rows = []
for g, vs in GROUPS[:4]:
    rows.append(["__H__", g])
    for v in vs: rows.append([f"  {LABEL[v]}"] + [f3(N["win"][w][v]) for w in WN])
TF("Table S3b. Odds ratios per 1 SD (95% CrI) refitted separately for 2011–2017 and 2018–2024", ["Characteristic"] + [w.split("_")[1].replace("-", "–") for w in WN], rows, port=True, fs=8,
   foot="The published table changed in 2018 and eligibility was extended in 2019; the periods were fixed before modelling.")
PHA = [("P5_excl_2020_2021", "Without 2020–2021"), ("P6_2019_2024_only", "2019–2024 only"), ("P7a_2017_2024_main", "2017–2024"), ("P7b_2017_2024_plus_manufacturing", "2017–2024 + manufacturing share"), ("P1_plus_sensitivity_vars", "+ Medical Aid and general hospitals (post hoc)"), ("P3_plus_popdens", "+ population density (post hoc)")]
rows = []
for g, vs in GROUPS[:4]:
    rows.append(["__H__", g])
    for v in vs: rows.append([f"  {LABEL[v]}"] + [f3(N["ph"].get(f"{a}|{COLM[v]}")) for a, _ in PHA])
rows.append(["__H__", "Additional terms"]); rows.append(["  Manufacturing employment share"] + ["–"] * 3 + [f3(N["ph"]["P7b_2017_2024_plus_manufacturing|manufacturing_share"])] + ["–"] * 2)
rows.append(["  Population density (log)"] + ["–"] * 5 + [f3(N["ph"]["P3_plus_popdens|popdens_log"])])
for v in ("walking", "public_fac", "village_fac", "tertiary", "alone_elderly"):
    pass
TF("Table S4. Prespecified period and workplace analyses and post hoc additions, odds ratios per 1 SD (95% CrI)", ["Characteristic"] + [h for _, h in PHA], rows, land=True, fs=7,
   foot="The first 4 columns were prespecified; manufacturing employment share is available for 2017–2024 only and is missing for Sejong (attendees set to missing). Post hoc analyses were added after the results were seen.")
BWV = [("walking", "ext__walking_rate"), ("mpa", "moderate_pa_rate"), ("public_fac", "ext__public_sport_fac_per100k"), ("village_fac", "ext__village_sport_fac_per100k"), ("tertiary", "tertiary_educated_share"), ("alone_elderly", "ext__living_alone_elderly")]
rows = [[f"  {LABEL[v]}", f3(N["ph"][f"P4_between_within|{c}__B"]), f3(N["ph"][f"P4_between_within|{c}__W"]), f3(N["covid_x"][v])] for v, c in BWV]
TF("Table S5a. Between-district and within-district components (post hoc) and change after 2020", ["Characteristic", "Between districts", "Within districts", "Interaction with 2020–2024"], rows, port=True, fs=8,
   foot="Between: district mean of the characteristic; within: yearly deviation from the district mean; both standardised and fitted together with the other characteristics. Interaction: ratio of the odds ratio in 2020–2024 to that in 2011–2019.")
EB = pd.read_csv(os.path.join(PAN, "SCRN_Ebinom.csv"), encoding="utf-8-sig"); g = EB.groupby("year")
rows = []
for y, d in g:
    rows.append([str(y), f"{d.Ntr.sum():,.0f}", f"{d.cases.sum():,.0f}", f"{100*d.cases.sum()/d.Ntr.sum():.1f}", f"{100*d.scr_남자.sum()/d.elig_남자.sum():.1f}", f"{100*d.scr_여자.sum()/d.elig_여자.sum():.1f}"])
TF("Table S5b. National eligible persons and first-stage attendees by year (sum of districts = national total)", ["Year", "Eligible persons", "Attendees", "Uptake, %", "Men, %", "Women, %"], rows, port=True, fs=8,
   foot="Source: DT_35007_N001 (2011–2017) and DT_35007_N001_1 (2018–2024).")
rs = N["rm_spec"]; LBL = {"principal": "Principal model", "forced_only": "Forced adjustments only", "parsimonious": "Parsimonious", "no_spatial": "No district effect", "iid_district": "Independent district effect only", "icar_district": "Intrinsic CAR only", "typeI_interaction": "Knorr-Held type I"}
rows = [[LBL.get(k, k), f"{v[0]:.3f}", "−0.0044", ("0.001" if v[1] < 0.001 else f"{v[1]:.3f}")] for k, v in rs.items()]
rows += [["__H__", "Negative-control exposures (OR per 1 SD, 95% CrI)"]] + [[f"  {dict(hit_and_run_rate='Hit-and-run accidents', traffic_culture_index='Traffic culture index', fires_per_10000='Fires per 10,000 residents')[k]}", f3(v), "", ""] for k, v in N["nc"].items()]
TF("Table S5c. Residual spatial autocorrelation by specification and negative-control exposures", ["Specification", "Moran's I of mean residual", "Expected I", "2-sided permutation P"], rows, port=True, fs=8,
   foot="Moran's I of district mean Pearson (or observation-level) residuals on the 593-pair contact graph, 999 permutations, 2-sided; I above its expected value indicates remaining positive autocorrelation. The structural suite recomputes residuals, so its principal-model value (0.178) differs slightly from the value in the main text (0.176). 999 permutations give a smallest attainable P of 0.001.")
ps = os.path.join(OUT, "Supplementary_material.docx"); J.doc_title = "Supplementary material"; J.save(ps)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_scrn_esm", "--convert-to", "pdf", "--outdir", OUT, ps], check=True, capture_output=True)
print("saved", os.path.basename(ps))
MH = [x[0] for x in C.METHODS]; RH = [x[0] for x in C.RESULTS]
CK = [("Title and abstract", "1", "Title page; Abstract"), ("Background/rationale", "2", "Introduction"), ("Objectives", "3", "Introduction, final paragraph"),
      ("Study design", "4", f"Methods, {MH[0]}"), ("Setting", "5", f"Methods, {MH[0]}"), ("Participants", "6", f"Methods, {MH[0]} (all eligible persons; ecological)"),
      ("Variables", "7", f"Methods, {MH[1]}; Table S1"), ("Data sources/measurement", "8", "Methods; Supporting Methods"),
      ("Bias", "9", f"Methods, {MH[2]}; Tables S2–S5"), ("Study size", "10", f"Methods, {MH[0]} (all 229 districts)"), ("Quantitative variables", "11", f"Methods, {MH[1]}"),
      ("Statistical methods", "12", f"Methods, {MH[2]}; Supporting Methods"), ("Participants (flow)", "13", "Not applicable (aggregate district data; no exclusions)"),
      ("Descriptive data", "14", f"Results, {RH[0]}; Table 1"), ("Outcome data", "15", f"Results, {RH[0]}; Table 1; Figure 1"),
      ("Main results", "16", f"Results, {RH[1]}; Table 2; Figure 2"), ("Other analyses", "17", f"Results, {RH[1]}; Tables S2–S5"),
      ("Key results", "18", "Discussion, Main findings"), ("Limitations", "19", "Discussion, Strengths and limitations"), ("Interpretation", "20", "Discussion, Interpretation"), ("Generalisability", "21", "Discussion; Conclusions"),
      ("Other information (funding, code)", "22", "Statements and Declarations (Funding; Data availability)")]
K = TX(cite="bracket"); K.para("<b>STROBE checklist</b>"); K.para(f"Manuscript \"{C.TITLE}\"" + (f", {JRN}. Seongdae Kim, Hongik University (kimsd@hongik.ac.kr)" if JRN else ""))
K.table_fit("STROBE checklist for this ecological study", ["Item", "No.", "Where reported"], [[a, b, c] for a, b, c in CK], "", fs_max=9, title_bold=True)
foot_row(K, "STROBE, Strengthening the Reporting of Observational Studies in Epidemiology. Section names refer to the main manuscript and the Supplementary material.", 8, 12)
pk = os.path.join(OUT, "STROBE_checklist.docx"); K.doc_title = "STROBE checklist"; K.save(pk)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_scrn_esm", "--convert-to", "pdf", "--outdir", OUT, pk], check=True, capture_output=True)
print("saved", os.path.basename(pk))

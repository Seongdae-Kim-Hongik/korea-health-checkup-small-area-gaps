# build_manuscript_base_scrn.py — 65호 SCRN 공통 조판(표 1·2, 그림 범례, Vancouver 참고문헌, 선언문 문구).
import os, re, json, subprocess, sys
from docx.shared import Pt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import content_scrn as C
from jkms_engine import JKMS
MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_scrn.json"), encoding="utf-8"))
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "[ZENODO DOI]"
_gf = os.path.join(OUT, "github_url.txt"); GITHUB = open(_gf).read().strip() if os.path.exists(_gf) else "[GITHUB URL]"
ORCID = "0000-0002-1525-0091"
AFFIL = "Department of Biohealth Convergence Open Sharing System, Hongik University, Seoul, Republic of Korea"
ADDRESS = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
PHONE = "+82-2-320-1114"
ETHICS = "The Institutional Review Board of Hongik University approved the study (7002340-202511-HR-012; continuing review 7002340-202611-HR-040) and waived informed consent because only published aggregate statistics were used."
AI_USE = ("The author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript. "
          "The author reviewed and edited all output and takes full responsibility for the content of this publication.")
CREDIT = "Seongdae Kim: conceptualisation, data curation, formal analysis, methodology, software, visualisation, writing – original draft, and writing – review and editing."
CONSENT_P = "Not applicable. Only published aggregate statistics were used, and the Institutional Review Board waived informed consent."
CONSENT_PUB = "Not applicable."
COI = "The author declared no potential conflicts of interest with respect to the research, authorship, and/or publication of this article."
FUNDING = "The author received no financial support for the research, authorship, and/or publication of this article."
def data_statement(): return ("All source data are publicly available aggregate statistics from the National Health Insurance Service, resident registration and the Korea Community Health Survey, accessed through the Korean Statistical Information Service. "
                             f"The analysis code that generates every number, table and figure is openly available on GitHub ({GITHUB}) and archived on Zenodo (https://doi.org/{ZENODO}). The processed district-year data are available from the author on reasonable request.")

class TX(JKMS):
    raw = False
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw: text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text)
        return super()._emit(p, text, sz, bold, italic)
def pandoc_cites(t):   # Vancouver: 위첨자 번호는 구두점 뒤
    t = re.sub(r"\s*\[(@[^\]]+)\]", lambda m: "{{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
    return re.sub(r"(\{\{[^}]+\}\})([.,;:])", r"\2\1", t)
def ref(k):
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. {r['title']}, {r['url']} ({r['year']}, accessed {r['accessed']})."
    au = r["authors"]; a = (au[0] if len(au) == 1 else ", ".join(au[:-1]) + " and " + au[-1]) if len(au) <= 3 else ", ".join(au[:3]) + ", et al"
    t = r["title"].rstrip("."); t = t + ("" if t.endswith(("?", "!")) else ".")
    s = f"{a}. {t} {r['journal']} {r['year']}"
    if r.get("vol"): s += f"; {r['vol']}"
    pg = r.get("pages") or r.get("elocation", "").replace("doi: ", "")
    if pg and not pg.startswith("10."):
        if "-" in pg:   # 축약 쪽수 전체로(405-12 → 405–412)
            a1, b1 = pg.split("-")[:2]
            if b1.isdigit() and a1.isdigit() and len(b1) < len(a1): b1 = a1[:len(a1) - len(b1)] + b1
            pg = f"{a1}–{b1}"
        s += f": {pg}"
    s += "."
    if r.get("doi"): s += f" DOI: {r['doi']}."
    return s
def f3(t): return f"{t[0]:.3f} ({t[1]:.3f}–{t[2]:.3f})"
TAB1 = [("walking", "Walking, %"), ("mpa", "Moderate-or-higher physical activity, %"), ("public_fac", "Public sports facilities, per 100,000"), ("village_fac", "Village sports facilities, per 100,000"),
        ("smoking", "Current smoking, %"), ("drinking", "High-risk drinking, %"), ("obesity", "Obesity (self-reported), %"), ("im_spec", "Internal-medicine specialists, per 100,000"),
        ("unmet", "Unmet healthcare need, %"), ("livelihood", "Basic livelihood recipients, %"), ("tertiary", "Tertiary-educated adults, %"), ("alone_elderly", "Older adults living alone, %"),
        ("urban", "Urban-zone population, %"), ("physicians", "Physicians, per 1000"), ("sex_ratio", "Sex ratio, men per 100 women"), ("fiscal", "Fiscal autonomy, %"), ("pop80", "Aged 80 years or older, %")]
WC = ["2011-2017", "2018-2024", "2011-2024"]; WH = ["2011–2017", "2018–2024", "2011–2024"]
def table1():
    T = N["T1"]
    rows = [["__H__", "Screening"], ["  District-years, No."] + [f"{T[c]['n']:,}" for c in WC], ["  Eligible persons, No."] + [f"{T[c]['elig']:,.0f}" for c in WC],
            ["  First-stage attendees, No. (%)"] + [f"{T[c]['scr']:,.0f} ({100*T[c]['rate']:.1f})" for c in WC],
            ["  District SUR, median (P10–P90)ᵃ"] + [f"{T[c]['sur_med']:.2f} ({T[c]['sur_p10']:.2f}–{T[c]['sur_p90']:.2f})" for c in WC], ["__H__", "District characteristics, mean (SD)"]]
    for v, lab in TAB1:
        mx = max(abs(T[c]['cov'][v][0]) for c in WC); dp = 0 if mx >= 100 else (2 if mx < 5 else 1)
        rows.append([f"  {lab}"] + [f"{T[c]['cov'][v][0]:.{dp}f} ({T[c]['cov'][v][1]:.{dp}f})" for c in WC])
    foot = ("Abbreviations: P10–P90, 10th–90th percentile; SD, standard deviation; SUR, standardised uptake ratio. ᵃObserved over sex-standardised expected attendees summed over the period. "
            "Characteristics are district-year means; the last 5 rows are the forced adjustments.")
    return (f"Table 1. Uptake of the general health check-up and district characteristics, {N['n_districts']} districts, Republic of Korea, 2011–2024", ["Characteristic"] + WH, rows, foot)
GROUPS = [("Physical activity", ["walking", "mpa", "public_fac", "village_fac"]), ("Health behaviours", ["smoking", "drinking", "obesity"]), ("Care access", ["im_spec", "unmet"]),
          ("Household and social", ["livelihood", "tertiary", "alone_elderly"]), ("Forced adjustments", ["urban", "physicians", "sex_ratio", "fiscal", "pop80"])]
LABEL = {"walking": "Walking (+)", "mpa": "Moderate-or-higher physical activity (+)", "public_fac": "Public sports facilities (+)", "village_fac": "Village sports facilities (+)",
         "smoking": "Current smoking (−)", "drinking": "High-risk drinking (−)", "obesity": "Obesity (±)", "im_spec": "Internal-medicine specialists (+)", "unmet": "Unmet healthcare need (−)",
         "livelihood": "Basic livelihood recipients (−)", "tertiary": "Tertiary-educated adults (+)", "alone_elderly": "Older adults living alone (−)",
         "urban": "Urban-zone population", "physicians": "Physicians", "sex_ratio": "Sex ratio", "fiscal": "Fiscal autonomy", "pop80": "Aged 80 years or older"}
def table2():
    rows = []
    for g, vs in GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            mv = N["mv"].get(v)
            rows.append([f"  {LABEL[v]}", f3(N["main"][v]), f"{100*mv[0]:.0f}" if mv else "Forced", f3(N["KH_typeII"][v]), f3(N["KH_typeIII"][v]), f3(N["KH_typeIV"][v]), f3(N["D1_spatial_plus"][v]), f3(N["RSR"][v])])
    foot = ("Values are OR (95% CrI). Abbreviations: CrI, credible interval; OR, odds ratio of uptake per 1 standard deviation; RSR, restricted spatial regression; expected direction in parentheses. Principal model: binomial with an observation-level random effect, a Besag-York-Mollié 2 district effect and random-walk and independent year effects, "
            "offset = logit of sex-standardised expected uptake. Knorr-Held type I gave the same estimates as the principal model to the third decimal (Supplementary Table S2). "
            "Credibility was judged on unrounded limits. ᵃShare of the covariate-subset models containing the characteristic (of 200 models) in which the CrI excluded 1. ᵇKnorr-Held space-time interaction added. ᶜSpatial+ with spatially filtered characteristics. ᵈRestricted spatial regression: district effect constrained to be orthogonal to district means of all characteristics.")
    return (f"Table 2. District characteristics and uptake of the general health check-up, {N['n_districts']} districts, Republic of Korea, 2011–2024",
            ["Characteristic", "Principal model", "Subsets credible, %ᵃ", "Type IIᵇ", "Type IIIᵇ", "Type IVᵇ", "Spatial+ᶜ", "RSRᵈ"], rows, foot)
FIGCAP = {
 1: "Uptake of the first-stage general health check-up, Republic of Korea, 2011–2024. (A) District standardised uptake ratio (observed over sex-standardised expected attendees, 14 years pooled), with Getis-Ord Gi* hot spots (solid outline) and cold spots (dashed outline) of the log ratio at P < 0.05 without correction for multiple testing. (B) Residual district effect from the principal model: exponentiated posterior mean of the combined structured and unstructured district effect, an odds ratio conditional on the district characteristics. (C) National uptake among eligible men and women by year; dotted lines mark the change of the published table and a 10% rise in eligible persons in 2018, the 2019 extension of eligibility to adults aged 20–39 years, and the COVID-19 pandemic from 2020.",
 2: "Odds ratios of uptake per 1 standard deviation (95% credible intervals) for the share of older adults living alone, tertiary-educated adults, walking and public sports facilities across alternative analyses: principal model, Knorr-Held type II and IV space-time interactions, Spatial+, restricted spatial regression, between-district and within-district components, and 2019–2024 only.",
}
def foot_row(J, text, sz=8, ls=12):   # 11/21: 각주는 표 안 병합 행이 아니라 표 바로 아래 문단(3선 마지막 가로줄이 보이도록, 69호 교훈)
    J.para(text, sz=sz, double=False, before=4, after=6)
def put_table(J, t, fs=9):
    J.table_fit(t[0], t[1], t[2], "", fs_max=fs, title_bold=True); foot_row(J, t[3], 8)
def declarations(J, lvl=2):
    for h, t in [("Ethical considerations", ETHICS), ("Consent to participate", CONSENT_P), ("Consent for publication", CONSENT_PUB),
                 ("Declaration of conflicting interests", COI), ("Funding", FUNDING), ("Data availability", data_statement())]:
        J.head(h, lvl); J.para(t)
def build(counts=None):
    J = TX(cite="sup"); c = counts or {}
    J.para(f"<b>{C.TITLE}</b>")
    J.para(f"<b>Running title:</b> {C.RUNNING}", before=6)
    J.para("Seongdae Kim, PhD", before=6); J.para(AFFIL)
    J.para(f"<b>Corresponding author:</b> Seongdae Kim, PhD, {ADDRESS}. Telephone: {PHONE}. Email: kimsd@hongik.ac.kr. ORCID: {ORCID}", before=6)
    J.para(f"<b>Word count:</b> main text, {c.get('main', '[M]')} words; abstract, {c.get('abstract', '[A]')} words; tables, 2; figures, 2; references, {c.get('refs', '[R]')}; supplementary files, 2 (Supplementary material and STROBE checklist).", before=6)
    J.page_break(); J.head("Abstract", 1)
    for h, t in C.ABSTRACT: J.para(f"<b>{h}:</b> {t}")
    J.para(f"<b>Keywords:</b> {C.KEYWORDS}", before=6)
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in C.INTRO: J.para(pandoc_cites(p), indent=True)
    J.head("Methods", 1)
    for x in C.METHODS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(pandoc_cites(p), indent=True)
    J.head("Results", 1)
    for x in C.RESULTS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(pandoc_cites(p), indent=True)
    J.head("Discussion", 1)
    for p in C.DISCUSSION:
        if p.startswith("### "): h = p[4:].strip(); J.head(h, 1 if h == "Conclusions" else 2); continue
        J.para(pandoc_cites(p), indent=True)
    J.counting = False
    J.head("Acknowledgements", 1); J.para("None.")
    J.head("Author contributions", 1); J.para(CREDIT)
    J.head("Use of artificial intelligence", 1); J.para(AI_USE)
    J.head("Statements and Declarations", 1); declarations(J)
    unused = set(REFS) - set(J.cites); assert not unused, unused
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for i, k in enumerate(J.cites, 1): s = f"{i}. " + ref(k); rl.append(s); J.para(s)
    J.raw = False
    J.page_break(); put_table(J, table1())
    J.new_page("landscape"); put_table(J, table2(), fs=8)
    J.new_page("portrait"); J.head("Figure legends", 1)
    for k in sorted(FIGCAP): J.para(f"<b>Figure {k}.</b> {FIGCAP[k]}", after=6)
    return J, rl
def docx_text(path):
    from docx import Document
    d = Document(path); t = [p.text for p in d.paragraphs]
    for tb in d.tables:
        for r in tb.rows:   # 병합 셀만 하나로(같은 값의 다른 셀은 그대로 — 11/19 /333 묶음에서 같은 값 칸이 사라져 보인 오류 교정)
            seen = []; [seen.append(c) for c in r.cells if not any(c._tc is x._tc for x in seen)]; t.append(" | ".join(c.text for c in seen))
    return "\n".join(t)
def main_words(path):
    t = docx_text(path); i = t.find("\nIntroduction\n"); j = t.find("\nAcknowledgements\n"); return len(t[i:j].split())

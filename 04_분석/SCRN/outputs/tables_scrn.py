# tables_scrn.py: writes the cell values of Tables 1 and 2 (no titles or notes) from numbers_scrn.json to table1_values.csv and table2_values.csv.
import os, json, csv
HERE = os.path.dirname(os.path.abspath(__file__)); N = json.load(open(os.path.join(HERE, "numbers_scrn.json")))
def f3(t): return f"{t[0]:.3f} ({t[1]:.3f}–{t[2]:.3f})"
TAB1 = [("walking", "Walking, %"), ("mpa", "Moderate-or-higher physical activity, %"), ("public_fac", "Public sports facilities, per 100,000"), ("village_fac", "Village sports facilities, per 100,000"),
        ("smoking", "Current smoking, %"), ("drinking", "High-risk drinking, %"), ("obesity", "Obesity (self-reported), %"), ("im_spec", "Internal-medicine specialists, per 100,000"),
        ("unmet", "Unmet healthcare need, %"), ("livelihood", "Basic livelihood recipients, %"), ("tertiary", "Tertiary-educated adults, %"), ("alone_elderly", "Older adults living alone, %"),
        ("urban", "Urban-zone population, %"), ("physicians", "Physicians, per 1000"), ("sex_ratio", "Sex ratio, men per 100 women"), ("fiscal", "Fiscal autonomy, %"), ("pop80", "Aged 80 years or older, %")]
WC = ["2011-2017", "2018-2024", "2011-2024"]; WH = ["2011–2017", "2018–2024", "2011–2024"]
GROUPS = [("Physical activity", ["walking", "mpa", "public_fac", "village_fac"]), ("Health behaviours", ["smoking", "drinking", "obesity"]), ("Care access", ["im_spec", "unmet"]),
          ("Household and social", ["livelihood", "tertiary", "alone_elderly"]), ("Forced adjustments", ["urban", "physicians", "sex_ratio", "fiscal", "pop80"])]
LABEL = {"walking": "Walking (+)", "mpa": "Moderate-or-higher physical activity (+)", "public_fac": "Public sports facilities (+)", "village_fac": "Village sports facilities (+)",
         "smoking": "Current smoking (−)", "drinking": "High-risk drinking (−)", "obesity": "Obesity (±)", "im_spec": "Internal-medicine specialists (+)", "unmet": "Unmet healthcare need (−)",
         "livelihood": "Basic livelihood recipients (−)", "tertiary": "Tertiary-educated adults (+)", "alone_elderly": "Older adults living alone (−)",
         "urban": "Urban-zone population", "physicians": "Physicians", "sex_ratio": "Sex ratio", "fiscal": "Fiscal autonomy", "pop80": "Aged 80 years or older"}
def table1():
    T = N["T1"]
    rows = [["Screening"], ["District-years, No."] + [f"{T[c]['n']:,}" for c in WC], ["Eligible persons, No."] + [f"{T[c]['elig']:,.0f}" for c in WC],
            ["First-stage attendees, No. (%)"] + [f"{T[c]['scr']:,.0f} ({100*T[c]['rate']:.1f})" for c in WC],
            ["District SUR, median (P10–P90)"] + [f"{T[c]['sur_med']:.2f} ({T[c]['sur_p10']:.2f}–{T[c]['sur_p90']:.2f})" for c in WC], ["District characteristics, mean (SD)"]]
    for v, lab in TAB1:
        mx = max(abs(T[c]['cov'][v][0]) for c in WC); dp = 0 if mx >= 100 else (2 if mx < 5 else 1)
        rows.append([lab] + [f"{T[c]['cov'][v][0]:.{dp}f} ({T[c]['cov'][v][1]:.{dp}f})" for c in WC])
    return ["Characteristic"] + WH, rows
def table2():
    rows = []
    for g, vs in GROUPS:
        rows.append([g])
        for v in vs:
            mv = N["mv"].get(v)
            rows.append([LABEL[v], f3(N["main"][v]), f"{100*mv[0]:.0f}" if mv else "Forced", f3(N["KH_typeII"][v]), f3(N["KH_typeIII"][v]), f3(N["KH_typeIV"][v]), f3(N["D1_spatial_plus"][v]), f3(N["RSR"][v])])
    return ["Characteristic", "Principal model", "Subsets credible, %", "Knorr-Held type II", "Knorr-Held type III", "Knorr-Held type IV", "Spatial+", "RSR"], rows
for name, (h, rows) in (("table1_values.csv", table1()), ("table2_values.csv", table2())):
    with open(os.path.join(HERE, name), "w", newline="", encoding="utf-8") as fo:
        w = csv.writer(fo); w.writerow(h); w.writerows(rows)
    print("saved", name, len(rows), "rows")

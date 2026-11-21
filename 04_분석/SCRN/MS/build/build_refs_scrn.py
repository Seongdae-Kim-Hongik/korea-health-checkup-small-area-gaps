import json, os, urllib.request, urllib.parse, time
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LP = json.load(open(os.path.join(AN, "LIPS/MS/build/refs_lips.json")))
PM = {"suh2017impact": 28886857, "kang2017current": 28286659, "kim2017first": 28203379, "eom2017effectiveness": 28239481, "kim2023regional": 36697026, "kim2026impact": 41929395,
      "hahm2017why": 27809458, "kang2014factors": 24815483, "lee2026occupational": 42581701, "hart1971inverse": 4100731, "liss2021general": 34100866, "tabuchi2015determinants": 25456306,
      "chiou2014changes": 23981547, "shim2019employment": 31046740, "kim2016impact": 26194373, "ko2016unmet": 27095277, "yamaguchi2018sociodemographic": 29716551,
      "sedani2025social": 39752162, "luu2023socioeconomic": 37752795, "park2022impact": 35760396, "igarashi2019nonparticipation": 31709716}
FROM_LP = ["cheolseong2017data", "inskip1983methods", "kang2015korea", "riebler2016intuitive", "simpson2017penalising", "rue2009approximate", "knorrheld2000bayesian",
           "steegen2016increasing", "dupont2022spatial", "lipsitch2010negative", "bell2015explaining", "morgenstern1995ecologic", "vonelm2007strengthening",
           "besag1991bayesian", "ord1995local", "web:mois2026population", "web:rcore2026"]
R = {}
ids = ",".join(str(v) for v in PM.values())
for k in range(6):
    try: d = json.loads(urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode(dict(db="pubmed", id=ids, retmode="json")), timeout=60).read())["result"]; break
    except Exception: time.sleep(5 + 5 * k)
for k, p in PM.items():
    x = d[str(p)]; doi = next((a["value"] for a in x.get("articleids", []) if a["idtype"] == "doi"), "")
    au = [a["name"] for a in x.get("authors", []) if a.get("authtype") == "Author"]
    R[k] = dict(type="journal", authors=au, title=x["title"].rstrip("."), journal=x["source"], year=int(x["pubdate"][:4]), vol=x.get("volume", ""), issue=x.get("issue", ""),
                pages=x.get("pages", ""), elocation=x.get("elocationid", ""), doi=doi, pmid=str(p), verified="PubMed esummary 2026-11-19")
for k in FROM_LP: R[k] = dict(LP[k]); R[k]["verified"] = "verified earlier reference set"
R["web:mois2026population"]["accessed"] = "November 19, 2026"; R["web:rcore2026"]["accessed"] = "November 19, 2026"
R["web:kosis2026scrn"] = dict(type="web", authors="National Health Insurance Service", title="General health screening statistics: eligible persons and attendees of the first-stage general health screening by district and sex (DT_35007_N001, 2010-2017; DT_35007_N001_1, 2018-2024) and examinees by sex and age (DT_35007_N099). Korean Statistical Information Service", url="https://kosis.kr", year=2026, accessed="November 19, 2026")
R["web:mohw2018youth"] = dict(type="web", authors="Ministry of Health and Welfare", title="Health screening extended to dependants and household members aged 20-39 years from January 2019 (amendment of the health screening implementation standards; in Korean). Newsis, July 19, 2018", url="https://www.newsis.com/view/NISX20180719_0000368123", year=2018, accessed="November 19, 2026")
R["web:mohw2020extension"] = dict(type="web", authors="Ministry of Health and Welfare", title="Health check-ups extended to June next year because of the spread of COVID-19 (in Korean). Korea Policy Briefing, November 29, 2020", url="https://www.korea.kr/news/policyNewsView.do?newsId=148880178", year=2020, accessed="November 19, 2026")
for k, r in R.items():
    if r.get("type") == "journal": assert r.get("doi") or r.get("pmid"), k
json.dump(R, open(os.path.join(HERE, "refs_scrn.json"), "w"), ensure_ascii=False, indent=1)
for k, r in R.items(): print(k, "|", r.get("journal"), r.get("year"), r.get("vol"), r.get("pages") or r.get("elocation"), "|", (r["authors"][:2] if isinstance(r["authors"], list) else r["authors"]), "|", r["title"][:70])
print(len(R))

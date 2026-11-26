#!/usr/bin/env python3

import os, sys, unicodedata, numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
TAG, VER = sys.argv[1], sys.argv[2]; R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fp = f"{R}/04_분석/{TAG}/panel_{TAG}_{VER}.csv"; D = pd.read_csv(fp, encoding="utf-8-sig"); D["fbd_region"] = D.fbd_region.map(NFC)
B = pd.read_csv(f"{R}/02_패널/{TAG}_Ebinom.csv", encoding="utf-8-sig"); B["fbd_region"] = B.fbd_region.map(NFC)
keep = ["Ntr", "pE", "off", "off_age", "off_pop", "off_crude"]
D = D.drop(columns=[c for c in keep + ["off_sens"] if c in D.columns]).merge(B[["year", "fbd_region", "cases"] + keep].rename(columns={"cases": "cases_chk"}), on=["year", "fbd_region"], how="left", validate="one_to_one")
assert D[keep].notna().all().all() and (D.cases == D.cases_chk).all() and (D.Ntr > 0).all() and (D.cases <= D.Ntr).all()
D = D.drop(columns="cases_chk")
if VER == "s8": D["off"] = D.off_age
D["off_sens"] = D.off_pop
D.to_csv(fp, index=False, encoding="utf-8-sig")
r = D.cases / D.Ntr; print(f"[99SC2] {fp}: {len(D)} rows, {D.fbd_region.nunique()} districts, uptake {r.min():.3f}~{r.max():.3f}, off {D.off.min():.3f}~{D.off.max():.3f}, Σcases/ΣNtr {D.cases.sum()/D.Ntr.sum():.4f}")

# Uptake of the national general health check-up across districts of South Korea, 2011-2024

Analysis code for the manuscript

> Kim S. *Persistent small-area gaps in uptake of Korea's organised health check-up among eligible adults.*

Archived version: Zenodo, https://doi.org/10.5281/zenodo.24412681 (v1.0.0).

This code is released under the MIT licence.

## Contents

This repository contains code only. The processed district-year data (analytic panel, expected counts, result tables and boundary file) are not included; they are available from the author on reasonable request. All source statistics are public (see Data sources).

| Path | What it is |
|---|---|
| `01_스크립트/` | Analysis scripts (below) |
| `04_분석/SCRN/` | Covariate pool and model settings (`make_pool_sets_scrn.py`, `sets_SCRN_*.json`, `config_SCRN_std3.json`, SHA-256 hashes of the settings fixed before fitting), the full model chain (`run_std3_chain.sh`) and the district adjacency graph (`graph_593.graph`). Sensitivity versions: queen contiguity graph `s577`, without the share aged 80 or older `s2`, expected uptake ignoring sex `s8` |
| `04_분석/SCRN/MS/build/` | Scripts that read the result tables and write every number, table and figure in the manuscript and supplementary material (`numbers_scrn.py`, `figs_scrn.py`, `content_scrn.py`, `build_manuscript_base_scrn.py`, `build_manuscript_scrn.py`, `esm_scrn.py`, `build_refs_scrn.py`; reference metadata verified against the author's reference library in `refs_zotero_scrn.json`) |

Folder and some column names are in Korean because the source tables are Korean; each script has a header comment describing its inputs and outputs.

## Data sources

All inputs are public, aggregated statistics. No individual-level data are included.

- First-stage general health screening eligible persons and attendees by district and sex: National Health Insurance Service screening statistics, KOSIS tables DT_35007_N001 (2011-2017) and DT_35007_N001_1 (2018-2024); national examinees by sex and age, DT_35007_N099.
- Population by sex and 5-year age group: Ministry of the Interior and Safety, resident registration statistics.
- District characteristics: Korea Community Health Survey (walking, moderate-or-higher physical activity, obesity, high-risk drinking, current smoking, unmet healthcare need), public and village sports facility registers, health-resource statistics (internal medicine specialists), public assistance statistics, census (tertiary education) and KOSIS local indicators (older adults living alone, fixed adjustments and negative controls).

## Pipeline

Set `ST_DATA_ROOT` and `ST_GPT_DATASET` to the local copies of the public source files and the read-only district database, then run from the repository root.

| Step | Script | Output |
|---|---|---|
| 1 | `99SC_build_Ebinom_scrn.py` (uses `38_build_Estd_all.py`, `40_region_crosswalk.py`, `50_build_master_panel.py`) | District eligible persons and attendees (code-based linkage; Sejong from province-level rows), national-total checks, sex-standardised expected uptake and the population-based alternative offset |
| 2 | `99c_extra_canonical_pool_digx.py`, `99c_extra_canonical_pool_lipt.py`, `04_분석/LIPS/make_pool_sets_lips.py`, then `04_분석/SCRN/make_pool_sets_scrn.py` | Covariate pool and model settings |
| 3 | `80_build_disease_panel_v.py SCRN` (`ST_VER=std3`) and `99SC2_attach_binom_scrn.py SCRN std3` | Analytic panel with binomial trials and offsets |
| 4 | `04_분석/SCRN/run_std3_chain.sh` | Likelihood comparison, principal model, covariate-subset models, windows, Knorr-Held interactions, Spatial+, sensitivity suite, posterior predictive checks |
| 5 | `81R_refit_check_scrn.R`, `88S_scrn_posthoc_binom.R`, `88R_rsr_scrn.R` | Refit reproducibility check, prespecified period and workplace analyses and post hoc additions, restricted spatial regression |
| 6 | `04_분석/SCRN/MS/build/*.py` | Numbers, figures, manuscript, supplementary material |

R 4.6.0 with R-INLA 25.10.19 (1 thread), Python 3.9 with pandas, geopandas and python-docx.

## Expected counts and offsets

The binomial offset is the logit of the sex-standardised expected uptake (eligible persons by sex x national uptake by sex and year); no constant is added to expected counts, offsets or denominators, and no district-year has zero eligible persons or attendees. In the population-based sensitivity offset the expected uptake is bounded to 0.02-0.98 so that its logit is defined; the bound applies in 2 of 3,206 district-years (Hanam 2016, ratio 1.02; Sejong 2015, 0.98). The descriptive Moran's I of yearly log ratios uses log((attendees + 0.5)/E); no district-year has zero attendees (minimum 1,978), and recomputing without the 0.5 changed yearly Moran's I by at most 0.0001.

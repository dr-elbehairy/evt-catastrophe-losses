# Heavy Tails in Catastrophe and Large-Fire Losses — replication package

Zenodo DOI: pending (release v1.0.0)

Code, data and results to reproduce every table and figure in

> Elbehairy, M. (2026). *Heavy Tails in Catastrophe and Large-Fire Losses: Threshold Choice, Capital Measures and Lessons for Egypt and Saudi Arabia.* Manuscript, Department of Statistics and Insurance, Faculty of Commerce, Suez Canal University.

## Abstract

Property insurers hold capital against the losses conventional models describe worst, and two emerging-market supervisors now decide how to measure them. The paper fits the peaks-over-threshold model to five observed loss registers (403 U.S. billion-dollar disasters 1980–2024, 2,167 Danish and 9,181 Norwegian fire losses, 144 New Zealand and 206 Australian catastrophes) with thresholds chosen by three automated rules, intervals on every estimate, a compound-Poisson U.S. annual aggregate and a reading of Egypt's fire line. All five tails are Pareto-type (shape 0.53–1.03); no register has a finite variance and the three catastrophe registers cannot exclude an infinite tail mean. A lognormal fitted to all data recovers 20–49 % of the generalized Pareto 99.5 % quantile, but fitted above the same threshold it recovers 71–94 %, so most of the familiar understatement comes from fitting the body; tail value-at-risk exceeds value-at-risk by a factor of 2.3–6.6. The U.S. shape falls from 0.94 at the median threshold to 0.53 at the 90th percentile, and the 1-in-200-year annual aggregate at the 2024 event frequency moves from about USD 4,600 billion to about USD 1,000 billion with it.

## What the package reproduces

| Script | Purpose | Output |
|---|---|---|
| `01_evt_analysis.py` | Core analysis: descriptive statistics, mean-excess and shape-stability grids, Bader–Yan–Zhang ForwardStop threshold (median upward), GPD maximum likelihood with profile-likelihood intervals, bootstrap AD and KS p-values, VaR/TVaR/return levels with 500-replicate bootstrap intervals, Hill estimates, high-threshold refit, normal/lognormal comparators, U.S. Poisson frequency trend, compound-Poisson annual aggregate at three frequencies, reinsurance layers (Tables 1–7, Figures 1–3, 5). | `evt_results.json`, `data/agg_*.npy` |
| `02_reviewer_checks.py` | ForwardStop sensitivity to the grid start (q0.10/0.25/0.50) and FDR level (0.01/0.05/0.10); EQD selector (Murphy, Tawn & Varty 2025); shape-stability selector; U.S. threshold ladder (seven thresholds) with bootstrap interval and Monte-Carlo error for the 1-in-200 aggregate; left-truncated and shifted lognormal comparators (Tables 5, 8, 9, Figure 4). | `results_review.json` |
| `02b_mc_median.py` | Monte-Carlo variability of the median-threshold U.S. aggregate (five seeds). | `results_review.json` |
| `run_all.py` | Runs 01 → 02 → 02b, merges `results_review.json` into `evt_results.json` under `review`, draws the figures. `--merge-only` just merges. | `evt_results.json` |
| `figures.py` | Figures 1–5 (300 dpi PNG). | `figures/` |
| `build_manuscript.py` | Regenerates the manuscript .docx from `evt_results.json` (`--blind`, `--ar-abstract`); writes `wordcount.json`. No number in the paper is typed by hand. | — |
| `common_evt.py` | Data loading and GPD utilities shared by the scripts. | — |

`results/` holds the JSON files the manuscript was built from, so every number can be traced without rerunning anything (≈ 10 minutes on an Apple M1 Pro for the full run; seed 2026 throughout).

## Data

* `data/noaa_clean.csv`, `data/noaa_events.csv` — U.S. billion-dollar weather and climate disasters 1980–2024, CPI-adjusted to 2024 dollars, from NOAA National Centers for Environmental Information (https://www.ncei.noaa.gov/access/billions/), now maintained by Climate Central. Public domain (U.S. Government work).
* `data/danishuni.csv`, `data/norfire.csv`, `data/nzcathist.csv`, `data/auscathist.csv` — Danish fire losses 1980–1990, Norwegian fire losses 1972–1992, New Zealand and Australian catastrophe registers 1967/68–2014, exported from the open **CASdatasets** collection (Dutang & Charpentier, 2020, http://cas.uqam.ca). Redistributed with attribution; the author of this package claims no rights in them.
* `egypt_fire.json` — Egypt's fire line 2014/15–2023/24 transcribed from the Financial Regulatory Authority's Insurance Statistical Books (Tables 1/6 and 2/6) and dated public statements; sources are listed in the manuscript's Table 7 note.

## Environment

```bash
pip install -r requirements.txt
python run_all.py
python build_manuscript.py            # full manuscript
python build_manuscript.py --blind    # blinded version
```

## Citation and licence

Code: MIT (see `LICENSE`). Data: see the attributions above. Please cite the manuscript and, once available, the archived Zenodo release.

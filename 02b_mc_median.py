"""02b_mc_median.py — Monte-Carlo variability of the 1-in-200 U.S. aggregate at the median threshold (five seeds), for Table 9's note."""
import json, numpy as np
from common_evt import *
DATA, noaa = load_data(); x = DATA[list(DATA)[0]]; R = json.load(open(f"{HERE}/results_review.json")); L = R["us_ladder"]
u, xi, beta = L["ladder"]["0.50"]["u"], L["ladder"]["0.50"]["xi"], L["ladder"]["0.50"]["beta"]
mc = [float(np.quantile(sim_annual(np.random.default_rng(s), x, L["lam_2024"], u, xi, beta, 0.50, 40000), .995)) for s in range(5)]
L["mc_p995_auto"] = dict(seeds=mc, sd=float(np.std(mc, ddof=1)), cv=float(np.std(mc, ddof=1) / np.mean(mc)), mean=float(np.mean(mc)))
json.dump(R, open(f"{HERE}/results_review.json", "w"), indent=2, default=float); print("median-threshold MC:", [round(m/1000) for m in mc], "cv", round(L["mc_p995_auto"]["cv"], 3))

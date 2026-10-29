"""figures.py — Figures 1–5 for the v4 manuscript (300 dpi, enlarged type). Reads evt_results.json (with the merged 'review' key)."""
import json, os, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy import stats
from common_evt import load_data, HERE
rcParams["font.family"] = "serif"; rcParams["font.serif"] = ["Times New Roman", "DejaVu Serif"]; rcParams["font.size"] = 11
rcParams["axes.labelsize"] = 11; rcParams["axes.titlesize"] = 11; rcParams["xtick.labelsize"] = 9.5; rcParams["ytick.labelsize"] = 9.5
NAVY, PETROL, GOLD, GREY, RED = "#1C4076", "#007A88", "#B8860B", "#5F6B6D", "#A23B3B"
FIGS = os.path.join(os.path.dirname(HERE), "figures"); os.makedirs(FIGS, exist_ok=True)
R = json.load(open(f"{HERE}/evt_results.json")); D = R["datasets"]; names = list(D); V = R["review"]
short = {n: ("U.S. disasters" if "US" in n else "Danish fire" if "Danish" in n else "Norwegian fire" if "Norwegian" in n else "New Zealand" if "Zealand" in n else "Australia") for n in names}
X, noaa = load_data(); cols = [NAVY, RED, GOLD, PETROL, GREY]

# Fig 1: log-log survival with fitted GPD tails
fig, ax = plt.subplots(figsize=(7.6, 4.4))
for (n, x), c in zip(X.items(), cols):
    x = np.sort(x); s = 1 - np.arange(1, len(x) + 1) / (len(x) + 1); ax.loglog(x / np.median(x), s, ".", ms=3.5, color=c, alpha=.75, label=f"{short[n]} (n = {len(x):,})")
    d = D[n]; u, xi, beta, nu = d["u"], d["xi"], d["beta"], d["nu"]; grid = np.linspace(u, x.max() * 3, 300); surv = (nu / len(x)) * (1 + xi * (grid - u) / beta) ** (-1 / xi)
    ax.loglog(grid / np.median(x), surv, "-", color=c, lw=1.4)
ax.set_xlabel("Loss ÷ median loss (log scale)"); ax.set_ylabel("P(Loss > x) (log scale)"); ax.legend(fontsize=9, frameon=False); ax.set_ylim(1e-4, 1)
plt.tight_layout(); plt.savefig(f"{FIGS}/fig1_tails.png", dpi=300, bbox_inches="tight"); plt.close()

# Fig 2: QQ plots at the automated threshold
fig, axes = plt.subplots(1, 5, figsize=(8.0, 2.5))
for a, (n, x), c in zip(axes, X.items(), cols):
    d = D[n]; y = np.sort(x[x > d["u"]] - d["u"]); q = stats.genpareto.ppf((np.arange(1, len(y) + 1) - .5) / len(y), d["xi"], 0, d["beta"])
    a.loglog(q, y, ".", ms=3.5, color=c); lim = [min(q.min(), y.min()), max(q.max(), y.max())]; a.plot(lim, lim, "k-", lw=.8); a.set_title(short[n], fontsize=9.5); a.set_xlabel("GPD quantile", fontsize=8.5); a.tick_params(labelsize=7.5)
axes[0].set_ylabel("Empirical excess", fontsize=8.5)
plt.tight_layout(); plt.savefig(f"{FIGS}/fig2_qq.png", dpi=300, bbox_inches="tight"); plt.close()

# Fig 3: U.S. frequency and simulated aggregate (high-threshold severity, 2024 rate)
F = R["noaa_freq"]; yrs = np.array(sorted(int(k) for k in F["counts"])); cnt = np.array([F["counts"][str(y)] for y in yrs])
fig, axes = plt.subplots(1, 2, figsize=(7.8, 3.3))
a = axes[0]; a.bar(yrs, cnt, color=NAVY, alpha=.6); a.plot(yrs, np.exp(np.log(F["rate_2024_fit"]) + F["poisson_trend"] * (yrs - 2024)), "-", color=RED, lw=1.8, label=f"Poisson trend {F['trend_pct']:.1f}% per year")
a.set_ylabel("Billion-dollar events per year"); a.legend(fontsize=9, frameon=False); a.set_title("(a) U.S. event frequency, 1980–2024", fontsize=10)
b = axes[1]; agg = np.load(f"{HERE}/data/agg_fitted_rate_2024.npy") / 1000; b.hist(agg, bins=120, range=(0, np.quantile(agg, .995)), density=True, color=PETROL, alpha=.6)
A = R["noaa_aggregate"]["fitted_rate_2024"]; b.axvline(A["p995"] / 1000, color="k", ls="--", lw=1.2, label=f"1-in-200-year aggregate: USD {A['p995']/1000:.0f} bn"); b.axvline(R["noaa_aggregate"]["empirical_annual"]["max"] / 1000, color=RED, ls=":", lw=1.4, label="worst observed year (2017)")
b.set_xlabel("Annual aggregate loss (USD bn, 2024 prices)"); b.set_ylabel("Density"); b.legend(fontsize=8.5, frameon=False); b.set_title("(b) Simulated annual aggregate, 2024 frequency", fontsize=10)
plt.tight_layout(); plt.savefig(f"{FIGS}/fig3_noaa_agg.png", dpi=300, bbox_inches="tight"); plt.close()

# Fig 4: threshold diagnostics for U.S. and Danish: mean excess; shape by threshold with profile band and the three selectors
fig, axes = plt.subplots(2, 2, figsize=(7.8, 5.8))
for j, n in enumerate([names[0], names[1]]):
    d = D[n]; me = np.array(d["mean_excess"]); st = np.array([[s[1], s[3]] for s in d["stability"]]); ci = d["xi_ci"]; S = V["selection"][n]
    a = axes[0, j]; a.plot(me[:, 0], me[:, 1], "o-", color=cols[j], ms=4); a.set_title(f"{short[n]}: mean excess", fontsize=10); a.set_xlabel("Threshold u"); a.set_ylabel("Mean excess e(u)")
    b = axes[1, j]; fits = S["fits"]; qq = sorted(float(k) for k in fits); b.plot([fits[f"{q}"]["u"] for q in qq], [fits[f"{q}"]["xi"] for q in qq], "s-", color=cols[j], ms=3.5, label="ξ̂(u), grid from the 10th percentile")
    b.axhspan(ci[0], ci[1], color=cols[j], alpha=.12, label="95% profile band, ForwardStop fit")
    b.axvline(d["u"], color="k", ls="--", lw=1, label="ForwardStop (median)"); b.axvline(S["eqd_choice"]["u"], color=GOLD, ls="-.", lw=1.3, label="EQD rule")
    if S["stability_choice"]: b.axvline(S["stability_choice"]["u"], color=PETROL, ls=":", lw=1.6, label="stability rule")
    b.axvline(d["hi"]["u"], color=GREY, ls="-", lw=1, alpha=.8, label="high threshold (q0.90)")
    b.set_title(f"{short[n]}: shape by threshold", fontsize=10); b.set_xlabel("Threshold u"); b.set_ylabel("ξ̂")
    if j == 0: b.legend(fontsize=7.5, frameon=False, loc="upper right")
plt.tight_layout(); plt.savefig(f"{FIGS}/fig4_threshold.png", dpi=300, bbox_inches="tight"); plt.close()

# Fig 5: return-level curves (automated vs high threshold) with empirical return periods
fig, axes = plt.subplots(1, 3, figsize=(8.0, 3.0))
for a, n, c in zip(axes, [names[0], names[1], names[3]], [NAVY, RED, PETROL]):
    d = D[n]; x = np.sort(X[n]); nn = len(x); T = nn / (nn + 1 - np.arange(1, nn + 1)); Ts = np.logspace(0.5, 3.3, 100)
    u, xi, beta, nu = d["u"], d["xi"], d["beta"], d["nu"]; rl = u + beta / xi * (((nn / nu) * (1 / Ts)) ** (-xi) - 1)
    a.semilogx(T, x, ".", ms=3.5, color=GREY); a.semilogx(Ts, rl, "-", color=c, lw=1.6, label="ForwardStop threshold")
    hh = d["hi"]; rlh = hh["u"] + hh["beta"] / hh["xi"] * (((nn / hh["nu"]) * (1 / Ts)) ** (-hh["xi"]) - 1); m = Ts >= nn / hh["nu"]; a.semilogx(Ts[m], rlh[m], "--", color=c, lw=1.3, label="high threshold")
    a.axvline(200, color="k", ls=":", lw=.9); a.set_title(short[n], fontsize=10); a.set_xlabel("Return period (events)"); a.set_yscale("log")
axes[0].set_ylabel("Return level (loss units)"); axes[0].legend(fontsize=8, frameon=False, loc="upper left")
plt.tight_layout(); plt.savefig(f"{FIGS}/fig5_returnlevel.png", dpi=300, bbox_inches="tight"); plt.close()
print("figures ok ->", FIGS)

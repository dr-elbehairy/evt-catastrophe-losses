"""
01_evt_analysis.py — core analysis (v4). Peaks-over-threshold / GPD modelling of catastrophe and large-fire losses on five observed datasets:
 NOAA/NCEI U.S. billion-dollar disasters 1980-2024 (403 events, CPI-adjusted USD m), Danish fire losses 1980-1990 (2,167, DKK m),
 Norwegian fire losses 1972-1992 (9,181, NOK k at 2012 prices), New Zealand catastrophe events 1968-2014 (NZD m, normalised 2014),
 Australian catastrophe events 1967-2014 (AUD m, normalised 2014).
Threshold: mean-excess and shape-stability diagnostics plus the Bader-Yan-Zhang (2018) automated rule (ordered Anderson-Darling tests
with ForwardStop). GPD by maximum likelihood; profile-likelihood CIs for xi; bootstrap CIs for VaR/TVaR; Hill estimator; comparison
with normal/lognormal fitted to all data; return levels; for NOAA a compound-Poisson annual aggregate with a Poisson trend in frequency.
"""
import numpy as np, pandas as pd, json, warnings
from scipy import stats, optimize
warnings.filterwarnings("ignore")
rng = np.random.default_rng(2026)
import os; H = os.path.dirname(os.path.abspath(__file__)); DATA_DIR = f"{H}/data"

noaa = pd.read_csv(f"{DATA_DIR}/noaa_clean.csv")
dan = pd.read_csv(f"{DATA_DIR}/danishuni.csv"); nor = pd.read_csv(f"{DATA_DIR}/norfire.csv"); nz = pd.read_csv(f"{DATA_DIR}/nzcathist.csv"); au = pd.read_csv(f"{DATA_DIR}/auscathist.csv")
DATA = {
 "US billion-dollar disasters 1980–2024 (USD m, 2024 prices)": noaa["CPI-Adjusted Cost"].values.astype(float),
 "Danish fire losses 1980–1990 (DKK m)": dan["Loss"].values.astype(float),
 "Norwegian fire losses 1972–1992 (NOK k, 2012 prices)": nor["Loss2012"].values.astype(float),
 "New Zealand catastrophes 1968–2014 (NZD m, 2014 prices)": nz["NormCost2014"].dropna().values.astype(float),
 "Australian catastrophes 1967–2014 (AUD m, 2014 prices)": au["NormCost2014"].dropna().values.astype(float),
}
KEY = {k: k.split(" ")[0] + ("_dis" if "disasters" in k else "_fire" if "fire" in k else "_cat") for k in DATA}

# ---------------------------------------------------------------- GPD tools
def gpd_fit(y):
    """MLE of (xi, beta) for excesses y>0 (loc fixed at 0)."""
    xi, _, beta = stats.genpareto.fit(y, floc=0)
    return float(xi), float(beta)
def gpd_loglik(y, xi, beta):
    return stats.genpareto.logpdf(y, xi, 0, beta).sum()
def profile_ci_xi(y, xi_hat, beta_hat, level=0.95):
    """Profile-likelihood CI for xi."""
    ll_max = gpd_loglik(y, xi_hat, beta_hat); crit = stats.chi2.ppf(level, 1) / 2
    def prof(xi):
        r = optimize.minimize_scalar(lambda b: -gpd_loglik(y, xi, b), bounds=(1e-6, 50 * beta_hat), method="bounded"); return -r.fun
    def f(xi): return prof(xi) - (ll_max - crit)
    lo = optimize.brentq(f, max(xi_hat - 2, -0.99), xi_hat) if f(max(xi_hat - 2, -0.99)) < 0 else max(xi_hat - 2, -0.99)
    hi = optimize.brentq(f, xi_hat, xi_hat + 3) if f(xi_hat + 3) < 0 else xi_hat + 3
    return float(lo), float(hi)
def ad_stat(y, xi, beta):
    """Anderson-Darling statistic for GPD fit of excesses."""
    z = np.sort(stats.genpareto.cdf(y, xi, 0, beta)); n = len(z); i = np.arange(1, n + 1)
    z = np.clip(z, 1e-10, 1 - 1e-10); return float(-n - np.mean((2 * i - 1) * (np.log(z) + np.log(1 - z[::-1]))))
def ad_pvalue(y, xi, beta, B=300):
    """Parametric-bootstrap p-value for the AD statistic."""
    a0 = ad_stat(y, xi, beta); n = len(y); cnt = 0
    for _ in range(B):
        ys = stats.genpareto.rvs(xi, 0, beta, size=n, random_state=rng); xb, bb = gpd_fit(ys); cnt += ad_stat(ys, xb, bb) >= a0
    return float(cnt / B)
def forward_stop(pvals, alpha=0.05):
    """Bader et al. (2018): stopping rule on ordered p-values (thresholds ascending). Returns index of first accepted threshold."""
    p = np.clip(np.array(pvals), 1e-12, 1 - 1e-12); fs = -np.cumsum(np.log(1 - p)) / np.arange(1, len(p) + 1)
    ok = np.where(fs <= alpha)[0]
    return int(ok.max() + 1) if len(ok) and ok.max() + 1 < len(p) else 0   # reject thresholds up to the last k with FS_k<=alpha
def hill(x, k):
    xs = np.sort(x)[::-1]; return float(np.mean(np.log(xs[:k]) - np.log(xs[k])))
def var_tvar(x, u, xi, beta, p):
    n = len(x); nu = (x > u).sum()
    var = u + beta / xi * (((n / nu) * (1 - p)) ** (-xi) - 1) if abs(xi) > 1e-8 else u + beta * np.log((n / nu) / (1 - p))
    tvar = var / (1 - xi) + (beta - xi * u) / (1 - xi) if xi < 1 else np.inf
    return float(var), float(tvar)
def return_level(x, u, xi, beta, T):
    """Loss exceeded once every T events."""
    return var_tvar(x, u, xi, beta, 1 - 1 / T)[0]

res = {"datasets": {}}
QGRID = np.round(np.arange(0.50, 0.96, 0.025), 3)
for name, x in DATA.items():
    x = x[np.isfinite(x) & (x > 0)]; n = len(x); k = KEY[name]; d = {"n": int(n), "mean": float(x.mean()), "median": float(np.median(x)), "sd": float(x.std(ddof=1)),
         "max": float(x.max()), "p90": float(np.quantile(x, .9)), "p99": float(np.quantile(x, .99)), "skew": float(stats.skew(x)), "top10_share": float(np.sort(x)[-10:].sum() / x.sum())}
    # mean excess function and shape stability
    me = []; stab = []
    for q in QGRID:
        u = np.quantile(x, q); y = x[x > u] - u
        if len(y) < 25: continue
        xi, beta = gpd_fit(y); me.append((float(u), float(y.mean()), int(len(y)))); stab.append((float(q), float(u), int(len(y)), xi, beta, float(beta - xi * u)))
    d["mean_excess"] = me; d["stability"] = stab
    # automated threshold (Bader et al. 2018): AD tests on ascending thresholds, ForwardStop at 5%
    cand = [s for s in stab if s[2] >= 40]
    pv = [ad_pvalue(x[x > s[1]] - s[1], s[3], s[4], B=200) for s in cand]
    idx = forward_stop(pv, 0.05); q_auto, u_auto = cand[idx][0], cand[idx][1]
    d["ad_pvalues"] = [(c[0], p) for c, p in zip(cand, pv)]
    # final threshold: automated choice (report also the 90th percentile as a fixed comparator)
    u = u_auto; y = x[x > u] - u; nu = len(y); xi, beta = gpd_fit(y); lo, hi = profile_ci_xi(y, xi, beta)
    d.update(q_u=float(q_auto), u=float(u), nu=int(nu), xi=xi, beta=beta, xi_ci=[lo, hi], ad_p=float(ad_pvalue(y, xi, beta, B=500)))
    ks = stats.kstest(y, lambda t: stats.genpareto.cdf(t, xi, 0, beta)); d["ks_p"] = float(ks.pvalue)
    # parametric-bootstrap KS p-value (parameters re-estimated in each replicate; the asymptotic p-value above is not exact)
    ks0 = ks.statistic; cntk = 0
    for _ in range(300):
        ys = stats.genpareto.rvs(xi, 0, beta, size=nu, random_state=rng); xb_, bb_ = gpd_fit(ys)
        cntk += stats.kstest(ys, lambda t: stats.genpareto.cdf(t, xb_, 0, bb_)).statistic >= ks0
    d["ks_p_boot"] = float(cntk / 300)
    d["hill"] = {str(kk): hill(x, kk) for kk in [int(0.05 * n), int(0.1 * n), nu] if kk >= 10}
    # risk measures with bootstrap CIs
    P = [0.99, 0.995, 0.999]; d["risk"] = {}
    boot = {p: [] for p in P}
    for _ in range(500):
        xb = rng.choice(x, n, replace=True); ub = np.quantile(xb, q_auto); yb = xb[xb > ub] - ub
        if len(yb) < 20: continue
        xib, bb = gpd_fit(yb)
        for p in P: boot[p].append(var_tvar(xb, ub, xib, bb, p))
    for p in P:
        v, t = var_tvar(x, u, xi, beta, p); bv = np.array(boot[p])
        d["risk"][str(p)] = dict(VaR=v, TVaR=t, VaR_ci=[float(np.quantile(bv[:, 0], .025)), float(np.quantile(bv[:, 0], .975))],
                                 TVaR_ci=[float(np.quantile(bv[:, 1][np.isfinite(bv[:, 1])], .025)), float(np.quantile(bv[:, 1][np.isfinite(bv[:, 1])], .975))] if xi < 1 else None,
                                 empirical=float(np.quantile(x, p)))
    d["return_levels"] = {str(T): return_level(x, u, xi, beta, T) for T in [10, 20, 50, 100, 200, 500, 1000]}
    # high-threshold (conservative-fit) comparator: largest grid quantile <= 0.90 with at least 25 exceedances
    cand_hi = [s_ for s_ in stab if s_[2] >= 25 and s_[0] <= 0.9001]; sh = cand_hi[-1]
    uh = sh[1]; yh = x[x > uh] - uh; xih, bh = gpd_fit(yh); loh, hih = profile_ci_xi(yh, xih, bh)
    d["hi"] = dict(q_u=float(sh[0]), u=float(uh), nu=int(len(yh)), xi=xih, beta=bh, xi_ci=[loh, hih], ad_p=float(ad_pvalue(yh, xih, bh, B=300)),
                   risk={str(p): dict(VaR=var_tvar(x, uh, xih, bh, p)[0], TVaR=var_tvar(x, uh, xih, bh, p)[1]) for p in P},
                   return_levels={str(T): return_level(x, uh, xih, bh, T) for T in [10, 20, 50, 100, 200, 500, 1000]})
    # conventional models on all data
    mu, sd = x.mean(), x.std(ddof=1); lmu, lsd = np.log(x).mean(), np.log(x).std(ddof=1)
    d["compare"] = {str(p): dict(normal=float(stats.norm.ppf(p, mu, sd)), lognormal=float(stats.lognorm.ppf(p, lsd, 0, np.exp(lmu))), gpd=d["risk"][str(p)]["VaR"], empirical=float(np.quantile(x, p))) for p in P}
    d["lognormal_TVaR_0995"] = float(np.exp(lmu + lsd ** 2 / 2) * stats.norm.cdf(lsd - stats.norm.ppf(0.995)) / 0.005)
    res["datasets"][name] = d
    print(f"{name[:40]:40s} n={n:5d} u=q{q_auto:.3f} nu={nu:4d} xi={xi:.3f} [{lo:.2f},{hi:.2f}] beta={beta:.1f} AD p={d['ad_p']:.2f} VaR99.5={d['risk']['0.995']['VaR']:.0f} TVaR={d['risk']['0.995']['TVaR']:.0f} emp={d['risk']['0.995']['empirical']:.0f}")

# ---------------------------------------------------------------- NOAA: frequency trend and annual aggregate
cnt = noaa.groupby("year").size().reindex(range(1980, 2025), fill_value=0)
import statsmodels.api as sm
X = sm.add_constant(np.arange(len(cnt)) + 1980 - 1980); pois = sm.GLM(cnt.values, X, family=sm.families.Poisson()).fit()
res["noaa_freq"] = dict(counts={int(k): int(v) for k, v in cnt.items()}, poisson_trend=float(pois.params[1]), trend_pct=float(100 * (np.exp(pois.params[1]) - 1)), p=float(pois.pvalues[1]),
                        mean_1980s=float(cnt.loc[1980:1989].mean()), mean_2015_24=float(cnt.loc[2015:2024].mean()), rate_2024_fit=float(np.exp(pois.params[0] + pois.params[1] * 44)))
ann = noaa.groupby("year")["CPI-Adjusted Cost"].sum().reindex(range(1980, 2025), fill_value=0.0)
res["noaa_annual"] = {int(k): float(v) for k, v in ann.items()}
# compound Poisson simulation: severity = empirical body below u, GPD tail above u; frequency = fitted 2024 rate and 1980-2024 mean
dn = res["datasets"][list(DATA)[0]]; x = DATA[list(DATA)[0]]
FITS = {"auto": (dn["u"], dn["xi"], dn["beta"], dn["q_u"]), "hi": (dn["hi"]["u"], dn["hi"]["xi"], dn["hi"]["beta"], dn["hi"]["q_u"])}
def sim_annual(lam, fit, nsim=100000):
    u, xi, beta, q_u = FITS[fit]; body = x[x <= u]
    N = rng.poisson(lam, nsim); tot = np.zeros(nsim)
    for i in range(nsim):
        if N[i] == 0: continue
        tailflag = rng.random(N[i]) > q_u
        sev = np.where(tailflag, u + stats.genpareto.rvs(xi, 0, beta, size=N[i], random_state=rng), rng.choice(body, N[i]))
        tot[i] = sev.sum()
    return tot
agg = {}
for fit in ["hi", "auto"]:
    for lab, lam in [("mean_rate_1980_2024", float(cnt.mean())), ("mean_rate_2015_2024", float(cnt.loc[2015:2024].mean())), ("fitted_rate_2024", res["noaa_freq"]["rate_2024_fit"])]:
        t = sim_annual(lam, fit, 40000); key = lab if fit == "hi" else lab + "_auto"
        agg[key] = dict(lam=lam, fit=fit, mean=float(t.mean()), p99=float(np.quantile(t, .99)), p995=float(np.quantile(t, .995)), p999=float(np.quantile(t, .999)), tvar995=float(t[t >= np.quantile(t, .995)].mean()))
        np.save(f"{H}/data/agg_{key}.npy", t)
agg["empirical_annual"] = dict(mean=float(ann.mean()), max=float(ann.max()), p95=float(np.quantile(ann, .95)), year_max=int(ann.idxmax()))
res["noaa_aggregate"] = agg
# reinsurance layer expected loss per event: E[min(max(X-a,0),l)] under GPD tail vs empirical
u, xi, beta, q_u = FITS["hi"]
def layer_gpd(a, l, n_sims=400000):
    tail = u + stats.genpareto.rvs(xi, 0, beta, size=n_sims, random_state=rng); ptail = 1 - q_u
    return float(ptail * np.clip(tail - a, 0, l).mean())
def layer_emp(a, l): return float(np.clip(x - a, 0, l).mean())
res["layers"] = {f"{l/1000:.0f}bn xs {a/1000:.0f}bn": dict(gpd=layer_gpd(a, l), empirical=layer_emp(a, l)) for a, l in [(10000, 40000), (50000, 50000), (100000, 100000)]}
json.dump(res, open(f"{H}/evt_results.json", "w"), indent=2, default=float)
print("NOAA freq trend %/yr", round(res["noaa_freq"]["trend_pct"], 2), "p", res["noaa_freq"]["p"]); print(agg); print(res["layers"]); print("saved")

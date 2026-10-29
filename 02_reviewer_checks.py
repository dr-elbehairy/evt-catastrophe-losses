"""
02_reviewer_checks.py — additional analyses for v4 (self-review against the promotion-committee rubric).
 (a) Sensitivity of the Bader–Yan–Zhang ForwardStop selection to the starting quantile of the grid and to the FDR level.
 (b) Two further selectors: the expected-quantile-discrepancy (EQD) rule of Murphy, Tawn & Varty (2025) and a shape-stability rule.
 (c) U.S. threshold ladder: shape, TVaR/VaR and the 1-in-200 annual aggregate at seven thresholds, with a bootstrap interval and
     Monte-Carlo error for the headline aggregate.
 (d) Fairer conventional comparators: left-truncated lognormal fitted above the same threshold, and a shifted lognormal on the excesses.
Writes results_review.json; 03_merge.py folds it into evt_results.json under the key "review".
"""
import json, numpy as np, time
from scipy import stats, optimize
from common_evt import *
import statsmodels.api as sm
rng = np.random.default_rng(2026); t0 = time.time()
DATA, noaa = load_data(); names = list(DATA)
QGRID = np.round(np.arange(0.10, 0.96, 0.025), 3)
R = {"selection": {}, "us_ladder": {}, "comparators": {}}

# ---------------------------------------------------------------- (a)+(b) threshold-selection rules
for name, x in DATA.items():
    n = len(x); fits = {}
    for q in QGRID:
        u = np.quantile(x, q); y = x[x > u] - u
        if len(y) < 25: continue
        xi, beta = gpd_fit(y); fits[q] = dict(u=float(u), nu=int(len(y)), xi=xi, beta=beta)
    cand = [q for q in fits if fits[q]["nu"] >= 40]
    pv = {q: ad_pvalue(x[x > fits[q]["u"]] - fits[q]["u"], fits[q]["xi"], fits[q]["beta"], rng, B=150) for q in cand}
    fs = {}
    for q0 in (0.10, 0.25, 0.50):
        sub = [q for q in cand if q >= q0 - 1e-9]
        for a in (0.01, 0.05, 0.10):
            idx = forward_stop([pv[q] for q in sub], a); fs[f"start{q0:.2f}_alpha{a:.2f}"] = dict(q=float(sub[idx]), nu=fits[sub[idx]]["nu"], xi=fits[sub[idx]]["xi"])
    # EQD (Murphy, Tawn & Varty 2025): mean absolute discrepancy between bootstrap-GPD quantiles and sample quantiles of the excesses
    eqd = {}
    m = 500; probs = (np.arange(1, m + 1)) / (m + 1)
    for q in cand:
        u = fits[q]["u"]; y = x[x > u] - u; qe = np.quantile(y, probs); acc = 0.0; B = 100
        for _ in range(B):
            yb = rng.choice(y, len(y), replace=True); xb, bb = gpd_fit(yb); acc += np.mean(np.abs(stats.genpareto.ppf(probs, xb, 0, bb) - qe))
        eqd[q] = float(acc / B / np.median(y))     # scaled by the median excess so datasets are comparable
    q_eqd = min(eqd, key=eqd.get)
    # stability rule: lowest threshold whose profile interval contains every higher-threshold estimate (>=25 exceedances)
    q_stab = None
    for q in sorted(fits):
        if fits[q]["nu"] < 40: continue
        u = fits[q]["u"]; y = x[x > u] - u; lo, hi = profile_ci_xi(y, fits[q]["xi"], fits[q]["beta"])
        if all(lo <= fits[qq]["xi"] <= hi for qq in fits if qq > q):
            q_stab = q; stab_ci = [lo, hi]; break
    R["selection"][name] = dict(grid_start=0.10, ad_pvalues={str(q): pv[q] for q in cand}, forward_stop=fs,
                                eqd={str(q): eqd[q] for q in cand}, eqd_choice=dict(q=float(q_eqd), **fits[q_eqd]),
                                stability_choice=(dict(q=float(q_stab), ci=stab_ci, **fits[q_stab]) if q_stab is not None else None),
                                fits={str(q): fits[q] for q in fits})
    print(f"{name[:28]:28s} FS(start .50,a.05) q={fs['start0.50_alpha0.05']['q']}  FS(start .10,a.05) q={fs['start0.10_alpha0.05']['q']}  EQD q={q_eqd} xi={fits[q_eqd]['xi']:.2f}  stab q={q_stab}", flush=True)

# ---------------------------------------------------------------- (c) U.S. threshold ladder and aggregate uncertainty
x = DATA[names[0]]; n = len(x)
cnt = noaa.groupby("year").size().reindex(range(1980, 2025), fill_value=0)
X = sm.add_constant(np.arange(45)); pois = sm.GLM(cnt.values, X, family=sm.families.Poisson()).fit()
lam24 = float(np.exp(pois.params[0] + pois.params[1] * 44)); lam_recent = float(cnt.loc[2015:2024].mean()); lam_all = float(cnt.mean())
ladder = {}
for q in (0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90):
    u = np.quantile(x, q); y = x[x > u] - u; xi, beta = gpd_fit(y); lo, hi = profile_ci_xi(y, xi, beta)
    v, t = var_tvar(x, u, xi, beta, 0.995)
    agg24 = sim_annual(rng, x, lam24, u, xi, beta, q, 40000); aggrec = sim_annual(rng, x, lam_recent, u, xi, beta, q, 40000)
    ladder[f"{q:.2f}"] = dict(u=float(u), nu=int(len(y)), xi=xi, xi_ci=[lo, hi], beta=beta, var995=v, tvar995=t, ratio=(t / v if np.isfinite(t) else None),
                              agg_p995_2024=float(np.quantile(agg24, .995)), agg_mean_2024=float(agg24.mean()), agg_p995_recent=float(np.quantile(aggrec, .995)))
    print(f"US q={q:.2f} nu={len(y)} xi={xi:.2f} [{lo:.2f},{hi:.2f}] TVaR/VaR={t/v if np.isfinite(t) else float('nan'):.2f} agg995(2024)={np.quantile(agg24,.995)/1000:.0f}bn", flush=True)
# bootstrap interval for the headline aggregate (q = 0.90): resample the register, refit at the fixed quantile, simulate 10,000 years
boot = []
for b in range(200):
    xb = rng.choice(x, n, replace=True); ub = np.quantile(xb, 0.90); yb = xb[xb > ub] - ub
    if len(yb) < 20: continue
    xib, bb = gpd_fit(yb)
    if xib >= 1.5: xib = 1.5
    boot.append(float(np.quantile(sim_annual(rng, xb, lam24, ub, xib, bb, 0.90, 10000), .995)))
boot = np.array(boot)
mc = [float(np.quantile(sim_annual(np.random.default_rng(s), x, lam24, ladder["0.90"]["u"], ladder["0.90"]["xi"], ladder["0.90"]["beta"], 0.90, 40000), .995)) for s in range(5)]
R["us_ladder"] = dict(lam_2024=lam24, lam_2015_2024=lam_recent, lam_1980_2024=lam_all, ladder=ladder,
                      boot_p995_hi=dict(ci=[float(np.quantile(boot, .025)), float(np.quantile(boot, .975))], median=float(np.median(boot)), n=int(len(boot))),
                      mc_p995_hi=dict(seeds=mc, sd=float(np.std(mc, ddof=1)), cv=float(np.std(mc, ddof=1) / np.mean(mc))))
print("boot CI (bn):", np.quantile(boot, [.025, .975]) / 1000, "MC sd (bn):", np.std(mc, ddof=1) / 1000, flush=True)

# ---------------------------------------------------------------- (d) fairer conventional comparators
def trunc_lognormal_fit(z, u):
    """MLE of a lognormal left-truncated at u, fitted to observations z > u."""
    lz = np.log(z)
    def nll(th):
        m, s = th[0], np.exp(th[1]); return -(stats.norm.logpdf(lz, m, s) - lz - stats.norm.logsf(np.log(u), m, s)).sum()
    r = optimize.minimize(nll, [lz.mean(), np.log(lz.std() + 1e-6)], method="Nelder-Mead"); return r.x[0], float(np.exp(r.x[1]))
for name, x in DATA.items():
    n = len(x); out = {}
    for lab, q in (("auto", 0.50), ("hi", None)):
        if q is None:
            # same high-threshold definition as the core analysis: highest grid quantile <= 0.90 with >= 25 exceedances
            qs = [qq for qq in np.round(np.arange(0.50, 0.96, 0.025), 3) if qq <= 0.9001 and (x > np.quantile(x, qq)).sum() >= 25]; q = qs[-1]
        u = np.quantile(x, q); z = x[x > u]; nu = len(z); y = z - u
        xi, beta = gpd_fit(y)
        m, s = trunc_lognormal_fit(z, u)
        def q_trunc(p):  # P(X > x) = (nu/n) * S(x)/S(u)
            target = (1 - p) * n / nu * stats.norm.sf(np.log(u), m, s); return float(np.exp(stats.norm.isf(target, m, s)))
        lm, ls = np.log(y).mean(), np.log(y).std(ddof=1)
        def q_shift(p): return float(u + np.exp(stats.norm.isf((1 - p) * n / nu, lm, ls)))
        res = {}
        for p in (0.995, 0.999):
            g = var_tvar(x, u, xi, beta, p)[0]; res[str(p)] = dict(gpd=g, trunc_lognormal=q_trunc(p), shifted_lognormal=q_shift(p), empirical=float(np.quantile(x, p)))
        out[lab] = dict(q=float(q), u=float(u), nu=int(nu), xi=xi, lognormal_mu=float(m), lognormal_sigma=float(s), quantiles=res)
    R["comparators"][name] = out
    a = out["auto"]["quantiles"]["0.995"]; print(f"{name[:28]:28s} 99.5%: GPD {a['gpd']:.0f} truncLN {a['trunc_lognormal']:.0f} shiftLN {a['shifted_lognormal']:.0f} emp {a['empirical']:.0f}", flush=True)
R["runtime_seconds"] = time.time() - t0
json.dump(R, open(f"{HERE}/results_review.json", "w"), indent=2, default=float); print("saved results_review.json in", round(R["runtime_seconds"]), "s")

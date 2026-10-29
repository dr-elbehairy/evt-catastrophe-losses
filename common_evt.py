"""Shared tools for the EVT catastrophe-loss paper (v4): data loading and generalized Pareto utilities."""
import os, numpy as np, pandas as pd
from scipy import stats, optimize

HERE = os.path.dirname(os.path.abspath(__file__)); DATA_DIR = f"{HERE}/data"

def load_data():
    noaa = pd.read_csv(f"{DATA_DIR}/noaa_clean.csv"); dan = pd.read_csv(f"{DATA_DIR}/danishuni.csv"); nor = pd.read_csv(f"{DATA_DIR}/norfire.csv")
    nz = pd.read_csv(f"{DATA_DIR}/nzcathist.csv"); au = pd.read_csv(f"{DATA_DIR}/auscathist.csv")
    DATA = {
     "US billion-dollar disasters 1980–2024 (USD m, 2024 prices)": noaa["CPI-Adjusted Cost"].values.astype(float),
     "Danish fire losses 1980–1990 (DKK m)": dan["Loss"].values.astype(float),
     "Norwegian fire losses 1972–1992 (NOK k, 2012 prices)": nor["Loss2012"].values.astype(float),
     "New Zealand catastrophes 1968–2014 (NZD m, 2014 prices)": nz["NormCost2014"].dropna().values.astype(float),
     "Australian catastrophes 1967–2014 (AUD m, 2014 prices)": au["NormCost2014"].dropna().values.astype(float)}
    DATA = {k: v[np.isfinite(v) & (v > 0)] for k, v in DATA.items()}
    return DATA, noaa

def gpd_fit(y):
    xi, _, beta = stats.genpareto.fit(y, floc=0); return float(xi), float(beta)
def gpd_loglik(y, xi, beta): return stats.genpareto.logpdf(y, xi, 0, beta).sum()
def profile_ci_xi(y, xi_hat, beta_hat, level=0.95):
    ll_max = gpd_loglik(y, xi_hat, beta_hat); crit = stats.chi2.ppf(level, 1) / 2
    def prof(xi):
        r = optimize.minimize_scalar(lambda b: -gpd_loglik(y, xi, b), bounds=(1e-6, 50 * beta_hat), method="bounded"); return -r.fun
    def f(xi): return prof(xi) - (ll_max - crit)
    lo = optimize.brentq(f, max(xi_hat - 2, -0.99), xi_hat) if f(max(xi_hat - 2, -0.99)) < 0 else max(xi_hat - 2, -0.99)
    hi = optimize.brentq(f, xi_hat, xi_hat + 3) if f(xi_hat + 3) < 0 else xi_hat + 3
    return float(lo), float(hi)
def ad_stat(y, xi, beta):
    z = np.sort(stats.genpareto.cdf(y, xi, 0, beta)); n = len(z); i = np.arange(1, n + 1)
    z = np.clip(z, 1e-10, 1 - 1e-10); return float(-n - np.mean((2 * i - 1) * (np.log(z) + np.log(1 - z[::-1]))))
def ad_pvalue(y, xi, beta, rng, B=200):
    a0 = ad_stat(y, xi, beta); n = len(y); cnt = 0
    for _ in range(B):
        ys = stats.genpareto.rvs(xi, 0, beta, size=n, random_state=rng); xb, bb = gpd_fit(ys); cnt += ad_stat(ys, xb, bb) >= a0
    return float(cnt / B)
def forward_stop(pvals, alpha=0.05):
    """Bader, Yan & Zhang (2018) ForwardStop on ordered p-values (thresholds ascending): index of the first threshold not rejected."""
    p = np.clip(np.array(pvals), 1e-12, 1 - 1e-12); fs = -np.cumsum(np.log(1 - p)) / np.arange(1, len(p) + 1)
    ok = np.where(fs <= alpha)[0]
    return int(ok.max() + 1) if len(ok) and ok.max() + 1 < len(p) else 0
def var_tvar(x, u, xi, beta, p):
    n = len(x); nu = (x > u).sum()
    var = u + beta / xi * (((n / nu) * (1 - p)) ** (-xi) - 1) if abs(xi) > 1e-8 else u + beta * np.log((n / nu) / (1 - p))
    tvar = var / (1 - xi) + (beta - xi * u) / (1 - xi) if xi < 1 else np.inf
    return float(var), float(tvar)
def sim_annual(rng, x, lam, u, xi, beta, q_u, nsim):
    """Vectorised compound-Poisson annual aggregate: empirical severity below u, GPD above u."""
    body = x[x <= u]; N = rng.poisson(lam, nsim); tot = int(N.sum())
    flag = rng.random(tot) > q_u
    sev = np.where(flag, u + stats.genpareto.rvs(xi, 0, beta, size=tot, random_state=rng), rng.choice(body, tot))
    return np.bincount(np.repeat(np.arange(nsim), N), weights=sev, minlength=nsim)

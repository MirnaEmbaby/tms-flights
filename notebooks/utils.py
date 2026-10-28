"""Small shared helpers for the TMS flights project (decision D15).

Everything here is plain and short so each notebook stays readable.
"""
from pathlib import Path
import random

import numpy as np
import pandas as pd

SEED = 42
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

TRAIN_MONTHS = list(range(1, 10))    # Jan-Sep: training part
VAL_MONTHS = [7, 8, 9]               # Jul-Sep: validation (models trained on Jan-Jun)
TEST_MONTHS = [10, 11, 12]           # Oct-Dec: test part, used once


def set_seed(seed: int = SEED) -> None:
    """Fix every random generator so the numbers are the same on every run."""
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
    except ImportError:
        pass


def profile(df: pd.DataFrame) -> pd.DataFrame:
    """One line per column: type, missing, distinct values, smallest and largest value."""
    rows = []
    for c in df.columns:
        s = df[c]
        try:
            lo, hi = s.min(), s.max()
        except TypeError:
            lo = hi = None
        rows.append({
            "column": c, "type": str(s.dtype), "missing": int(s.isna().sum()),
            "distinct": int(s.nunique()), "min": lo, "max": hi,
        })
    return pd.DataFrame(rows).set_index("column")


# ---------------------------------------------------------------------------
# Statistics helpers used from Task 2 on
# ---------------------------------------------------------------------------
def day_table(df, group, y="late", day="date"):
    """Per-day sums and counts for every group value (the building block of the day bootstrap)."""
    g = df.groupby([day, group], observed=True)[y].agg(["sum", "count"]).reset_index()
    s = g.pivot(index=day, columns=group, values="sum").fillna(0.0)
    c = g.pivot(index=day, columns=group, values="count").fillna(0.0)
    return s, c


def day_bootstrap_rate(df, group, y="late", day="date", n_boot=1000, seed=SEED):
    """Rate of `y` per group with a 95% interval. Flights on the same day are not independent
    (a storm hits all of them), so whole DAYS are resampled, not single flights."""
    s, c = day_table(df, group, y, day)
    S, C = s.values, c.values
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(S), len(S))
        cs = C[idx].sum(0)
        boots.append(np.where(cs > 0, S[idx].sum(0) / np.where(cs > 0, cs, 1), np.nan))
    lo, hi = np.nanpercentile(np.array(boots), [2.5, 97.5], axis=0)
    return pd.DataFrame({"flights": C.sum(0).astype(int), "rate": S.sum(0) / C.sum(0), "low": lo, "high": hi}, index=s.columns)


def day_bootstrap(per_day, stat, n_boot=1000, seed=SEED):
    """Generic day bootstrap. per_day = one row per day with ADDITIVE columns;
    stat = function(Series of column totals) -> number. Returns (estimate, low, high)."""
    X, cols = per_day.values.astype(float), list(per_day.columns)
    rng = np.random.default_rng(seed)
    est = stat(pd.Series(X.sum(0), index=cols))
    vals = [stat(pd.Series(X[rng.integers(0, len(X), len(X))].sum(0), index=cols)) for _ in range(n_boot)]
    lo, hi = np.nanpercentile(vals, [2.5, 97.5])
    return float(est), float(lo), float(hi)


def chi2_effect(table):
    """Chi-square test on a contingency table, plus Cramer's V (effect size, 0 = none, 1 = perfect)."""
    from scipy import stats
    chi2, p, dof, _ = stats.chi2_contingency(table)
    n = np.asarray(table).sum()
    v = float(np.sqrt(chi2 / (n * (min(np.asarray(table).shape) - 1))))
    return {"chi2": float(chi2), "dof": int(dof), "p": float(p), "cramers_v": v}


def oof_target_stat(df, key, y, fit_mask, k=20):
    """Smoothed mean of target `y` for each value of `key`, without leaking a row's own label (decision T9).

    Rows inside `fit_mask` (the training rows): leave-one-month-out. The value of a row is computed from
    the training rows of all OTHER months, so its own label (and its own month) is never used.
    Rows outside `fit_mask` (test, or validation when tuning): computed from all training rows.
    Smoothing: (sum + k * global_rate) / (count + k); an unseen key gets the global rate.
    """
    fit_mask = np.asarray(fit_mask)
    fit = df.loc[fit_mask, [key, "month", y]].copy()
    fit[y] = fit[y].astype(float)
    out = pd.Series(np.nan, index=df.index)
    # outside the training rows: all training rows
    g = fit.groupby(key)[y].agg(["sum", "count"])
    glob = fit[y].mean()
    stat = (g["sum"] + k * glob) / (g["count"] + k)
    out[~fit_mask] = df.loc[~fit_mask, key].map(stat).fillna(glob).to_numpy()
    # inside: leave one month out
    tot_s, tot_n = fit[y].sum(), len(fit)
    mon_s = fit.groupby("month")[y].transform("sum"); mon_n = fit.groupby("month")[y].transform("size")
    glob_ex = (tot_s - mon_s) / (tot_n - mon_n)
    km_s = fit.groupby([key, "month"])[y].transform("sum"); km_n = fit.groupby([key, "month"])[y].transform("size")
    k_s = fit.groupby(key)[y].transform("sum"); k_n = fit.groupby(key)[y].transform("size")
    out[fit_mask] = (((k_s - km_s) + k * glob_ex) / ((k_n - km_n) + k)).to_numpy()
    return out


# ---------------------------------------------------------------------------------------------
# Task 6 helpers: PR-AUC with day-clustered bootstrap, threshold metrics, top-k table
# ---------------------------------------------------------------------------------------------
def sort_for_ap(score):
    """Order flights by score (high first) and mark the last flight of each distinct score (ties are one threshold)."""
    score = np.asarray(score, dtype=float)
    order = np.argsort(-score, kind="stable")
    s = score[order]
    ends = np.r_[np.nonzero(np.diff(s))[0], len(s) - 1]
    return order, ends


def ap_weighted(y, w, order, ends):
    """Average precision (the same definition as scikit-learn) where flight i counts w[i] times."""
    y = np.asarray(y, dtype=float)[order]; w = np.asarray(w, dtype=float)[order]
    tp = np.cumsum(w * y)[ends]; fp = np.cumsum(w * (1 - y))[ends]
    if tp[-1] == 0:
        return np.nan
    precision = np.divide(tp, tp + fp, out=np.zeros_like(tp), where=(tp + fp) > 0); recall = tp / tp[-1]     # 0/0 (nothing drawn yet) counts as 0
    return float(np.sum(np.diff(np.r_[0.0, recall]) * precision))


def day_bootstrap_ap(y, scores, day, n_boot=1000, seed=SEED):
    """95% interval of PR-AUC for several score columns at once.

    Whole DAYS are resampled (flights of one day share weather and airport problems, so they are not independent).
    scores: dict name -> array of scores. Returns (table with estimate, low, high; array of all bootstrap draws per name).
    """
    y = np.asarray(y)
    day_codes, uniq = pd.factorize(np.asarray(day))
    n_days = len(uniq)
    srt = {k: sort_for_ap(v) for k, v in scores.items()}
    rng = np.random.default_rng(seed)
    draws = {k: np.empty(n_boot) for k in scores}
    for b in range(n_boot):
        counts = np.bincount(rng.integers(0, n_days, n_days), minlength=n_days)
        w = counts[day_codes]
        for k, (order, ends) in srt.items():
            draws[k][b] = ap_weighted(y, w, order, ends)
    ones = np.ones(len(y))
    rows = {k: dict(pr_auc=ap_weighted(y, ones, *srt[k]), low=np.nanpercentile(draws[k], 2.5), high=np.nanpercentile(draws[k], 97.5))
            for k in scores}
    return pd.DataFrame(rows).T, draws


def best_f1_threshold(y, score):
    """The score cut-off with the highest F1 (computed on validation, then applied unchanged to the test part)."""
    from sklearn.metrics import precision_recall_curve
    p, r, t = precision_recall_curve(y, score)
    f1 = 2 * p[:-1] * r[:-1] / np.maximum(p[:-1] + r[:-1], 1e-12)
    return float(t[int(np.nanargmax(f1))])


def at_threshold(y, score, thr):
    """Confusion matrix and precision, recall, F1 for the rule 'flag the flight if score >= thr'."""
    y = np.asarray(y).astype(bool); flag = np.asarray(score) >= thr
    tp = int((flag & y).sum()); fp = int((flag & ~y).sum()); fn = int((~flag & y).sum()); tn = int((~flag & ~y).sum())
    prec = tp / (tp + fp) if tp + fp else np.nan; rec = tp / (tp + fn) if tp + fn else np.nan
    f1 = 2 * prec * rec / (prec + rec) if tp else 0.0
    return dict(threshold=thr, flagged_share=flag.mean(), tp=tp, fp=fp, fn=fn, tn=tn, precision=prec, recall=rec, f1=f1)


def topk_table(y, score, shares=(0.01, 0.02, 0.05, 0.10, 0.20)):
    """Flag the top x% of flights by score: recall, precision and lift (recall divided by the share flagged = vs random)."""
    y = np.asarray(y).astype(bool); order = np.argsort(-np.asarray(score), kind="stable")
    ys = y[order]; rows = []
    for s in shares:
        k = int(round(s * len(y))); tp = int(ys[:k].sum())
        rows.append(dict(top_share=s, flagged=k, precision=tp / k, recall=tp / y.sum(), lift=(tp / y.sum()) / s))
    return pd.DataFrame(rows).set_index("top_share")

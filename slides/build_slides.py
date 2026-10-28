"""Builds slides/tms_final.pdf (12 slides) and slides/speaker_notes.md.

Charts are drawn from the files that the notebooks save in data/processed/ (run notebooks 01-07 first).
Numbers that come from a notebook's printed output and not from a saved file are written below in the
dict NB and carry the notebook number; README.md has the ledger "slide | number | notebook | cell title".

Needs: pandas, numpy, matplotlib (requirements.txt) and playwright with chromium (only for the PDF step).
Run from the repo root:  python slides/build_slides.py
"""
import base64
import io
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SEED = 42
np.random.seed(SEED)
ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
OUT = ROOT / "slides"

NAVY, BLUE, ORANGE, GREY, RED, GREEN = "#1f3a5f", "#2f6fb0", "#e07b39", "#8a94a0", "#c0392b", "#2e8b57"
plt.rcParams.update({"font.size": 13, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 14, "axes.titleweight": "bold", "axes.edgecolor": "#555",
                     "figure.dpi": 150})


def fig_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150, facecolor="white")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def img(fig, cls=""):
    return f'<img class="{cls}" src="data:image/png;base64,{fig_b64(fig)}"/>'


# --------------------------------------------------------------------------- data
fl = pd.read_parquet(PROC / "flights_clean.parquet")
we = pd.read_parquet(PROC / "weather_clean.parquet")
met = pd.read_parquet(PROC / "metrics_monthly.parquet")
grp = pd.read_parquet(PROC / "groups_airport.parquet")
p1 = pd.read_parquet(PROC / "pred1_test.parquet")
p2 = pd.read_parquet(PROC / "pred2_test.parquet")

assert len(fl) == 435_352
fl["date"] = fl.sched_dt.dt.tz_localize(None).dt.normalize() if fl.sched_dt.dt.tz is not None else fl.sched_dt.dt.normalize()
tr = fl[fl.month <= 9].copy()                       # training months only (Jan-Sep)
assert len(tr) == 330_883

# bad days: at least 45% of the day's flights late or cancelled (notebook 02, finding 2)
daily = tr.groupby("date").late.mean()
bad = daily >= 0.45
tr["bad_day"] = tr.date.map(bad)
assert int(bad.sum()) == 27 and len(daily) == 273
share_flights = tr.bad_day.mean() * 100
share_late = tr[tr.bad_day].late.sum() / tr.late.sum() * 100
share_canc = tr[tr.bad_day].cancelled.sum() / tr.cancelled.sum() * 100
assert abs(share_flights - 9.8) < 0.05 and abs(share_late - 21.9) < 0.05 and abs(share_canc - 57.5) < 0.05

# numbers printed by notebooks (source tag in the ledger of README.md)
NB = {
    "res1": pd.DataFrame({
        "model": ["Dumb answer", "Hour only", "Logistic reg.", "Gradient boosting", "Random forest", "Neural network"],
        "pr": [0.1406, 0.1836, 0.3238, 0.3466, 0.3407, 0.3388],
        "lo": [0.1289, 0.1653, 0.2876, 0.3099, 0.3054, 0.3011],
        "hi": [0.1521, 0.2012, 0.3575, 0.3807, 0.3759, 0.3757]}),
    "res2": pd.DataFrame({
        "model": ["Dumb answer", "Hour only", "Logistic reg.", "Gradient boosting", "Random forest"],
        "pr": [0.0021, 0.0020, 0.1197, 0.0539, 0.0427],
        "lo": [0.0008, 0.0009, 0.0016, 0.0020, 0.0019],
        "hi": [0.0045, 0.0041, 0.2332, 0.1188, 0.1069]}),
}

# --------------------------------------------------------------------------- charts


def chart_hour():
    t = tr.groupby("hour").late.agg(["mean", "size"])
    fig, ax = plt.subplots(figsize=(6.6, 4.3))
    ax.bar(t.index, 100 * t["mean"], color=BLUE)
    ax.set_xticks(t.index)
    ax.set_xticklabels([f"{h}\n{n/1000:.0f}k" for h, n in zip(t.index, t["size"])], fontsize=8)
    ax.set_xlabel("scheduled hour (flights in thousands under each bar)", fontsize=10)
    ax.set_ylabel("flights late or cancelled (%)", fontsize=10)
    ax.set_title("Later flights are late more often", fontsize=12)
    return img(fig)


def chart_badday():
    vals = [share_flights, share_late, share_canc]
    fig, ax = plt.subplots(figsize=(6.0, 4.3))
    b = ax.bar(["all flights", "late or\ncancelled flights", "cancelled\nflights"], vals, color=[GREY, BLUE, ORANGE])
    for r, v in zip(b, vals):
        ax.text(r.get_x() + r.get_width() / 2, v + 1, f"{v:.1f}%", ha="center", fontsize=11)
    ax.set_ylim(0, 70)
    ax.set_ylabel("share on the 27 worst days (%)", fontsize=10)
    ax.set_title("27 of 273 days carry most cancellations", fontsize=12)
    return img(fig)


def chart_weather():
    w = tr.merge(we[["origin", "time_hour_utc", "precip"]], on=["origin", "time_hour_utc"], how="inner")
    w = w[w.precip.notna()]
    w["rain"] = w.precip > 0
    t = w.groupby("rain").late.agg(["mean", "size"])
    assert abs(100 * (t.loc[True, "mean"] - t.loc[False, "mean"]) - 14.5) < 0.1
    fig, ax = plt.subplots(figsize=(5.4, 4.3))
    vals = [100 * t.loc[False, "mean"], 100 * t.loc[True, "mean"]]
    ns = [t.loc[False, "size"], t.loc[True, "size"]]
    b = ax.bar([f"no rain or snow\n({ns[0]:,} flights)", f"rain or snow\n({ns[1]:,} flights)"], vals, color=[GREY, BLUE])
    for r, v in zip(b, vals):
        ax.text(r.get_x() + r.get_width() / 2, v + 1, f"{v:.1f}%", ha="center", fontsize=11)
    ax.set_ylim(0, 50)
    ax.set_ylabel("flights late or cancelled (%)", fontsize=10)
    ax.set_title("Rain or snow: +14.5 points", fontsize=12)
    ax.tick_params(axis="x", labelsize=9)
    return img(fig)


def chart_airlines():
    cars = ["YX", "9E", "UA", "WN", "NK", "B6", "AA", "DL"]
    g = tr[tr.carrier.isin(cars)].groupby(["carrier", "bad_day"]).cancelled.mean().unstack() * 100
    g = g.loc[cars]
    assert abs(g.loc["YX", True] - 29.43) < 0.05 and abs(g.loc["DL", True] - 8.60) < 0.05
    x = np.arange(len(cars))
    fig, ax = plt.subplots(figsize=(6.6, 3.7))
    ax.bar(x - 0.2, g[False], 0.4, color=GREY, label="ordinary days")
    ax.bar(x + 0.2, g[True], 0.4, color=ORANGE, label="the 27 bad days")
    ax.set_xticks(x)
    ax.set_xticklabels(cars)
    ax.set_ylabel("flights cancelled (%)", fontsize=10)
    ax.set_title("Airlines differ on bad days, not on ordinary days", fontsize=12)
    ax.legend(fontsize=9, frameon=False)
    return img(fig)


def chart_weekday():
    names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    tr["dow"] = tr.date.dt.dayofweek
    a = tr.groupby("dow").cancelled.mean() * 100
    b = tr[~tr.bad_day].groupby("dow").cancelled.mean() * 100
    assert abs(a[3] - 1.51) < 0.01 and abs(a[6] - 4.73) < 0.01
    x = np.arange(7)
    fig, ax = plt.subplots(figsize=(6.0, 3.7))
    ax.bar(x - 0.2, a, 0.4, color=BLUE, label="all days")
    ax.bar(x + 0.2, b, 0.4, color=GREY, label="without the 27 bad days")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("flights cancelled (%)", fontsize=10)
    ax.set_title("The weekday gap disappears", fontsize=12)
    ax.legend(fontsize=9, frameon=False)
    return img(fig)


def chart_monthly():
    m = met.sort_values("month")
    cols = list(m.columns)
    c1 = [c for c in cols if c.startswith("M1")][0]
    c3 = [c for c in cols if c.startswith("M3")][0]
    c5 = [c for c in cols if c.startswith("M5")][0]
    mn = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    fig, ax = plt.subplots(1, 2, figsize=(9.6, 4.2), gridspec_kw={"width_ratios": [1.5, 1]})
    ax[0].plot(mn, m[c1], marker="o", color=BLUE, label="M1 on-time (departed flights)")
    ax[0].plot(mn, m[c5], marker="s", color=ORANGE, label="M5 late or cancelled (all flights)")
    ax[0].set_ylabel("% of flights", fontsize=10)
    ax[0].set_title("On-time and late-or-cancelled, by month", fontsize=11)
    ax[0].legend(fontsize=8, frameon=False, loc="center right")
    ax[0].tick_params(axis="x", labelsize=8)
    ax[1].bar(mn, m[c3], color=RED)
    ax[1].set_title("M3 cancelled (% of flights)", fontsize=11)
    ax[1].tick_params(axis="x", labelsize=7, rotation=90)
    assert abs(m[c5].iloc[6] - 39.07) < 0.01 and abs(m[c3].iloc[6] - 8.68) < 0.01
    return img(fig)


def chart_ablation():
    fig, ax = plt.subplots(1, 2, figsize=(9.6, 4.3))
    lab = ["all features", "no plane", "no previous\nflight", "no airport\nstate"]
    ax[0].bar(lab, [0.621, 0.618, 0.606, 0.518], color=[BLUE, GREY, GREY, RED])
    ax[0].axhline(0.2912, color="k", ls="--", lw=1)
    ax[0].text(3.45, 0.30, "dumb answer 0.291", ha="right", fontsize=8)
    ax[0].set_ylim(0, 0.75)
    ax[0].set_title("Late or cancelled: validation PR-AUC", fontsize=11)
    ax[0].tick_params(axis="x", labelsize=8)
    lab2 = ["all\nfeatures", "D10 fill\n(no plane)", "no airport\nstate", "plane data\nmissing = leak"]
    ax[1].bar(lab2, [0.263, 0.251, 0.159, 0.458], color=[BLUE, GREY, RED, ORANGE])
    ax[1].axhline(0.0512, color="k", ls="--", lw=1)
    ax[1].text(3.45, 0.065, "dumb answer 0.051", ha="right", fontsize=8)
    ax[1].set_ylim(0, 0.55)
    ax[1].set_title("Cancelled: validation PR-AUC", fontsize=11)
    ax[1].tick_params(axis="x", labelsize=8)
    return img(fig)


def chart_results():
    fig, ax = plt.subplots(1, 2, figsize=(11.2, 3.3), gridspec_kw={"width_ratios": [1.1, 1], "wspace": 0.55})
    for a, key, ttl, col in [(ax[0], "res1", "Late or cancelled: test PR-AUC", BLUE), (ax[1], "res2", "Cancelled: test PR-AUC", ORANGE)]:
        r = NB[key]
        y = np.arange(len(r))[::-1]
        colors = [GREY if i < 2 else col for i in range(len(r))]
        a.barh(y, r.pr, color=colors)
        a.errorbar(r.pr, y, xerr=[r.pr - r.lo, r.hi - r.pr], fmt="none", ecolor="k", capsize=3, lw=1)
        a.set_yticks(y)
        a.set_yticklabels(r.model, fontsize=9)
        a.axvline(r.pr[0], color="k", ls="--", lw=1)
        a.set_title(ttl, fontsize=11)
        a.set_xlabel("PR-AUC with 95% interval (dashed = dumb answer)", fontsize=8)
        for yi, v, h in zip(y, r.pr, r.hi):
            a.text(h + 0.004 * (1 if key == "res1" else 0.5), yi - 0.12, f"{v:.3f}" if key == "res1" else f"{v:.4f}", fontsize=8)
    return img(fig)


C = {k: v() for k, v in dict(hour=chart_hour, badday=chart_badday, weather=chart_weather, airlines=chart_airlines,
                              weekday=chart_weekday, monthly=chart_monthly, ablation=chart_ablation,
                              results=chart_results).items()}

# --------------------------------------------------------------------------- slides (HTML)
CSS = """
@page { size: 1280px 720px; margin: 0 }
* { box-sizing: border-box }
body { margin: 0; font-family: 'Helvetica Neue', Arial, 'DejaVu Sans', sans-serif; color: #1c2430 }
.slide { width: 1280px; height: 720px; padding: 38px 56px 30px; page-break-after: always; position: relative; background: #fff; overflow: hidden }
h1 { font-size: 31px; line-height: 1.2; margin: 0 0 18px; color: #1f3a5f; font-weight: 700; max-width: 1160px }
.num { position: absolute; right: 34px; bottom: 16px; font-size: 13px; color: #8a94a0 }
.foot { position: absolute; left: 56px; bottom: 16px; font-size: 12px; color: #8a94a0 }
.tag { font-size: 11px; color: #8a94a0; font-weight: 400; vertical-align: super; margin-left: 2px; white-space: nowrap }
.cols { display: flex; gap: 26px } .col { flex: 1 }
ul { margin: 6px 0 0 0; padding-left: 22px } li { margin: 8px 0; font-size: 22px; line-height: 1.32 }
p { font-size: 22px; line-height: 1.35; margin: 6px 0 }
.small, .small li { font-size: 18px } .tiny { font-size: 15px; color: #555 }
.box { background: #f1f5fa; border-left: 5px solid #2f6fb0; padding: 10px 16px; margin: 10px 0; border-radius: 4px }
.warn { background: #fdf3ea; border-left-color: #e07b39 }
img { max-width: 100%; display: block } img.w { width: 100% }
.big { font-size: 44px; font-weight: 700; color: #1f3a5f; line-height: 1 } .lab { font-size: 14px; color: #555 }
table { border-collapse: collapse; width: 100%; font-size: 18px } th { background: #1f3a5f; color: #fff; text-align: left; padding: 6px 8px; font-weight: 600 }
td { padding: 6px 8px; border-bottom: 1px solid #d5dbe3; vertical-align: top } td.n, th.n { text-align: right }
.kpis { display: flex; gap: 14px; margin: 8px 0 } .kpi { flex: 1; background: #f1f5fa; padding: 10px 12px; border-radius: 6px; text-align: left }
.kpi .big { font-size: 40px } .kpi .lab { font-size: 15px } .kpi.o { background: #fdf3ea } .kpi.o .big { color: #b85a1d }
.timeline { display: flex; height: 54px; margin: 10px 0 4px; font-size: 15px; color: #fff; font-weight: 600 }
.timeline div { display: flex; align-items: center; justify-content: center; text-align: center }
.card { font-size: 18px } .card li { font-size: 18px; margin: 5px 0; line-height: 1.3 }
"""


ZOOM = {5: 1.2, 6: 1.1, 8: 1.15, 10: 1.22, 12: 1.2}


def slide(n, title, body, foot=""):
    z = ZOOM.get(n, 1)
    body = f'<div style="zoom:{z}">{body}</div>' if z != 1 else body
    return f'<section class="slide"><h1>{title}</h1>{body}<div class="foot">{foot}</div><div class="num">{n} / 12</div></section>'


def t(x):
    return f'<span class="tag">[{x}]</span>'


S = []

# 1
S.append(slide(1, "A travel agency can warn its clients two hours before a flight, if the data shows which flights will go wrong", f"""<div style="zoom:1.25">
<p class="tiny">TMS · NYC flights 2023 · 435,352 flights leaving JFK, LaGuardia and Newark {t('01')}</p>
<div class="box"><p><b>Q1.</b> Which flights will leave more than 15 minutes late or be cancelled, so the agency can warn clients two hours before departure?</p></div>
<div class="box"><p><b>Q2.</b> Which airlines, airports, hours and months are the most and least reliable, and how much does the weather explain?</p></div>
<div class="box warn"><p><b>Q3.</b> Which flights will be cancelled, so clients can be rebooked before it happens?</p></div>
<p class="small">Data: nycflights23 (C. Ismay, S. P. Couch, H. Wickham, 2025, CC0). Training: January to September 2023. Test: October to December 2023, used once.</p></div>""",
                       "Mirna Embaby · Queen's University · ML week"))

# 2
S.append(slide(2, "Five files, 435,352 flights, and two traps that would have fooled any model", f"""<div style="zoom:1.2">
<div class="cols"><div class="col" style="flex:1.15">
<table><tr><th>Problem found</th><th class="n">Rows</th><th>Decision</th></tr>
<tr><td>Cancelled flights (no departure time)</td><td class="n">10,738</td><td>keep, they are the target</td></tr>
<tr><td>Tail number missing</td><td class="n">1,913</td><td>keep, never a feature</td></tr>
<tr><td>Tail not in planes file</td><td class="n">9,371</td><td>keep, fill later</td></tr>
<tr><td>Departed, arrival data missing</td><td class="n">715</td><td>keep, flag</td></tr>
<tr><td>Delays over 12 hours</td><td class="n">365</td><td>keep, flag (real)</td></tr>
<tr><td>Weather hours missing</td><td class="n">73</td><td>leave empty</td></tr>
<tr><td>Duplicates</td><td class="n">0</td><td>none</td></tr></table>
<p class="tiny">Every problem has a count, a decision and a reason; no flight was removed. {t('01')}</p></div>
<div class="col"><div class="box warn"><p><b>Trap 1: the weather file is in UTC</b>, the flights in New York time. A plain join pairs a flight with weather 4 to 5 hours off, so flights are converted to UTC first. {t('01')}</p></div>
<div class="box warn"><p><b>Trap 2: a missing tail number means cancelled.</b> All 1,913 flights with no tail are cancelled flights, so a model would learn the answer from the gap. Plane data is never left empty. {t('01')}</p></div></div></div></div>""",
                       "Source: notebook 01, section 6 (data report)"))

# 3
S.append(slide(3, "Findings 1 to 3: delays build up through the day, a few bad days carry the cancellations, and rain adds 14.5 points", f"""
<div class="cols">
<div class="col" style="flex:1.2">{C['hour']}<p class="small"><b>13.4%</b> of flights at 5-8 h are late or cancelled, <b>39.9%</b> at 19-22 h: gap <b>26.5 points</b> (interval 24.2 to 28.9). {t('02')}<br><i>Action:</i> warn evening flights first.</p></div>
<div class="col" style="flex:1.1">{C['badday']}<p class="small">27 days with 45% or more flights late or cancelled hold <b>57.5%</b> of all cancellations (27 random days: 10%). {t('02')}<br><i>Action:</i> needs a real-time bad-day alert.</p></div>
<div class="col" style="flex:0.95">{C['weather']}<p class="small">Gap <b>+14.5 points</b> (interval 11.1 to 18.1); still 1.48 times the expected rate after hour, month and airport. {t('02')}<br><i>Action:</i> use weather in the model.</p></div></div>""",
                       "Source: notebook 02, training months (330,883 flights); intervals resample whole days"))

# 4
S.append(slide(4, "Findings 4 and 5: airlines differ on bad days, and the 'safe Thursday' was only luck", f"""
<div class="cols"><div class="col">{C['airlines']}<p class="small"><b>Finding 4.</b> On ordinary days big airlines cancel 1.0% to 1.7% of flights; on bad days Republic (YX) cancels <b>29%</b> and Endeavor (9E) <b>27%</b>, Delta 9%. {t('02')}<br><i>Action:</i> rebook YX and 9E clients first on a bad day.</p></div>
<div class="col">{C['weekday']}<p class="small"><b>Finding 5 (a strange pattern).</b> Thursday looked safest (1.5%) and Sunday worst (4.7%). Without the 27 bad days the gap nearly vanishes (Cramer's V 0.057 to 0.023). Thursday had 0 bad days, Sunday 6; a weekday with none happens in 8.7% of random placements. {t('02')}<br><i>Action:</i> do not tell clients Thursday is safer.</p></div></div>""",
                       "Source: notebook 02, training months"))

# 5
g1, g2, g3 = (grp[grp.dest_group == k] for k in ("G1", "G2", "G3"))
assert (len(g1), len(g2), len(g3)) == (57, 45, 7)
S.append(slide(5, "Destination airports fall into three groups, and each needs a different action", f"""
<table><tr><th>Group</th><th class="n">Airports</th><th class="n">Flights</th><th>Typical (Jan-Sep)</th><th>What the agency does</th></tr>
<tr><td><b>G1</b> short-haul, mild delays, most cancellations</td><td class="n">57</td><td class="n">101,287</td><td>late 21.2%, cancelled 4.3%, 588 miles; 81% YX and 9E</td><td>keep rebooking ready first</td></tr>
<tr><td><b>G2</b> main long-haul, delays build up through the day</td><td class="n">45</td><td class="n">226,896</td><td>late 27.8%; morning 15% to evening 42%, 1,426 miles</td><td>warn earlier on afternoon and evening flights, check connections</td></tr>
<tr><td><b>G3</b> chronic delays on few flights (BQN, SMF, ONT, PSE, ABQ, SJC, RNO)</td><td class="n">7</td><td class="n">2,374</td><td>late 53.1%, mean delay 41.5 minutes; 77% from JFK, 77% JetBlue</td><td>always warn and check connections; re-check monthly</td></tr></table>
<p class="small">9 destinations with fewer than 100 flights are labelled 'small'. k = 3 groups of destination airports (k-means on 8 delay columns). Honest limit: the silhouette score is 0.322, a weak structure; the same groups came back in 10 runs (adjusted Rand index at least 0.965). {t('03')}</p>
<p class="tiny">Groups are fitted on January to September only, so they can be used as a model column without leakage.</p>""",
                       "Source: notebook 03, sections 4 and 7"))

# 6
S.append(slide(6, "Five metrics tell the agency how reliable its flights are; July was the worst month", f"""
<div class="cols"><div class="col" style="flex:0.95"><ul class="small">
<li><b>M1 on-time</b>: departed flights with delay of 15 minutes or less / departed flights (whole year 79.03%)</li>
<li><b>M2 average delay</b>: mean departure delay of departed flights, minutes (13.84)</li>
<li><b>M3 cancelled</b>: flights with no departure / all scheduled flights (2.47%)</li>
<li><b>M4 over an hour late</b>: delay above 60 minutes / departed flights (8.41%)</li>
<li><b>M5 late or cancelled</b>: delay above 15 minutes or no departure / all scheduled flights (22.91%)</li></ul>
<p class="tiny">Whole-year values {t('04')}</p></div>
<div class="col" style="flex:1.35">{C['monthly']}</div></div>
<div class="box small"><b>Unusual months.</b> Only July's cancellation rate (8.68% of flights) is a statistical outlier (modified z-score 4.1 against a limit of 3.5). June and July were not wetter or windier; the 27 bad days hold 76% and 69% of their cancellations, and Newark and United stand out. Cause of the bad days: not explained by the available data. {t('04')}</div>""",
                       "Source: notebook 04, sections 1, 2 and 4; flights = 435,352 (monthly 33,362 to 39,514)"))

# 7
S.append(slide(7, "The strongest new column is how late the airport already is, and no column uses information from after the prediction moment", f"""
<div class="cols"><div class="col" style="flex:1.35">{C['ablation']}<p class="tiny">Quick model trained on January-June and scored on July-September; dashed line = dumb answer. {t('05')}</p></div>
<div class="col"><ul class="small">
<li><b>51 new columns</b>: calendar, route, plane, weather (two sets), airport traffic, <b>airport state</b> (delays of flights that left the same airport in the last 2 hours), previous flight of the same plane, airline and route history.</li>
<li><b>Rule:</b> prediction moment = scheduled departure minus 2 hours; only what is known then is used.</li>
<li><b>Leak tests pass</b>: no forbidden column; 1,000 flights recomputed by a slow loop agree; deleting all later flights changes nothing; strict weather is never later than the moment. It also caught a tie bug. {t('05')}</li>
<li>A naive empty plane column lifts cancellation PR-AUC to 0.458 (a leak); the random same-airline plane fill gives 0.263.</li></ul></div></div>""",
                       "Source: notebook 05, sections 11 and 12"))

# 8
S.append(slide(8, "Both predictions are tested the honest way: time split, a dumb answer to beat, and no accuracy", f"""
<div class="timeline"><div style="flex:6;background:#2f6fb0">train: Jan-Jun</div><div style="flex:3;background:#e07b39">validation: Jul-Sep</div><div style="flex:3;background:#1f3a5f">test: Oct-Dec (scored once)</div></div>
<p class="tiny">Models are tuned on Jul-Sep (fit on Jan-Jun), then refit on Jan-Sep (330,883 flights) and scored once on Oct-Dec (104,469 flights). {t('06')}</p>
<div class="cols"><div class="col"><ul class="small">
<li><b>Dumb answer:</b> 'nobody is late' scores PR-AUC = the share of late flights: 0.1406 on test (cancelled: 0.0021). It is 85.9% accurate and flags nobody, so accuracy is never used. {t('06')}</li>
<li><b>Hour-only rule</b> is a second bar to beat (late 0.1836). For cancellations it does not beat the dumb answer.</li>
<li><b>Test late rate is 14.1% against 25.7% in training</b> (drift), so each score is compared with the dumb answer of the same part.</li></ul></div>
<div class="col"><p class="small"><b>Columns removed (leakage list):</b></p><ul class="small">
<li>departure and arrival times, delays, air time: written after the event</li>
<li>tail number and 'tail missing': missing = cancelled for 1,913 flights</li>
<li>flags and targets built from the outcome; flight number; year</li>
<li>anything computed from flights after the prediction moment {t('06')}</li></ul></div></div>""",
                       "Source: notebook 06, sections A2, A5, B5"))

# 9
S.append(slide(9, "Every model beats the dumb answer, but the models cannot be told apart and cancellations stay hard", f"""
{C['results']}
<div class="cols"><div class="col"><p class="small" style="font-size:16px"><b>Late or cancelled (104,469 test flights):</b> neural network 0.339, gradient boosting 0.347, random forest 0.341, logistic regression 0.324; all inside the same interval, about 2.4 times the dumb answer. Weather join choice changes the score by 0.004 or less (inside the interval). {t('06')}</p></div>
<div class="col"><p class="small" style="font-size:16px"><b>Cancelled (224 flights):</b> logistic regression 0.120 against 0.0021, but the interval is wide (0.002 to 0.233): 115 of 224 cancellations are on one day, 18 December. Without week 51: 0.0071 against 0.0011. {t('06')}</p></div>
<div class="col"><p class="small" style="font-size:16px"><b>Weak spots:</b> morning recall 5.8%, Newark 20.5% (late); all 39 Newark cancellations missed. The model flags Alaska, American and Endeavor less than their real risk. {t('06')}</p></div></div>""",
                       "Source: notebook 06, sections E2, E3, D2, D3"))

# 10
S.append(slide(10, "Card 1: flag 11.5% of flights and catch 30.5% of late or cancelled flights, 2.7 times better than random", f"""
<div class="kpis"><div class="kpi"><div class="big">0.597</div><div class="lab">cut-off on the network score, chosen on Jul-Sep {t('07')}</div></div>
<div class="kpi"><div class="big">37.4%</div><div class="lab">precision, interval 34.2 to 40.6 (4,481 of 11,974 flags) {t('07')}</div></div>
<div class="kpi"><div class="big">30.5%</div><div class="lab">recall, interval 25.4 to 35.1 (of 14,685 cases) {t('07')}</div></div>
<div class="kpi"><div class="big">2.7x</div><div class="lab">better than picking 11,974 flights at random (14.1%) {t('07')}</div></div></div>
<div class="cols card"><div class="col"><ul>
<li><b>Question:</b> will the flight leave over 15 minutes late or be cancelled, two hours before departure?</li>
<li><b>Action:</b> message the client of each flagged flight and check connections; warn earlier on afternoon and evening flights (long-haul group G2).</li>
<li><b>Workload:</b> 130 flights a day in Oct-Dec.</li>
<li><b>Model:</b> neural network, 37 columns, trained Jan-Sep. PR-AUC 0.339 [0.301, 0.376] against dumb 0.141.</li></ul></div>
<div class="col"><ul>
<li><b>Weak spots:</b> mornings recall 5.8% (evenings 51.0%); Newark 20.5% (JFK 40.2%).</li>
<li><b>Re-check when</b> weekly recall is below 14% two weeks running (14 test weeks ranged 14.3% to 51.7%).</li>
<li><b>Human check:</b> confirm the flight status on the airline's feed; never auto-rebook; message says 'possible delay'.</li>
<li><b>Finding:</b> how late the airport already is beats weather ten times over (0.228 against 0.023).</li></ul></div></div>""",
                       "Source: notebook 07, section 7 (card 1); flights = 104,469 test flights"))

# 11
S.append(slide(11, "Card 2: 5 flagged flights a day catch 42% of cancellations, but only 19 in 100 flags are real", f"""
<div class="kpis"><div class="kpi o"><div class="big">0.137</div><div class="lab">cut-off on the probability, chosen on Jul-Sep {t('07')}</div></div>
<div class="kpi o"><div class="big">19.4%</div><div class="lab">precision, interval 0.6 to 25.9 (94 of 484 flags) {t('07')}</div></div>
<div class="kpi o"><div class="big">42.0%</div><div class="lab">recall, interval 1.0 to 60.5 (of 224 cancellations) {t('07')}</div></div>
<div class="kpi o"><div class="big">91x</div><div class="lab">better than random (0.21% of flights) {t('07')}</div></div></div>
<div class="cols card"><div class="col"><ul>
<li><b>Question:</b> will the flight be cancelled, two hours before departure?</li>
<li><b>Action:</b> offer a rebooking to the client of each flagged flight; never rebook automatically. Strongest for short-haul G1 (precision 25.1%, 81 cases).</li>
<li><b>Workload:</b> 5.3 flights a day; top 1% of scores = 11 a day: precision 10.2%, recall 47.8%.</li>
<li><b>Model:</b> logistic regression, 37 columns. PR-AUC 0.120 [0.002, 0.233] against dumb 0.0021.</li></ul></div>
<div class="col"><ul>
<li><b>Weak spots:</b> none of 39 Newark cancellations found; recall 0% in October, 5% in November, 60% in December.</li>
<li><b>Re-check when</b> a bad-day block of 4 weeks (at least 30 cancellations) has recall under 23%. Weekly counts are too small.</li>
<li><b>Human check:</b> confirm the flight is still scheduled; a flag means 'high risk'.</li>
<li><b>Finding:</b> 115 of 224 cancellations fell on one day, 18 December (9.8% of that day's 1,174 flights; Endeavor and Republic). Weather was ordinary: cause not explained by the available data.</li></ul></div></div>
<p class="tiny">Precision is low in absolute terms and the result rests on one day; it is a ranking aid for rebooking capacity, not a promise.</p>""",
                       "Source: notebook 07, section 7 (card 2); flights = 104,469 test flights"))

# 12
S.append(slide(12, "AI helped to write and check the code; every number was re-computed and the limits are stated", f"""
<div class="cols"><div class="col"><p><b>Where AI helped</b></p><ul class="small">
<li>drafting notebook code and the helper file</li>
<li>debugging (memory crash, a tie bug in the previous-flight column, a divide-by-zero in the bootstrap)</li>
<li>wording of explanations and of this deck</li></ul>
<p><b>What was checked</b></p><ul class="small">
<li>all counts of the data report match the plan; the 15 metric check values are asserted in code</li>
<li>four leak tests pass; test part scored once; notebooks run top to bottom with identical numbers on a re-run</li>
<li>every slide number has a line in the README ledger</li></ul></div>
<div class="col"><p><b>Limits</b></p><ul class="small">
<li>One year, three airports; weather is observed, not a forecast</li>
<li>Train and test differ strongly: late 25.7% against 14.1%, cancelled 3.18% against 0.21%</li>
<li>Cancellation precision is low, and half of the test cancellations are on one day</li>
<li>Group structure is weak (silhouette 0.322)</li>
<li>Models of the same family are not separable in the test interval</li></ul>
<p class="small"><b>Next:</b> a real weather forecast feed and a cancellation timestamp.</p></div></div>""",
                       "Source: README.md (how AI was used), notebooks 01 to 07"))

html = f'<!doctype html><html><head><meta charset="utf-8"><title>TMS final</title><style>{CSS}</style></head><body>{"".join(S)}</body></html>'
(OUT / "_deck.html").write_text(html, encoding="utf-8")

NOTES = """# Speaker notes (one sentence to say, number to read out, likely question)

1. **Say:** The agency wants to warn clients two hours before a flight; I answer three questions with 2023 New York flights. **Number:** 435,352 flights. **Question:** why two hours? Because the agency's own warning moment is two hours before departure, so only what is known then may be used.
2. **Say:** Two traps changed my work: the weather file is in UTC, and a missing tail number means cancelled. **Number:** 1,913 flights with no tail, all cancelled. **Question:** what changes with a plain join? Weather is 4 to 5 hours off; the score barely moves (difference 0.004 or less), but the UTC join is the correct one.
3. **Say:** Delays build up through the day, a few bad days carry the cancellations, and rain adds 14.5 points. **Number:** gap of 26.5 points; 57.5% of cancellations on 27 days. **Question:** is it only a chain of delays? No: even a plane's first flight of the day goes from 11.4% to 43.4% late.
4. **Say:** Airlines cancel differently only on bad days, and the weekday pattern was luck. **Number:** YX 29% and 9E 27% against Delta 9% on bad days. **Question:** how do you know Thursday is luck? Thursday had 0 bad days; an empty weekday happens in 8.7% of random placements.
5. **Say:** Destinations form three groups with three actions. **Number:** silhouette 0.322. **Question:** is the structure strong? No, it is weak; I chose k = 3 because k = 2 splits 100 against 9 and k of 4 or more makes groups under 5 airports.
6. **Say:** Five metrics with exact formulas; July is the outlier. **Number:** M5 22.91% for the year; July cancellations 8.68%. **Question:** why July? Not weather; bad days hold 69% of July's cancellations and the cause is not in the data.
7. **Say:** The strongest new column is how late the airport already is; leak tests prove nothing comes from after the moment. **Number:** removing airport state drops validation PR-AUC from 0.621 to 0.518. **Question:** how do you know no feature uses the future? Deleting every later flight does not change any feature value.
8. **Say:** Time split, dumb answer, no accuracy. **Number:** accuracy of the dumb answer 85.9%; PR-AUC 0.1406. **Question:** why is test late rate so different (14.1% against 25.7%)? Autumn was calmer; so every score is compared with the dumb answer of the same part.
9. **Say:** All models beat the dumb answer, none beats the others. **Number:** 0.339 to 0.347 for late; 0.120 for cancelled with a wide interval. **Question:** which model do you choose? Best on validation: the neural network for late, logistic regression for cancelled; the differences on test are inside the intervals.
10. **Say:** Card 1 flags 130 flights a day and catches 30.5% of late or cancelled flights. **Number:** 2.7 times better than random. **Question:** is 37.4% precision useful? It is 2.7 times the base rate and a false warning costs one message.
11. **Say:** Card 2 is weak in precision and I say so. **Number:** 94 of 484 flags real; 115 of 224 cancellations on 18 December. **Question:** why is it still useful? It ranks flights; 5 flags a day find 42% of cancellations, but the interval is wide.
12. **Say:** AI wrote and debugged code with me; I re-computed and checked every number. **Number:** 4 leak tests; 15 metric check values. **Question:** what would you do with more data? A real weather forecast feed and a cancellation timestamp.
"""
(OUT / "speaker_notes.md").write_text(NOTES, encoding="utf-8")

# --------------------------------------------------------------------------- PDF
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    pg.goto((OUT / "_deck.html").as_uri())
    pg.wait_for_timeout(500)
    pg.pdf(path=str(OUT / "tms_final.pdf"), width="1280px", height="720px", print_background=True)
    b.close()
(OUT / "_deck.html").unlink()
print("saved", OUT / "tms_final.pdf")

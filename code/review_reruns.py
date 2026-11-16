"""Sensitivity checks added after the main results were seen (14 Nov 2026). Run after the other scripts.
R1  Drop days with implausible outturn inertia: at least 40 of 48 half-hours below 90 GVA.s
    (whole-day faults; three June 2026 days with a few half-hours at 81-89 GVA.s are kept).
R2  Cluster standard errors by week instead of by day.
R3  Floor effect only where the floor binds: counterfactual inertia = max(market inertia, floor).
R4  Floor effect (120 -> 102) across all reported specifications.
R5  Drop 2022 (S3), with and without the R1 faulty days.
"""
import json, sys, numpy as np, pandas as pd, statsmodels.formula.api as smf

ctrl = "C(year) + C(moy) + C(hour) + weekend + lognd + ewsh + essh"
R = {}

b = pd.read_csv("out/analysis_halfhours_adj.csv")
v = json.load(open("data/grid_dc.json"))
rows = [r for k, arr in v.items() if not k.startswith("__") for r in arr]
dc = pd.DataFrame([r.split(",") for r in rows], columns=["bin_utc", "n2", "sumG", "n100"]).astype(
    {"bin_utc": "int64", "n2": int, "sumG": float, "n100": int})
b = b.merge(dc, on="bin_utc", how="left")
b["Y5"] = np.log1p(b.sumG.where(b.n2 >= 1700)); b["Y6"] = np.log1p(b.n100.where(b.n2 >= 1700))
sd = pd.to_datetime(b.settlement_date)
b["week"] = sd.dt.strftime("%G-%V")


def q(m, k):
    lo, hi = m.conf_int().loc[k]
    return [round(float(m.params[k]), 4), round(float(lo), 4), round(float(hi), 4)]


def era_model(y, d, a="logH_pre", c="logH_post", cl="date"):
    d = d.dropna(subset=[y, "lognd", "ewsh", "essh"])
    m = smf.ols(f"{y} ~ {a} + {c} + {ctrl}", data=d).fit(cov_type="cluster", cov_kwds={"groups": d[cl]})
    cv = m.cov_params(); df_ = m.params[c] - m.params[a]
    se = float(np.sqrt(cv.loc[c, c] + cv.loc[a, a] - 2 * cv.loc[c, a]))
    return dict(pre=q(m, a), post=q(m, c), diff=[round(df_, 4), round(df_ - 1.96 * se, 4), round(df_ + 1.96 * se, 4)], n=int(m.nobs))


k = np.log(102 / 120)
pct = lambda beta: round(100 * (np.exp(beta * k) - 1), 2)
floor = lambda p: [pct(p[0]), pct(p[2]), pct(p[1])]  # point, low, high

# ---- R1: bad inertia days
cnt = b.assign(low=b.H < 90).groupby("settlement_date").low.sum()
bad_days = sorted(cnt[cnt >= 40].index.tolist())
R["R1_bad_days"] = bad_days
R["R1_halfhours_dropped"] = int(b.settlement_date.isin(bad_days).sum())
c = b[~b.settlement_date.isin(bad_days)]
R["R1"] = {}
for y in ["Y1", "Y2", "Y3", "Y4", "Y5", "Y6"]:
    r = era_model(y, c); r["floor_pct"] = floor(r["post"]); R["R1"][y] = r
r = era_model("Y1", c, "logHa_pre", "logHa_post"); r["floor_pct"] = floor(r["post"]); R["R1"]["Y1_pathfinder_adj"] = r

# ---- R2: week clustering (full pre-specified sample)
R["R2"] = {}
for y in ["Y1", "Y5", "Y6"]:
    rd = era_model(y, b, cl="date"); rw = era_model(y, b, cl="week")
    R["R2"][y] = dict(day=rd, week=rw, floor_pct_day=floor(rd["post"]), floor_pct_week=floor(rw["post"]),
                      se_ratio_post=round((rw["post"][2] - rw["post"][1]) / (rd["post"][2] - rd["post"][1]), 2))

# ---- R3: where the floor binds (since 18 Jun 2024, floor 120)
s = b[sd >= "2024-06-18"].dropna(subset=["Hm"]).copy()
R["R3_n_halfhours"] = int(len(s))
betas = {y: R["R2"][y]["day"]["post"] for y in ["Y1", "Y5", "Y6"]}
steps = {"120_to_102": (120, 102), "120_to_110": (120, 110), "110_to_102": (110, 102)}
R["R3"] = {}
for nm, (old, new) in steps.items():
    x = np.log(np.maximum(s.Hm, new) / np.maximum(s.Hm, old))
    aff = x < 0
    out = dict(share_affected=round(float(aff.mean()), 3))
    for y, bp in betas.items():
        eff = lambda beta: 100 * (np.exp(beta * x) - 1)
        out[y] = dict(mean_in_affected=[round(float(eff(bp[0])[aff].mean()), 2), round(float(eff(bp[2])[aff].mean()), 2), round(float(eff(bp[1])[aff].mean()), 2)],
                      mean_all=[round(float(eff(bp[0]).mean()), 2), round(float(eff(bp[2]).mean()), 2), round(float(eff(bp[1]).mean()), 2)])
    R["R3"][nm] = out
R["R3_share_Hm_below"] = {str(t): round(float((s.Hm < t).mean()), 3) for t in [102, 110, 120]}

# ---- R4: floor effect (Y1, 120->102, where binding fully) across specifications
ew = json.load(open("out/explore_wind.json")); se_ = json.load(open("out/sens_eras_binscatter.json"))
r0 = json.load(open("out/results.json")); a1 = json.load(open("out/a1_pathfinder.json"))
spec = {
    "pre-specified (pooled)": r0["main"]["Y1"]["post"]["b"],
    "each era separately": se_["Y1_sep_post"][0],
    "Pathfinder-adjusted (A1)": a1["adj"]["post"][0],
    "market inertia (S3)": r0["S3"]["market_inertia"]["post"]["b"],
    "no loss-event half-hours (S3)": r0["S3"]["no_event_halfhours"]["post"]["b"],
    "excluding 2022 (S3)": r0["S3"]["excl_2022"]["post"]["b"],
    "+ wind, solar, imports": ew["+wind_solar_imports"]["logH_post"][0],
    "+ full fuel mix": ew["+full_mix"]["logH_post"][0],
    "bad inertia days dropped (R1)": R["R1"]["Y1"]["post"][0],
}
R["R4"] = {n: dict(beta_post=round(float(v_), 3), floor_pct=pct(v_)) for n, v_ in spec.items()}
fp = [x["floor_pct"] for x in R["R4"].values()]
R["R4_range"] = [min(fp), max(fp)]

# ---- R5: drop 2022, with and without the faulty days
no22 = b[sd.dt.year != 2022]
R["R5"] = dict(drop2022=era_model("Y1", no22),
               drop2022_and_faulty_days=era_model("Y1", no22[~no22.settlement_date.isin(bad_days)]))

json.dump(R, open("out/review_reruns.json", "w"), indent=1)
print(json.dumps(R, indent=1))

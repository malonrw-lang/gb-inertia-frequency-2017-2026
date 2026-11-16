import os
"""Pre-registered analysis: grid inertia vs 1-second frequency dynamics (GB).
Follows PREREGISTRATION_grid_inertia.md. Usage: python analysis.py <datadir> <outdir>
"""
import sys, json, glob, io
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from zoneinfo import ZoneInfo

D = sys.argv[1] if len(sys.argv) > 1 else "data"
O = sys.argv[2] if len(sys.argv) > 2 else "out"
LON = ZoneInfo("Europe/London")
R = {}  # results


def to_sp(utc_seconds):
    """UTC epoch seconds (start of half-hour) -> (settlement_date, settlement_period) in UK local time."""
    ts = pd.to_datetime(pd.Series(utc_seconds), unit="s", utc=True)
    loc = ts.dt.tz_convert(LON)
    sdate = loc.dt.normalize().dt.tz_localize(None)
    mid_local = loc.dt.normalize()                      # local midnight (tz-aware)
    mid_utc = mid_local.dt.tz_convert("UTC")
    sp = ((ts - mid_utc).dt.total_seconds() // 1800).astype(int) + 1
    return sdate.dt.date, sp, loc


def load_inertia():
    frames = []
    for f in sorted(glob.glob(f"{D}/inertia_*.csv")):
        x = pd.read_csv(f)
        x.columns = [c.strip().lower().replace(" ", "_") for c in x.columns]
        frames.append(x)
    x = pd.concat(frames, ignore_index=True)
    x["settlement_date"] = parse_dates(x["settlement_date"])
    x = x.rename(columns={"settlement_period": "sp", "outturn_inertia": "H", "market_provided_inertia": "Hm"})
    return x[["settlement_date", "sp", "H", "Hm"]].drop_duplicates(["settlement_date", "sp"])


def parse_dates(s):
    s = s.astype(str).str.strip().str.strip('"')
    out = pd.Series(pd.NaT, index=s.index)
    for fmt in ("%Y-%m-%d", "%d-%b-%Y", "%d-%b-%y"):
        m = out.isna()
        out[m] = pd.to_datetime(s[m], format=fmt, errors="coerce")
    assert out.notna().all(), s[out.isna()].head()
    return out.dt.date


def load_demand():
    frames = []
    for f in sorted(glob.glob(f"{D}/demand_*.csv")):
        x = pd.read_csv(f)
        x.columns = [c.strip().upper() for c in x.columns]
        frames.append(x[["SETTLEMENT_DATE", "SETTLEMENT_PERIOD", "ND", "EMBEDDED_WIND_GENERATION", "EMBEDDED_SOLAR_GENERATION"]])
    x = pd.concat(frames, ignore_index=True)
    x["settlement_date"] = parse_dates(x["SETTLEMENT_DATE"])
    x = x.rename(columns={"SETTLEMENT_PERIOD": "sp", "ND": "nd", "EMBEDDED_WIND_GENERATION": "ew", "EMBEDDED_SOLAR_GENERATION": "es"})
    return x[["settlement_date", "sp", "nd", "ew", "es"]].drop_duplicates(["settlement_date", "sp"])


def era_of(d):
    d = pd.to_datetime(d)
    e = np.where(d < "2020-10-01", "pre", np.where(d < "2021-01-01", "trans", "post"))
    return e


def fit(formula, df, cluster):
    m = smf.ols(formula, data=df).fit(cov_type="cluster", cov_kwds={"groups": df[cluster]})
    return m


def coef(m, name):
    b = m.params[name]; se = m.bse[name]; lo, hi = m.conf_int().loc[name]
    return dict(b=float(b), se=float(se), lo=float(lo), hi=float(hi), p=float(m.pvalues[name]), n=int(m.nobs))


def main():
    qc = pd.read_csv(f"{D}/grid_qc.csv")
    days = qc["month"].apply(lambda m: pd.Period(m, "M").days_in_month)
    qc["coverage"] = qc["rows"] / (days * 86400)
    qc["excluded"] = qc["coverage"] < 0.95
    R["qc"] = dict(months=int(len(qc)), excluded=int(qc.excluded.sum()), excluded_list=qc.loc[qc.excluded, "month"].tolist(),
                   min_coverage=float(qc.coverage.min()))
    R["qc"]["STOP"] = bool(qc.excluded.mean() > 0.20)
    bad_months = set(qc.loc[qc.excluded, "month"])

    H = load_inertia(); Dm = load_demand()

    # ---- bins
    b = pd.read_csv(f"{D}/grid_bins.csv")
    b["settlement_date"], b["sp"], loc = to_sp(b["bin_utc"])
    b["month"] = pd.to_datetime(b["bin_utc"], unit="s").dt.strftime("%Y-%m")
    b["hour"] = loc.dt.hour.values
    b = b[~b["month"].isin(bad_months)]
    b = b[b["n"] >= 1700]
    b = b.merge(H, on=["settlement_date", "sp"], how="inner").merge(Dm, on=["settlement_date", "sp"], how="left")
    sd = pd.to_datetime(b["settlement_date"])
    b["era"] = era_of(sd); b = b[b.era != "trans"].copy()
    b["year"] = sd.dt.year; b["moy"] = sd.dt.month; b["weekend"] = (sd.dt.dayofweek >= 5).astype(int)
    b["date"] = b["settlement_date"].astype(str)
    b["logH"] = np.log(b["H"]); b["logHm"] = np.log(b["Hm"].clip(lower=1))
    b["Y1"] = np.log(b["p999_mHz"].where(b["p999_mHz"] > 0))
    b["Y2"] = np.log(b["sd"].where(b["sd"] > 0)); b["Y3"] = b["r1"]; b["Y4"] = (b["n_outband"] > 0).astype(int)
    b["lognd"] = np.log(b["nd"]); b["ewsh"] = b["ew"] / b["nd"]; b["essh"] = b["es"] / b["nd"]
    b["pre"] = (b.era == "pre").astype(int); b["post"] = (b.era == "post").astype(int)
    b["logH_pre"] = b.logH * b.pre; b["logH_post"] = b.logH * b.post
    R["bins"] = dict(n=int(len(b)), n_pre=int(b.pre.sum()), n_post=int(b.post.sum()), y1_zero=int(b.Y1.isna().sum()),
                     nd_missing=int(b.nd.isna().sum()))
    b.to_csv(f"{O}/analysis_halfhours.csv", index=False)

    # ---- Gate G1
    e = pd.read_csv(f"{D}/grid_events.csv")
    e["bin"] = (e["t_utc"] // 1800) * 1800
    e["settlement_date"], e["sp"], eloc = to_sp(e["bin"])
    e["month"] = pd.to_datetime(e["t_utc"], unit="s").dt.strftime("%Y-%m")
    e = e[~e["month"].isin(bad_months)]
    e = e.merge(H, on=["settlement_date", "sp"], how="inner")
    esd = pd.to_datetime(e["settlement_date"])
    e["era"] = era_of(esd); e["moy"] = esd.dt.month; e["hour"] = eloc.dt.hour.reindex(e.index).values if False else pd.to_datetime(e["t_utc"], unit="s", utc=True).dt.tz_convert(LON).dt.hour
    e["date"] = e["settlement_date"].astype(str)
    e = e[(e.rocof_mHz > 0) & (e.depth_mHz > 0)].copy()
    e["logK"] = np.log(e.rocof_mHz / e.depth_mHz); e["logH"] = np.log(e.H)
    e.to_csv(f"{O}/analysis_events.csv", index=False)
    g = fit("logK ~ logH + C(era) + C(moy) + C(hour)", e, "date")
    gate = coef(g, "logH")
    epre = e[e.era == "pre"]
    gpre = coef(fit("logK ~ logH + C(moy) + C(hour)", epre, "date"), "logH") if len(epre) > 30 else None
    gate_pass = (gate["hi"] < 0) and (len(e) >= 50)
    R["gate"] = dict(pooled=gate, pre_only=gpre, n_events=int(len(e)), events_by_era=e.era.value_counts().to_dict(), PASS=bool(gate_pass))
    # descriptive companions (not decisive)
    R["gate"]["rocof_on_logH"] = coef(fit("np.log(rocof_mHz) ~ logH + C(era) + C(moy) + C(hour)", e, "date"), "logH")
    R["gate"]["depth_on_logH"] = coef(fit("np.log(depth_mHz) ~ logH + C(era) + C(moy) + C(hour)", e, "date"), "logH")
    if (not gate_pass or R["qc"]["STOP"]) and os.environ.get("FORCE") != "1":
        R["decision"] = "STOP"
        return

    # ---- Main models
    ctrl = "C(year) + C(moy) + C(hour) + weekend + lognd + ewsh + essh"  # era main effect is collinear with year FE (absorbed); removed to restore full rank
    R["main"] = {}
    for y in ["Y1", "Y2", "Y3", "Y4"]:
        d = b.dropna(subset=[y, "lognd", "ewsh", "essh"])
        m = fit(f"{y} ~ logH_pre + logH_post + {ctrl}", d, "date")
        cv = m.cov_params()
        diff = m.params["logH_post"] - m.params["logH_pre"]
        se = float(np.sqrt(cv.loc["logH_post", "logH_post"] + cv.loc["logH_pre", "logH_pre"] - 2 * cv.loc["logH_post", "logH_pre"]))
        R["main"][y] = dict(pre=coef(m, "logH_pre"), post=coef(m, "logH_post"),
                            diff=dict(b=float(diff), se=se, lo=float(diff - 1.96 * se), hi=float(diff + 1.96 * se)), n=int(m.nobs))
    y1 = R["main"]["Y1"]
    R["H1"] = "supported" if y1["pre"]["hi"] < 0 else "not supported"
    R["H2"] = "weakened" if y1["diff"]["lo"] > 0 else ("strengthened" if y1["diff"]["hi"] < 0 else "no evidence of change")
    k = np.log(102 / 120)
    R["H3"] = dict(pct=float(100 * (np.exp(y1["post"]["b"] * k) - 1)), lo=float(100 * (np.exp(y1["post"]["hi"] * k) - 1)),
                   hi=float(100 * (np.exp(y1["post"]["lo"] * k) - 1)))

    # ---- S1 floor natural experiment (after 2024-06-18, floor 120)
    s = b[(pd.to_datetime(b.settlement_date) >= "2024-06-18") & (b.Hm.between(90, 150))].dropna(subset=["Y1"]).copy()
    s["x"] = s.Hm - 120; s["below"] = (s.x < 0).astype(int)
    if len(s) > 200:
        fs = fit("H ~ below + x + below:x + C(hour) + C(moy)", s, "date")
        rf = fit("Y1 ~ below + x + below:x + C(hour) + C(moy)", s, "date")
        R["S1"] = dict(n=int(len(s)), first_stage=coef(fs, "below"), reduced_form=coef(rf, "below"))

    # ---- S2 placebo shuffles
    rng = np.random.default_rng(20261113)
    d = b.dropna(subset=["Y1", "lognd", "ewsh", "essh"]).copy()
    pb = []
    for i in range(50):
        d["logH_s"] = d.groupby(["year", "moy", "hour"])["logH"].transform(lambda v: rng.permutation(v.values))
        d["s_pre"] = d.logH_s * d.pre; d["s_post"] = d.logH_s * d.post
        m = smf.ols(f"Y1 ~ s_pre + s_post + {ctrl}", data=d).fit()
        pb.append((m.params["s_pre"], m.params["s_post"]))
    pb = np.array(pb)
    R["S2"] = dict(pre_mean=float(pb[:, 0].mean()), pre_sd=float(pb[:, 0].std()), post_mean=float(pb[:, 1].mean()), post_sd=float(pb[:, 1].std()))

    # ---- S3 sensitivities on Y1
    R["S3"] = {}
    d = b.dropna(subset=["Y1", "lognd", "ewsh", "essh"]).copy()
    d["m_pre"] = np.log(d.Hm.clip(lower=1)) * d.pre; d["m_post"] = np.log(d.Hm.clip(lower=1)) * d.post
    m = fit(f"Y1 ~ m_pre + m_post + {ctrl}", d, "date"); R["S3"]["market_inertia"] = dict(pre=coef(m, "m_pre"), post=coef(m, "m_post"))
    evbins = set(e["bin"])
    d2 = d[~(((pd.to_datetime(d["settlement_date"]).astype("int64") // 10**9)).isin([]))]
    d2 = d[~d["bin_utc"].isin(evbins)]
    m = fit(f"Y1 ~ logH_pre + logH_post + {ctrl}", d2, "date"); R["S3"]["no_event_halfhours"] = dict(pre=coef(m, "logH_pre"), post=coef(m, "logH_post"))
    d3 = d[d.year != 2022]
    m = fit(f"Y1 ~ logH_pre + logH_post + {ctrl}", d3, "date"); R["S3"]["excl_2022"] = dict(pre=coef(m, "logH_pre"), post=coef(m, "logH_post"))
    R["decision"] = "GATE PASSED; main results reported" if gate_pass and not R["qc"]["STOP"] else "FORCED RUN (gate not passed) - not a valid result"


if __name__ == "__main__":
    try:
        main()
    finally:
        json.dump(R, open(f"{O}/results.json", "w"), indent=1, default=str)
        print(json.dumps(R, indent=1, default=str)[:6000])

"""A3: known-answer gate normalised by MW lost (Elexon REMIT unplanned unavailability).
Physics: initial RoCoF = dP * f0 / (2 * E_kin)  ->  log RoCoF = const - 1*log E + 1*log dP.
Matching rules fixed before looking at results (see PREREG_ADDENDUM_2.md).
"""
import json, sys, numpy as np, pandas as pd, statsmodels.formula.api as smf

EV = "out/analysis_events.csv"
RM = sys.argv[1] if len(sys.argv) > 1 else "data/grid_remit_unplanned.json"
OUT = "out/a3_mwgate.json"

e = pd.read_csv(EV)
cols = ["mrid", "rev", "pub", "start", "end", "unit", "asset", "fuel", "normal", "avail", "unavail", "etype", "atype"]
r = pd.DataFrame(json.load(open(RM)), columns=cols)
r = r.drop_duplicates(["mrid", "rev"])
for c in ["pub", "start", "end"]:
    r[c] = pd.to_datetime(r[c], utc=True, errors="coerce")
# first notification per message
r = r.sort_values(["mrid", "rev"]).groupby("mrid", as_index=False).first()
r["unit_key"] = r["asset"].fillna(r["unit"]).str.upper().str.replace(r"^[TE]_", "", regex=True)
r = r[r.unavail >= 100].copy()
r["ts"] = (r.start - pd.Timestamp("1970-01-01", tz="UTC")).dt.total_seconds().round().astype("int64")
r["tp"] = (r.pub - pd.Timestamp("1970-01-01", tz="UTC")).dt.total_seconds().round().astype("int64")

# start-time precision diagnostics
sec_zero = float((r.start.dt.second == 0).mean())
on_halfhour = float(((r.start.dt.minute % 30 == 0) & (r.start.dt.second == 0)).mean())

r = r.sort_values("ts").reset_index(drop=True)
TS = r.ts.values

def match(t, lo, hi):
    i0, i1 = np.searchsorted(TS, t + lo), np.searchsorted(TS, t + hi, side="right")
    c = r.iloc[i0:i1]
    c = c[(c.tp >= t - 60) & (c.tp <= t + 6 * 3600)]
    # one row per unit (a unit can have overlapping messages)
    return c.sort_values("unavail", ascending=False).drop_duplicates("unit_key")

def build(lo, hi):
    rows = []
    for _, ev in e.iterrows():
        c = match(int(ev.t_utc), lo, hi)
        if len(c) == 0:
            continue
        rows.append(dict(t_utc=int(ev.t_utc), n_cand=len(c), mw_one=float(c.unavail.iloc[0]) if len(c) == 1 else np.nan,
                         mw_sum=float(c.unavail.sum()), units=";".join(c.unit_key), fuel=";".join(map(str, c.fuel)),
                         etype=";".join(map(str, c.etype))))
    m = pd.DataFrame(rows)
    return e.merge(m, on="t_utc") if len(m) else m

def fit(d, mwcol):
    d = d[d[mwcol] > 0].copy()
    d["logR"] = np.log(d.rocof_mHz.clip(lower=1))
    d["logMW"] = np.log(d[mwcol])
    d["logK"] = d.logR - d.logMW
    out = {"n": int(len(d))}
    if len(d) < 30:
        return out
    for name, f in [("ratio", "logK ~ logH"), ("joint", "logR ~ logH + logMW"), ("joint_ctrl", "logR ~ logH + logMW + C(hour) + C(moy)")]:
        fm = smf.ols(f, d).fit(cov_type="HC1")
        ci = fm.conf_int().loc["logH"]
        out[name] = dict(b_logH=float(fm.params.logH), ci=[float(ci[0]), float(ci[1])])
        if "logMW" in fm.params:
            c2 = fm.conf_int().loc["logMW"]
            out[name].update(b_logMW=float(fm.params.logMW), ci_MW=[float(c2[0]), float(c2[1])])
    # by era
    for era in ["pre", "post"]:
        s = d[d.era == era]
        if len(s) >= 30:
            fm = smf.ols("logK ~ logH", s).fit(cov_type="HC1")
            ci = fm.conf_int().loc["logH"]
            out[f"ratio_{era}"] = dict(n=int(len(s)), b=float(fm.params.logH), ci=[float(ci[0]), float(ci[1])])
    return out

R = {"remit_unplanned_ge100": int(len(r)), "start_on_whole_minute": sec_zero, "start_on_halfhour": on_halfhour}
for tag, (lo, hi) in {"primary_-180_+120": (-180, 120), "tight_-60_+60": (-60, 60), "wide_-900_+300": (-900, 300)}.items():
    m = build(lo, hi)
    if len(m) == 0:
        R[tag] = {"matched": 0}; continue
    R[tag] = {"matched_events": int(len(m)), "unique": int((m.n_cand == 1).sum()),
              "unique_fit": fit(m[m.n_cand == 1], "mw_one"), "sum_fit": fit(m, "mw_sum")}
    if tag.startswith("primary"):
        m.to_csv("out/a3_matched_events.csv", index=False)
        R[tag]["fuel_mix_unique"] = m[m.n_cand == 1].fuel.value_counts().head(10).to_dict()
        R[tag]["etype_unique"] = m[m.n_cand == 1].etype.value_counts().to_dict()
        R[tag]["mw_unique_quantiles"] = m[m.n_cand == 1].mw_one.quantile([.1, .5, .9]).round(0).tolist()
json.dump(R, open(OUT, "w"), indent=1)
print(json.dumps(R, indent=1))

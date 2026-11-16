# Pre-registration — Is fast battery response covering for Britain's lost inertia?

Locked 13 Nov 2026 (approx. 19:45 UTC), approved to proceed by Ryan Malone ("I say go"). Written before any frequency outcome was computed. Only data-quality facts were seen beforehand (Oct 2026 file completeness; inertia table completeness and annual means).

## Data
- NESO 1-second system frequency, Jul 2017 – Oct 2026 (112 monthly files). Older files carry explicit UTC offsets; newer files are GMT.
- NESO outturn and market-provided inertia per settlement period (half-hour), Apr 2017 onward.
- NESO historic demand (national demand ND, embedded wind generation, embedded solar generation), per settlement period.
- Unit of analysis: settlement period (UK local half-hour), mapped from UTC.

## Quality control
- A half-hour is analysed if at least 1,700 of 1,800 seconds are present.
- A month is excluded if under 95% of its seconds are present. STOP if more than 20% of months are excluded.

## Outcomes per half-hour
- Y1 (primary): log of the 99.9th percentile of |Δf| between consecutive seconds (mHz/s).
- Y2: log of the standard deviation of frequency.
- Y3: lag-1 autocorrelation of 1-second deviations about the half-hour mean (how slowly frequency returns).
- Y4: any seconds outside 49.8–50.2 Hz (yes/no).

## Eras
- Pre-battery: 1 Jul 2017 – 30 Sep 2020.
- Transition (excluded): 1 Oct 2020 – 31 Dec 2020 (Dynamic Containment launched 1 Oct 2020).
- Post-battery: 1 Jan 2021 – 31 Oct 2026.

## Gate G1 — known-answer test (run first; STOP if it fails)
Physics: for the same shock, frequency falls faster when inertia is lower.
- Loss event: a second with Δf ≤ −20 mHz/s, followed within 30 s by a minimum at least 100 mHz below the mean of the previous 10 s. Events within 120 s of an earlier event are merged into it.
- Per event: RoCoF = largest one-second fall in the first 5 s; depth D = pre-event mean minus the minimum within 60 s; K = RoCoF / D (cancels the unknown size of the lost generation, to first order).
- Model: log K on log outturn inertia of the event's half-hour, with month-of-year and local-hour fixed effects and an era indicator; standard errors clustered by date.
- Pass: coefficient < 0 with 95% CI upper bound < 0 in the pooled sample, with at least 50 events. Pre-battery-era estimate reported alongside.
- Fail or fewer than 50 events: STOP — 1-second data cannot resolve inertia.

## Main model (only if G1 passes)
Y = β_pre·log(H)·[pre] + β_post·log(H)·[post] + era + year FE + month-of-year FE + local-hour FE + weekend + log(ND) + embedded wind/ND + embedded solar/ND. H = outturn inertia. OLS; standard errors clustered by settlement date. Run for Y1–Y4 (Y4 as a linear probability model).

## Hypotheses and decision language (Y1 primary)
- H1: β_pre < 0 (lower inertia, bigger frequency jolts before batteries). Supported if the 95% CI upper bound < 0.
- H2 (main): Δ = β_post − β_pre. "Dependence weakened after batteries" only if the 95% CI lies above 0; "strengthened" only if it lies below 0; otherwise "no evidence of change".
- H3 (policy): post-battery predicted change in Y1 from 120 to 102 GVA.s = β_post·ln(102/120), reported as a percentage with 95% CI.

## Secondary and sensitivity (reported, not decisive)
- S1 floor natural experiment (after 18 Jun 2024, floor 120 GVA.s): half-hours with market-provided inertia within ±30 GVA.s of the floor; local-linear comparison either side; first stage (jump in outturn inertia) and reduced form (Y1).
- S2 placebo: inertia shuffled within year × month × hour cells; β should be about 0.
- S3: market-provided instead of outturn inertia; excluding half-hours containing loss events; excluding 2022.
- E1 exploratory: geomagnetic Kp index, if obtainable.

## Known limits
- Inertia figures are NESO estimates and exclude Stability Pathfinder units.
- NESO adds inertia when it judges risk high (reverse causality); S1 addresses this partially.
- 1-second sampling smooths sub-second dynamics.
- Low inertia coincides with low demand and high renewables; controlled, residual risk.

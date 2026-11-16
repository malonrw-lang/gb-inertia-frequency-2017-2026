# GB grid inertia and second-to-second frequency volatility: Stage 1 results

Run 13 Nov 2026 against the pre-registration locked at 19:45 UTC the same day.

## Verdict: GO to write-up (draft for Ryan's review, not for submission)

- **Effect:** lower system inertia means rougher second-to-second frequency. A 10% drop in inertia raises the 99.9th-percentile one-second frequency change by about 3.4%.
- **No change after batteries:** this link did not weaken after the battery fast-response service (Dynamic Containment) launched in October 2020.
- **Floor cut:** lowering the inertia floor from 120 to 102 GVA.s is predicted to raise that measure by about **5.4%** (95% CI 4.5–6.4%).

## Data

| Item | Value |
|---|---|
| NESO 1-second frequency | 109 months, Jul 2017 – Jul 2026 |
| Month excluded by QC | 1 (2024-05; coverage 66.5% < 95% rule) |
| Analysed half-hours | 152,148 (57,022 pre-battery; 95,126 post) |
| Inertia | NESO outturn and market-provided, half-hourly (ends 26 Jul 2026) |
| Demand and embedded wind/solar | NESO historic demand data |

## Known-answer gate G1: PASSED

- **Pre-registered rule:** pass if the inertia coefficient on log(RoCoF/depth) has an upper 95% bound below 0, with at least 50 events.
- **Pooled:** β = −0.164 [−0.223, −0.104], n = 3,385 loss events.
- **Pre-battery only:** β = −0.195 [−0.332, −0.057].
- **Caveat: the pass comes from event depth, not event RoCoF.**
  - Depth rises with inertia: +0.160 [0.118, 0.201].
  - The largest 1-s fall does not change with inertia: −0.004 [−0.067, 0.059].
  - The likely reason is truncation. Events are selected by a 1-s fall of at least 20 mHz/s, and the median event RoCoF is only 24–25 mHz/s, so there is little range left for inertia to act on.
  - This means 1-s data cannot resolve the inertial RoCoF of individual events directly. The outcomes below are best described as second-to-second frequency roughness, not RoCoF.

## Main results (Y1 = log 99.9th percentile of |Δf| per half-hour)

| | Pre-battery | Post-battery | Difference |
|---|---|---|---|
| β on log inertia | −0.348 [−0.403, −0.294] | −0.326 [−0.383, −0.269] | +0.023 [−0.009, +0.054] |

**Hypotheses:**
- **H1 (lower inertia → rougher frequency):** supported.
- **H2 (batteries changed the link):** no evidence of change.
- **H3 (floor 120 → 102):** +5.4% [4.5, 6.4].

**Secondary outcomes:**
- **Y2 (log SD):** pre +0.059 [0.026, 0.092]; post +0.008 [−0.016, 0.033]. Within-half-hour wander is not reduced by inertia.
- **Y3 (lag-1 autocorrelation):** effect of ~0.001, negligible.
- **Y4 (any seconds outside 49.8–50.2 Hz):** null in both eras.

## Sensitivity checks (pre-registered)

- **S1, floor natural experiment:** uninformative. The first stage is weak: −0.85 [−2.25, 0.56].
- **S2, placebo shuffles (50 shuffles within year × month × hour):**
  - mean β pre −0.054 (SD 0.005); post −0.006 (SD 0.004);
  - the real effects (−0.35 / −0.33) are far outside the placebo distribution.
- **S3, robustness of Y1 (pre / post):**
  - market-provided inertia: −0.297 / −0.277;
  - excluding event half-hours: −0.327 / −0.305;
  - excluding 2022: −0.389 / −0.353.

## Exploratory check (not pre-registered): is it really just wind?

- Added transmission wind, solar and import shares (NESO historic generation mix) as controls.
  - β pre −0.381 [−0.501, −0.261]; post −0.356 [−0.480, −0.232].
  - Wind share itself: −0.004 [−0.151, 0.142].
- With the full fuel mix added: β −0.380 / −0.373. The effect holds.
- Collinearity is high: the controls explain 93–94% of the variance in log inertia. Even so, the confidence intervals stay well clear of zero.

## Deviations from the pre-registration

1. **Window end:** the post-battery era ends 26 Jul 2026, not 31 Oct, because NESO inertia data stop there.
2. **Era term:** the era main effect was dropped from the main models. It is perfectly collinear with year fixed effects (absorbed, not a change in estimand); keeping it gave singular cluster covariance.
3. **Y2:** half-hours with SD = 0 (n = 7, frozen data) were set to missing for the log.
4. **Gate events:** the gate model also included 86 transition-era events, through an era fixed effect.

## Files

- results.json
- explore_wind.json
- analysis_events.csv
- analysis.py
- explore_wind.py

# Numbers check: "Inertia and grid frequency roughness in Great Britain, 2017–2026" (doc rev 14)

Checked against /home/claude/grid/out/*.json and *.csv. I also recomputed numbers from the half-hour table, the event table, raw inertia CSVs, grid_dc.json, the pre-registration (/mnt/attach/outputs/grid/PREREGISTRATION_grid_inertia.md) and Addendum 1 (/mnt/attach/outputs/grid_results/PREREG_ADDENDUM_1.md). Recompute scripts: /home/claude/verify/v1.py–v5.py.

Notation: "unadj" = NESO outturn inertia H; "adj" = Pathfinder-adjusted H_adj (A1). Floor effect = 100·(exp(β·ln(102/120)) − 1).

## A. WRONG / UNSUPPORTED / internally inconsistent (fix before submission)

| # | Location | Claim as written | Verified value | Status | Fix |
|---|---|---|---|---|---|
| 1 | 4.3, para 1 | "Stability Pathfinder units were providing inertia in **26% of battery-era half-hours**" | 0.2605 is the share of **all** analysed half-hours, both eras (a1_pathfinder.py takes the mean over the whole sample `d`). Battery-era share = **41.7%**. Since Sep 2023 = 82.0%. First non-zero Pathfinder half-hour = 1 Mar 2024. | WRONG | "in 42% of battery-era half-hours (82% since September 2023)", or "26% of all half-hours analysed". |
| 2 | 4.5, note under table | "Floor effects use Pathfinder-adjusted inertia (A1); **unadjusted results are within 0.01**." | Y5 β: adj vs unadj differ by 0.006 (true). **Y6 β_post: −0.253 adj vs −0.279 unadj (0.026). Y6 β_pre: −0.141 vs −0.169 (0.028).** Floor %: Y5 0.7% adj vs 0.8% unadj (0.83, CI 0.35–1.32); **Y6 4.2% adj vs 4.6% unadj (4.65, CI 2.26–7.08)**. "Within 0.01" holds for Y6 only if read as a proportion (0.042 vs 0.046), which nobody will read from a table printed in %. | WRONG for Y6 | Drop the sentence or give both: "Unadjusted: Y5 +0.8% (0.3–1.3%), Y6 +4.6% (2.3–7.1%)." |
| 3 | 4.5 table | β before/after columns (Y5 −0.067/−0.051; Y6 −0.169/−0.279) next to floor column (+0.7%, +4.2%) | β columns are **unadj** (a2 `Y5_H`, `Y6_H`). Floor column is **adj** (a2 `Y*_H_adj`). From the printed Y6 β_after (−0.279), a reader gets **+4.6%**, not +4.2%. | INCONSISTENT | Use one basis per row. Either print adj βs (Y5 −0.061/−0.045; Y6 −0.141/−0.253) or print unadj floor effects (0.8%, 4.6%). |
| 4 | Abstract para 1, Discussion para 1, Conclusion | Y1: "about 5% rougher (95% CI 4.5–6.4%)"; Y6: "about 4% to the time … more than 0.1 Hz from target" | The Y1 CI 4.5–6.4 is **unadj** (results.json H3: 5.44, 4.47–6.41). The Y6 "about 4%" is **adj** (4.20). Unadj Y6 = 4.65% ("about 5%"). Two headline numbers in the same sentence pair use different exposures. | INCONSISTENT | Pick one basis. All unadj: Y1 5.4% (4.5–6.4), Y6 4.6% (2.3–7.1), Y5 0.8%. All adj: Y1 5.3% (4.4–6.3), Y6 4.2% (1.8–6.7), Y5 0.7% (0.2–1.2). Say which in the abstract. |
| 5 | 4.3 bullet "floor effect" | "5.4% (4.3–6.4%)" (adj) | From unrounded adj β (−0.32052; CI −0.37855, −0.26249): **5.35% (4.36–6.35%) → 5.3% (4.4–6.3%)**. The JSON value comes from rounding β to 3 dp first, then rounding again. | IMPRECISE (double rounding) | "5.3% (4.4–6.3%)", or compute from unrounded β in a1_pathfinder.py. |
| 6 | 3.5, "Exploratory." | "**One check** was not pre-registered: transmission wind, solar and import shares, and then the full fuel mix" | Also not in the pre-registration or the addendum: (a) separate-era Y1 fits (sens_separate_eras.json, cited in H2 para); (b) separate-era Y5/Y6 fits (cited in 4.5 and in the Discussion's main interpretation); (c) Figure 1 binscatter. No script in /home/claude/grid produces sens_separate_eras.json or binscatter.csv. I reproduced the Y1 separate-era numbers (−0.2545 / −0.3304; diff −0.076, −0.171 to 0.019) with `Y1 ~ logH + controls` per era. | WRONG / UNSUPPORTED (no code) | Label the separate-era fits and Figure 1 as exploratory. Add the script that generates them to the repository. |
| 7 | 1 (end) | "every deviation is reported" | Unreported deviations: (a) the gate keeps **86 transition-quarter (Oct–Dec 2020) events** (3,385 = 920 pre + 2,379 post + 86 trans), but the pre-registration and Section 2 say Oct–Dec 2020 is excluded; (b) pre-registered E1 (Kp geomagnetic index) is never mentioned; (c) A2 floor effects use H_adj, but the addendum says A2 uses "the same model as the main model" (H). | WRONG | Report all three, or rerun the gate without the 86 events. |
| 8 | 4.1 | "Across 3,385 loss events …" (and Section 2: "Oct–Dec 2020 … was excluded as a transition period") | 3,385 includes the 86 transition events (results.json `events_by_era`). | INCONSISTENT | "3,385 events (920 pre, 2,379 post, 86 in the Oct–Dec 2020 transition)". Or exclude them and rerun. |
| 9 | 4.4, para after table | "Once inertia is in the model, wind share itself adds nothing: −0.004 (−0.151 to 0.142)" | That is the +wind/solar/imports model. In the **full fuel-mix model**, which the table also reports, wind share = **+0.422 (0.280 to 0.563)**, clearly significant. | WRONG (selective) | "With wind, solar and imports added, wind share is null (−0.004, −0.151 to 0.142). With the full mix it becomes positive (+0.42, 0.28–0.56), but the inertia coefficient is unchanged." |
| 10 | Discussion, "Batteries and inertia do different jobs" | "has not weakened the link … **if anything it is slightly steeper in the battery era**" | Pre-registered joint model (and abstract): **less** steep after, −0.348 → −0.326 (Δ +0.023). A1 adj: −0.337 → −0.321 (less steep). Only the non-pre-registered separate-era fit is steeper (−0.255 → −0.330, which is 30% steeper, not "slightly"). Binscatter slopes: −0.24 pre vs −0.38 post. | INCONSISTENT with Abstract and 4.2 table | "The pre-registered model shows no change (−0.35 vs −0.33). Era-by-era fits point slightly the other way. Neither difference is significant." |
| 11 | 4.2 Figure 1 text | "The battery-era dots … are, if anything, slightly steeper" | Matches the binscatter (OLS slope through bin points −0.238 pre, −0.385 post) and the separate-era fit. But the figure is "each era fitted separately", so it shows the exploratory specification, not the pre-registered one, which goes the other way. On the figure, −0.24 vs −0.38 is visibly steeper, not "slightly". | IMPRECISE | Say the figure shows era-by-era fits and that the pre-registered joint model shows no steepening. |
| 12 | 4.5 last para; Discussion | "Batteries appear to have dulled the effect of low inertia on how far and how long frequency strays … but not on how sharply it jolts"; Discussion: "This fits the physics … So batteries look like they contain how far and how long frequency strays" | Rests entirely on the separate-era fits. In the pre-registered joint model the direction reverses for every outcome: Y1 weaker after (+0.023); **Y6 stronger after (β −0.169 → −0.279, Δ −0.111)**; Y5 Δ +0.016 (n.s.). 4.5 itself says "this is a pattern to report, not a finding", but the Discussion then builds a physical explanation on it. | INCONSISTENT / overclaim | In the Discussion, keep the caveat and drop "This fits the physics … So batteries look like …", or state plainly that the joint model shows the opposite for Y6. |
| 13 | Limitations, "Exposure" | "Measurement error would bias the estimates toward zero, so the reported effects are conservative" | No output supports this. NESO inertia error is not classical noise. The one measured correction (A1, adding missing Pathfinder inertia) moved β_post toward zero (−0.326 → −0.321) and Y6 β_post toward zero (−0.279 → −0.253), the opposite of what attenuation predicts. | UNSUPPORTED | "If the error were classical it would bias toward zero, but the A1 correction moved estimates slightly toward zero, so the direction of any remaining bias is unknown." |
| 14 | Limitations, "Confounding" | "Controls for … the full fuel mix **leave the estimate unchanged**" | β_pre −0.348 → −0.381 / −0.380; β_post −0.326 → −0.356 / −0.373 (9–14% larger in magnitude). CIs widen to about (−0.52, −0.23). R² of logH on controls rises 0.84 → 0.94, so only about 6% of inertia variation is left to identify the effect. | IMPRECISE | "do not shrink the estimate (it grows by about 10%)". Also mention the R² point. |
| 15 | Intro para 2 | "a change estimated to save **about** £96m a year [2]" | The Ofgem May 2026 decision quotes NESO: "potential savings (**up to** £96m per year)". | IMPRECISE | "up to £96m a year". |
| 16 | 4.1 / gate interpretation | "Depth rose with inertia: +0.160 (0.118 to 0.201)"; the gate "passed" | The numbers are correct. But depth rising with inertia is the **opposite** of the physics the gate is meant to test: for the same loss, more inertia gives a shallower fall. That points to loss size rising with inertia, the confound K was meant to cancel. Because the initial fall is flat (−0.004), K falls only because its denominator grows. So the gate passed through an artefact, not through physics. The text blames selection for the flat initial fall but never says the depth sign is counter-physical. A referee will spot this. | INTERPRETATION GAP | Add one sentence: depth rising with inertia likely reflects larger losses at high-inertia times, so the gate pass is weak evidence that one-second data resolve inertia. |
| 17 | Abstract | "The result held when we … ran placebo shuffles" | Placebo means: pre **−0.054 (SD 0.005)**, about 11 SD from zero and about 15% of the real β_pre. Post −0.006 (SD 0.004). The pre-registration says placebo "β should be about 0". The pre-era placebo is not zero, probably because year, month and hour effects enter additively while shuffling is within their interaction. | IMPRECISE | In 4.4, say the pre-era placebo retains about 15% of the effect and give the likely reason. The real effect is still about 6× larger. |
| 18 | Ref 3 | "Bell, K. (2026)" | The Ofgem page (3 Mar 2026) names no author. | UNSUPPORTED | Confirm the author from the PDF, or cite as Ofgem (2026). |
| 19 | Section 4.2 / Methods outcomes vs QC | "Seven half-hours where frequency was frozen (zero variance) were set to missing" | Confirmed: 7 half-hours with sd = 0. They are missing only for Y1–Y3. They stay in the Y4 sample (N 152,148) and in Y5/Y6 (n_used 152,148). | IMPRECISE | "…were set to missing for Y1–Y3." |

## B. Minor / wording

| # | Location | Claim | Verified | Status | Fix |
|---|---|---|---|---|---|
| 20 | Abstract para 4; Discussion | "about 1%" (DC proxy for the cut); Discussion "about 1% more energy" | 0.7% adj (0.2–1.2), 0.8% unadj (0.3–1.3) | IMPRECISE | "under 1%". "Energy" overstates a delivery-fraction-seconds proxy. Use "delivery". |
| 21 | 4.5 table, Y6 typical value | "309 (mean)" | Mean 308.5 ✓. Median 212. The distribution is skewed, and the next row uses a median (Y5, 21). | IMPRECISE | Use the median (212) for consistency, or label both. |
| 22 | Conclusion | "Less inertia means … more time off target" | Y6 pre-battery joint β −0.169 (−0.356 to 0.019) is not significant. Post is significant. | IMPRECISE | "more time off target in the battery era". |
| 23 | 4.2 Y2/Y3 | "The secondary outcomes showed little": Y2 "+0.059 … none after"; Y3 "negligible" | Numbers ✓. Not mentioned: the Y2 era change is significant (Δ −0.051, −0.077 to −0.024), and Y2's positive sign means *more* inertia goes with more wander. Y3 is significant in both eras (pre 0.0019, p ≈ 1e-19; post 0.0008) with a significant Δ (−0.0011), although the magnitudes are tiny. | IMPRECISE (omission) | Report the Y2 Δ and its sign. Say Y3 is "statistically detectable but tiny". |
| 24 | 4.2 H1 | "A 10% fall in inertia raises … jolts by about 3.5–3.7%" | 3.74% (pre), 3.49% (post) ✓. These are the two era point estimates, not a CI. | OK / clarify | "3.7% before batteries, 3.5% after". |
| 25 | Figure 1 caption vs abstract | 152,141 vs 152,148 half-hours | 152,148 analysed. 152,141 in the Y1 regressions (7 frozen dropped) ✓ | OK, note | Leave as is, or add one clause explaining the 7. |
| 26 | Data table, Pathfinder | "Sep 2023 onward" | The data start 4 Sep 2023, but the first non-zero Pathfinder half-hour is 1 Mar 2024. Mid-term Y-1 is non-zero only from 4 Oct 2025 (3,265 half-hours). | OK, could clarify | The "since Sep 2023" subsample includes about 6 months with zero Pathfinder. |
| 27 | Intro | "Average GB inertia fell from about 260 to 175 GVA.s between 2017–18 and 2025–26" | FY mean outturn: 2017–18 259.9; 2025–26 174.8 ✓ (2026–27 partial to 26 Jul: 151.2) | OK | — |

## C. Verified OK

| Location | Claim | Verified value |
|---|---|---|
| Abstract | β −0.35 before, −0.33 after | −0.3483, −0.3257 |
| Abstract/Data | 152,148 half-hours; 57,022 / 95,126 | results.json bins ✓; pre 2017-07-01–2020-09-30, post 2021-01-01–2026-07-26 ✓ |
| Data | 109 months; May 2024 excluded at 66.5% | 109; 0.66531 ✓ |
| Data | ≥95% month coverage; ≥1,700 of 1,800 seconds | code ✓ (the 1,700 rule dropped 9 half-hours) |
| Data | Inertia Apr 2017 – 26 Jul 2026 | 2017-04-01 to 2026-07-26 ✓ |
| Methods | Loss-event definition (20 mHz, 30 s, 100 mHz below 10-s mean, 120 s merge); per-event measures | pipeline_v4.js ✓ |
| Methods | DC curve (0 to ±0.015; 5% at 0.2; 100% at 0.5) | pass2.js ✓ |
| Methods | Controls, clustering by date, era main effect dropped | analysis.py ✓ |
| 4.1 | β −0.164 (−0.223 to −0.104); pre-only −0.195 (−0.332 to −0.057) | ✓ (pre n = 920) |
| 4.1 | depth +0.160 (0.118–0.201); fall −0.004 (−0.067–0.059) | ✓ |
| 4.1 | median fall 24–25 mHz | overall 25; pre 24; post 25 ✓ |
| 4.2 table | −0.348 (−0.403, −0.294); −0.326 (−0.383, −0.269); +0.023 (−0.009, +0.054) | ✓ |
| 4.2 H2 sep-era | −0.255 vs −0.330; Δ −0.076 (−0.171, 0.019) | reproduced: −0.2545, −0.3304, −0.0759 (−0.1708, 0.0191) ✓ |
| 4.2 H3 | 5.4% (4.5–6.4%) | 5.436 (4.467–6.414) unadj ✓ |
| 4.2 Y2 pre | +0.059 (0.026–0.092) | ✓ |
| 4.3 | median 9.9 GVA.s; about 6% of measured inertia | 9.895; 0.0595 ✓ |
| 4.3 | β_post −0.321 (−0.379, −0.262); Δ +0.016 (−0.016, 0.048) | ✓ |
| 4.3 | since Sep 2023: −0.388 → −0.357 | ✓ (N 48,327) |
| 4.4 table | S3 −0.297/−0.277; −0.327/−0.305; −0.389/−0.353; placebo −0.054 (0.005)/−0.006 (0.004); +wsi −0.381/−0.356; full mix −0.380/−0.373 | ✓ all |
| 4.4 | S1 first stage −0.85 (−2.25 to 0.56) | ✓ (n 15,911) |
| 4.5 | Y5 −0.067 (−0.105, −0.030); −0.051 (−0.081, −0.021); Δ +0.016 (−0.013, 0.045) | unadj ✓ |
| 4.5 | Y6 −0.169 (−0.356, 0.019); −0.279 (−0.421, −0.138); Δ −0.111 (−0.258, 0.036) | unadj ✓ |
| 4.5 | Floor Y5 +0.7% (0.2–1.2); Y6 +4.2% (1.8–6.7) | adj: 0.73 (0.23–1.23); 4.20 (1.75–6.72) ✓ (see #2–#4) |
| 4.5 | 21 FDE-seconds (median) | 20.95 ✓ |
| 4.5 | sep-era Y5 −0.163 vs −0.042; Y6 −0.76 vs −0.22 | −0.163/−0.042; −0.760/−0.216 ✓ |
| 4.5 | H4 supported in both eras | Y5 CIs exclude 0 in both eras ✓ (Y6 pre does not) |
| Discussion | 15% cut | 1 − 102/120 = 0.150 ✓ |
| Methods | Pre-registration before 1-s data processed (13 Nov 2026) | prereg file 13:37 CST; full frequency data 16:39 CST ✓. Addendum 18:22 CST; Pathfinder data 18:26, DC data 19:41/20:48 ✓ |
| Intro refs | Floor 140→130 Feb 2024, →120 Jun 2024; Ofgem 28 May 2026, 110 then 102, ≥10-week trial; Ofgem quotes | Watt-Logic: 140 until 28 Feb 2024, 130 until 18 Jun 2024 ✓. Ofgem decision 28 May 2026 ✓. Independent review 3 Mar 2026, both quotes ✓ |

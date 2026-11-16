# Pre-registration Addendum 1: GB grid inertia study

Locked 13 Nov 2026, ~00:30 UTC on 14 Nov, after the main results were seen.

Everything here is labelled **post-hoc but specified before the new data are computed**. Neither new analysis can change the primary results already reported; both are reported in full whatever they show.

## A1. Missing inertia from Stability Pathfinder units

**Why:** NESO's outturn inertia excludes Stability Pathfinder units. These units run from Sep 2023 onward, inside the post-battery era only, so their omission could bias the H2 comparison.

**Data:** NESO Stability Pathfinder Utilisation Reports (2023-24 onward) and the Stability Mid-term Y-1 utilisation report, all half-hourly, per unit.

**Method:**
1. **Adjusted inertia:** H_adj = H + Σ unit inertia in the half-hour, counting a unit only where it is instructed or delivering in that half-hour.
2. **Rerun with H_adj:** the main Y1 model and H2.
3. **Report:**
   - β_post and Δ with H_adj;
   - β_post restricted to half-hours from Sep 2023 onward, using H vs H_adj.

**Interpretation rule:** the H2 conclusion stands if Δ's 95% CI under H_adj still includes 0, and the point estimate does not move by more than 0.05.

## A2. Operational outcome: Dynamic Containment (DC) delivery proxy

**Why:** Y1 measures second-to-second roughness. The operational quantity that matters is how much fast frequency response the system calls on.

**Definition:** for each second, compute the DC delivery fraction g(|Δf|) from the published DC service curve:
- 0 inside the deadband, |Δf| ≤ 0.015 Hz;
- rises linearly to 5% at 0.2 Hz;
- rises linearly from 5% to 100% between 0.2 and 0.5 Hz;
- 100% beyond 0.5 Hz.

**Outcomes per half-hour:**
- **Y5** = log(1 + Σ g), the DC delivery proxy, in delivery-fraction-seconds. Primary for A2.
- **Y6** = log(1 + number of seconds with |Δf| > 0.1 Hz).

**Model:** the same as the main model (logH × era, with the same fixed effects and controls), clustered by date.

**Hypothesis H4:** lower inertia means more DC delivery, i.e. β < 0, in both eras.

**Interpretation:**
- If β_post's 95% CI excludes 0: report the predicted % change in Y5 for moving the floor from 120 to 102 GVA.s, the same calculation as H3.
- If it includes 0: report that inertia does not measurably change how much fast response is called on, alongside the roughness result.

**Note:** g applies the battery-era service curve to both eras. Before Oct 2020 it is a hypothetical demand, "what DC would have had to deliver", not actual delivery.

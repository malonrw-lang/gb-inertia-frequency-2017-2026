# Pre-registration addendum 2 — A3: known-answer check normalised by MW lost

Written 2026-11-13, before any REMIT data were matched to frequency events or any model was fitted.

## Why
The original gate divided RoCoF by the depth of the dip. Depth itself depends on inertia and on the response services, so it is a weak denominator. Physics gives a cleaner known answer: in the first seconds after a loss,
RoCoF = ΔP · f0 / (2 · E_kin). With ΔP measured independently, log RoCoF should fall one-for-one with log inertia.

## Data
Elexon BMRS REMIT messages (public API, dataset REMIT), all messages with unavailabilityType = "Unplanned", published 30 Jun 2017 – 31 Jul 2026.
Per message, the first revision only (the initial notification). Only messages with unavailableCapacity ≥ 100 MW.

## Matching (fixed in advance)
- Detected loss events are the existing 3,385 events (unchanged definition).
- A REMIT message matches an event at time t if its eventStartTime is in [t − 180 s, t + 120 s] and it was published between t − 60 s and t + 6 h.
- One row per unit (largest message kept if a unit has several).
- Primary sample: events with exactly one matched unit. MW lost = that message's unavailableCapacity.
- Sensitivity 1: all matched events, MW lost = sum across matched units.
- Sensitivity 2: windows ±60 s, and [−900 s, +300 s].
- Sensitivity 3 (closer to the MW actually lost): for primary matches, MW lost = min(unavailableCapacity, the unit's Physical Notification level at the event time, from Elexon PN). Events where PN cannot be found for the unit are dropped from this sensitivity only.

## Models
- Primary: log(RoCoF / MW) ~ log H, robust (HC1) SEs. Prediction: slope < 0, CI excluding 0. Physics value is −1.
- Joint: log RoCoF ~ log H + log MW (expect −1 and +1), and the same with hour and month controls.
- By era (pre-battery, battery) for the primary model.

## Reading the result
- PASS (gate): primary slope negative with CI excluding 0, on ≥ 50 matched events.
- Known answer recovered: CI includes −1. A slope between 0 and −1 is expected attenuation (1-s sampling, RoCoF measured as the largest 1-s fall in the first 5 s, response services acting within that window, unavailable capacity ≥ actual output) and will be reported as such, not as failure.
- Fewer than 50 unique matches: report as not feasible with public data; keep the paper's current "weak support" wording.

## Known limitations, stated in advance
- unavailableCapacity is declared capacity lost, not the MW actually being generated at the moment of the trip; it overstates ΔP for part-loaded units. This biases the MW slope toward 0 and adds noise, not a sign flip in the inertia slope.
- REMIT start times may be rounded; the start-time precision is reported.
- Interconnector and embedded-generation losses may be missing from REMIT.

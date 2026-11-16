# Data sources

All inputs are public. They are included so the analysis runs without downloading anything.

| File(s) | What it is | Publisher | Where |
|---|---|---|---|
| `inertia_gb_system_inertia_-_*.csv` | Half-hourly outturn and market-provided inertia (GVA.s) | NESO | NESO data portal, "System Inertia" |
| `demand_historic_demand_data_*.csv` | Half-hourly national demand and embedded wind and solar | NESO | NESO data portal, "Historic Demand Data" |
| `genmix_2017on.csv` | Half-hourly generation mix | NESO | NESO data portal, "Historic generation mix" |
| `grid_freq_full.json` | Half-hour frequency summaries and loss events computed by `code/pipeline.js` from NESO's 1-second system frequency files | Derived from NESO | NESO data portal, "System Frequency Data" |
| `grid_pathfinder.json` | Stability Pathfinder utilisation (MVA.s per unit per settlement period) | NESO | NESO data portal, Stability Pathfinder utilisation reports |
| `grid_dc.json` | Per half-hour, computed by `code/pass2.js` from the 1-second files: seconds observed, summed Dynamic Containment delivery proxy, and seconds beyond ±0.1 Hz | Derived from NESO | As above |
| `grid_remit_unplanned.json` | First notification of each unplanned REMIT outage of 100 MW or more, 2017–2026 | Elexon | Elexon Insights Solution API, dataset REMIT |

NESO data are published under the NESO Open Data Licence, which allows reuse with attribution. Contains public sector information from the National Energy System Operator (NESO).

Elexon data are reused under Elexon's open data licence for the Insights Solution (BMRS), which allows reuse with attribution: Contains BMRS data © Elexon Limited copyright and database right.

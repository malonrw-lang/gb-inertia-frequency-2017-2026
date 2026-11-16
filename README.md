# Inertia and grid frequency roughness in Great Britain, 2017–2026

Code and data for the paper of the same name.

**What it shows.** Great Britain's system operator is cutting its minimum grid inertia from 120 to 102 GVA.s, a change it estimates saves up to £96m a year. Projecting nine years of public one-second frequency data, matched to the operator's half-hourly inertia estimates, onto that change: second-to-second frequency about 4% rougher (95% CI 3.5–5.1%) in the third of half-hours when the floor binds, about 1.4% averaged over all half-hours. There is no evidence that the battery fast-response service launched in 2020 has weakened the link.

## Reproduce every number in the paper

Needs Python 3.10+ and the packages in `requirements.txt`.

```bash
pip install -r requirements.txt
./run_all.sh
```

It takes a few minutes. Outputs go to `out/`. Compare them with `results_reference/`, which holds the outputs used in the paper. A clean re-run from this repository matched the reference files exactly (13 Nov 2026).

## What's here

| Folder | Contents |
|---|---|
| `prereg/` | The written analysis plan, fixed before the one-second data were processed, and two addenda (each written before its own analysis was run). Not lodged with an external registry. |
| `code/` | `pipeline.js`, `pipeline_v4.js`, `pass2.js`: the browser-side scripts that read NESO's one-second frequency files and reduced them to half-hour summaries and loss events. `split.py` unpacks their output. `analysis.py` is the pre-registered analysis. `a1_pathfinder.py`, `a2_dc.py`, `a3_mwgate.py` are the addendum analyses. `explore_wind.py` and `sens_eras_binscatter.py` are exploratory and sensitivity checks |
| `data/` | Inputs (see `DATA_SOURCES.md`) |
| `verify/` | Scripts used for an independent check of the numbers |
| `results_reference/` | Outputs used in the paper, the results summary, and the independent check report |

## Order of the analysis

1. `split.py` turns `data/grid_freq_full.json` (half-hour summaries and loss events computed from 1-second data) into CSVs.
2. `analysis.py` joins them to inertia and demand, and runs the known-answer gate and hypotheses H1–H3.
3. `a1_pathfinder.py` adds Stability Pathfinder inertia back in (addendum 1).
4. `a2_dc.py` tests the Dynamic Containment delivery proxy (addendum 1, H4).
5. `explore_wind.py`, `sens_eras_binscatter.py`: exploratory and sensitivity analyses, labelled as such in the paper.
6. `a3_mwgate.py` tries to divide loss events by megawatts lost, using REMIT outage notices (addendum 2). It did not work; see the paper, Section 4.1.
7. `review_reruns.py` runs the checks added after pre-submission review: dropping five days of faulty inertia data, grouping standard errors by week, and counting the floor effect only when the floor binds.

The one-second files themselves are not included (several GB). `code/pipeline.js` documents exactly how they were reduced; the files are on NESO's data portal.

## Licence

Code: MIT (see `LICENSE`). Data: reused from NESO and Elexon under their terms (see `DATA_SOURCES.md`).

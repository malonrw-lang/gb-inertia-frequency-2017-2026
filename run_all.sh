#!/usr/bin/env bash
# Re-runs every analysis in the paper from the files in data/. Takes a few minutes.
# Requires Python 3.10+ with numpy, pandas, statsmodels (see requirements.txt).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p out
python code/split.py data/grid_freq_full.json data          # 1-s pipeline output -> grid_bins/events/qc.csv
python code/analysis.py data out                            # pre-specified analysis (H1-H3, gate, S1)
python code/a1_pathfinder.py                                # addendum 1: Pathfinder-adjusted inertia
python code/a2_dc.py data/grid_dc.json                      # addendum 1: Dynamic Containment proxy (H4)
python code/explore_wind.py                                 # exploratory: wind share
python code/sens_eras_binscatter.py                         # sensitivities + Figure 1 data
python code/a3_mwgate.py data/grid_remit_unplanned.json     # addendum 2: MW-normalised gate
python code/review_reruns.py                                 # post-hoc sensitivity checks (faulty days, week clustering, drop-2022, floor binding)
echo "Done. Compare out/ with results_reference/."

#!/usr/bin/env python
"""Run the full model comparison: baseline + every candidate model, then report.

Run directly with `python scripts/run_experiment.py`. It's deliberately separate from
`python -m model_origin evaluate` (a single model's numbers, used by `make reproduce`
for the quick-start check) — this script is the one that produces the comparison
table in README.md and the experiment log in results/experiments.md, including a
model we tried and rejected (see the SVM entry below): the negative result is
recorded here on purpose, not deleted, because a documented dead end is part of
showing the actual work, not a failure to hide.
"""

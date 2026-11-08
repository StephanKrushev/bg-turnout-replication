"""Closing forecasts from the paper's original q=0 filter, one assumption changed at a time."""
import csv
import json
from pathlib import Path

import numpy as np

from turnout_filter import run

root = Path(__file__).resolve().parent
baseline = json.loads((root / 'forecast_figure_results.json').read_text())['cutoffs']
settings = [
    ('Baseline', {}), ('Persistence 1 h', {'tau': 1}), ('Persistence 4 h', {'tau': 4}),
    ('Log-rate SD 0.075', {'s': .075}), ('Log-rate SD 0.30', {'s': .30}),
    ('Reporting SD 0.25 pp', {'report_sd': .0025}), ('Reporting SD 1 pp', {'report_sd': .01}),
    ('Prior multiplier 1.0', {'prior_multiplier': 1}),
]
with (root / 'ou_sensitivity.csv').open('w', newline='') as out, (root / 'ou_sensitivity_table.tex').open('w') as table:
    writer = csv.writer(out)
    writer.writerow(['change', 'cutoff', 'latent_p05', 'median', 'latent_p95', 'report_p05', 'report_p95'])
    for label, params in settings:
        for cutoff in ([12, 16] if label in ('Baseline', 'Prior multiplier 1.0') else [16]):
            endpoints = [run(cutoff, seed, endpoint_only=True, **params)[0][-1, 1:]
                         for seed in (418, 419, 420)]
            row = np.mean(endpoints, axis=0)
            if not params:
                np.testing.assert_allclose(row, baseline[str(cutoff)]['path'][-1][1:], atol=1e-8)
            low, median, high, report_low, report_high = row
            writer.writerow([label, cutoff, *row])
            table.write(f'{label} & {cutoff}:00 & {median:.2f} & {low:.2f}--{high:.2f} & '
                        f'{report_low:.2f}--{report_high:.2f} '+r'\\'+'\n')

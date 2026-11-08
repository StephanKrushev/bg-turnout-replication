"""Particle filter shared by the forecast figure and parameter checks."""
import csv
from pathlib import Path

import numpy as np

P = Path(__file__).resolve().parent
with (P / 'working_turnout.csv').open() as stream:
    records = list(csv.DictReader(stream))
base = np.array([float(r['round1_percent']) / 100 for r in records])
obs = np.array([float(r['round2_percent']) / 100 for r in records if r['round2_percent']])
hazard = -np.diff(np.log1p(-base))


def run(cut, seed, N=40000, *, tau=2, s=.15, report_sd=.005, prior_multiplier=1.2,
        endpoint_only=False):
    rng = np.random.default_rng(seed)
    plot_rng = np.random.default_rng(seed + 10000)
    turnout = np.full(N, obs[0])
    theta = rng.normal(np.log(prior_multiplier), .25, N)
    deviation = rng.normal(0, s, N)
    persistence = np.exp(-1 / (12 * tau))
    innovation_sd = s * np.sqrt(1 - persistence**2)
    rows = []
    scale = None

    def summary(time, report):
        latent = np.quantile(turnout, [.05, .5, .95]) * 100
        reported = np.quantile(report, [.05, .95]) * 100
        return [time, *latent, *reported]

    for hour in range(9, 21):
        for step in range(12):
            deviation = persistence * deviation + innovation_sd * rng.normal(size=N)
            rate = hazard[hour - 9] * np.exp(theta + deviation)
            turnout = 1 - (1 - turnout) * np.exp(-rate / 12)
            if hour > cut and step < 11 and not endpoint_only:
                report = turnout + plot_rng.normal(0, report_sd, N)
                rows.append(summary(hour - 1 + (step + 1) / 12, report))
        if hour <= cut:
            log_weight = -.5 * ((turnout - obs[hour - 8]) / report_sd)**2
            weight = np.exp(log_weight - log_weight.max())
            weight /= weight.sum()
            positions = (rng.random() + np.arange(N)) / N
            indices = np.searchsorted(np.cumsum(weight), positions)
            turnout, theta, deviation = turnout[indices], theta[indices], deviation[indices]
            if hour == cut:
                rows.append(summary(cut, turnout + plot_rng.normal(0, report_sd, N)))
                scale = np.quantile(np.exp(theta), [.05, .5, .95]).tolist()
        else:
            # Keep hourly report draws in the original simulation stream.
            report = turnout + rng.normal(0, report_sd, N)
            if not endpoint_only or hour == 20:
                rows.append(summary(hour, report))
    return np.array(rows), scale

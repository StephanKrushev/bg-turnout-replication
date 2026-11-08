"""Figures for the short working paper, using the archived forecast and historical age weights."""
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

root = Path(__file__).resolve().parent
with (root / 'working_turnout.csv').open() as f:
    inputs = list(csv.DictReader(f))
hours = np.array([int(r['hour']) for r in inputs])
first = [float(r['round1_percent']) for r in inputs]
second = [float(r['round2_percent']) for r in inputs if r['round2_percent']]
with (root / 'official_turnout_audit.csv').open() as f:
    close = next(float(r['turnout_percent']) for r in csv.DictReader(f)
                 if r['round'] == '2' and r['hour'] == '20')
forecasts = json.loads((root / 'forecast_figure_results.json').read_text())['cutoffs']
t, low, median, high, report_low, report_high = np.array(forecasts['16']['path']).T

fig, (ax, closing) = plt.subplots(1, 2, figsize=(9, 3.2), layout='constrained',
                                  gridspec_kw={'width_ratios': [1.55, 1]})
ax.plot(hours, first, color='0.5', label='First round')
ax.fill_between(t, report_low, report_high, color='#cfdfed', label='90% future report')
ax.fill_between(t, low, high, color='#85b1cf', label='90% latent turnout')
ax.plot(t, median, color='#185782', label='Median')
ax.scatter(hours[:9], second[:9], s=15, color='black', label='Inputs through 16:00')
ax.scatter([17, 18], second[9:], facecolors='white', edgecolors='#ae591b', label='Later reports')
ax.scatter([20], [close], color='#ae591b', marker='D', label='Official close')
ax.set(xlabel='Hour of day', ylabel='Turnout (%)', xticks=range(8, 21, 2), title='Forecast from the 16:00 measurement')
ax.legend(loc='upper left', fontsize=7, ncol=2, frameon=False)
cutoffs = [12, 14, 16, 18]
ends = np.array([forecasts[str(c)]['path'][-1] for c in cutoffs])
closing.vlines(cutoffs, ends[:,4], ends[:,5], color='#cfdfed', lw=10)
closing.vlines(cutoffs, ends[:,1], ends[:,3], color='#85b1cf', lw=5)
closing.plot(cutoffs, ends[:,2], 'o-', color='#185782', ms=4)
closing.axhline(close, ls='--', color='#ae591b', label='Official close 28.67%')
closing.legend(frameon=False, fontsize=8)
closing.set(xticks=cutoffs, xlabel='Last measurement hour', ylabel='Closing turnout (%)',
            title='Forecast by cutoff')
for a in (ax, closing):
    a.spines[['top', 'right']].set_visible(False)
fig.savefig(root / 'paper_forecast.pdf')
plt.close(fig)

# Use the same rounded valid-vote counts as the historical appendix illustration.
weights = np.array([67, 702, 1131]) / 1900
age_index = np.arange(3)
shifts = .6 * (age_index - weights @ age_index)
t = np.linspace(8, 20, 241)
progress = np.interp(t, [*hours[:len(second)], 20], [*second, close]) / close
curves = progress[:, None] + np.outer(progress * (1-progress), shifts)
np.testing.assert_allclose(curves @ weights, progress, atol=1e-12)
assert np.all(np.diff(curves, axis=0) >= 0)
fig, ax = plt.subplots(figsize=(7.6, 2.9), layout='constrained')
for curve, label, color in zip(curves.T, ('18–30','31–60','61+'), ('#996127','#398564','#236a9e')):
    ax.plot(t, 100*curve, label=label, color=color)
ax.plot(t, 100*progress, '--', color='black', label='Common schedule / aggregate')
ax.set(ylabel="Share of group's final valid votes (%)", xlabel='Hour of day',
       xticks=range(8,21,2), yticks=range(0,101,25))
ax.spines[['top','right']].set_visible(False)
ax.legend(frameon=False, fontsize=9)
fig.savefig(root / 'paper_schedules.pdf')

with (root / 'presidential_history.csv').open() as stream:
    history = list(csv.DictReader(stream))
fig, axes = plt.subplots(2, 1, figsize=(7.0, 4.2), sharex=True, layout='constrained')
for number, label, marker, color in [('1', 'First round', 'o', '#205c86'),
                                     ('2', 'Runoff', 's', '#a14b22')]:
    rows = [row for row in history if row['round'] == number]
    years = [int(row['year']) for row in rows]
    assert years == [1992, 1996, 2001, 2006, 2011, 2016, 2021, 2026]
    counts = np.array([int(row['voters']) for row in rows])
    electorate = np.array([int(row['electorate']) for row in rows])
    turnout = 100 * counts / electorate
    np.testing.assert_allclose(turnout, [float(row['turnout_pct']) for row in rows], atol=.005)
    for axis, values in zip(axes, (turnout, counts / 1e6)):
        axis.plot(years, values, color=color, marker=marker, markersize=4,
                  linestyle='-' if number == '1' else '--', label=label)
axes[0].set(ylabel='Turnout (%)', ylim=(0,84), yticks=range(0,81,20))
axes[0].legend(frameon=False, ncol=2, loc='upper right')
axes[1].set(ylabel='Voters (millions)', ylim=(0,5.7), xticks=years, xlabel='Election year')
for axis in axes:
    axis.grid(axis='y', alpha=.18)
    axis.spines[['top','right']].set_visible(False)
fig.savefig(root / 'presidential_history.pdf')
plt.close(fig)

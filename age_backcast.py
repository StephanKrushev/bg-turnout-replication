"""Conditional continuous bounds, with exact domestic category totals."""
import csv
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

root = Path(__file__).resolve().parent
with (root / 'vote_counts.csv').open() as f:
    votes = list(csv.DictReader(f))
assert [row['choice'] for row in votes] == ['Yotova', 'Gyurov', 'Neither']
counts = np.array([int(row['national']) - int(row['overseas']) for row in votes])
total = counts.sum()
# Rows: age groups 18-30, 31-60, 61+. Columns: Yotova, Gyurov, neither.
poll = np.array([[32,61,7],[50,46,4],[63,35,2]]) / 100
cells = np.eye(9).reshape(3,3,9)
ages = cells.sum(axis=1)
categories = cells.sum(axis=0)

def solve(objective, tolerance):
    lower = (poll - tolerance)[:,:,None] * ages[:,None,:] - cells
    upper = cells - (poll + tolerance)[:,:,None] * ages[:,None,:]
    lhs = np.concatenate([lower, upper]).reshape(-1,9)
    result = linprog(objective, A_eq=categories, b_eq=counts/total,
                     A_ub=lhs, b_ub=np.zeros(len(lhs)), bounds=(0,None), method='highs')
    if result.success:
        assert max(abs(categories @ result.x - counts/total)) < 1e-7
        assert max(lhs @ result.x) < 1e-7
    return result

assert solve(np.zeros(9), 0).status == 2  # infeasible at the published percentages
rows = []
for tolerance_pp in (0.5,1,2):
    for g,age in enumerate(('18-30','31-60','61+')):
        for label,objective in zip(('all valid categories','Yotova','Gyurov','neither'),
                                   (ages[g],*cells[g])):
            bounds = []
            for sign in (1,-1):
                fit = solve(sign*objective, tolerance_pp/100)
                assert fit.success, fit.message
                bounds.append(float(objective @ fit.x) * total)
            rows.append([tolerance_pp, age, label, *bounds])
with (root / 'age_backcast_bounds.csv').open('w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['within_age_tolerance_pp','age','category','min_votes','max_votes'])
    writer.writerows(rows)

# At fixed tolerance both questions are feasibility tests on nested polytopes.
def threshold(allow_half):
    def feasible(tolerance):
        result = solve(ages[2], tolerance)
        if result.status == 2:
            return False
        assert result.success, result.message
        return not allow_half or result.fun <= .5

    lo, hi = 0., .03
    assert not feasible(lo) and feasible(hi)
    while hi - lo > 1e-9:
        mid = (lo + hi) / 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid
    return 100 * hi

with (root / 'age_thresholds.csv').open('w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['condition', 'minimum_uniform_tolerance_pp'])
    for label, half in [('Any feasible allocation', False), ('Oldest share at most one half', True)]:
        writer.writerow([label, threshold(half)])

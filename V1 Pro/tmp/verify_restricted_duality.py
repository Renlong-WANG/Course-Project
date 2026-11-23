import json
from pathlib import Path
import numpy as np
from scipy.optimize import linprog

rng = np.random.default_rng(596)
solves = 0
max_error = 0.0
cdf_checks = 0

def discrepancy(q, p, n):
    if p == 0 or p == 1:
        return -np.inf if q == p else np.inf
    if q == 0:
        kl = -np.log1p(-p)
    elif q == 1:
        kl = -np.log(p)
    else:
        kl = q * np.log(q / p) + (1-q) * np.log((1-q)/(1-p))
    lo, hi = min(q, p), max(q, p)
    v = min(max(0.5, lo), hi)
    rho = np.log(1 - np.log(4*v*(1-v)))
    return n * max(0.0, kl) - rho - np.log1p(rho*rho)

def endpoints(n, theta):
    a, b = [], []
    for j in range(n+1):
        q = j/n
        lo, hi = 0.0, q
        for _ in range(65):
            mid = (lo+hi)/2
            if discrepancy(q, mid, n) <= theta:
                hi = mid
            else:
                lo = mid
        a.append(hi if j else 0.0)
        lo, hi = q, 1.0
        for _ in range(65):
            mid = (lo+hi)/2
            if discrepancy(q, mid, n) <= theta:
                lo = mid
            else:
                hi = mid
        b.append(lo if j < n else 1.0)
    a, b = np.array(a), np.array(b)
    assert np.all(np.diff(a) >= -1e-12)
    assert np.all(np.diff(b) >= -1e-12)
    assert np.max(np.abs(a - (1-b[::-1]))) < 1e-12
    return a, b

def solve(c, aub, bub, aeq=None, beq=None, bounds=(0, None)):
    global solves
    result = linprog(c, A_ub=aub, b_ub=bub, A_eq=aeq, b_eq=beq,
                     bounds=bounds, method='highs',
                     options={'primal_feasibility_tolerance': 1e-9,
                              'dual_feasibility_tolerance': 1e-9})
    assert result.success, result.message
    solves += 1
    return result.fun

samples = [[0], [-1, 1], [-1, -1, 2], [-2, 0, 1, 1],
           [-1, 0, 1, 2], [0, 0, 0, 0], [-2, -1, 0, 1, 2, 2],
           [-3, -3, -1, 0, 1, 3, 3]]
scenarios = 0
for sample in samples:
    sample = np.array(sample, dtype=float)
    n = len(sample)
    r = np.unique(sample)
    k, jcount = len(r), 2*len(r)+1
    nrows = k+1
    counts = np.array([(sample <= x).sum() for x in r])
    previous = np.r_[0, counts[:-1]]
    thresholds = np.r_[r[0]-2, r, (r[:-1]+r[1:])/2, r[-1]+2]
    grid_base = np.unique(np.r_[sample, thresholds])
    grid = np.unique(np.r_[grid_base[0]-1, grid_base,
                           (grid_base[:-1]+grid_base[1:])/2, grid_base[-1]+1])
    na, ng = len(thresholds), len(grid)
    open_grid = (grid[None, :] < r[:, None]).astype(float)
    closed_grid = (grid[None, :] <= r[:, None]).astype(float)
    original_eq = np.kron(np.eye(na), np.ones((1, ng)))
    original_ub = np.r_[np.tile(open_grid, (1, na)),
                        -np.tile(closed_grid, (1, na))]
    original_cost = (grid[None, :] <= thresholds[:, None]).astype(float).ravel()
    indices = np.arange(1, jcount+1)
    open_cells = (indices[None, :] < 2*np.arange(1, k+1)[:, None]).astype(float)
    closed_cells = (indices[None, :] <= 2*np.arange(1, k+1)[:, None]).astype(float)
    aggregate_eq = np.kron(np.eye(nrows), np.ones((1, jcount)))
    aggregate_ub = np.r_[np.tile(open_cells, (1, nrows)),
                         -np.tile(closed_cells, (1, nrows))]
    bins = np.arange(nrows)
    hi_cost = (indices[None, :] <= 2*bins[:, None]+1).astype(float)
    low_cost = (indices[None, :] <= 2*bins[:, None]).astype(float)
    def cell(x):
        return np.searchsorted(r, x, side='right')

    for theta in [0.0, 0.01, 0.5, 4.0]:
        alpha, beta = endpoints(n, theta)
        ell, upper = alpha[counts], beta[previous]
        bub = np.r_[upper, -ell]
        for atom_only in [False, True]:
            weights = rng.dirichlet(np.ones(na))
            if atom_only:
                weights[:] = 0
                weights[1 + k//2] = 1
            w = np.zeros(nrows)
            for t, mass in zip(thresholds, weights):
                w[cell(t)] += mass
            orig_lo = solve(original_cost, original_ub, bub, original_eq, weights)
            orig_hi = -solve(-original_cost, original_ub, bub, original_eq, weights)
            ag_lo = solve(low_cost.ravel(), aggregate_ub, bub, aggregate_eq, w)
            ag_hi = -solve(-hi_cost.ravel(), aggregate_ub, bub, aggregate_eq, w)
            upper_rows, lower_rows = [], []
            for i in range(nrows):
                for j in range(jcount):
                    row = np.r_[-open_cells[:, j], closed_cells[:, j], np.zeros(nrows)]
                    row[2*k+i] = -1
                    upper_rows.append(row)
                    row = row.copy()
                    row[2*k+i] = 1
                    lower_rows.append(row)
            bounds = [(0, None)]*(2*k) + [(None, None)]*nrows
            dual_hi = solve(np.r_[upper, -ell, w], upper_rows,
                            -hi_cost.ravel(), bounds=bounds)
            dual_lo = -solve(np.r_[upper, -ell, -w], lower_rows,
                             low_cost.ravel(), bounds=bounds)
            h = np.array([weights[thresholds >= x].sum() for x in r])
            restricted_hi = 1 + solve(upper+h-1, np.ones((1,k)), [1.0])
            restricted_lo = -solve(-(ell+h-1), np.ones((1,k)), [1.0])
            cf_hi = min(1.0, np.min(upper+h))
            cf_lo = max(0.0, np.max(ell+h-1))
            error = max(abs(v-orig_hi) for v in [ag_hi, dual_hi, restricted_hi, cf_hi])
            error = max(error, *(abs(v-orig_lo) for v in [ag_lo, dual_lo, restricted_lo, cf_lo]))
            max_error = max(max_error, error)
            assert error < 1e-8, (sample, theta, atom_only, error)
            # Check the all-threshold CDF band independently of the rank constraints.
            for empirical in [True, False]:
                masses = rng.dirichlet(np.ones(ng))
                if empirical:
                    masses[:] = 0
                    for x in sample:
                        masses[np.flatnonzero(grid == x)[0]] += 1/n
                tests = np.unique(np.r_[grid, r, (grid[:-1]+grid[1:])/2,
                                        grid[0]-1, grid[-1]+1])
                ranks = (sample[:, None] <= tests[None, :]).sum(axis=0)
                cdf = (masses[:, None]*(grid[:, None] <= tests[None, :])).sum(axis=0)
                band = np.all((cdf >= alpha[ranks]-1e-10) & (cdf <= beta[ranks]+1e-10))
                rank = np.all(open_grid @ masses <= upper+1e-10) and np.all(closed_grid @ masses >= ell-1e-10)
                assert band == rank
                cdf_checks += 1
            scenarios += 1

report = {'representation': 'K-weight restricted duals vs full duals and primal allocations', 'scenarios': scenarios, 'linear_program_solves': solves,
          'cdf_band_equivalence_checks': cdf_checks, 'max_absolute_difference': max_error,
          'covered_cases': ['theta=0', 'positive theta', 'single residual',
                            'tied residuals', 'threshold equality',
                            'atomic input law', 'unequal input weights', 'zero cell masses']}
Path('tmp/restricted_duality_verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))

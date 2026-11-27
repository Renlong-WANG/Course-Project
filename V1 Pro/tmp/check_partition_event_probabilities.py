"""Independent finite LP checks for the partition-only proof and event formulas."""
import ast
import json
from pathlib import Path
import numpy as np
from scipy.optimize import linprog

rng = np.random.default_rng(20261125596)
parsed = ast.parse(Path('tmp/verify_engineering_reformulation.py').read_text(encoding='utf-8'))
helpers = ast.Module(body=[node for node in parsed.body if isinstance(node, ast.FunctionDef)
                          and node.name in {'discrepancy', 'endpoints'}], type_ignores=[])
scope = {'np': np}
exec(compile(helpers, '<DW scalar inversion>', 'exec'), scope)
solves = fixed_cases = allocation_cases = event_cases = bounded_cases = 0
max_error = 0.0

def optimize(cost, aeq, beq, aub=None, bub=None):
    global solves
    result = linprog(cost, A_eq=aeq, b_eq=beq, A_ub=aub, b_ub=bub,
                     bounds=(0, None), method='highs')
    assert result.success, result.message
    solves += 1
    return result.fun

def representatives(observed):
    result = np.empty(2 * len(observed) + 1)
    result[0], result[-1] = observed[0] - 1, observed[-1] + 1
    result[1::2] = observed
    result[2:-1:2] = (observed[:-1] + observed[1:]) / 2
    return result

def transport_extrema(input_masses, observed, residual_masses):
    K, J = len(observed), 2 * len(observed) + 1
    row_eq = np.kron(np.eye(K + 1), np.ones((1, J)))
    col_eq = np.tile(np.eye(J), (1, K + 1))
    aeq, beq = np.r_[row_eq, col_eq], np.r_[input_masses, residual_masses]
    columns = np.arange(1, J + 1)[None, :]
    rows = np.arange(K + 1)[:, None]
    lower = optimize((columns <= 2 * rows).astype(float).ravel(), aeq, beq)
    upper = -optimize(-(columns <= 2 * rows + 1).astype(float).ravel(), aeq, beq)
    return lower, upper

for K in range(1, 6):
    observed = np.arange(K, dtype=float)
    residual_points = representatives(observed)
    for mode in range(3):
        input_masses = rng.dirichlet(np.ones(K + 1))
        residual_masses = rng.dirichlet(np.ones(2 * K + 1))
        if mode == 1:
            input_masses[:] = 0
            input_masses[-1] = 1
        if mode == 2:
            residual_masses[::2] = 0
            residual_masses /= residual_masses.sum()
        actual_lower, actual_upper = transport_extrema(input_masses, observed, residual_masses)
        open_prob = (residual_points[None, :] < observed[:, None]) @ residual_masses
        closed_prob = (residual_points[None, :] <= observed[:, None]) @ residual_masses
        input_tails = np.array([input_masses[k:].sum() for k in range(1, K + 1)])
        expected_upper = min(1, min(input_tails + open_prob))
        expected_lower = max(0, max(input_tails + closed_prob - 1))
        error = max(abs(actual_upper - expected_upper), abs(actual_lower - expected_lower))
        max_error = max(max_error, float(error))
        assert error < 1e-9
        fixed_cases += 1

for sample in [np.array([0.]), np.array([-1., 0., 0., 2.])]:
    observed = np.unique(sample)
    counts = np.array([(sample <= value).sum() for value in observed])
    K, J = len(observed), 2 * len(observed) + 1
    residual_points = representatives(observed)
    for theta in [0., .5]:
        alpha, beta = scope['endpoints'](len(sample), theta)
        if theta == 0 and len(sample) % 2 == 0:
            alpha[len(sample) // 2] = beta[len(sample) // 2] = .5
        lower, upper = alpha[counts], beta[np.r_[0, counts[:-1]]]
        plus, minus = np.zeros(J), np.zeros(J)
        plus[0] = upper[0]
        plus[1::2] = np.diff(np.r_[upper, 1.])
        minus[1::2] = np.diff(np.r_[0., lower])
        minus[-1] = 1 - lower[-1]
        for masses, is_upper in [(plus, True), (minus, False)]:
            assert np.min(masses) > -1e-12 and abs(masses.sum() - 1) < 1e-12
            opened = (residual_points[None, :] < observed[:, None]) @ masses
            closed = (residual_points[None, :] <= observed[:, None]) @ masses
            assert np.all(opened <= upper + 1e-10) and np.all(closed >= lower - 1e-10)
            assert np.max(abs(opened - upper if is_upper else closed - lower)) < 1e-10
            allocation_cases += 1

        responses = np.array([-3., 0., 1., 4.])
        input_masses = np.array([.1, .4, .2, .3])
        for c in [-1., 0., 1., 2.]:
            thresholds = c - responses
            event_prob = (responses[None, :] <= c - observed[:, None]) @ input_masses
            cells = np.searchsorted(observed, thresholds, side='right')
            cell_prob = np.bincount(cells, weights=input_masses, minlength=K + 1)
            assert np.max(abs(event_prob - np.array([cell_prob[k:].sum() for k in range(1, K + 1)]))) < 1e-12
            for interval in [None, (observed[0], observed[-1])]:
                breaks = np.unique(np.r_[observed, thresholds])
                if interval is None:
                    residual_grid = np.unique(np.r_[breaks[0] - 1, breaks,
                        (breaks[:-1] + breaks[1:]) / 2, breaks[-1] + 1])
                    expected_upper = min(1, min(upper + event_prob))
                    expected_lower = max(0, max(lower + event_prob - 1))
                else:
                    a, b = interval
                    breaks = np.unique(np.r_[a, b, breaks[(breaks >= a) & (breaks <= b)]])
                    residual_grid = np.unique(np.r_[breaks, (breaks[:-1] + breaks[1:]) / 2])
                    expected_upper = min(input_masses[responses <= c - a].sum(), min(upper + event_prob))
                    expected_lower = max(input_masses[responses <= c - b].sum(), max(lower + event_prob - 1))
                width = len(residual_grid)
                aeq = np.kron(np.eye(len(responses)), np.ones((1, width)))
                opened = (residual_grid[None, :] < observed[:, None]).astype(float)
                closed = (residual_grid[None, :] <= observed[:, None]).astype(float)
                aub = np.r_[np.tile(opened, (1, len(responses))), -np.tile(closed, (1, len(responses)))]
                cost = (responses[:, None] + residual_grid[None, :] <= c).astype(float).ravel()
                actual_lower = optimize(cost, aeq, input_masses, aub, np.r_[upper, -lower])
                actual_upper = -optimize(-cost, aeq, input_masses, aub, np.r_[upper, -lower])
                error = max(abs(actual_upper - expected_upper), abs(actual_lower - expected_lower))
                max_error = max(max_error, float(error))
                assert error < 1e-9
                event_cases += int(interval is None)
                bounded_cases += int(interval is not None)

# The finite transportation optimum fixes cell masses, not a full residual law.
partition_upper = transport_extrema(np.array([0., 1.]), np.array([0.]), np.array([0., .4, .6]))[1]
fixed_law_probability = float(np.array([.4, .6]) @ (np.array([0., .75]) <= .5))
assert abs(partition_upper - 1) < 1e-12 and abs(fixed_law_probability - .4) < 1e-12

report = {'linear_programs_solved': solves, 'fixed_partition_transport_cases': fixed_cases,
          'candidate_law_allocations_checked': allocation_cases,
          'response_threshold_cases': event_cases, 'bounded_support_threshold_cases': bounded_cases,
          'theta_zero_and_singleton_support_included': True,
          'fixed_partition_vs_full_law_distinction_checked': True,
          'maximum_difference': max_error}
Path('tmp/partition_event_probability_verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))

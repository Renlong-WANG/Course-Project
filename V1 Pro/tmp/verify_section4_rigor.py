"""Independent atomic-law LPs and explicit joint-law witnesses for the Section 4 audit."""
import ast
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

# Reuse only the scalar DW inversion; all probability allocations are checked below.
parsed = ast.parse(Path('tmp/verify_engineering_reformulation.py').read_text(encoding='utf-8'))
helpers = ast.Module(body=[node for node in parsed.body if isinstance(node, ast.FunctionDef)
                          and node.name in {'discrepancy', 'endpoints'}], type_ignores=[])
scope = {'np': np}
exec(compile(helpers, '<DW scalar inversion>', 'exec'), scope)
endpoints = scope['endpoints']
rng = np.random.default_rng(59620261124)
tol = 2e-8
solves = scenarios = bounded_scenarios = reconstructions = forced_moves = band_checks = 0
theta_zero_cases = binding_prefix_cases = 0
maximum_error = 0.0
maximum_marginal_error = 0.0


def solve(cost, aub, bub, aeq, beq, bounds=(0, None)):
    global solves
    result = linprog(cost, A_ub=aub, b_ub=bub, A_eq=aeq, b_eq=beq,
                     bounds=bounds, method='highs',
                     options={'primal_feasibility_tolerance': 1e-9,
                              'dual_feasibility_tolerance': 1e-9})
    assert result.success, result.message
    solves += 1
    return result


def full_problem(residual, thresholds, weights, observed, lower, upper):
    a = (residual[None, :] < observed[:, None]).astype(float)
    b = (residual[None, :] <= observed[:, None]).astype(float)
    equality = np.kron(np.eye(len(thresholds)), np.ones((1, len(residual))))
    ranks = np.r_[np.tile(a, (1, len(thresholds))), -np.tile(b, (1, len(thresholds)))]
    cost = (residual[None, :] <= thresholds[:, None]).astype(float).ravel()
    rhs = np.r_[upper, -lower]
    return (solve(cost, ranks, rhs, equality, weights).fun,
            -solve(-cost, ranks, rhs, equality, weights).fun)


def reconstruct(matrix, thresholds, weights, observed, lower, upper, maximize):
    global reconstructions, maximum_marginal_error
    k = len(observed)
    jcount = 2 * k + 1
    input_cells = np.searchsorted(observed, thresholds, side='right')
    row_mass = np.bincount(input_cells, weights=weights, minlength=k + 1)
    representatives = np.empty(jcount)
    representatives[0] = observed[0] - 1
    representatives[1::2] = observed
    representatives[2:-1:2] = (observed[:-1] + observed[1:]) / 2
    representatives[-1] = observed[-1] + 1
    actual_rows = np.zeros(len(thresholds))
    actual_matrix = np.zeros_like(matrix)
    opened = np.zeros(k)
    closed = np.zeros(k)
    failure = 0.0
    for point, (threshold, point_mass, cell) in enumerate(zip(thresholds, weights, input_cells)):
        if point_mass == 0:
            continue
        assert row_mass[cell] > 0
        for column, cell_mass in enumerate(matrix[cell]):
            mass = point_mass * cell_mass / row_mass[cell]
            if mass == 0:
                continue
            residual = representatives[column]
            if column == 2 * cell:
                residual = (threshold if maximize else
                            (threshold + observed[cell]) / 2 if cell < k else threshold + 1)
            actual_rows[point] += mass
            opened += mass * (residual < observed)
            closed += mass * (residual <= observed)
            failure += mass * (residual <= threshold)
            position = np.searchsorted(observed, residual, side='left')
            actual_column = (2 * position + 1 if position < k and residual == observed[position]
                             else 2 * position)
            actual_matrix[cell, actual_column] += mass
    marginal_error = np.max(np.abs(actual_rows - weights))
    maximum_marginal_error = max(maximum_marginal_error, marginal_error)
    assert marginal_error < tol
    assert np.all(opened <= upper + tol) and np.all(closed >= lower - tol)
    indices = np.arange(1, jcount + 1)
    a = (indices[None, :] < 2 * np.arange(1, k + 1)[:, None]).astype(float)
    b = (indices[None, :] <= 2 * np.arange(1, k + 1)[:, None]).astype(float)
    assert np.max(np.abs(opened - a @ matrix.sum(axis=0))) < tol
    if maximize:
        assert np.min(closed - b @ matrix.sum(axis=0)) > -tol
    else:
        assert np.max(np.abs(actual_matrix - matrix)) < tol
    cost = (indices[None, :] <= 2 * np.arange(k + 1)[:, None] + int(maximize)).astype(float)
    assert abs(failure - np.sum(cost * matrix)) < tol
    reconstructions += 1
    return failure, actual_matrix


samples = [[0], [-1, 1], [-1, -1, 2], [-2, 0, 1, 1], [-1, 0, 1, 2],
           [0, 0, 0, 0], [-2, -1, 0, 1, 2, 2], [-3, -3, -1, 0, 1, 3, 3]]
for sample_values in samples:
    sample = np.asarray(sample_values, dtype=float)
    observed = np.unique(sample)
    k, jcount = len(observed), 2 * len(observed) + 1
    counts = np.array([(sample <= value).sum() for value in observed])
    thresholds = np.unique(np.r_[observed[0] - 2, observed,
                                 (observed[:-1] + observed[1:]) / 2, observed[-1] + 2])
    critical = np.unique(np.r_[observed, thresholds])
    residual_grid = np.unique(np.r_[critical[0] - 1, critical,
                                    (critical[:-1] + critical[1:]) / 2, critical[-1] + 1])
    indices = np.arange(1, jcount + 1)
    open_cells = (indices[None, :] < 2 * np.arange(1, k + 1)[:, None]).astype(float)
    closed_cells = (indices[None, :] <= 2 * np.arange(1, k + 1)[:, None]).astype(float)
    equality = np.kron(np.eye(k + 1), np.ones((1, jcount)))
    ranks = np.r_[np.tile(open_cells, (1, k + 1)), -np.tile(closed_cells, (1, k + 1))]
    upper_cost = (indices[None, :] <= 2 * np.arange(k + 1)[:, None] + 1).astype(float)
    lower_cost = (indices[None, :] <= 2 * np.arange(k + 1)[:, None]).astype(float)
    for theta in [0.0, 0.05, 1.0]:
        alpha, beta = endpoints(len(sample), theta)
        if theta == 0 and len(sample) % 2 == 0:
            # Analytic zero-width interval: psi(1/2,p)=0, so KL=0 forces p=1/2.
            alpha[len(sample) // 2] = beta[len(sample) // 2] = 0.5
        lower, upper = alpha[counts], beta[np.r_[0, counts[:-1]]]
        rhs = np.r_[upper, -lower]
        for mode in ['mixed', 'first_equality', 'last_equality']:
            weights = rng.dirichlet(np.ones(len(thresholds)))
            if mode != 'mixed':
                weights[:] = 0
                value = observed[0] if mode == 'first_equality' else observed[-1]
                weights[np.flatnonzero(thresholds == value)[0]] = 1
            cells = np.searchsorted(observed, thresholds, side='right')
            w = np.bincount(cells, weights=weights, minlength=k + 1)
            extended = np.r_[-np.inf, observed, np.inf]
            cdf_w = np.array([weights[thresholds >= extended[i]].sum()
                              - weights[thresholds >= extended[i + 1]].sum() for i in range(k + 1)])
            assert np.max(np.abs(w - cdf_w)) < 1e-12
            h = np.array([weights[thresholds >= value].sum() for value in observed])
            full_lower, full_upper = full_problem(residual_grid, thresholds, weights, observed, lower, upper)
            aggregate_upper = solve(-upper_cost.ravel(), ranks, rhs, equality, w)
            aggregate_lower = solve(lower_cost.ravel(), ranks, rhs, equality, w)
            dual_upper, dual_lower = [], []
            for i in range(k + 1):
                for j in range(jcount):
                    row = np.r_[-open_cells[:, j], closed_cells[:, j], np.zeros(k + 1)]
                    row[2 * k + i] = -1
                    dual_upper.append(row)
                    row = row.copy()
                    row[2 * k + i] = 1
                    dual_lower.append(row)
            free = [(0, None)] * (2 * k) + [(None, None)] * (k + 1)
            upper_dual = solve(np.r_[upper, -lower, w], dual_upper, -upper_cost.ravel(), None, None, free).fun
            lower_dual = -solve(np.r_[upper, -lower, -w], dual_lower, lower_cost.ravel(), None, None, free).fun
            closed_upper, closed_lower = min(1, min(upper + h)), max(0, max(lower + h - 1))
            values_upper = [full_upper, -aggregate_upper.fun, upper_dual, closed_upper]
            values_lower = [full_lower, aggregate_lower.fun, lower_dual, closed_lower]
            error = max(np.ptp(values_upper), np.ptp(values_lower))
            maximum_error = max(maximum_error, error)
            assert error < tol, (sample_values, theta, mode, values_upper, values_lower)
            reconstruct(aggregate_upper.x.reshape(k + 1, jcount), thresholds, weights, observed, lower, upper, True)
            reconstruct(aggregate_lower.x.reshape(k + 1, jcount), thresholds, weights, observed, lower, upper, False)
            empirical = np.zeros((k + 1, jcount))
            empirical[:, 1::2] = w[:, None] * np.diff(np.r_[0, counts])[None, :] / len(sample)
            assert np.all(open_cells @ empirical.sum(axis=0) <= upper + tol)
            assert np.all(closed_cells @ empirical.sum(axis=0) >= lower - tol)
            if mode == 'last_equality':
                provisional = np.zeros_like(empirical)
                provisional[k, 1::2] = np.diff(np.r_[0, lower])
                provisional[k, -1] = 1 - lower[-1]
                value, actual = reconstruct(provisional, thresholds, weights, observed, lower, upper, True)
                assert abs(value - 1) < tol
                assert provisional[k, -1] > 0 and abs(actual[k, -1]) < tol
                forced_moves += 1
            if theta == 0:
                theta_zero_cases += 1
                binding_prefix_cases += int(k > 1 and np.any(np.abs(lower[:-1] - upper[1:]) < 1e-14))

            for left, right in [(observed[0], observed[-1]), (observed[0] - 0.5, observed[-1] + 0.5)]:
                points = np.unique(np.r_[left, right, observed, thresholds[(left <= thresholds) & (thresholds <= right)]])
                bounded_grid = np.unique(np.r_[points, (points[:-1] + points[1:]) / 2])
                bound_lower, bound_upper = full_problem(bounded_grid, thresholds, weights, observed, lower, upper)
                expected_upper = min(weights[thresholds >= left].sum(), min(upper + h))
                expected_lower = max(weights[thresholds >= right].sum(), max(lower + h - 1))
                assert abs(bound_upper - expected_upper) < tol and abs(bound_lower - expected_lower) < tol
                bounded_scenarios += 1

            for is_empirical in [True, False]:
                masses = rng.dirichlet(np.ones(len(residual_grid)))
                if is_empirical:
                    masses[:] = 0
                    for value in sample:
                        masses[np.flatnonzero(residual_grid == value)[0]] += 1 / len(sample)
                tests = np.unique(np.r_[residual_grid, (residual_grid[:-1] + residual_grid[1:]) / 2,
                                        residual_grid[0] - 1, residual_grid[-1] + 1])
                empirical_rank = (sample[:, None] <= tests[None, :]).sum(axis=0)
                candidate_cdf = (masses[:, None] * (residual_grid[:, None] <= tests[None, :])).sum(axis=0)
                band = np.all(candidate_cdf >= alpha[empirical_rank] - tol) and np.all(candidate_cdf <= beta[empirical_rank] + tol)
                rank = (np.all((residual_grid[None, :] < observed[:, None]) @ masses <= upper + tol)
                        and np.all((residual_grid[None, :] <= observed[:, None]) @ masses >= lower - tol))
                assert band == rank
                band_checks += 1
            scenarios += 1

report = {'unbounded_support_scenarios': scenarios, 'bounded_support_scenarios': bounded_scenarios,
          'theta_zero_scenarios': theta_zero_cases, 'binding_adjacent_prefix_scenarios': binding_prefix_cases,
          'linear_programs_solved': solves, 'constructed_joint_laws_checked': reconstructions,
          'forced_threshold_equality_endpoint_moves': forced_moves, 'cdf_band_rank_equivalence_checks': band_checks,
          'maximum_primal_dual_closed_form_difference': maximum_error,
          'maximum_input_marginal_difference': maximum_marginal_error,
          'covered': ['tied test residuals', 'K=1', 'input atoms exactly at first and last residuals',
                      'zero-probability input cells', 'theta=0 with exact zero-width median acceptance',
                      'upper endpoint moves preserving open probabilities and increasing closed probabilities',
                      'lower construction preserving the entire cell matrix',
                      'known support endpoints coinciding with observations', 'singleton residual support']}
Path('tmp/section4_rigor_verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))

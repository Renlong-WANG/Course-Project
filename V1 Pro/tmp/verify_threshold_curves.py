"""Compare shifted response-threshold formulas with independent atomic measure LPs."""
from pathlib import Path
import ast
import json
import numpy as np
from scipy.optimize import linprog

parsed = ast.parse(Path('tmp/verify_engineering_reformulation.py').read_text(encoding='utf-8'))
helpers = ast.Module(body=[node for node in parsed.body if isinstance(node, ast.FunctionDef)
                          and node.name in {'discrepancy', 'endpoints'}], type_ignores=[])
scope = {'np': np}
exec(compile(helpers, '<DW inversion>', 'exec'), scope)
endpoints = scope['endpoints']
response = np.array([-2., 0., 0., .5, 2., 4.])
weights = np.full(6, 1 / 6)
samples = [np.array([-1., -1., 0., 2., 2., 2.]), np.zeros(6),
           np.array([-2., -1., -1., 1., 1., 3.])]
solves = profiles = boundary_thresholds = exact_curve_coverage_checks = 0
maximum_difference = 0.

for sample in samples:
    observed = np.unique(sample)
    counts = np.searchsorted(np.sort(sample), observed, side='right')
    critical = np.unique((response[:, None] + observed[None, :]).ravel())
    coverage_grid = np.unique(np.r_[critical[0] - 2, critical,
        (critical[:-1] + critical[1:]) / 2, critical[-1] + 2, 0.])
    selected = critical[np.unique(np.linspace(0, len(critical) - 1, min(7, len(critical))).astype(int))]
    lp_grid = np.unique(np.r_[selected[0] - 2, selected,
        (selected[:-1] + selected[1:]) / 2, selected[-1] + 2, 0.])
    for theta in [0., 1.2]:
        alpha, beta = endpoints(len(sample), theta)
        if theta == 0:
            alpha[len(sample) // 2] = beta[len(sample) // 2] = .5
        lower_rank = alpha[counts]
        upper_rank = beta[np.r_[0, counts[:-1]]]
        for bounded in [False, True]:
            profiles += 1
            lower_support, upper_support = sample.min(), sample.max()
            def H(t):
                return np.sum(weights * (response <= t))
            def formulas(c):
                upper_outer = H(c - lower_support) if bounded else 1.
                lower_outer = H(c - upper_support) if bounded else 0.
                upper = min(upper_outer, np.min(upper_rank + np.array([H(c - r) for r in observed])))
                lower = max(lower_outer, np.max(lower_rank + np.array([H(c - r) for r in observed]) - 1))
                return lower, upper
            curve = np.array([formulas(c) for c in coverage_grid])
            true_curve = np.array([np.sum(weights * (response + sample <= c)) for c in coverage_grid])
            assert np.all(curve[:, 0] <= true_curve + 1e-12)
            assert np.all(true_curve <= curve[:, 1] + 1e-12)
            assert np.all(np.diff(curve, axis=0) >= -1e-12)
            exact_curve_coverage_checks += len(coverage_grid)
            for c in lp_grid:
                thresholds = c - response
                breaks = np.unique(np.r_[thresholds, observed])
                residual_grid = np.unique(np.r_[breaks[0] - 1, breaks,
                    (breaks[:-1] + breaks[1:]) / 2, breaks[-1] + 1])
                if bounded:
                    residual_grid = residual_grid[(lower_support <= residual_grid) & (residual_grid <= upper_support)]
                opened = (residual_grid[None, :] < observed[:, None]).astype(float)
                closed = (residual_grid[None, :] <= observed[:, None]).astype(float)
                aub = np.r_[np.tile(opened, (1, len(response))), -np.tile(closed, (1, len(response)))]
                bub = np.r_[upper_rank, -lower_rank]
                aeq = np.kron(np.eye(len(response)), np.ones((1, len(residual_grid))))
                cost = (response[:, None] + residual_grid[None, :] <= c).astype(float).ravel()
                low = linprog(cost, A_ub=aub, b_ub=bub, A_eq=aeq, b_eq=weights,
                              bounds=(0, None), method='highs')
                high = linprog(-cost, A_ub=aub, b_ub=bub, A_eq=aeq, b_eq=weights,
                               bounds=(0, None), method='highs')
                solves += 2
                assert low.success and high.success
                expected = formulas(c)
                error = max(abs(low.fun - expected[0]), abs(-high.fun - expected[1]))
                maximum_difference = max(maximum_difference, error)
                assert error < 1e-8
                if np.any(response[:, None] + observed[None, :] == c):
                    boundary_thresholds += 1

report = {'profiles': profiles, 'measure_linear_programs_solved': solves,
          'threshold_equality_cases': boundary_thresholds,
          'exact_coverage_and_monotonicity_checks': exact_curve_coverage_checks,
          'maximum_lp_formula_difference': maximum_difference,
          'includes_theta_zero_and_zero_width_acceptance': True,
          'includes_tied_residuals_and_surrogate_response_atoms': True,
          'includes_interval_and_singleton_residual_support': True, 'passed': True}
Path('tmp/threshold_curves_verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))

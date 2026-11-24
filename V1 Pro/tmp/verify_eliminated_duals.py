import ast
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

# Reuse the existing scalar DW inversion without rerunning earlier experiments.
source = ast.parse(Path('tmp/verify_balanced_duality.py').read_text(encoding='utf-8'))
helpers = ast.Module(body=[node for node in source.body
                          if isinstance(node, ast.FunctionDef)
                          and node.name in {'discrepancy', 'endpoints'}], type_ignores=[])
scope = {'np': np}
exec(compile(helpers, '<existing DW scalar inversion>', 'exec'), scope)
endpoints = scope['endpoints']
rng = np.random.default_rng(2411)
solves = scenarios = envelope_checks = 0
max_error = 0.0


def solve(c, aub, bub, aeq=None, beq=None, bounds=(0, None)):
    global solves
    result = linprog(c, A_ub=aub, b_ub=bub, A_eq=aeq, b_eq=beq,
                     bounds=bounds, method='highs')
    assert result.success, result.message
    solves += 1
    return result


for sample in [[0], [-1, 1], [-1, -1, 0, 2], [-2, -1, 0, 1, 1, 2]]:
    sample = np.array(sample, dtype=float)
    r = np.unique(sample)
    k = len(r)
    support = np.unique(np.r_[r[0]-1, r, (r[:-1]+r[1:])/2, r[-1]+1])
    thresholds = np.unique(np.r_[r[0]-2, r, (r[:-1]+r[1:])/2, r[-1]+2])
    m, jcount = len(thresholds), len(support)
    h = (support[None, :] <= thresholds[:, None]).astype(float)
    a = (support[None, :] < r[:, None]).astype(float)
    b = (support[None, :] <= r[:, None]).astype(float)
    rows = np.kron(np.eye(m), np.ones((1, jcount)))
    ranks = np.r_[np.tile(a, (1, m)), -np.tile(b, (1, m))]
    full_upper, full_lower = [], []
    for i in range(m):
        for j in range(jcount):
            row = np.r_[-a[:, j], b[:, j], np.zeros(m)]
            row[2*k+i] = -1
            full_upper.append(row)
            row = row.copy()
            row[2*k+i] = 1
            full_lower.append(row)
    for theta in [0.0, 0.6]:
        alpha, beta = endpoints(len(sample), theta)
        counts = np.array([(sample <= t).sum() for t in r])
        lower = alpha[counts]
        upper = beta[np.r_[0, counts[:-1]]]
        rhs = np.r_[upper, -lower]
        for atomic in [False, True]:
            weights = rng.dirichlet(np.ones(m))
            if atomic:
                weights[:] = 0
                weights[np.flatnonzero(thresholds == r[k//2])[0]] = 1
            primal_hi = -solve(-h.ravel(), ranks, rhs, rows, weights).fun
            primal_lo = solve(h.ravel(), ranks, rhs, rows, weights).fun
            bounds = [(0, None)]*(2*k)+[(None, None)]*m
            dual_hi = solve(np.r_[upper, -lower, weights], full_upper,
                            -h.ravel(), bounds=bounds)
            dual_lo = solve(np.r_[upper, -lower, -weights], full_lower,
                            h.ravel(), bounds=bounds)

            def evaluate(parameters):
                lam, gam = parameters[:k], parameters[k:]
                eta = lam @ a - gam @ b
                phi_hi = np.max(h-eta, axis=1)
                phi_lo = np.min(h+eta, axis=1)
                assert np.max(h-phi_hi[:, None]-eta) < 1e-10
                assert np.min(h-phi_lo[:, None]+eta) > -1e-10
                assert np.min(np.diff(phi_hi)) > -1e-10
                assert np.min(np.diff(phi_lo)) > -1e-10
                return (lam @ upper - gam @ lower + weights @ phi_hi,
                        -lam @ upper + gam @ lower + weights @ phi_lo)

            reduced_hi = evaluate(dual_hi.x[:2*k])[0]
            reduced_lo = evaluate(dual_lo.x[:2*k])[1]
            error = max(abs(reduced_hi-primal_hi), abs(reduced_lo-primal_lo),
                        abs(dual_hi.fun-primal_hi), abs(-dual_lo.fun-primal_lo))
            max_error = max(max_error, error)
            assert error < 1e-8
            for _ in range(4):
                x, y = rng.uniform(0, 3, (2, 2*k))
                t = rng.uniform()
                fx, fy = evaluate(x), evaluate(y)
                fm = evaluate(t*x+(1-t)*y)
                assert fm[0] <= t*fx[0]+(1-t)*fy[0]+1e-9
                assert fm[1] >= t*fx[1]+(1-t)*fy[1]-1e-9
                assert fx[0] >= primal_hi-1e-9 and fx[1] <= primal_lo+1e-9
                envelope_checks += 1
            scenarios += 1

report = {'scenarios': scenarios, 'linear_program_solves': solves,
          'fixed_multiplier_envelope_and_curvature_checks': envelope_checks,
          'max_primal_full_dual_reduced_dual_difference': max_error,
          'covered_cases': ['theta=0', 'positive theta', 'tied residuals',
                            'threshold equality', 'atomic input law',
                            'zero-probability input points', 'finite Borel residual support']}
Path('tmp/eliminated_dual_verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))

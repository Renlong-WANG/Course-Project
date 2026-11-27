"""Check endpoint conventions and sharp-CDF reductions against atomic transport LPs."""
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

rng = np.random.default_rng(20261124)
checks = []


def transport_extrema(response, input_mass, residual, residual_mass):
    cost = (response[:, None] + residual[None, :] <= 0).astype(float).ravel()
    rows, columns = len(response), len(residual)
    equality = np.vstack([
        np.kron(np.eye(rows), np.ones((1, columns))),
        np.kron(np.ones((1, rows)), np.eye(columns)),
    ])
    mass = np.r_[input_mass, residual_mass]
    lower = linprog(cost, A_eq=equality, b_eq=mass, bounds=(0, None), method="highs")
    upper = linprog(-cost, A_eq=equality, b_eq=mass, bounds=(0, None), method="highs")
    assert lower.success and upper.success
    return lower.fun, -upper.fun


for case in range(100):
    response = np.unique(rng.integers(-4, 5, size=rng.integers(1, 8))).astype(float)
    residual = np.unique(rng.integers(-4, 5, size=rng.integers(1, 8))).astype(float)
    input_mass = rng.dirichlet(np.ones(len(response)))
    residual_mass = rng.dirichlet(np.ones(len(residual)))
    lower, upper = transport_extrema(response, input_mass, residual, residual_mass)
    endpoints = np.unique(np.r_[residual, -response])
    thresholds = np.r_[endpoints, (endpoints[:-1] + endpoints[1:]) / 2,
                       endpoints[0] - 1, endpoints[-1] + 1]
    upper_cdf = min(1, min(residual_mass[residual < t].sum()
                           + input_mass[response <= -t].sum() for t in thresholds))
    lower_cdf = max(0, max(residual_mass[residual <= t].sum()
                           + input_mass[response <= -t].sum() - 1 for t in thresholds))
    assert abs(upper - upper_cdf) < 1e-8, (case, upper, upper_cdf)
    assert abs(lower - lower_cdf) < 1e-8, (case, lower, lower_cdf)
    checks.append(max(abs(upper - upper_cdf), abs(lower - lower_cdf)))

for case in range(100):
    observed = np.unique(rng.integers(-3, 4, size=rng.integers(1, 8))).astype(float)
    count = len(observed)
    empirical_mass = rng.dirichlet(np.ones(count))
    empirical_cdf = empirical_mass.cumsum()
    # Some cases impose exact empirical bounds; these check zero-width constraints.
    if case % 4 == 0:
        lower_rank = empirical_cdf
        upper_rank = np.r_[0, empirical_cdf[:-1]]
    else:
        lower_rank = np.minimum.accumulate((empirical_cdf * rng.random(count))[::-1])[::-1]
        upper_rank = np.maximum.accumulate(
            np.r_[0, empirical_cdf[:-1]]
            + (1 - np.r_[0, empirical_cdf[:-1]]) * rng.random(count))
    assert np.all(lower_rank[:-1] <= upper_rank[1:] + 1e-12)
    response = np.unique(np.r_[rng.integers(-5, 6, size=6), -observed]).astype(float)
    input_mass = rng.dirichlet(np.ones(len(response)))
    h_rank = np.array([input_mass[response <= -value].sum() for value in observed])
    left_tail, right_tail = observed[0] - 0.25, observed[-1] + 0.25
    upper_residual = np.r_[left_tail, observed]
    upper_mass = np.r_[upper_rank[0], np.diff(np.r_[upper_rank, 1])]
    lower_residual = np.r_[observed, right_tail]
    lower_mass = np.r_[np.diff(np.r_[0, lower_rank]), 1 - lower_rank[-1]]
    for values, mass in [(upper_residual, upper_mass), (lower_residual, lower_mass)]:
        assert np.all(mass >= -1e-12) and abs(mass.sum() - 1) < 1e-12
        for k, value in enumerate(observed):
            assert mass[values < value].sum() <= upper_rank[k] + 1e-12
            assert mass[values <= value].sum() >= lower_rank[k] - 1e-12
    _, upper = transport_extrema(response, input_mass, upper_residual, upper_mass)
    lower, _ = transport_extrema(response, input_mass, lower_residual, lower_mass)
    upper_formula = min(input_mass[response <= -left_tail].sum(), min(upper_rank + h_rank))
    lower_formula = max(input_mass[response <= -right_tail].sum(), max(lower_rank + h_rank - 1))
    assert abs(upper - upper_formula) < 1e-8
    assert abs(lower - lower_formula) < 1e-8
    checks.append(max(abs(upper - upper_formula), abs(lower - lower_formula)))

for case in range(40):
    observed = (np.array([0.0]) if case % 5 == 0 else
                np.unique(rng.integers(-3, 4, size=6)).astype(float))
    empirical_cdf = rng.dirichlet(np.ones(len(observed))).cumsum()
    lower_rank = empirical_cdf * 0.6
    upper_rank = 0.4 + np.r_[0, empirical_cdf[:-1]] * 0.6
    left_endpoint = observed[0] if case % 2 == 0 else observed[0] - 1
    right_endpoint = observed[-1] if case % 3 == 0 else observed[-1] + 1
    if len(observed) == 1:
        left_endpoint = right_endpoint = observed[0]
    response = np.unique(np.r_[rng.integers(-5, 6, size=6), -observed,
                                -left_endpoint, -right_endpoint]).astype(float)
    input_mass = rng.dirichlet(np.ones(len(response)))
    h_rank = np.array([input_mass[response <= -value].sum() for value in observed])
    upper_residual = np.r_[left_endpoint, observed]
    upper_mass = np.r_[upper_rank[0], np.diff(np.r_[upper_rank, 1])]
    lower_residual = np.r_[observed, right_endpoint]
    lower_mass = np.r_[np.diff(np.r_[0, lower_rank]), 1 - lower_rank[-1]]
    for values, mass in [(upper_residual, upper_mass), (lower_residual, lower_mass)]:
        for k, value in enumerate(observed):
            assert mass[values < value].sum() <= upper_rank[k] + 1e-12
            assert mass[values <= value].sum() >= lower_rank[k] - 1e-12
    _, upper = transport_extrema(response, input_mass, upper_residual, upper_mass)
    lower, _ = transport_extrema(response, input_mass, lower_residual, lower_mass)
    upper_formula = min(input_mass[response <= -left_endpoint].sum(), min(upper_rank + h_rank))
    lower_formula = max(input_mass[response <= -right_endpoint].sum(), max(lower_rank + h_rank - 1))
    assert abs(upper - upper_formula) < 1e-8
    assert abs(lower - lower_formula) < 1e-8
    checks.append(max(abs(upper - upper_formula), abs(lower - lower_formula)))

report = {"atomic_cases": 240, "transport_lps": 760,
          "includes_threshold_equalities": True,
          "includes_single_distinct_residual": True,
          "includes_zero_width_rank_constraints": True,
          "includes_coincident_support_endpoints": True,
          "includes_singleton_support": True,
          "maximum_absolute_error": max(checks)}
Path("tmp/minimax_verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
